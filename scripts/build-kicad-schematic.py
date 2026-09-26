#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""Generate standalone KiCad 6 schematic skeletons for ARDF-MeshTuneFox80.

Reads
-----
  hardware/schematic/netlist.csv          181 pin-to-pin connections (data source)
  hardware/schematic/kicad-symbol-map.csv refdes -> suggested symbol / page / nets
  hardware/bom/bom-summary.csv            refdes -> parameter / package (authoritative BOM)

Writes (into hardware/schematic/)
---------------------------------
  atu-module.kicad_sch   pa-module.kicad_sch    lpf-module.kicad_sch
  mcu-ui.kicad_sch       power-module.kicad_sch core-board.kicad_sch
  interconnect.kicad_sch antenna.kicad_sch
  kicad-net-map.csv      (sheet,ref,pin_number,pin_name,net_label,label_kind)
  kicad-row-coverage.csv (row,net,net_label,src,dst,status,detail)
  kicad-build-report.md

Design rules (rationale: hardware/schematic/KIcad-skeleton-decision.md)
-----------------------------------------------------------------------
  * every symbol is defined inline in the file's own ``lib_symbols`` section, so
    KiCad never has to resolve an external symbol library;
  * one file per module, no hierarchical sheets - each file opens on its own;
  * a net that appears on more than one file (or is a power net) is written as
    ``global_label``, everything else as a local ``label``;
  * no wires at all: every pin carries a net label, so connectivity is explicit
    and no long wire can be drawn wrongly;
  * files are pure ASCII, UTF-8 without BOM, LF line endings;
  * ids are deterministic (SHA-1 seeded UUIDs, no timestamps) -> re-running the
    script byte-for-byte reproduces the same files.

