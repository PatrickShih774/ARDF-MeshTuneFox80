#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""Self-check the generated KiCad schematics (no KiCad installation needed).

What it verifies
----------------
  A  encoding      no BOM, LF only, pure ASCII (.kicad_sch must be ASCII)
  B  syntax        real s-expression parse (so parentheses must balance),
                   root token ``kicad_sch``, version 20211123, and no KiCad
                   7/8/9-only token that would break a KiCad 6 reader
  C  library       every ``(lib_id "ARDF:X")`` used by an instance is defined in
                   that file's own ``lib_symbols``; every ``(pin "N")`` in the
                   instance exists in the library definition, with an identical
                   pin set; every instance has Reference/Value/Footprint/Datasheet
  D  connectivity  every label/global_label sits exactly on a pin connection
                   point or a wire endpoint (a label floating in space would
                   silently lose its net); no pin carries two labels (which
                   would short two nets); uuids are unique
  E  cross file    reference designators and uuids unique over all files; a net
                   that appears on more than one sheet is a global label
                   everywhere; power nets are always global
  F  manifests     kicad-net-map.csv reproduces exactly the pin->net map that is
                   really in the files; kicad-row-coverage.csv accounts for all
                   181 netlist.csv rows with no SKIPPED row
  G  control group the hand written minimal schematic must PASS and four
                   deliberately broken files must FAIL - this proves the checker
                   itself is not a no-op

Usage
-----
    python scripts/check-kicad-schematic.py            # full run (exit 0 = pass)
    python scripts/check-kicad-schematic.py --quiet    # only failures + summary