Run:  python scripts/build-kicad-schematic.py
Check: python scripts/check-kicad-schematic.py
Stdout is ASCII only (the Windows console is GBK).
"""

from __future__ import annotations

import csv
import hashlib
import io
import os
import re
import sys

REPO = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
BOM_DIR = os.path.join(REPO, "hardware", "bom")
SCH_DIR = os.path.join(REPO, "hardware", "schematic")

NETLIST_CSV = os.path.join(SCH_DIR, "netlist.csv")
SYMBOL_MAP_CSV = os.path.join(SCH_DIR, "kicad-symbol-map.csv")
BOM_SUMMARY_CSV = os.path.join(BOM_DIR, "bom-summary.csv")

# ---------------------------------------------------------------------------
# KiCad file format constants
#
# version 20211123 is the KiCad 6.0 s-expression schematic version.  KiCad 6 is
# the oldest release that uses the s-expression .kicad_sch format, and it is the
# version the LCEDA "format converter" documents as supported (KiCad 6+), while
# KiCad 7/8/9 tokens ((exclude_from_sim), (dnp yes), (instances), (fields_autoplaced
# yes), (generator_version ...)) are deliberately NOT used.
# ---------------------------------------------------------------------------
FILE_VERSION = "20211123"
FILE_GENERATOR = "eeschema"

GRID = 2.54
PIN_LEN = 2.54
H_GAP = 17.78          # horizontal gap between symbol bounding boxes
V_GAP = 15.24          # vertical gap between placement rows
MARGIN = 15.24
NOTE_LINE = 5.08       # line pitch of the sheet note blocks
PAPERS = [("A4", 297.0, 210.0), ("A3", 420.0, 297.0),
          ("A2", 594.0, 420.0), ("A1", 841.0, 594.0)]

POWER_NETS = ("GND", "+12V", "+5V", "+3V3_DIG", "+3V3_RF", "VBAT")

# --all-global: emit global_label for every net.  Fallback for an importer that
# drops local labels; see hardware/schematic/IMPORT-TO-LCEDA.md.
ALL_GLOBAL = False


def is_global_net(net, net_sheets):
    return (ALL_GLOBAL or net in POWER_NETS or
            len(net_sheets.get(net, ())) > 1)


def uid(seed):
    """Deterministic RFC-4122-shaped (version 4) identifier."""
    h = hashlib.sha1(("ardf-meshtunefox80:" + seed).encode("utf-8")).hexdigest()
    h = h[:12] + "4" + h[13:16] + "8" + h[17:32]
    return "%s-%s-%s-%s-%s" % (h[0:8], h[8:12], h[12:16], h[16:20], h[20:32])


def num(v):
    """Format a coordinate: fixed 2 decimals, trailing zeros removed."""
    s = "%.2f" % v
    if "." in s:
        s = s.rstrip("0").rstrip(".")
    if s in ("-0", ""):
        s = "0"
    return s


def check_ascii(text, what):
    for ch in text:
        if ord(ch) > 127:
            raise SystemExit("NON-ASCII in %s: %r (in %r)"
                             % (what, ch, text[:80]))
    if '"' in text or "\\" in text:
        raise SystemExit("quote/backslash in %s: %r" % (what, text))


def ascii_safe(text):
    """Replace non-ASCII characters so a string can go into a .kicad_sch note.

    netlist.csv contains Chinese pin tokens (e.g. the relay coil pins).  The
    schematic files must stay pure ASCII, so such tokens are shown as '?' in the
    sheet note and identified by row number instead.
    """
    return "".join(ch if ord(ch) < 128 else "?" for ch in text)


# ---------------------------------------------------------------------------
# s-expression writer.  Using a tree (instead of string templates) makes
# unbalanced parentheses impossible by construction.
# ---------------------------------------------------------------------------
class Atom(object):
    __slots__ = ("text",)

    def __init__(self, text):
        self.text = str(text)
        check_ascii(self.text, "atom")

    def inline(self):
        return self.text


class QStr(object):
    __slots__ = ("text",)

    def __init__(self, text):
        self.text = str(text)
        check_ascii(self.text, "string")

    def inline(self):
        return '"%s"' % self.text


LINE_LIMIT = 72


class SList(object):
    __slots__ = ("items", "_inline")

    def __init__(self, *items):
        self.items = list(items)
        self._inline = None

    def inline(self):
        """The one-line rendering of this node, or '' when it must break."""
        if self._inline is None:
            parts = []
            ok = True
            for it in self.items:
                s = it.inline()
                if not s:
                    ok = False
                    break
                parts.append(s)
            joined = "(" + " ".join(parts) + ")"
            self._inline = joined if (ok and len(joined) <= LINE_LIMIT) else ""
        return self._inline


def a(text):
    return Atom(text)


def q(text):
    return QStr(text)


def L(*items):
    return SList(*items)


def render(node, level=0):
    """Render a node into a list of lines (KiCad-like line breaking)."""
    inline = node.inline()
    if inline:
        return ["  " * level + inline]
    indent = "  " * level
    lines = []
    line = indent + "("
    broken = False
    for it in node.items:
        sub = it.inline()
        if not broken and sub:
            cand = line + ("" if line.endswith("(") else " ") + sub
            if len(cand) <= LINE_LIMIT:
                line = cand
                continue
        if not broken:
            lines.append(line)
            broken = True
        lines.extend(render(it, level + 1))
    if not broken:
        lines.append(line)
    lines.append(indent + ")")
    return lines


# ---------------------------------------------------------------------------
# Custom symbol library.  Every symbol is drawn by this script, so the generated
# schematic files never reference an external library.
#
# "npins" is the electrical pin count of the real part.  For parts whose
# physical pin numbering is frozen in the docs (ULN2003A, TCA9535, ...) the pin
# *number* is the datasheet pin number.  For parts whose physical numbering is
# explicitly "waiting for incoming inspection / not frozen" (HK4100F relay,
# ESP32-C3 module, LCD module, ...) the pin number IS the functional name used
# by hardware/*/relay-wiring.md and docs/05 - no physical pin number is invented.
# ---------------------------------------------------------------------------
class Sym(object):
    def __init__(self, key, pins, hide_numbers=False, policy="FUNCTIONAL",
                 source="", note=""):
        self.key = key
        self.pins = pins          # list of (number, name, etype, side)
        self.hide_numbers = hide_numbers
        self.policy = policy
        self.source = source
        self.note = note
        self.alias = {}
        self.numbers = [p[0] for p in pins]
        self.names = dict((p[0], p[1]) for p in pins)

    def map_token(self, token):
        if token in self.alias:
            return self.alias[token]
        if token in self.numbers:
            return token
        return None


def LR(pins):
    """Give explicit sides: first half left, second half right."""
    half = (len(pins) + 1) // 2
    out = []
    for i, p in enumerate(pins):
        side = "L" if i < half else "R"
        out.append((p[0], p[1], p[2], p[3] if len(p) > 3 else side))
    return out


def P(number, name, etype, side):
    return (number, name, etype, side)


SYMBOLS = {}

# reference designator prefix used in the inline library definition
SYM_PREFIX = {"R": "R", "C": "C", "C_POL": "C", "L": "L", "D": "D",
              "ZENER": "D", "RELAY_SPDT": "K", "XFMR": "T", "BS170": "Q",
              "IRF510": "Q", "2N7002": "Q", "ULN2003A": "U", "TCA9535": "U",
              "SN74ACT244": "U", "LM358": "U", "ESP32C3_MODULE": "U",
              "ST7567_MODULE": "U", "SI5351A": "U", "BOOST_12V": "U",
              "MP2315": "U", "MD7673": "U", "MODULE_HEADER": "J", "SMA": "J",
              "USB_C": "J", "CONN_01x04": "J", "EC11": "U", "SW_PUSH": "SW",
              "BUZZER": "LS", "BATTERY": "BT", "FERRITE": "FB",
              "TESTPOINT": "TP", "CRYSTAL": "X"}


def defsym(key, pins, **kw):
    if not isinstance(pins[0], tuple) or len(pins[0]) < 4:
        pins = LR(pins)
    SYMBOLS[key] = Sym(key, pins, **kw)


# --- two terminal passives -------------------------------------------------
defsym("R", [P("1", "1", "passive", "L"), P("2", "2", "passive", "R")],
       hide_numbers=True, source="datasheet (2-terminal)")
defsym("C", [P("1", "1", "passive", "L"), P("2", "2", "passive", "R")],
       hide_numbers=True, source="datasheet (2-terminal)")
defsym("C_POL", [P("1", "+", "passive", "L"), P("2", "-", "passive", "R")],
       hide_numbers=True, source="datasheet (2-terminal, polarized)")
defsym("L", [P("1", "1", "passive", "L"), P("2", "2", "passive", "R")],
       hide_numbers=True, source="datasheet (2-terminal)")
defsym("D", [P("A", "A", "passive", "L"), P("K", "K", "passive", "R")],
       hide_numbers=True, source="datasheet (2-terminal)")

# --- Zener with the SOT-23 tab pin, BZX84 ---------------------------------
defsym("ZENER", [P("1", "A", "passive", "L"), P("3", "K", "passive", "R"),
                 P("2", "NC_TAB", "passive", "R")],
       hide_numbers=False, policy="PHYSICAL",
       source="BZX84 SOT-23 (1=A, 2=NC, 3=K) - CONFIRM against datasheet")
SYMBOLS["ZENER"].alias.update({"A": "1", "K": "3"})

# --- relay: HK4100F.  Physical pin numbers are NOT frozen, see
# hardware/atu-module/relay-wiring.md 2.5 ("must not be guessed"). ----------
defsym("RELAY_SPDT", [P("COIL+", "COIL+", "passive", "L"),
                      P("COIL-", "COIL-", "passive", "L"),
                      P("COM", "COM", "passive", "R"),
                      P("NO", "NO", "passive", "R"),
                      P("NC", "NC", "passive", "R")],
       source="relay-wiring.md 2.4/2.5 - functional names, pin numbers pending")
SYMBOLS["RELAY_SPDT"].alias.update({
    "\u7ebf\u5708+": "COIL+", "\u7ebf\u5708-": "COIL-"})

# --- tandem match transformer (FT37-43, 1 turn primary / 10 turn secondary)
defsym("XFMR", [P("P1", "P1", "passive", "L"), P("P2", "P2", "passive", "L"),
                P("SEC+", "SEC+", "passive", "R"), P("SEC-", "SEC-", "passive", "R")],
       source="atu-module/README.md 3; docs/05 3.2")
SYMBOLS["XFMR"].alias.update({"\u6b21\u7ea7+": "SEC+", "\u6b21\u7ea7-": "SEC-"})

# --- discrete transistors --------------------------------------------------
defsym("BS170", [P("1", "D", "passive", "L"), P("2", "G", "input", "L"),
                 P("3", "S", "passive", "R")],
       policy="PHYSICAL", source="BS170 TO-92 1=D 2=G 3=S")
SYMBOLS["BS170"].alias.update({"D": "1", "G": "2", "S": "3",
                               "D (\u5e76\u8054)": "1"})
defsym("IRF510", [P("1", "G", "input", "L"), P("2", "D", "passive", "R"),
                  P("3", "S", "passive", "R")],
       policy="PHYSICAL", source="IRF510 TO-220 1=G 2=D 3=S")
SYMBOLS["IRF510"].alias.update({"G": "1", "D": "2", "S": "3"})
defsym("2N7002", [P("1", "G", "input", "L"), P("2", "S", "passive", "L"),
                  P("3", "D", "passive", "R")],
       policy="PHYSICAL", source="2N7002 SOT-23 1=G 2=S 3=D")
SYMBOLS["2N7002"].alias.update({"G": "1", "S": "2", "D": "3"})

# --- relay driver, IO expander, line driver, op-amp ------------------------
defsym("ULN2003A", [P("1", "IN1", "input", "L"), P("2", "IN2", "input", "L"),
                    P("3", "IN3", "input", "L"), P("4", "IN4", "input", "L"),
                    P("5", "IN5", "input", "L"), P("6", "IN6", "input", "L"),
                    P("7", "IN7", "input", "L"), P("8", "GND", "power_in", "L"),
                    P("9", "COM", "passive", "L"),
                    P("10", "OUT7", "output", "R"), P("11", "OUT6", "output", "R"),
                    P("12", "OUT5", "output", "R"), P("13", "OUT4", "output", "R"),
                    P("14", "OUT3", "output", "R"), P("15", "OUT2", "output", "R"),
                    P("16", "OUT1", "output", "R")],
       policy="PHYSICAL", source="ULN2003A DIP/SOIC-16 datasheet pinout")
SYMBOLS["ULN2003A"].alias.update({
    "IN1": "1", "IN2": "2", "IN3": "3", "IN4": "4", "IN5": "5", "IN6": "6",
    "IN7": "7", "GND": "8", "COM": "9", "OUT1": "16", "OUT2": "15",
    "OUT3": "14", "OUT4": "13", "OUT5": "12", "OUT6": "11", "OUT7": "10"})

_tca = [P("1", "INT", "output", "L"), P("2", "A1", "input", "L"),
        P("3", "A2", "input", "L")]
for _i in range(8):
    _tca.append(P("%d" % (4 + _i), "P0.%d" % _i, "bidirectional", "L"))
_tca.append(P("12", "GND", "power_in", "L"))
for _i in range(8):
    _tca.append(P("%d" % (13 + _i), "P1.%d" % _i, "bidirectional", "R"))
_tca += [P("21", "A0", "input", "R"), P("22", "SCL", "input", "R"),
         P("23", "SDA", "bidirectional", "R"), P("24", "VCC", "power_in", "R")]
defsym("TCA9535", _tca, policy="PHYSICAL",
       source="TCA9535/PCA9535 TSSOP-24 datasheet pinout")
SYMBOLS["TCA9535"].alias.update({
    "INT": "1", "A1": "2", "A2": "3", "GND": "12", "A0": "21", "SCL": "22",
    "SDA": "23", "VCC": "24"})
for _i in range(8):
    SYMBOLS["TCA9535"].alias["P0.%d" % _i] = "%d" % (4 + _i)
    SYMBOLS["TCA9535"].alias["P1.%d" % _i] = "%d" % (13 + _i)

defsym("SN74ACT244", [P("1", "1OE", "input", "L"), P("2", "1A1", "input", "L"),
                      P("3", "1Y1", "output", "L"), P("4", "1A2", "input", "L"),
                      P("5", "1Y2", "output", "L"), P("6", "1A3", "input", "L"),
                      P("7", "1Y3", "output", "L"), P("8", "1A4", "input", "L"),
                      P("9", "1Y4", "output", "L"), P("10", "GND", "power_in", "L"),
                      P("11", "2Y4", "output", "R"), P("12", "2A4", "input", "R"),
                      P("13", "2Y3", "output", "R"), P("14", "2A3", "input", "R"),
                      P("15", "2Y2", "output", "R"), P("16", "2A2", "input", "R"),
                      P("17", "2Y1", "output", "R"), P("18", "2A1", "input", "R"),
                      P("19", "2OE", "input", "R"), P("20", "VCC", "power_in", "R")],
       policy="PHYSICAL", source="SN74x244 TSSOP-20 datasheet pinout")
SYMBOLS["SN74ACT244"].alias.update({
    "1A": "2", "1Y": "3", "2A": "18", "2Y": "17", "VCC": "20", "GND": "10",
    "1OE": "1", "2OE": "19"})

defsym("LM358", [P("1", "OUT1", "output", "L"), P("2", "IN1-", "input", "L"),
                 P("3", "IN1+", "input", "L"), P("4", "GND", "power_in", "L"),
                 P("5", "IN2+", "input", "R"), P("6", "IN2-", "input", "R"),
                 P("7", "OUT2", "output", "R"), P("8", "V+", "power_in", "R")],
       policy="PHYSICAL", source="LM358 DIP-8/SOIC-8 datasheet pinout")
SYMBOLS["LM358"].alias.update({"IN+": "3", "IN-": "2", "OUT": "1",
                               "V+": "8", "GND": "4"})

# --- modules / connectors whose physical numbering is not frozen -----------
ESP_PINS = [P("3V3", "3V3", "power_in", "L"), P("GND", "GND", "power_in", "L"),
            P("5V", "5V", "power_in", "L"), P("EN", "EN", "input", "L")]
for _g in [0, 1, 2, 3, 4, 5, 6, 7, 8, 9, 10, 11, 12, 13, 18, 19, 20, 21]:
    ESP_PINS.append(P("GPIO%d" % _g, "GPIO%d" % _g, "bidirectional", "L"))
defsym("ESP32C3_MODULE", ESP_PINS,
       source="docs/05 2.2 - module header pinout not frozen, names used as numbers")

defsym("ST7567_MODULE", [P("VDD/VDDIO", "VDD/VDDIO", "power_in", "L"),
                         P("VSS", "VSS", "power_in", "L"),
                         P("SCK/CLK", "SCK/CLK", "input", "L"),
                         P("MOSI/SI", "MOSI/SI", "input", "L"),
                         P("A0/DC", "A0/DC", "input", "L"),
                         P("CS", "CS", "input", "L"),
                         P("RST", "RST", "input", "L"),
                         P("V0/VOUT", "V0/VOUT", "passive", "L"),
                         P("LED+", "LED+", "passive", "R"),
                         P("LED-", "LED-", "passive", "R")],
       source="mcu-ui-module/README.md 4 - module flex pinout not frozen")
SYMBOLS["ST7567_MODULE"].alias["VDD"] = "VDD/VDDIO"

defsym("SI5351A", [P("CLK0", "CLK0", "output", "L"), P("CLK1", "CLK1", "output", "L"),
                   P("CLK2", "CLK2", "output", "L"), P("GND", "GND", "power_in", "L"),
                   P("XA", "XA", "passive", "L"), P("XB", "XB", "passive", "L"),
                   P("SDA", "SDA", "bidirectional", "R"), P("SCL", "SCL", "input", "R"),
                   P("VDDO", "VDDO", "power_in", "R"), P("VDD", "VDD", "power_in", "R")],
       source="Si5351A MSOP-10 - pin NUMBERS unverified, confirm against datasheet")

defsym("BOOST_12V", [P("VIN", "VIN", "power_in", "L"), P("GND", "GND", "power_in", "L"),
                     P("OUT", "OUT", "power_out", "R"), P("FB", "FB", "input", "R")],
       source="docs/05 3.3 - off-the-shelf boost module, pinout not frozen")

defsym("MP2315", [P("IN", "IN", "power_in", "L"), P("GND", "GND", "power_in", "L"),
                  P("EN", "EN", "input", "L"), P("BST", "BST", "passive", "L"),
                  P("SW", "SW", "output", "R"), P("FB", "FB", "input", "R"),
                  P("VCC", "VCC", "power_out", "R"), P("SS", "SS", "passive", "R")],
       source="MP2315 SOT-23-8 - pin NUMBERS unverified, confirm against datasheet")
SYMBOLS["MP2315"].alias.update({"VIN": "IN", "OUT": "SW"})

defsym("MD7673", [P("IN", "IN", "power_in", "L"), P("GND", "GND", "power_in", "L"),
                  P("EN", "EN", "input", "L"), P("NC", "NC", "passive", "L"),
                  P("OUT", "OUT", "power_out", "R")],
       source="MD7673 SOT-23-5 LDO typical pinout - confirm against datasheet")

defsym("MODULE_HEADER",
       [P("12V", "12V", "power_in", "L"), P("5V", "5V", "power_in", "L"),
        P("3V3_RF", "3V3_RF", "power_in", "L"), P("3V3_DIG", "3V3_DIG", "power_in", "L"),
        P("CTRL_GPIO", "CTRL_GPIO", "passive", "L"),
        P("ADC_SWR", "ADC_SWR", "passive", "L"),
        P("I2C_SDA", "I2C_SDA", "bidirectional", "R"),
        P("I2C_SCL", "I2C_SCL", "bidirectional", "R"),
        P("GND", "GND", "power_in", "R")],
       source="bom J1-J6 / pre-fab C-09 - module socket pinout not frozen")

defsym("SMA", [P("CENTER", "CENTER", "passive", "R"), P("SHIELD", "SHIELD", "passive", "L")],
       source="Conn_Coaxial")
SYMBOLS["SMA"].alias["\u4e2d\u5fc3"] = "CENTER"

defsym("USB_C", [P("VBUS", "VBUS", "power_in", "L"), P("GND", "GND", "power_in", "L"),
                 P("D+", "D+", "bidirectional", "R"), P("D-", "D-", "bidirectional", "R"),
                 P("CC1", "CC1", "bidirectional", "R"), P("CC2", "CC2", "bidirectional", "R"),
                 P("SHIELD", "SHIELD", "passive", "R")],
       source="USB Type-C receptacle")

defsym("CONN_01x04", [P("TX", "TX", "input", "L"), P("RX", "RX", "output", "L"),
                      P("3V3", "3V3", "power_in", "R"), P("GND", "GND", "power_in", "R")],
       source="Conn_01x04")

defsym("EC11", [P("A", "A", "passive", "L"), P("B", "B", "passive", "L"),
                P("C", "C", "passive", "L"), P("SW1", "SW1", "passive", "R"),
                P("SW2", "SW2", "passive", "R")],
       source="EC11 with push switch (5 pin) - numbering not frozen")
SYMBOLS["EC11"].alias.update({"SW": "SW1", "SW2 (\u53e6\u4e00\u7aef)": "SW2"})

defsym("SW_PUSH", [P("1", "1", "passive", "L"), P("2", "2", "passive", "R")],
       hide_numbers=True, source="SW_Push")
defsym("BUZZER", [P("+", "+", "passive", "L"), P("-", "-", "passive", "R")],
       hide_numbers=True, source="Buzzer")
defsym("BATTERY", [P("+", "+", "passive", "L"), P("-", "-", "passive", "R")],
       hide_numbers=True, source="Battery")
defsym("FERRITE", [P("IN", "IN", "passive", "L"), P("OUT", "OUT", "passive", "R")],
       hide_numbers=True, source="FerriteBead")
defsym("TESTPOINT", [P("TP", "TP", "passive", "R")],
       hide_numbers=True, source="TestPoint")
defsym("CRYSTAL", [P("1", "1", "passive", "L"), P("2", "2", "passive", "R")],
       hide_numbers=True, source="Crystal")

# ---------------------------------------------------------------------------
# mapping: kicad-symbol-map.csv "suggested symbol" -> our inline symbol key
# ---------------------------------------------------------------------------
SYM_FROM_SUGGESTION = {
    "MCU_Espressif:ESP32-C3": "ESP32C3_MODULE",
    "Oscillator:Si5351A-B-GT": "SI5351A",
    "Interface_Expansion:TCA9535": "TCA9535",
    "Transistor_Array:ULN2003A": "ULN2003A",
    "74xGxx:74ACT244": "SN74ACT244",
    "Regulator_Switching:MP2315": "MP2315",
    "Regulator_Linear:MD7673": "MD7673",
    "Module:Boost_Module_12V": "BOOST_12V",
    "Display:ST7567_128x64": "ST7567_MODULE",
    "Device:Rotary_Encoder_Switch": "EC11",
    "Amplifier_Operational:LM358": "LM358",
    "Relay:HK4100F-DC-12V": "RELAY_SPDT",
    "Device:Transformer_1P_SS": "XFMR",
    "Device:L": "L",
    "Device:C": "C",
    "Device:C_Polarized": "C_POL",
    "Diode:1N5711": "D",
    "Diode:HSMS-2850": "D",
    "Diode:BZX84C10": "ZENER",
    "Transistor_FET:BS170": "BS170",
    "Transistor_FET:IRF510": "IRF510",
    "Transistor_FET:2N7002": "2N7002",
    "Device:R": "R",
    "Device:Battery": "BATTERY",
    "Device:Crystal": "CRYSTAL",
    "Device:Buzzer": "BUZZER",
    "Switch:SW_Push": "SW_PUSH",
    "Connector_Generic:Conn_02x??_Odd_Even": "MODULE_HEADER",
    "Connector:Conn_Coaxial": "SMA",
    "Connector:USB_C_Receptacle": "USB_C",
    "Connector_Generic:Conn_01x04": "CONN_01x04",
    "Device:FerriteBead": "FERRITE",
    "Connector:TestPoint": "TESTPOINT",
}

# ---------------------------------------------------------------------------
# one file per module (no hierarchy).  Flow order = left-to-right placement.
# ---------------------------------------------------------------------------
SHEETS = [
    ("atu-module", "atu-module.kicad_sch",
     "ATU: tandem match coupler, detectors, relay switched L/C network",
     "hardware/atu-module/relay-wiring.md; docs/04 3.4; docs/05 3.2",
     ["J_ATU_IN", "T1", "T2", "R_sense_F", "R_sense_R", "D1", "D3", "D2", "D4",
      "U3", "L1", "L2", "L3", "K1", "K2", "K3", "K4", "K5", "K6", "C3", "C4", "C5",
      "U2", "R_RLY1", "R_RLY2", "R_RLY3", "R_RLY4", "R_RLY5", "R_RLY6"]),
    ("pa-module", "pa-module.kicad_sch",
     "PA: 3x BS170 class-E switch, 74ACT244 gate driver, fixed bias",
     "docs/04 3.2; docs/05 2.5/3.1; ADR-0008 3.2",
     ["U8", "R8", "R9", "R10", "R1", "R2", "Q1", "Q2", "Q3", "D5", "C6", "C244",
      "Q4", "J_PA_OUT"]),
    ("lpf-module", "lpf-module.kicad_sch",
     "LPF: 3rd order elliptic low pass filter (component values TBD)",
     "docs/04 3.3; hardware/lpf-module/README.md",
     ["L4", "C8", "L5", "C9", "L6", "C10"]),
    ("mcu-ui", "mcu-ui.kicad_sch",
     "MCU and UI: ESP32-C3, Si5351, TCA9535, ST7567 LCD, EC11, I2C/SPI pulls",
     "docs/05 2.2/2.3/2.7; ADR-0008 3.1; docs/04 3.5",
     ["U4", "U7", "U1", "U5", "U6", "Q5", "R_BL", "R_BL2", "R_BLLED",
      "R3", "R4", "R5", "R6", "R7", "R_VBAT1", "R_VBAT2", "R_VBAT3", "C_VBAT",
      "R12", "LS1", "SW1", "SW2", "X1", "J_USB", "J_UART"]),
    ("power-module", "power-module.kicad_sch",
     "Power: 2S battery, MP2315 5V buck, MD7673 3.3V RF LDO, 12V boost module",
     "docs/04 3.6; docs/05 3.3",
     ["BT1", "U9", "U10", "U11", "FB1", "C11", "C12", "C13", "C_3V3RF"]),
    ("core-board", "core-board.kicad_sch",
     "Base board: module sockets, RF SMA, test points, star ground",
     "docs/04 3.1; hardware/core-board/README.md; hardware/interconnect/README.md",
     ["J1", "J2", "J3", "J4", "J5", "J6", "J7", "J8", "J9", "J10",
      "TP1", "TP2", "TP3", "TP4", "TP5", "TP6", "TP7", "TP8"]),
    ("interconnect", "interconnect.kicad_sch",
     "Interconnect: module side SMA connectors and coax jumpers",
     "hardware/interconnect/README.md",
     ["J11", "J12", "J13", "J14", "J15", "J16"]),
    ("antenna", "antenna.kicad_sch",
     "Antenna: feed point and static discharge path",
     "docs/04 3.4; hardware/antenna/README.md",
     ["J_ANT", "R_esd"]),
]
SHEET_KEYS = [s[0] for s in SHEETS]

# the 图页 column of kicad-symbol-map.csv uses short module names
PAGE_TO_SHEET = {"atu": "atu-module", "pa": "pa-module", "lpf": "lpf-module",
                 "mcu-ui": "mcu-ui", "power": "power-module",
                 "core": "core-board", "interconnect": "interconnect",
                 "antenna": "antenna"}

# refs that appear in netlist.csv but not in kicad-symbol-map.csv -> derived here
DERIVED = {
    "R_BL": ("R", "mcu-ui", "docs/05 2.3 (TCA9535 P1.1 -> 2N7002 gate)"),
    "R_BL2": ("R", "mcu-ui", "docs/05 2.3 (gate pulldown)"),
    "R_BLLED": ("R", "mcu-ui", "docs/05 2.3 (backlight LED series resistor)"),
    "C244": ("C", "pa-module",
             "symbol map row 34 lists C6,C_decout; netlist uses C244 - same part"),
    "J_PA_OUT": ("SMA", "pa-module", "docs/05 4.1 PA output SMA"),
    "J_ATU_IN": ("SMA", "atu-module", "relay-wiring.md 2.1 ATU input SMA"),
    "J_ANT": ("SMA", "antenna", "docs/04 3.4 antenna socket"),
}
for _i in range(1, 7):
    DERIVED["R_RLY%d" % _i] = ("R", "atu-module",
                               "relay-wiring.md 4.2/4.4 ULN2003A input pulldown")

# refdes aliases: the netlist and the symbol map use two names for one part
REF_ALIAS = {"D5_prot": "D5", "C_decout": "C244"}

# net label aliases.  Each entry is justified by two rows of netlist.csv that
# share one component pin, i.e. the two labels provably name the same node.
# The row numbers are 1-based data rows (same numbering as kicad-row-coverage.csv).
NET_ALIAS = {
    "ANT_ESD": "ATU_L3_LO",        # rows 126/150 both carry J_ANT.CENTER
    "LCD_BL_GATE_PD": "LCD_BL_CTRL",  # rows 62/63 both carry Q5.G
    "RF_SRC_PD": "RF_SRC_CLK",     # rows 72/73 both carry U8.1A
    "PA_GATE_PD": "PA_GATE",       # rows 75/78 both carry Q1.G
    "DEC244": "+5V",               # rows 100/102 both carry U8.VCC
    "XFWD_SEC": "DET_FWD",         # rows 105/107 both carry R_sense_F.1
    "XREV_SEC": "DET_REV",         # rows 111/113 both carry R_sense_R.1
    "PA_BYPASS": "PA_DRAIN",       # rows 87/89 both carry Q1.D
    "LM358_IN": "ADC_FWD",         # rows 109/117 both carry D1.K
}
NET_ALIAS_WHY = {
    "ANT_ESD": "data rows 126 and 150 both land on J_ANT.CENTER",
    "LCD_BL_GATE_PD": "data rows 62 and 63 both land on Q5.G",
    "RF_SRC_PD": "data rows 72 and 73 both land on U8.1A",
    "PA_GATE_PD": "data rows 75 and 78 both land on Q1.G",
    "DEC244": "data rows 100 and 102 both land on U8.VCC",
    "XFWD_SEC": "data rows 105 and 107 both land on R_sense_F.1",
    "XREV_SEC": "data rows 111 and 113 both land on R_sense_R.1",
    "PA_BYPASS": "data rows 87 and 89 both land on Q1.D",
    "LM358_IN": "data rows 109 and 117 both land on D1.K",
}

# non-component endpoints.  A name that is also a net label acts as a net
# anchor:  "row: R12.1 -> PA_PWR_PWM" means R12.1 belongs to net PA_PWR_PWM.
PSEUDO_REFS = ("-", "GND", "+12V", "+5V", "+3V3_DIG", "+3V3_RF", "VBAT",
               "PA_PWR_PWM", "RESET_BOARD", "LCD_BIAS", "GND_DIG", "GND_RF",
               "GND_PWR")

# values that cannot be derived from the BOM without ending up with garbage
VALUE_FIX = {
    "K1": "HK4100F-DC-12V", "Q1": "BS170", "Q2": "BS170", "Q3": "BS170",
    "Q4": "IRF510-DNP", "D5": "BZX84-C10", "U1": "TCA9535",
    "U5": "ST7567-12864", "U6": "EC11", "U7": "Si5351A", "U9": "MP2315",
    "U10": "MD7673", "U11": "BOOST-12V-MODULE", "BT1": "2S-500mAh-7.4V",
    "FB1": "PI-RC-FILTER", "X1": "32.768kHz-DNP", "C11": "CAP-KIT",
    "T1": "FT37-43-10T", "R_sense_F": "1kohm", "U2": "ULN2003A",
}
for _r in ("C3", "C4", "C5", "C6", "C244", "C_VBAT", "C8", "C9", "C10",
           "C11", "C12", "C13", "C_3V3RF", "C14", "C15", "C16", "C17", "C18",
           "C19", "C20"):
    VALUE_FIX.setdefault(_r, None)
VALUE_FIX = dict((k, v) for k, v in VALUE_FIX.items() if v)

# refs that only exist in netlist.csv / the derived table (no BOM line)
VALUE_EXTRA = {
    "J_PA_OUT": "SMA-50ohm", "J_ATU_IN": "SMA-50ohm", "J_ANT": "SMA-50ohm",
    "J_USB": "USB-C", "J_UART": "Conn_01x04", "R_BLLED": "TBD-LED-R",
    "LS1": "BUZZER-3V3", "C244": "100nF", "C12": "CAP-KIT",
    "C13": "CAP-KIT", "C8": "TBD-NP0", "C9": "TBD-NP0", "C10": "TBD-NP0",
    "L4": "TBD-T106-6", "L5": "TBD-T106-6", "L6": "TBD-T106-6",
    "R_sense_R": "1kohm",
}
for _i in range(1, 9):
    VALUE_EXTRA["TP%d" % _i] = "TP"
for _i in range(1, 7):
    VALUE_EXTRA["R_RLY%d" % _i] = "10kohm"
    VALUE_EXTRA["J%d" % _i] = "2.54mm-HEADER"
    VALUE_EXTRA["J%d" % (_i + 10)] = "SMA-50ohm"
for _i in (7, 8, 9, 10):
    VALUE_EXTRA["J%d" % _i] = "SMA-50ohm"
VALUE_EXTRA["SW1"] = "TACT-SW"
VALUE_EXTRA["SW2"] = "TACT-SW"
VALUE_FIX.update(VALUE_EXTRA)

DNP_REFS = ("Q4", "X1")

# ---------------------------------------------------------------------------
# input readers
# ---------------------------------------------------------------------------

def read_csv(path):
    with io.open(path, "r", encoding="utf-8-sig", newline="") as f:
        return list(csv.DictReader(f))


def expand_refs(token):
    """Expand a BOM/symbol-map 位号 cell into a list of refdes."""
    token = re.sub(r"\([^)]*\)", " ", token or "")
    out = []
    for part in token.split(","):
        part = part.strip()
        if not part or part == "-":
            continue
        m = re.match(r"^([A-Za-z_]*?)(\d+)\s*(?:\.\.|-)\s*([A-Za-z_]*?)(\d+)$", part)
        if m:
            prefix = m.group(1) or m.group(3)
            lo, hi = int(m.group(2)), int(m.group(4))
            if 0 < lo <= hi <= lo + 64:
                for i in range(lo, hi + 1):
                    out.append("%s%d" % (prefix, i))
                continue
        out.append(part)
    return out


def ascii_extract(text):
    """Keep the ASCII runs of a (possibly Chinese) BOM cell."""
    runs = re.findall(r"[ -~]+", text or "")
    out = " ".join(r.strip() for r in runs if r.strip())
    out = re.sub(r"\s+", " ", out)
    for _ in range(3):
        out = re.sub(r"\(\s*\)", " ", out)
        out = re.sub(r"([(\[])\s*([)\]}])", " ", out)
    out = re.sub(r"\s+", " ", out).strip()
    out = out.strip(" ,;:/+-")
    return out


def build_bom_index():
    """refdes -> (value, package, source-of-value)."""
    idx = {}
    for row in read_csv(BOM_SUMMARY_CSV):
        for ref in expand_refs(row.get("位号", "")):
            if ref not in idx:
                idx[ref] = (ascii_extract(row.get("参数", "")),
                            row.get("封装", "").strip(),
                            ascii_extract(row.get("建议型号", "")))
    # one BOM line covers both sense resistors
    if "R_sense" in idx:
        idx["R_sense_F"] = idx["R_sense"]
        idx["R_sense_R"] = idx["R_sense"]
    return idx


def resolve_values(refs, bom):
    """refdes -> value (ASCII) with the source of the string recorded."""
    out = {}
    for ref in refs:
        if ref in VALUE_FIX:
            out[ref] = (VALUE_FIX[ref], "script override")
            continue
        v = bom.get(ref)
        if v:
            param, _pkg, suggested = v
            if param and len(param) >= 2:
                out[ref] = (param, "bom parameter")
                continue
            if suggested and len(ascii_extract(suggested)) >= 2:
                out[ref] = (ascii_extract(suggested), "bom suggested part")
                continue
        out[ref] = ("TBD", "not found in bom-summary.csv")
    return out


def build_symbol_map():
    """refdes -> dict(symbol=key, sheet=key, suggested=..., source=row)"""
    out = {}
    for rowno, row in enumerate(read_csv(SYMBOL_MAP_CSV), start=2):
        suggested = row["建议 KiCad 符号"].strip()
        key = SYM_FROM_SUGGESTION.get(suggested)
        if key is None:
            raise SystemExit("no inline symbol for suggestion %r" % suggested)
        pages = [p.strip() for p in row["图页"].split(";") if p.strip()]
        for ref in expand_refs(row["位号"]):
            ref = REF_ALIAS.get(ref, ref)
            out[ref] = {"symbol": key, "pages": pages, "suggested": suggested,
                        "source": "kicad-symbol-map.csv:%d" % rowno}
    return out


def sheet_of_ref(ref, entry):
    """Decide the sheet for a refdes.  See KIcad-skeleton-decision.md."""
    if entry is None:
        raise SystemExit("ref %s has no symbol/pages" % ref)
    if ref in ("J_ANT", "R_esd"):
        # antenna.kicad_sch would otherwise be empty; the antenna socket and its
        # ESD bleeder physically live together at the feed point.
        return "antenna"
    if ref in ("J7", "J8", "J9", "J10"):
        return "core-board"       # bom-summary: J7-J9 base board, J10 antenna socket
    if ref in ("J11", "J12", "J13", "J14", "J15", "J16", "J17", "J18", "J19",
               "J20", "J21", "J22", "J23", "J24"):
        return "interconnect"     # bom-summary: J11-J16 module side SMA
    page = entry["pages"][0]
    sheet = PAGE_TO_SHEET.get(page)
    if sheet is None:
        raise SystemExit("kicad-symbol-map page %r has no sheet" % page)
    return sheet


# ---------------------------------------------------------------------------
# netlist resolution
# ---------------------------------------------------------------------------
class Resolver(object):
    def __init__(self, ref_symbol, net_names):
        self.ref_symbol = ref_symbol
        self.net_names = net_names
        self.node_net = {}       # (ref, pin) -> net label
        self.node_row = {}       # (ref, pin) -> data row number
        self.node_alt = {}       # (ref, pin) -> [(net, row), ...] shadowed
        self.row_status = []     # per data row
        self.unresolved = []     # (row, net, reason)
        self.notes = []          # (row, net, text) rows with no component pin
        self.anchors = []        # (row, declared label, anchor net)

    def endpoint(self, ref_raw, pin_raw):
        raw = ref_raw.strip()
        ref = REF_ALIAS.get(raw, raw)
        if ref in self.ref_symbol:
            sym = SYMBOLS[self.ref_symbol[ref]]
            token = pin_raw.strip()
            pn = sym.map_token(token)
            if pn is None:
                return ("bad", None,
                        "row pin token '%s' is not a pin of %s (%s) - see "
                        "netlist.csv row" % (ascii_safe(pin_raw), ref, sym.key))
            return ("pin", (ref, pn), None)
        if ref in self.net_names:
            return ("net", ref, None)
        if ref in PSEUDO_REFS:
            # documented board level placeholder: "-" (no component at all),
            # GND_DIG / GND_RF / GND_PWR (star ground notes), RESET_BOARD,
            # LCD_BIAS (to-be-frozen sub-nodes)
            return ("doc", ref, None)
        return ("bad", None, "non-component ref '%s' is not a known net or "
                "placeholder" % ascii_safe(ref))

    def assign(self, node, net, rowno):
        """True when `node` ends up on `net` because of this row."""
        if node not in self.node_net:
            self.node_net[node] = net
            self.node_row[node] = rowno
            return True
        if self.node_net[node] == net:
            return True
        self.node_alt.setdefault(node, []).append((net, rowno))
        return False

    def pin_display(self, node):
        ref, pn = node
        return "%s.%s" % (ref, SYMBOLS[self.ref_symbol[ref]].names.get(pn, pn))

    def run(self, rows):
        for i, r in enumerate(rows, start=1):
            label = NET_ALIAS.get(r["net_label"], r["net_label"])
            st = self.endpoint(r["src_ref"], r["src_pin"])
            dt = self.endpoint(r["dst_ref"], r["dst_pin"])
            pins = [t for t in (st, dt) if t[0] == "pin"]
            nets = [t for t in (st, dt) if t[0] == "net"]
            # A trailing placeholder ref that happens to be a net name (e.g.
            # "R3.2 -> +3V3_DIG") pins the component onto that net.  A *leading*
            # rail placeholder ("+12V -> Q1.D", net PA_DRAIN) must NOT, because
            # the rail reaches the drain through the RF choke, i.e. through a
            # different node.
            target = label
            if len(pins) == 1 and len(nets) == 1 and dt[0] == "net":
                target = nets[0][1]
                if target != label:
                    self.anchors.append((i, label, target))
            oks, problems = [], []
            attached = []
            for t in pins:
                if self.assign(t[1], target, i):
                    oks.append(self.pin_display(t[1]))
                else:
                    problems.append("%s stays on %s (row %d)"
                                    % (self.pin_display(t[1]),
                                       self.node_net[t[1]], self.node_row[t[1]]))
                if self.node_net.get(t[1]) == target:
                    attached.append("%s.%s" % (t[1][0], t[1][1]))
            for t in (st, dt):
                if t[0] == "bad":
                    problems.append(t[2])
                    self.unresolved.append((i, r["net_label"], t[2]))
            if target != label and target in [n[1] for n in nets]:
                problems.append("netlist.csv declares net %s but the other end is "
                                "net name %s, so the pin was placed on %s"
                                % (label, target, target))
            if not pins:
                status = "NOTE"
                text = "; ".join(t[2] for t in (st, dt) if t[0] == "bad")
                self.notes.append((i, label, text or "label only, no component pin"))
            elif not oks:
                status = "SKIPPED"
            elif problems:
                status = "PARTIAL"
            else:
                status = "DRAWN"
            self.row_status.append({
                "row": i, "net": r["net"], "net_label": label,
                "src": "%s.%s" % (r["src_ref"], r["src_pin"]),
                "dst": "%s.%s" % (r["dst_ref"], r["dst_pin"]),
                "status": status, "pins": ";".join(attached),
                "detail": " | ".join(problems)})


# ---------------------------------------------------------------------------
# geometry
# ---------------------------------------------------------------------------
def geometry(sym):
    n = len(sym.pins)
    body_w = 12.7 if n <= 8 else 17.78 if n <= 16 else 22.86
    rows = max(sum(1 for p in sym.pins if p[3] == "L"),
               sum(1 for p in sym.pins if p[3] == "R"), 1)
    body_h = rows * GRID + 2 * GRID
    li = ri = 0
    local = {}
    for number, name, etype, side in sym.pins:
        if side == "L":
            y = (rows - 1) * GRID / 2.0 - li * GRID
            x = -(body_w / 2.0 + PIN_LEN)
            ang = 0
            li += 1
        else:
            y = (rows - 1) * GRID / 2.0 - ri * GRID
            x = (body_w / 2.0 + PIN_LEN)
            ang = 180
            ri += 1
        local[number] = (x, y, ang)
    return {"body_w": body_w, "body_h": body_h, "local": local,
            "w": body_w + 2 * PIN_LEN, "h": body_h}


def layout(flow, papers, sheet_geom):
    """Left-to-right, top-to-bottom placement.  Returns (paper, placements, info)."""
    for name, pw, ph in papers:
        x = MARGIN
        y = MARGIN
        row_h = 0.0
        placed = []
        ok = True
        for ref in flow:
            g = sheet_geom[ref]
            if x > MARGIN and x + g["w"] > pw - MARGIN:
                x = MARGIN
                y += row_h + V_GAP
                row_h = 0.0
            if x + g["w"] > pw - MARGIN:
                ok = False
                break
            placed.append((ref, x + g["w"] / 2.0, y + g["h"] / 2.0))
            x += g["w"] + H_GAP
            row_h = max(row_h, g["h"])
        if ok:
            return name, pw, ph, placed, y + row_h
    return None


# ---------------------------------------------------------------------------
# emit one sheet
# ---------------------------------------------------------------------------
def pin_label_effects(angle):
    if angle == 0:
        return L(a("effects"), L(a("font"), L(a("size"), a("1.27"), a("1.27"))),
                 L(a("justify"), a("left"), a("bottom")))
    return L(a("effects"), L(a("font"), L(a("size"), a("1.27"), a("1.27"))),
             L(a("justify"), a("right"), a("bottom")))


def global_label_effects(angle):
    if angle == 0:
        return L(a("effects"), L(a("font"), L(a("size"), a("1.27"), a("1.27"))),
                 L(a("justify"), a("left")))
    return L(a("effects"), L(a("font"), L(a("size"), a("1.27"), a("1.27"))),
             L(a("justify"), a("right")))


def lib_symbol_node(sym):
    items = [a("symbol"), q("ARDF:" + sym.key)]
    if sym.hide_numbers:
        items.append(L(a("pin_numbers"), a("hide")))
    items.append(L(a("pin_names"), L(a("offset"), a("1.016"))))
    items.append(L(a("in_bom"), a("yes")))
    items.append(L(a("on_board"), a("yes")))
    for pid, pname in (("Reference", SYM_PREFIX.get(sym.key, "U")),
                       ("Value", sym.key),
                       ("Footprint", ""), ("Datasheet", "~")):
        eff = [L(a("effects"), L(a("font"), L(a("size"), a("1.27"), a("1.27"))))]
        if pid in ("Footprint", "Datasheet"):
            eff = [L(a("effects"), L(a("font"), L(a("size"), a("1.27"), a("1.27"))),
                     a("hide"))]
        items.append(L(a("property"), q(pid), q(pname), L(a("id"), a(str(
            ("Reference", "Value", "Footprint", "Datasheet").index(pid)))),
            L(a("at"), a("0"), a("0"), a("0")), *eff))
    g = geometry(sym)
    items.append(L(a("symbol"), q("%s_0_1" % sym.key),
                   L(a("rectangle"),
                     L(a("start"), a(num(-g["body_w"] / 2.0)), a(num(g["body_h"] / 2.0))),
                     L(a("end"), a(num(g["body_w"] / 2.0)), a(num(-g["body_h"] / 2.0))),
                     L(a("stroke"), L(a("width"), a("0.254")), L(a("type"), a("default")),
                       L(a("color"), a("0"), a("0"), a("0"), a("0"))),
                     L(a("fill"), L(a("type"), a("none"))))))
    unit = [a("symbol"), q("%s_1_1" % sym.key)]
    for number, name, etype, _side in sym.pins:
        lx, ly, ang = g["local"][number]
        unit.append(L(a("pin"), a(etype), a("line"),
                      L(a("at"), a(num(lx)), a(num(ly)), a(str(int(ang)))),
                      L(a("length"), a(num(PIN_LEN))),
                      L(a("name"), q(name),
                        L(a("effects"), L(a("font"), L(a("size"), a("1.27"), a("1.27"))))),
                      L(a("number"), q(number),
                        L(a("effects"), L(a("font"), L(a("size"), a("1.27"), a("1.27")))))))
    items.append(SList(*unit))
    return SList(*items)


def text_node(text, x, y, scope, size=1.27):
    return L(a("text"), q(text), L(a("at"), a(num(x)), a(num(y)), a("0")),
             L(a("effects"), L(a("font"), L(a("size"), a(num(size)), a(num(size)))),
               L(a("justify"), a("left"), a("bottom"))),
             L(a("uuid"), a(uid("text:%s:%s:%s:%s"
                                % (scope, text, num(x), num(y))))))


def build_sheet(sheet, refs, meta, resolves):
    key, fname, title, docs, _flow = sheet
    sheet_uuid = uid("sheet:" + key)
    placements = meta["placements"]
    paper = meta["paper"]
    notes = meta["notes"]

    # which nets are global?  nets on 2+ sheets, plus every power net.
    # resolves.net_sheets is computed once, over all sheets, in main().
    net_sheets = resolves.net_sheets

    root = [a("kicad_sch"),
            L(a("version"), a(FILE_VERSION)), L(a("generator"), a(FILE_GENERATOR)),
            L(a("uuid"), a(sheet_uuid)), L(a("paper"), q(paper)),
            L(a("title_block"),
              L(a("title"), q(title)),
              L(a("rev"), q("V1.0-skeleton")),
              L(a("comment"), a("1"),
                q("Auto-generated skeleton - see hardware/schematic/IMPORT-TO-LCEDA.md"))),
            ]

    # --- lib_symbols: only the symbols actually placed on this sheet ---------
    used = []
    for ref, _x, _y in placements:
        s = resolves.ref_symbol[ref]
        if s not in used:
            used.append(s)
    libs = [a("lib_symbols")]
    for s in used:
        libs.append(lib_symbol_node(SYMBOLS[s]))
    root.append(SList(*libs))

    # --- labels -------------------------------------------------------------
    for ref, cx, cy in placements:
        s = SYMBOLS[resolves.ref_symbol[ref]]
        g = geometry(s)
        for number, name, _etype, _side in s.pins:
            lx, ly, _ang = g["local"][number]
            px, py = cx + lx, cy - ly
            net = resolves.node_net.get((ref, number))
            if net is None:
                continue
            is_global = is_global_net(net, net_sheets)
            if is_global:
                root.append(L(a("global_label"), q(net), L(a("shape"), a("input")),
                              L(a("at"), a(num(px)), a(num(py)), a("0") if lx > 0 else a("180")),
                              L(a("fields_autoplaced")),
                              global_label_effects(0 if lx > 0 else 180),
                              L(a("uuid"), a(uid("glabel:%s:%s:%s" % (key, ref, number)))),
                              L(a("property"), q("Intersheetrefs"), q("${INTERSHEET_REFS}"),
                                L(a("id"), a("0")),
                                L(a("at"), a(num(px)), a(num(py)), a("0")),
                                L(a("effects"), L(a("font"), L(a("size"), a("1.27"), a("1.27"))),
                                  a("hide")))))
            else:
                root.append(L(a("label"), q(net),
                              L(a("at"), a(num(px)), a(num(py)), a("0") if lx > 0 else a("180")),
                              pin_label_effects(0 if lx > 0 else 180),
                              L(a("uuid"), a(uid("label:%s:%s:%s" % (key, ref, number))))))

    # --- symbol instances ---------------------------------------------------
    inst_paths = []
    for ref, cx, cy in placements:
        skey = resolves.ref_symbol[ref]
        s = SYMBOLS[skey]
        g = geometry(s)
        value, _value_src = resolves.values[ref]
        dnp = ref in DNP_REFS
        items = [a("symbol"), L(a("lib_id"), q("ARDF:" + skey)),
                 L(a("at"), a(num(cx)), a(num(cy)), a("0")), L(a("unit"), a("1")),
                 L(a("in_bom"), a("no") if dnp else a("yes")),
                 L(a("on_board"), a("yes")),
                 L(a("uuid"), a(uid("symbol:%s:%s" % (key, ref))))]
        items.append(L(a("property"), q("Reference"), q(ref), L(a("id"), a("0")),
                       L(a("at"), a(num(cx)), a(num(cy - g["body_h"] / 2.0 - 2.54)), a("0")),
                       L(a("effects"), L(a("font"), L(a("size"), a("1.27"), a("1.27"))))))
        items.append(L(a("property"), q("Value"), q(value), L(a("id"), a("1")),
                       L(a("at"), a(num(cx)), a(num(cy + g["body_h"] / 2.0 + 2.54)), a("0")),
                       L(a("effects"), L(a("font"), L(a("size"), a("1.27"), a("1.27"))))))
        for pid, idn in (("Footprint", 2), ("Datasheet", 3)):
            items.append(L(a("property"), q(pid), q("" if pid == "Footprint" else "~"),
                           L(a("id"), a(str(idn))),
                           L(a("at"), a(num(cx)), a(num(cy)), a("0")),
                           L(a("effects"), L(a("font"), L(a("size"), a("1.27"), a("1.27"))),
                             a("hide"))))
        for number, _n, _e, _s in s.pins:
            items.append(L(a("pin"), q(number),
                           L(a("uuid"), a(uid("pin:%s:%s:%s" % (key, ref, number))))))
        root.append(SList(*items))
        inst_paths.append((ref, value))

    # --- notes --------------------------------------------------------------
    for i, line in enumerate(notes):
        root.append(text_node(line, MARGIN, meta["notes_y"] + i * NOTE_LINE, key))

    root.append(L(a("sheet_instances"), L(a("path"), q("/"), L(a("page"), q("1")))))
    si = [a("symbol_instances")]
    for ref, value in inst_paths:
        si.append(L(a("path"), q("/" + sheet_uuid),
                    L(a("reference"), q(ref)), L(a("unit"), a("1")),
                    L(a("value"), q(value)), L(a("footprint"), q(""))))
    root.append(SList(*si))

    return render(SList(*root)), net_sheets


# ---------------------------------------------------------------------------
# main
# ---------------------------------------------------------------------------
USAGE = """usage: build-kicad-schematic.py [--all-global] [--help]