Stdout is ASCII only (the Windows console is GBK).
"""

from __future__ import annotations

import csv
import io
import os
import sys

REPO = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
SCH_DIR = os.path.join(REPO, "hardware", "schematic")
TEST_DIR = os.path.join(SCH_DIR, "tests")

SHEET_FILES = ["atu-module.kicad_sch", "pa-module.kicad_sch",
               "lpf-module.kicad_sch", "mcu-ui.kicad_sch",
               "power-module.kicad_sch", "core-board.kicad_sch",
               "interconnect.kicad_sch", "antenna.kicad_sch"]
NET_MAP = os.path.join(SCH_DIR, "kicad-net-map.csv")
ROW_COVERAGE = os.path.join(SCH_DIR, "kicad-row-coverage.csv")
NETLIST = os.path.join(SCH_DIR, "netlist.csv")

FILE_VERSION = "20211123"
POWER_NETS = ("GND", "+12V", "+5V", "+3V3_DIG", "+3V3_RF", "VBAT")
PAPER_MM = {"A5": (210.0, 148.0), "A4": (297.0, 210.0), "A3": (420.0, 297.0),
            "A2": (594.0, 420.0), "A1": (841.0, 594.0), "A0": (1189.0, 841.0),
            "A": (279.4, 215.9), "B": (431.8, 279.4), "C": (558.8, 431.8),
            "D": (863.6, 558.8), "E": (1117.6, 863.6)}

# tokens that only exist in KiCad 7/8/9 - a KiCad 6 reader may choke on them
FORBIDDEN = ["exclude_from_sim", "generator_version", "embedded_fonts",
             "exclude_from_bom", "exclude_from_board"]

FIXTURES_PASS = ["minimal-1r-1label.kicad_sch"]
FIXTURES_FAIL = [
    ("bad-01-unbalanced-paren.kicad_sch", "B01"),
    ("bad-02-missing-lib-symbol.kicad_sch", "C02"),
    ("bad-03-dangling-label.kicad_sch", "D01"),
    ("bad-04-pin-not-in-symbol.kicad_sch", "C03"),
    ("bad-05-nonascii.kicad_sch", "A03"),
]


class QS(str):
    """A quoted string token (kept distinguishable from a bare atom)."""


class ParseError(Exception):
    pass


def parse(text):
    """Parse an s-expression into nested lists of str / QS."""
    n = len(text)
    pos = [0]

    def skip_ws():
        while pos[0] < n and text[pos[0]] in " \t\r\n":
            pos[0] += 1

    def node():
        skip_ws()
        if pos[0] >= n:
            raise ParseError("unexpected end of file")
        c = text[pos[0]]
        if c == "(":
            pos[0] += 1
            items = []
            while True:
                skip_ws()
                if pos[0] >= n:
                    raise ParseError("unexpected end of file inside a list "
                                     "(missing ')')")
                if text[pos[0]] == ")":
                    pos[0] += 1
                    return items
                items.append(node())
        if c == ")":
            raise ParseError("stray ')' at offset %d" % pos[0])
        if c == '"':
            pos[0] += 1
            buf = []
            while True:
                if pos[0] >= n:
                    raise ParseError("unterminated string")
                ch = text[pos[0]]
                if ch == "\\":
                    buf.append(text[pos[0]:pos[0] + 2])
                    pos[0] += 2
                    continue
                if ch == '"':
                    pos[0] += 1
                    return QS("".join(buf))
                buf.append(ch)
                pos[0] += 1
        start = pos[0]
        while pos[0] < n and text[pos[0]] not in " \t\r\n()\"":
            pos[0] += 1
        if pos[0] == start:
            raise ParseError("empty token at offset %d" % pos[0])
        return text[start:pos[0]]

    tree = node()
    skip_ws()
    if pos[0] != n:
        raise ParseError("trailing content at offset %d" % pos[0])
    if not isinstance(tree, list):
        raise ParseError("top level is not a list")
    return tree


def head(n):
    if isinstance(n, list) and n and isinstance(n[0], str):
        return str(n[0])
    return None


def kids(n, name):
    return [c for c in n if isinstance(c, list) and head(c) == name]


def kid(n, name):
    k = kids(n, name)
    return k[0] if k else None


def text_of(node):
    """The first quoted/numbered argument of a node like (at 1 2 3)."""
    for it in node[1:]:
        if isinstance(it, str):
            return str(it)
    return None


class Sheet(object):
    def __init__(self, path):
        self.path = path
        self.name = os.path.basename(path)
        with io.open(path, "rb") as f:
            self.raw = f.read()
        self.text = self.raw.decode("ascii", "replace") if all(
            b < 128 for b in self.raw) else None
        self.tree = None
        self.lib = {}          # lib name -> {pin number: (x, y, ang)}
        self.inst = []         # (ref, lib_id, cx, cy, rot, [pin numbers])
        self.labels = []       # (kind, text, x, y)
        self.wires = []        # (x, y)
        self.uuids = []
        self.pinpoints = {}    # (x, y) -> (ref, pin number)
        self.bbox = {}         # lib name -> (minx, miny, maxx, maxy) local
        self.paper = None
        self.texts = []        # (x, y)
        self.bad = []          # (code, message)

    def err(self, code, msg):
        self.bad.append((code, msg))

    def load(self):
        # A: encoding
        if self.raw[:3] == b"\xef\xbb\xbf":
            self.err("A01", "file starts with a UTF-8 BOM")
        if b"\r" in self.raw:
            self.err("A02", "file contains CR bytes (must be LF only)")
        high = [b for b in self.raw if b > 127]
        if high:
            self.err("A03", "%d byte(s) > 127 - file is not pure ASCII"
                     % len(high))
        if self.text is None:
            return
        # B: syntax
        try:
            self.tree = parse(self.text)
        except ParseError as exc:
            self.err("B01", "s-expression parse failed: %s" % exc)
            return
        if head(self.tree) != "kicad_sch":
            self.err("B02", "root token is %r, expected 'kicad_sch'"
                     % head(self.tree))
        ver = kid(self.tree, "version")
        if ver is None or text_of(ver) != FILE_VERSION:
            self.err("B03", "version is %r, expected %r"
                     % (text_of(ver) if ver else None, FILE_VERSION))
        for tok in FORBIDDEN:
            if tok in self.text:
                self.err("B04", "contains KiCad 7/8+ token %r" % tok)
        if "(fields_autoplaced yes)" in self.text or "(dnp " in self.text:
            self.err("B04", "contains KiCad 7/8+ syntax")

        # C: library
        libs = kid(self.tree, "lib_symbols")
        if libs is None:
            self.err("C01", "no lib_symbols section")
            return
        for sym in kids(libs, "symbol"):
            name = str(sym[1]) if len(sym) > 1 else "?"
            if name in self.lib:
                self.err("C01", "duplicate lib symbol %r" % name)
            pins = {}
            corners = []
            for sub in kids(sym, "symbol"):
                for rect in kids(sub, "rectangle"):
                    st, en = kid(rect, "start"), kid(rect, "end")
                    if st is not None and en is not None:
                        corners.append((float(st[1]), float(st[2])))
                        corners.append((float(en[1]), float(en[2])))
                for p in kids(sub, "pin"):
                    num = kid(p, "number")
                    at = kid(p, "at")
                    if num is None or at is None:
                        self.err("C01", "pin without number/at in %s" % name)
                        continue
                    pnum = str(num[1])
                    if pnum in pins:
                        self.err("C01", "duplicate pin %r in %s" % (pnum, name))
                    pins[pnum] = (float(at[1]), float(at[2]), float(at[3]))
                    corners.append((float(at[1]), float(at[2])))
            if not pins:
                self.err("C01", "lib symbol %r has no pins" % name)
            self.lib[name] = pins
            if corners:
                self.bbox[name] = (min(c[0] for c in corners),
                                   min(c[1] for c in corners),
                                   max(c[0] for c in corners),
                                   max(c[1] for c in corners))

        # instances
        for sym in kids(self.tree, "symbol"):
            lid = kid(sym, "lib_id")
            at = kid(sym, "at")
            if lid is None or at is None:
                self.err("C02", "instance without lib_id/at")
                continue
            lib_id = str(lid[1])
            cx, cy = float(at[1]), float(at[2])
            rot = float(at[3]) if len(at) > 3 else 0.0
            ref = None
            for prop in kids(sym, "property"):
                if str(prop[1]) == "Reference":
                    ref = str(prop[2])
            have_props = set(str(p[1]) for p in kids(sym, "property"))
            missing = set(["Reference", "Value", "Footprint", "Datasheet"]) - have_props
            if missing:
                self.err("C04", "%s misses properties %s"
                         % (ref or lib_id, sorted(missing)))
            inums = [str(p[1]) for p in kids(sym, "pin")]
            self.inst.append((ref, lib_id, cx, cy, rot, inums))
            if lid and lib_id not in self.lib:
                self.err("C02", "instance %s uses lib_id %r which is not in "
                                "lib_symbols" % (ref, lib_id))
                continue
            libpins = self.lib[lib_id]
            if sorted(inums) != sorted(libpins):
                only_i = sorted(set(inums) - set(libpins))
                only_l = sorted(set(libpins) - set(inums))
                self.err("C03", "pin set mismatch for %s: instance-only=%s "
                                "lib-only=%s" % (ref, only_i, only_l))
            if rot != 0.0:
                self.err("C99", "instance %s has rotation %g; the position "
                                "check assumes 0" % (ref, rot))
                continue
            for pnum, (lx, ly, _ang) in libpins.items():
                sx, sy = round(cx + lx, 3), round(cy - ly, 3)
                if (sx, sy) in self.pinpoints:
                    self.err("D02", "two pins share the point (%g,%g): %s and %s"
                             % (sx, sy, self.pinpoints[(sx, sy)], (ref, pnum)))
                self.pinpoints[(sx, sy)] = (ref, pnum)

        # labels, wires, uuids, paper, text
        for node in self.tree:
            if not isinstance(node, list):
                continue
            h = head(node)
            if h in ("label", "global_label"):
                at = kid(node, "at")
                self.labels.append(("global" if h == "global_label" else "local",
                                    str(node[1]), float(at[1]), float(at[2])))
            elif h == "wire":
                pts = kid(node, "pts")
                for xy in kids(pts, "xy") if pts is not None else []:
                    self.wires.append((float(xy[1]), float(xy[2])))
            elif h == "text":
                at = kid(node, "at")
                self.texts.append((float(at[1]), float(at[2])))
            elif h == "paper":
                self.paper = str(node[1])
        for node in walk(self.tree):
            if isinstance(node, list) and head(node) == "uuid":
                self.uuids.append(str(node[1]))

        # D: labels must sit on a pin or on a wire end
        attach = set(self.pinpoints) | set((round(x, 3), round(y, 3))
                                           for x, y in self.wires)
        seen_label_pt = {}
        for kind, text, x, y in self.labels:
            pt = (round(x, 3), round(y, 3))
            if pt not in attach:
                self.err("D01", "label %r at (%g,%g) is not on any pin or wire "
                                "end - its net would be lost" % (text, x, y))
            elif pt in seen_label_pt and seen_label_pt[pt] != text:
                self.err("D02", "two different labels on one pin at (%g,%g): "
                                "%r and %r" % (x, y, seen_label_pt[pt], text))
            else:
                seen_label_pt[pt] = text
        dup = set(u for u in self.uuids if self.uuids.count(u) > 1)
        if dup:
            self.err("D03", "duplicate uuid(s): %s" % sorted(dup)[:3])

        # G: geometry - no overlapping symbols, everything inside the page
        boxes = []
        for ref, lib_id, cx, cy, rot, inums in self.inst:
            if lib_id not in self.bbox or rot != 0.0:
                continue
            x0, y0, x1, y1 = self.bbox[lib_id]
            boxes.append((ref, cx + x0, cy - y1, cx + x1, cy - y0))
        boxes.sort(key=lambda b: (b[1], b[2]))
        for i in range(len(boxes)):
            for j in range(i + 1, len(boxes)):
                a, b = boxes[i], boxes[j]
                if b[1] >= a[3] - 1e-6:
                    break
                ox = min(a[3], b[3]) - max(a[1], b[1])
                oy = min(a[4], b[4]) - max(a[2], b[2])
                if ox > 0.01 and oy > 0.01:
                    self.err("G01", "%s and %s overlap by %.2f x %.2f mm"
                             % (a[0], b[0], ox, oy))
        if self.paper in PAPER_MM:
            pw, ph = PAPER_MM[self.paper]
            pts = ([(x, y, "pin") for (x, y) in self.pinpoints] +
                   [(x, y, "label") for _k, _t, x, y in self.labels] +
                   [(x, y, "text") for x, y in self.texts])
            out = [(k, x, y) for x, y, k in pts
                   if x < 0 or y < 0 or x > pw or y > ph]
            if out:
                self.err("G02", "%d element(s) outside the %s page, e.g. %s"
                         % (len(out), self.paper, out[:3]))


def walk(node):
    yield node
    if isinstance(node, list):
        for c in node:
            for x in walk(c):
                yield x


def check_control_group():
    """The hand written fixtures: minimal must pass, broken ones must fail."""
    out = []
    for name in FIXTURES_PASS:
        path = os.path.join(TEST_DIR, name)
        if not os.path.exists(path):
            out.append((name, False, ["missing fixture file"]))
            continue
        sh = Sheet(path)
        sh.load()
        out.append((name, not sh.bad, ["%s: %s" % b for b in sh.bad]))
    for name, want in FIXTURES_FAIL:
        path = os.path.join(TEST_DIR, name)
        if not os.path.exists(path):
            out.append((name, False, ["missing fixture file"]))
            continue
        sh = Sheet(path)
        sh.load()
        codes = sorted(set(c for c, _ in sh.bad))
        ok = want in codes
        out.append((name, ok, ["expected %s, got %s" % (want, codes or "no error")]))
    return out


USAGE = """usage: check-kicad-schematic.py [--quiet] [--help]