Generates the 8 standalone KiCad 6 (.kicad_sch) module schematics in
hardware/schematic/ plus kicad-net-map.csv, kicad-row-coverage.csv and
kicad-build-report.md.

  --all-global   write every net as a global_label (fallback for an importer
                 that drops local labels); default mode uses global labels only
                 for power nets and for nets that span more than one sheet
  --help         show this text

Exit codes: 0 ok, 1 input/consistency error, 2 usage error."""


def main():
    global ALL_GLOBAL
    args = sys.argv[1:]
    if "--help" in args or "-h" in args:
        print(USAGE)
        return 0
    unknown = [x for x in args if x != "--all-global"]
    if unknown:
        sys.stderr.write("unknown argument(s): %s\n\n%s\n"
                         % (" ".join(unknown), USAGE))
        return 2
    if "--all-global" in args:
        ALL_GLOBAL = True
    rows = read_csv(NETLIST_CSV)
    sym_map = build_symbol_map()
    bom = build_bom_index()

    # ---- refdes -> symbol key / sheet / value -----------------------------
    ref_symbol = {}
    ref_sheet = {}
    for ref, entry in sym_map.items():
        ref_symbol[ref] = entry["symbol"]
        ref_sheet[ref] = sheet_of_ref(ref, entry)
    for ref, (skey, sh, _why) in DERIVED.items():
        ref_symbol[ref] = skey
        ref_sheet[ref] = sh
    unplaced = []
    for r in rows:
        for side in ("src", "dst"):
            ref = REF_ALIAS.get(r[side + "_ref"].strip(), r[side + "_ref"].strip())
            if ref in ref_symbol or ref in PSEUDO_REFS:
                continue
            if ref not in unplaced:
                unplaced.append(ref)
    if unplaced:
        raise SystemExit("netlist refs with no symbol/sheet: %s" % unplaced)

    place = []
    for sh in SHEET_KEYS:
        place.append((sh, [r for r in ref_symbol
                           if ref_sheet[r] == sh]))
    unresolved_pages = [r for r in ref_symbol if ref_sheet.get(r) not in SHEET_KEYS]
    if unresolved_pages:
        raise SystemExit("refs with unknown sheet: %s" % unresolved_pages)

    # ---- resolve connectivity --------------------------------------------
    net_names = set(NET_ALIAS.get(r["net_label"], r["net_label"]) for r in rows)
    res = Resolver(ref_symbol, net_names)
    for sh, flow in ((s[0], s[4]) for s in SHEETS):
        for ref in flow:
            if ref not in ref_symbol:
                raise SystemExit("sheet %s flow lists unknown ref %s" % (sh, ref))
    extra = [r for r in ref_symbol if r not in
             [x for s in SHEETS for x in s[4]]]
    if extra:
        raise SystemExit("refs not present in any sheet flow order: %s" % extra)
    res.run(rows)
    res.values = resolve_values(sorted(ref_symbol), bom)
    res.ref_symbol = ref_symbol
    res.ref_sheet = ref_sheet

    # ---- geometry / paper selection / notes -------------------------------
    sheet_geom = {}
    for sh, flow in ((s[0], s[4]) for s in SHEETS):
        for ref in flow:
            sheet_geom[(sh, ref)] = geometry(SYMBOLS[ref_symbol[ref]])

    build = {}
    net_sheets = {}
    for sheet in SHEETS:
        key, fname, title, docs, flow = sheet
        notes = sheet_notes(key, flow, res, rows)
        note_h = len(notes) * NOTE_LINE + V_GAP
        geom = dict((ref, sheet_geom[(key, ref)]) for ref in flow)
        got = None
        for i in range(len(PAPERS)):
            r = layout(flow, PAPERS[i:i + 1], geom)
            if r is None:
                continue
            nm, pw, ph, placed, bottom = r
            if bottom + note_h + MARGIN <= ph:
                got = (nm, pw, ph, placed, bottom)
                break
        if got is None:
            nm, pw, ph, placed, bottom = layout(flow, [PAPERS[-1]], geom)
            note_h = 0.0
            got = (nm, pw, ph, placed, bottom)
        nm, pw, ph, placed, bottom = got
        build[key] = {"paper": nm, "placements": placed,
                      "notes": notes, "notes_y": bottom + V_GAP}
        for ref, _x, _y in placed:
            for (r, pn), net in res.node_net.items():
                if r == ref:
                    net_sheets.setdefault(net, set()).add(key)
    res.net_sheets = net_sheets

    # ---- write the schematic files ---------------------------------------
    written = []
    for sheet in SHEETS:
        key, fname, title, docs, flow = sheet
        text, _ns = build_sheet(sheet, [r for r, _x, _y in build[key]["placements"]],
                                build[key], res)
        text = "\n".join(text)
        path = os.path.join(SCH_DIR, fname)
        with io.open(path, "w", encoding="ascii", newline="\n") as f:
            f.write(text + "\n")
        written.append((fname, path, len(text.splitlines()),
                        os.path.getsize(path)))

    # ---- machine readable manifests --------------------------------------
    netmap = []
    for sheet in SHEETS:
        key = sheet[0]
        for ref, _x, _y in build[key]["placements"]:
            s = SYMBOLS[ref_symbol[ref]]
            for number, name, _e, _sd in s.pins:
                net = res.node_net.get((ref, number))
                if net is None:
                    continue
                kind = "global" if is_global_net(net, net_sheets) else "local"
                netmap.append({"sheet": key, "ref": ref, "pin_number": number,
                               "pin_name": name, "net_label": net,
                               "label_kind": kind})
    write_csv(os.path.join(SCH_DIR, "kicad-net-map.csv"),
              ["sheet", "ref", "pin_number", "pin_name", "net_label", "label_kind"],
              netmap)
    write_csv(os.path.join(SCH_DIR, "kicad-row-coverage.csv"),
              ["row", "net", "net_label", "src", "dst", "status", "pins",
               "detail"],
              res.row_status)

    # ---- report -----------------------------------------------------------
    report = build_report(build, res, sym_map, bom, ref_symbol, ref_sheet,
                          netmap, rows, written)
    with io.open(os.path.join(SCH_DIR, "kicad-build-report.md"), "w",
                 encoding="utf-8", newline="\n") as f:
        f.write(report)

    # ---- stdout ----------------------------------------------------------
    for fname, path, lines, size in written:
        print("WROTE %-24s lines=%-5d bytes=%d" % (fname, lines, size))
    st = {}
    for r in res.row_status:
        st[r["status"]] = st.get(r["status"], 0) + 1
    print("ROWS total=%d %s" % (len(res.row_status),
                                " ".join("%s=%d" % kv for kv in sorted(st.items()))))
    print("NETS  pins_with_net=%d labels=%d" % (len(netmap), len(
        set(m["net_label"] for m in netmap))))
    print("WARN  unresolved_endpoints=%d shadowed_labels=%d note_rows=%d"
          % (len(res.unresolved),
             sum(len(v) for v in res.node_alt.values()), len(res.notes)))
    return 0


def sheet_notes(key, flow, res, rows):
    """Human readable note block printed at the bottom of every sheet."""
    meta = dict((s[0], s) for s in SHEETS)[key]
    notes = []
    notes.append("%s - AUTO-GENERATED SKELETON, REVIEW BEFORE USE" % key.upper())
    notes.append("Source: %s" % meta[3])
    notes.append("Generator: scripts/build-kicad-schematic.py "
                 "(KiCad 6 s-expression, version %s)" % FILE_VERSION)
    notes.append("All symbols are defined inside this file (lib_symbols ARDF:*); "
                 "no external symbol library is required.")
    notes.append("No wires are drawn - every pin carries a net label. Nets used on "
                 "more than one sheet, and all power nets, use global labels.")
    if ALL_GLOBAL:
        notes.append("MODE: --all-global (every net is a global label).")
    shadow = []
    for (ref, pn), alts in res.node_alt.items():
        if ref not in flow:
            continue
        for net, rowno in alts:
            shadow.append("%s.%s row %d also lists net %s (kept %s)"
                          % (ref, pn, rowno, net, res.node_net[(ref, pn)]))
    if shadow:
        notes.append("CONFLICTING NET CLAIMS: netlist.csv names two different nets on "
                     "one pin; only the first was applied (under-connect, not short):")
        notes.extend("  " + s for s in sorted(shadow)[:10])
        if len(shadow) > 10:
            notes.append("  (+%d more - see kicad-build-report.md section 6)"
                         % (len(shadow) - 10))
    flowset = set(flow)
    orphans = [ref for ref in flow
               if not any(r == ref for (r, _p) in res.node_net)]
    if orphans:
        notes.append("No row in netlist.csv (placed unconnected on purpose, "
                     "wiring is still to be designed):")
        line = "  " + ", ".join(orphans)
        while len(line) > 110:
            cut = line.rfind(",", 0, 110)
            notes.append(line[:cut + 1])
            line = "  " + line[cut + 2:]
        notes.append(line)
    bad = []
    for r in res.row_status:
        if r["status"] == "DRAWN":
            continue
        src_ref = REF_ALIAS.get(rows[r["row"] - 1]["src_ref"].strip(),
                                rows[r["row"] - 1]["src_ref"].strip())
        dst_ref = REF_ALIAS.get(rows[r["row"] - 1]["dst_ref"].strip(),
                                rows[r["row"] - 1]["dst_ref"].strip())
        if src_ref in flowset or dst_ref in flowset:
            bad.append("row %d (%s): %s" % (r["row"], r["net_label"], r["detail"]))
    if bad:
        notes.append("ROWS THIS MODULE CANNOT CARRY VERBATIM (%d):" % len(bad))
        notes.extend("  " + s for s in bad[:10])
        if len(bad) > 10:
            notes.append("  (+%d more - see kicad-build-report.md section 6)"
                         % (len(bad) - 10))
    return notes


def write_csv(path, header, rows):
    buf = io.StringIO()
    w = csv.DictWriter(buf, fieldnames=header, lineterminator="\n")
    w.writeheader()
    for r in rows:
        w.writerow(r)
    with io.open(path, "w", encoding="utf-8", newline="\n") as f:
        f.write(buf.getvalue())


def build_report(build, res, sym_map, bom, ref_symbol, ref_sheet, netmap, rows,
                 written):
    L_ = []
    A = L_.append
    A("# KiCad schematic build report (generated)\n")
    A("> Generated by `scripts/build-kicad-schematic.py` - do not edit by hand.")
    A("> Machine readable companions: `kicad-net-map.csv`, `kicad-row-coverage.csv`.\n")
    A("## 1. Files\n")
    A("| file | lines | bytes | symbols | sheet |")
    A("|---|---|---|---|---|")
    cnt = {}
    for m in netmap:
        cnt[m["sheet"]] = cnt.get(m["sheet"], 0) + 0
    for fname, path, lines, size in written:
        key = fname[:-len(".kicad_sch")]
        A("| `%s` | %d | %d | %d | %s |" % (fname, lines, size,
                                            len(build[key]["placements"]),
                                            build[key]["paper"]))
    st = {}
    for r in res.row_status:
        st[r["status"]] = st.get(r["status"], 0) + 1
    A("\n## 2. Netlist coverage\n")
    A("| status | rows | meaning |")
    A("|---|---|---|")
    A("| DRAWN | %d | both endpoints carry the net label |" % st.get("DRAWN", 0))
    A("| DRAWN_PARTIAL | %d | at least one endpoint carries the label; the other "
      "end is a placeholder ref, an un-resolvable pin token, or was claimed by "
      "another net first |" % st.get("DRAWN_PARTIAL", 0))
    A("| NOTE | %d | no component pin in the row (label-only / board-level note); "
      "recorded as sheet text instead |" % st.get("NOTE", 0))
    A("| **total** | **%d** | netlist.csv data rows |" % len(res.row_status))

    A("\n## 3. Every net and where it lands\n")
    A("| net | sheets | pins | kind |")
    A("|---|---|---|---|")
    per = {}
    for m in netmap:
        per.setdefault(m["net_label"], []).append(m)
    for net in sorted(per):
        ms = per[net]
        sheets = sorted(set(m["sheet"] for m in ms))
        A("| `%s` | %s | %s | %s |" % (
            net, ", ".join(sheets),
            ", ".join("%s.%s" % (m["ref"], m["pin_number"]) for m in ms),
            ms[0]["label_kind"]))

    A("\n## 4. Symbol library (all inline in lib_symbols)\n")
    A("| lib_id | pins | pin numbering | provenance |")
    A("|---|---|---|---|")
    for k in sorted(set(ref_symbol.values())):
        s = SYMBOLS[k]
        A("| `ARDF:%s` | %d | %s | %s |" % (k, len(s.pins), s.policy, s.source))

    A("\n## 5. Pin numbers / names that are NOT frozen by the documentation\n")
    A("Rows below are the reason a symbol carries a functional name instead of a "
      "physical pin number. All of them must be confirmed against the real part "
      "before the board is ordered.\n")
    A("| lib_id | issue |")
    A("|---|---|")
    A("| `ARDF:RELAY_SPDT` | `relay-wiring.md` 2.5 forbids guessing COM/NO/NC pad "
      "numbers; the pin number IS the function name |")
    A("| `ARDF:ESP32C3_MODULE` | module header pinout not frozen (docs/05 2.1/2.2) |")
    A("| `ARDF:ST7567_MODULE` | module flex pinout not frozen (mcu-ui README 3/4) |")
    A("| `ARDF:SI5351A`, `ARDF:MP2315`, `ARDF:MD7673` | MSOP-10 / SOT-23-8 / "
      "SOT-23-5 pin numbers unverified |")
    A("| `ARDF:MODULE_HEADER` | J1-J6 socket pinout is pre-fab checklist item C-09 |")
    A("| `ARDF:BOOST_12V`, `ARDF:EC11`, `ARDF:SMA` | functional pin names only |")

    A("\n## 6. Rows that could not be drawn exactly as written\n")
    A("| row | net | src | dst | status | detail |")
    A("|---|---|---|---|---|---|")
    for r in res.row_status:
        if r["status"] != "DRAWN":
            A("| %d | `%s` | `%s` | `%s` | %s | %s |" % (
                r["row"], r["net_label"], r["src"], r["dst"], r["status"],
                r["detail"].replace("|", "\\|")))

    A("\n## 7. Net label aliases applied\n")
    A("| label in netlist.csv | canonical label | justification |")
    A("|---|---|---|")
    for k in sorted(NET_ALIAS):
        A("| `%s` | `%s` | %s |" % (k, NET_ALIAS[k], NET_ALIAS_WHY[k]))

    A("\n## 8. Values used for the Value field\n")
    A("| ref | value | source |")
    A("|---|---|---|")
    for ref in sorted(res.values):
        A("| `%s` | `%s` | %s |" % (ref, res.values[ref][0], res.values[ref][1]))

    A("\n## 9. Refs placed but not connected by netlist.csv\n")
    A("These come from `kicad-symbol-map.csv` (or the derived table) and have no "
      "row in `netlist.csv`, so they are placed unconnected on purpose.\n")
    conn = set(m["ref"] for m in netmap)
    orphan = [r for r in sorted(ref_symbol) if r not in conn]
    A(", ".join("`%s`" % r for r in orphan) if orphan else "_none_")
    A("")
    return "\n".join(L_)


if __name__ == "__main__":
    sys.exit(main())