Checks the 8 generated .kicad_sch files in hardware/schematic/ (encoding,
s-expression syntax, inline library references, label attachment, cross-file
uniqueness, manifests, geometry) and runs the control group in
hardware/schematic/tests/.  See the module docstring for the full check list.

  --quiet   only print failures, the control group and the summary
  --help    show this text

Exit codes: 0 all checks passed, 1 at least one check failed, 2 usage error."""


def main():
    args = sys.argv[1:]
    if "--help" in args or "-h" in args:
        print(USAGE)
        return 0
    unknown = [x for x in args if x != "--quiet"]
    if unknown:
        sys.stderr.write("unknown argument(s): %s\n\n%s\n"
                         % (" ".join(unknown), USAGE))
        return 2
    quiet = "--quiet" in args
    sheets = []
    fatal = []
    for name in SHEET_FILES:
        path = os.path.join(SCH_DIR, name)
        if not os.path.exists(path):
            fatal.append("missing file %s - run scripts/build-kicad-schematic.py"
                         % name)
            continue
        sh = Sheet(path)
        sh.load()
        sheets.append(sh)

    # E: cross-file uniqueness and label-kind consistency
    refs = {}
    all_uuids = {}
    net_kind = {}
    for sh in sheets:
        for ref, lib_id, cx, cy, rot, inums in sh.inst:
            if ref in refs:
                sh.err("E01", "reference %s also used in %s" % (ref, refs[ref]))
            refs[ref] = sh.name
        for u in sh.uuids:
            if u in all_uuids:
                sh.err("E02", "uuid %s also used in %s" % (u, all_uuids[u]))
            all_uuids[u] = sh.name
        for kind, text, x, y in sh.labels:
            net_kind.setdefault(text, {})[sh.name] = kind
    for net, per in sorted(net_kind.items()):
        kinds = set(per.values())
        if net in POWER_NETS and kinds != set(["global"]):
            fatal.append("power net %s is not a global label everywhere (%s)"
                         % (net, per))
        if len(per) > 1 and kinds != set(["global"]):
            fatal.append("net %s spans sheets %s but is not global everywhere"
                         % (net, sorted(per)))

    # F1: the net map CSV must equal what is really in the files
    real = {}
    for sh in sheets:
        key = sh.name[:-len(".kicad_sch")]
        lab = {}
        for kind, text, x, y in sh.labels:
            lab[(round(x, 3), round(y, 3))] = (text, kind)
        for ref, lib_id, cx, cy, rot, inums in sh.inst:
            if lib_id not in sh.lib:
                continue
            for pnum, (lx, ly, _a) in sh.lib[lib_id].items():
                pt = (round(cx + lx, 3), round(cy - ly, 3))
                if pt in lab:
                    real[(key, ref, pnum)] = lab[pt]
    listed = {}
    with io.open(NET_MAP, "r", encoding="utf-8", newline="") as f:
        for row in csv.DictReader(f):
            listed[(row["sheet"], row["ref"], row["pin_number"])] = (
                row["net_label"], row["label_kind"])
    for k in sorted(set(real) | set(listed)):
        if k not in listed:
            fatal.append("net map CSV misses %s -> %s" % (k, real[k]))
        elif k not in real:
            fatal.append("net map CSV lists %s -> %s but the file has no label"
                         % (k, listed[k]))
        elif real[k] != listed[k]:
            fatal.append("net map mismatch for %s: file=%s csv=%s"
                         % (k, real[k], listed[k]))
    if len(real) != len(listed):
        fatal.append("net map size differs: file=%d csv=%d" % (len(real), len(listed)))

    # F2: every netlist.csv row is accounted for, and every (ref, pin) pair the
    # coverage manifest claims to have attached really carries a label in a file
    with io.open(NETLIST, "r", encoding="utf-8-sig", newline="") as f:
        nrows = len(list(csv.DictReader(f)))
    with io.open(ROW_COVERAGE, "r", encoding="utf-8", newline="") as f:
        cov = list(csv.DictReader(f))
    if len(cov) != nrows:
        fatal.append("row coverage has %d rows, netlist.csv has %d"
                     % (len(cov), nrows))
    bad_status = [r["row"] for r in cov
                  if r["status"] not in ("DRAWN", "PARTIAL", "NOTE")]
    if bad_status:
        fatal.append("row coverage contains statuses %s for rows %s"
                     % (sorted(set(r["status"] for r in cov)), bad_status[:10]))
    real_by_refpin = {}
    for (key, ref, pnum), (net, kind) in real.items():
        real_by_refpin.setdefault((ref, pnum), set()).add(net)
    attached_total = 0
    for r in cov:
        for pair in [p for p in r.get("pins", "").split(";") if p]:
            ref, _, pnum = pair.rpartition(".")
            attached_total += 1
            if (ref, pnum) not in real_by_refpin:
                fatal.append("coverage row %s claims %s carries a label, but no "
                             "file has that on a pin" % (r["row"], pair))
                continue
            if r["status"] == "DRAWN" and r["net_label"] not in real_by_refpin[(ref, pnum)]:
                fatal.append("coverage row %s: %s carries %s in the file, not %s"
                             % (r["row"], pair,
                                sorted(real_by_refpin[(ref, pnum)]), r["net_label"]))
    if attached_total < 200:
        fatal.append("only %d pin attachments claimed - expected > 200"
                     % attached_total)

    # ---- report ----------------------------------------------------------
    n_fail = 0
    for sh in sheets:
        if sh.bad and not quiet:
            print("FAIL %s" % sh.name)
            for code, msg in sh.bad:
                print("   %s  %s" % (code, msg))
        elif not sh.bad and not quiet:
            print("PASS %-24s paper=%-3s instances=%-4d libs=%-3d labels=%-4d "
                  "pins=%-4d" % (sh.name, sh.paper or "?", len(sh.inst),
                                 len(sh.lib), len(sh.labels), len(sh.pinpoints)))
        n_fail += len(sh.bad)
    for msg in fatal:
        print("FAIL %s" % msg)
        n_fail += 1

    if not quiet:
        print("")
    print("CONTROL GROUP (proves the checker is not a no-op)")
    ctrl_ok = True
    for name, ok, msgs in check_control_group():
        print("  %-4s %-42s %s" % ("PASS" if ok else "FAIL", name,
                                   "" if ok else "; ".join(msgs)))
        if not ok:
            ctrl_ok = False
    if not ctrl_ok:
        n_fail += 1

    print("")
    print("SUMMARY files=%d instances=%d pins=%d labels=%d nets=%d "
          "netlist_rows=%d attached=%d problems=%d"
          % (len(sheets), sum(len(s.inst) for s in sheets),
             sum(len(s.pinpoints) for s in sheets),
             sum(len(s.labels) for s in sheets), len(net_kind), len(cov),
             attached_total, n_fail))
    if n_fail:
        print("RESULT FAIL")
        return 1
    print("RESULT PASS")
    return 0


if __name__ == "__main__":
    sys.exit(main())
