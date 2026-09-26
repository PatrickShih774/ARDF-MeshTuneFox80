#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""Generate the pin-by-pin netlist (CSV) for the LCEDA import pack.

Outputs (all UTF-8 with BOM + LF):
  hardware/bom/netlist.csv      - Chinese-header, human readable, per-connection rows
  hardware/schematic/netlist.csv- machine readable (ASCII headers), one row per pin
  hardware/schematic/netlist.md - Markdown rendering + subsystem coverage

Every row carries a source citation (docs section / README section). Rows whose
wiring is only partially derivable from the docs are flagged in the "说明" column
so they are not mistaken for frozen connectivity.

The ATU relay/L-C network section (step 12) implements
hardware/atu-module/relay-wiring.md, which closed pre-fab-checklist item C-06 on
2026-09-26.  The former single abstract row "RELAY_CONTACTS ... unfrozen" is gone;
the former "RF_THRU: J_ATU_IN -> J_ANT" abstract row became the L-chain entry node
ATU_L_IN, and the output node ATU_L3_LO -> J_ANT carries the matching network.

Run:  python scripts/build-lceda-import-pack.py  (this file is imported by it)
Stdout is ASCII-only (Windows console is GBK).
"""

from __future__ import annotations

import csv
import io
import os

REPO = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
BOM_DIR = os.path.join(REPO, "hardware", "bom")
SCH_DIR = os.path.join(REPO, "hardware", "schematic")

H_CN = ["网络名", "源器件.引脚", "目标器件.引脚", "说明", "依据来源"]
H_EN = ["net", "net_label", "src_ref", "src_pin", "dst_ref", "dst_pin", "note", "source"]

D05 = "docs/05-hw-sw-interface-contract.md"
D17 = "docs/17-gpio-allocation-audit.md"
D04 = "docs/04-hardware-architecture.md"


def N(net, label, src, sp, dst, dp, note, source):
    return {"net": net, "net_label": label, "src_ref": src, "src_pin": sp,
            "dst_ref": dst, "dst_pin": dp, "note": note, "source": source}


def build():
    R = []
    A = R.append

    # ---------------- 1. ESP32-C3 direct GPIO (docs/05 §2.2, §2.8) ----------------
    S = D05 + " §2.2/§2.8"
    A(N("ADC_FWD", "ADC_FWD", "U4", "GPIO0", "T1", "1 (次级)", "ADC1_CH0 前向检波输入; 满量程由耦合器与 R_sense 决定; 2W 下读数应落量程 20%-80%", S + "; §3.2"))
    A(N("ADC_REV", "ADC_REV", "U4", "GPIO1", "T2", "1 (次级)", "ADC1_CH1 反向检波输入; SWR=2.0@2W 时读数应 >=量程 5%", S + "; §3.2"))
    A(N("ADC_VBAT", "ADC_VBAT", "U4", "GPIO3", "R_VBAT3", "2", "ADC1_CH3 电池电压(经 22k/9.1k/1k 分压 + 0.1uF); 6.0V->1.76V, 8.4V->2.46V", S + "; §2.7"))
    A(N("EC11_A", "EC11_A", "U4", "GPIO2", "U6", "A", "strapping 脚: 必须有 10kohm 上拉(R3), 静止为高; 上电时勿转动旋钮", S + "; §2.6"))
    A(N("EC11_B", "EC11_B", "U4", "GPIO8", "U6", "B", "strapping 脚: 必须有 10kohm 上拉(R4), 静止为高", S + "; §2.6"))
    A(N("EC11_SW", "EC11_SW", "U4", "GPIO13", "U6", "SW", "按下接 GND + 10kohm 上拉(R5), 中断驱动; GPIO13 = SPIWP, 固件须先 gpio_reset_pin 撤销 MSPI 保留", S + "; " + D17 + " §12.6.3"))
    A(N("KEY_USER", "KEY_USER", "U4", "GPIO9", "SW2", "1", "BOOT 按键(strapping): 上电前不可下拉; 启动后可作 KEY_USER", S + "; §2.6"))
    A(N("I2C_SDA", "I2C_SDA", "U4", "GPIO4", "R6", "1", "I2C0 SDA, 开漏; 4.7kohm 上拉到 3.3V; 共享总线 Si5351 + TCA9535", S))
    A(N("I2C_SCL", "I2C_SCL", "U4", "GPIO5", "R7", "1", "I2C0 SCL, 开漏; 4.7kohm 上拉到 3.3V", S))
    A(N("PA_PWR_PWM", "PA_PWR_PWM", "U4", "GPIO12", "U11", "FB", "LEDC PWM -> 升压模块 FB 网络; 低=最低功率; 高阻/高=有推向满功率风险", S + "; §2.10.2"))
    A(N("VDD_SPI_NC", "VDD_SPI_NC", "U4", "GPIO11", "-", "NC", "🔴 不可用: VDD_SPI, 已决定不解锁 eFuse; 原理图上标注 NC/保留, 不得接任何网络", S + " §2.1"))
    A(N("USB_DM", "USB_DM", "U4", "GPIO18", "J_USB", "D-", "原生 USB Serial/JTAG: 日志/中控/下载", S + " §2.2"))
    A(N("USB_DP", "USB_DP", "U4", "GPIO19", "J_USB", "D+", "同上", S + " §2.2"))
    A(N("UART0_TX", "UART0_TX", "U4", "GPIO20", "J_UART", "TX", "UART0 备用串口(板载 USB-UART 桥)", S + " §2.2"))
    A(N("UART0_RX", "UART0_RX", "U4", "GPIO21", "J_UART", "RX", "同上", S + " §2.2"))

    # pull-ups on strapping / encoder pins
    A(N("EC11_A", "EC11_A", "R3", "2", "+3V3_DIG", "-", "EC11_A 上拉 10kohm(strapping 强制要求)", S + " §2.6"))
    A(N("EC11_B", "EC11_B", "R4", "2", "+3V3_DIG", "-", "EC11_B 上拉 10kohm(strapping 强制要求)", S + " §2.6"))
    A(N("EC11_SW", "EC11_SW", "R5", "2", "+3V3_DIG", "-", "EC11_SW 上拉 10kohm", D05 + " §2.2; ADR-0008 §8.3"))
    A(N("GND", "GND", "U6", "SW2 (另一端)", "GND", "-", "EC11_SW 按下时把 EC11_SW 拉低", D05 + " §2.2; ADR-0008 §8.3"))
    A(N("I2C_SDA", "I2C_SDA", "R6", "2", "+3V3_DIG", "-", "I2C SDA 上拉 4.7kohm", S))
    A(N("I2C_SCL", "I2C_SCL", "R7", "2", "+3V3_DIG", "-", "I2C SCL 上拉 4.7kohm", S))

    # ---------------- 2. I2C devices: Si5351 + TCA9535 ----------------
    A(N("I2C_SDA", "I2C_SDA", "U7", "SDA", "U4", "GPIO4", "Si5351 I2C 数据(地址 0x60)", D05 + " §2.3/§2.5; " + D04 + " §3.5"))
    A(N("I2C_SCL", "I2C_SCL", "U7", "SCL", "U4", "GPIO5", "Si5351 I2C 时钟", D05 + " §2.3/§2.5"))
    A(N("I2C_SDA", "I2C_SDA", "U1", "SDA", "U4", "GPIO4", "TCA9535 I2C 数据(地址 0x20; A2/A1/A0 接法待确认)", D05 + " §2.3, §7 #2"))
    A(N("I2C_SCL", "I2C_SCL", "U1", "SCL", "U4", "GPIO5", "TCA9535 I2C 时钟", D05 + " §2.3"))
    A(N("TCA9535_INT", "TCA9535_INT", "U1", "INT", "-", "NC", "本方案 A 不使用 INT; 若日后走 C/C-prime 方案需 10kohm 上拉到 3.3V", D17 + " §3.5, §7 R6"))

    # ---------------- 3. TCA9535 16-bit expander (docs/05 §2.3) ----------------
    S3 = D05 + " §2.3; " + D17 + " §2.1"
    for i, k in enumerate(["K1", "K2", "K3", "K4", "K5", "K6"]):
        A(N("IOEXP_RELAY_%s" % k, "IOEXP_RELAY_%s" % k, "U1", "P0.%d" % i, "U2", "IN%d" % (i + 1),
          "TCA9535 P0.%d -> ULN2003A IN%d(3.3V 并行, 6 根)" % (i, i + 1), S3))
    A(N("IOEXP_LCD_BL", "IOEXP_LCD_BL", "U1", "P1.1", "R_BL", "1", "背光开关: P1.1 -> R 1kohm -> 2N7002 栅极", D05 + " §2.3"))
    A(N("IOEXP_SPARE_P1_0", "IOEXP_SPARE_P1_0", "U1", "P1.0", "-", "NC", "预留(原 EC11 按键, 已释放)", S3))
    for p in ["P0.6", "P0.7", "P1.2", "P1.3", "P1.4", "P1.5", "P1.6", "P1.7"]:
        A(N("IOEXP_SPARE_" + p.replace(".", "_"), "IOEXP_SPARE_" + p.replace(".", "_"), "U1", p, "-", "NC",
          "预留 9 位之一(蜂鸣器/状态灯/散热风扇/天线泄放等)", S3))

    # ---------------- 4. ULN2003A relay driver chain ----------------
    A(N("+12V_RELAY", "+12V", "U2", "COM", "+12V", "-",
      "🔴 COM 必须接 +12V: 内部续流二极管靠它生效(不接则继电器反峰无抑制)", D05 + " §2.4"))
    for i, k in enumerate(["K1", "K2", "K3", "K4", "K5", "K6"]):
        A(N("RELAY_%s_COIL" % k, "RELAY_%s_COIL" % k, "U2", "OUT%d" % (i + 1), k, "线圈+",
          "ULN2003A OUT%d 低边吸合 %s 线圈; 16.7mA/只, 6 只同吸 <110mA" % (i + 1, k), D05 + " §2.4"))
        A(N("+12V_RELAY", "+12V", k, "线圈-", "+12V", "-",
          "%s 线圈另一端接 +12V 功放轨; 线圈得电压 12-0.9=11.1V=92%% (>75%% 吸合阈值)" % k, D05 + " §2.4"))
    A(N("GND", "GND", "U2", "GND", "GND", "-", "ULN2003A 地(e 脚)", D05 + " §2.4"))

    # ---------------- 5. SPI2 -> ST7567 (docs/05 §2.2; ADR-0008 §3.1) ----------------
    S5 = D05 + " §2.2; ADR-0008 §3.1"
    A(N("LCD_SCK", "LCD_SCK", "U4", "GPIO6", "U5", "SCK/CLK", "SPI2 SCK -> ST7567", S5))
    A(N("LCD_MOSI", "LCD_MOSI", "U4", "GPIO7", "U5", "MOSI/SI", "SPI2 MOSI -> ST7567", S5))
    A(N("LCD_DC", "LCD_DC", "U4", "GPIO10", "U5", "A0/DC", "命令/数据选择, 必须直连(每字节翻转, 不可挂 I2C 扩展器)", S5 + "; §3.1"))
    A(N("GND", "GND", "U5", "CS", "GND", "-", "🔴 CS 接 GND: ST7567 是 SPI2 上唯一从机 -> 省 1 个 GPIO", S5))
    A(N("LCD_RST", "LCD_RST", "U5", "RST", "RESET_BOARD", "-", "🔴 RST 与板复位共用: 上电复位即可 -> 省 1 脚与 RC 电路", S5))
    A(N("LCD_BL_CTRL", "LCD_BL_CTRL", "R_BL", "2", "Q5", "G", "P1.1 经 1kohm 到 2N7002 栅极", D05 + " §2.3"))
    A(N("LCD_BL_GATE_PD", "LCD_BL_GATE_PD", "R_BL2", "1", "Q5", "G", "🔴 栅极 10kohm 下拉到 GND: TCA9535 上电为输入高阻, 否则背光状态不定", D05 + " §2.3"))
    A(N("GND", "GND", "R_BL2", "2", "GND", "-", "背光 MOS 栅极下拉另一端", D05 + " §2.3"))
    A(N("LCD_BL_K", "LCD_BL_K", "Q5", "D", "U5", "LED-", "2N7002 漏极接背光 LED 阴极串", D05 + " §2.3"))
    A(N("GND", "GND", "Q5", "S", "GND", "-", "2N7002 源极", D05 + " §2.3"))
    A(N("+3V3_DIG", "+3V3_DIG", "R_BLLED", "1", "U5", "LED+", "背光 LED 阳极经限流电阻(R_BLLED 阻值待模组规格确定)", D05 + " §2.3"))
    A(N("+3V3_DIG", "+3V3_DIG", "U5", "VDD/VDDIO", "U5", "VDD/VDDIO", "LCD 逻辑供电 3.3V", S5))
    A(N("LCD_V0", "LCD_V0", "U5", "V0/VOUT", "LCD_BIAS", "-", "对比度偏置网络: 模组自带或外接可调(未冻结)", D05 + " §2.3"))
    A(N("GND", "GND", "U5", "VSS", "GND", "-", "LCD 地", S5))

    # ---------------- 6. CW keying chain + PA drive (docs/05 §2.5; ADR-0008 §3.2) ----------------
    S6 = D05 + " §2.5; ADR-0008 §3.2"
    A(N("CW_KEY_SRC", "CW_KEY_SRC", "U4", "I2C 写 CLKx_DIS", "U7", "CLKx_CONTROL", 
      "🔴 CW 键控 = Si5351 使能命令(I2C 写 CLKx_DIS 位), 不占任何 GPIO; 无插入损耗/无开关损耗/无静态电流",
      S6))
    A(N("RF_SRC_CLK", "RF_SRC_CLK", "U7", "CLK0", "U8", "1A", "Si5351 3.3V CMOS 方波 -> 244 输入", S6))
    A(N("RF_SRC_PD", "RF_SRC_PD", "R8", "1", "U8", "1A", "🔴 244 输入侧 10kohm 下拉到 GND: Si5351 停振时输入悬空会使 244 振荡 -> PA 自激发射", S6))
    A(N("GND", "GND", "R8", "2", "GND", "-", "输入下拉另一端", S6))
    A(N("PA_GATE", "PA_GATE", "U8", "1Y", "Q1", "G", "244 输出 0-5V 方波(+/-24mA) -> BS170 栅极(Class-E 开关)", S6))
    A(N("PA_GATE", "PA_GATE", "U8", "1Y", "Q2", "G", "3 管并联: 栅极共连", S6))
    A(N("PA_GATE", "PA_GATE", "U8", "1Y", "Q3", "G", "3 管并联: 栅极共连", S6))
    for q in ["Q1", "Q2", "Q3"]:
        A(N("PA_GATE_PD", "PA_GATE_PD", "R10", "1", q, "G", "🔴 MOS 栅极下拉: 保证 OE/停振时 MOS 可靠截止", S6))
    A(N("GND", "GND", "R10", "2", "GND", "-", "栅极下拉另一端(3 管共用描述)", S6))
    A(N("PA_BIAS", "PA_BIAS", "R1", "2", "R2", "1", "栅极固定偏置分压中点 约2.1V(纯固定偏置, 无温度补偿)", D05 + " §3.1; " + D17 + " §12.5"))
    A(N("+5V", "+5V", "R1", "1", "+5V", "-", "偏置分压上臂接 5V 主轨", D04 + " §3.6"))
    A(N("GND", "GND", "R2", "2", "GND", "-", "偏置分压下臂直接接地(NTC 已取消)", D17 + " §12.5"))
    for q in ["Q1", "Q2", "Q3"]:
        A(N("PA_BIAS", "PA_BIAS", "R1", "2", q, "G", "固定栅极偏置到各管栅极", D04 + " §3.2"))
        A(N("GND", "GND", "D5_prot", "A", q, "G", "BZX84-C10 10V 稳压管栅极保护(每管1只)", D04 + " §3.2"))
        A(N("PA_DRAIN", "PA_DRAIN", "+12V", "-", q, "D", "BS170 漏极 12-13.8V(升压可调); 3 管并联", D05 + " §3.1"))
        A(N("GND", "GND", q, "S", "GND", "-", "BS170 源极", D04 + " §3.2"))
        A(N("PA_BYPASS", "PA_BYPASS", "C6", "1", q, "D", "100nF 旁路电容(每管1只)", D04 + " §3.2"))
    A(N("+5V", "+5V", "U8", "VCC", "+5V", "-", "🔴 244 必须 5V 供电(ACT 系列 4.5-5.5V, TTL 输入阈值)", S6))
    A(N("GND", "GND", "U8", "GND", "GND", "-", "244 地", S6))
    A(N("DEC244", "DEC244", "C244", "1", "U8", "VCC", "🔴 244 每个 Vcc 引脚 100nF 去耦", S6))
    A(N("PA_RF_OUT", "PA_RF_OUT", "Q1", "D (并联)", "J_PA_OUT", "中心", "PA 输出 -> LPF, 经 SMA 50ohm", D05 + " §4.1"))

    # ---------------- 7. Tandem Match coupler + detectors ----------------
    S7 = D05 + " §3.2; hardware/atu-module/README.md §3"
    # 注：RF_THRU 原写作 J_ATU_IN -> J_ANT 直连（"主线"的抽象写法），会让整个 L 型匹配网络
    #     被短路。2026-09-26 按 hardware/atu-module/relay-wiring.md §2.1 细化为 L 链入口节点，
    #     出口节点由第 12 节的 ATU_L3_LO -> J_ANT.中心 给出。
    A(N("ATU_L_IN", "ATU_L_IN", "J_ATU_IN", "中心", "L1", "1",
      "ATU 主线入口节点 N0：输入 SMA →(Tandem Match 耦合器主线)→ L 链第一只电感；本行取代原 'RF_THRU: J_ATU_IN→J_ANT 直连' 的抽象写法",
      D05 + " §4.1; " + D04 + " §3.4; hardware/atu-module/relay-wiring.md §2.1"))
    A(N("XFWD_SEC", "XFWD_SEC", "T1", "次级+", "R_sense_F", "1", "T1 次级(初级1匝穿芯 + 次级10匝; 耦合度 20+/-3dB)", S7))
    A(N("GND", "GND", "R_sense_F", "2", "GND", "-", "前向 R_sense 1kohm 初值, 需 NanoVNA 微调", D05 + " §3.2, §7 #4"))
    A(N("DET_FWD", "DET_FWD", "R_sense_F", "1", "D1", "A", "1N5711 检波(前向)", S7))
    A(N("DET_FWD", "DET_FWD", "R_sense_F", "1", "D3", "A", "HSMS-2850 零偏置检波, 与 1N5711 并行对照", S7))
    A(N("ADC_FWD", "ADC_FWD", "D1", "K", "U4", "GPIO0", "检波输出 -> ADC1_CH0(两条检波支路由固件选优/融合)", S7))
    A(N("ADC_FWD", "ADC_FWD", "D3", "K", "U4", "GPIO0", "同上(并行对照)", S7))
    A(N("XREV_SEC", "XREV_SEC", "T2", "次级+", "R_sense_R", "1", "T2 次级(反向)", S7))
    A(N("GND", "GND", "R_sense_R", "2", "GND", "-", "反向 R_sense 1kohm 初值", D05 + " §7 #4"))
    A(N("DET_REV", "DET_REV", "R_sense_R", "1", "D2", "A", "1N5711 检波(反向)", S7))
    A(N("DET_REV", "DET_REV", "R_sense_R", "1", "D4", "A", "HSMS-2850 并行对照", S7))
    A(N("ADC_REV", "ADC_REV", "D2", "K", "U4", "GPIO1", "检波输出 -> ADC1_CH1", S7))
    A(N("ADC_REV", "ADC_REV", "D4", "K", "U4", "GPIO1", "同上(并行对照)", S7))
    A(N("LM358_IN", "LM358_IN", "D1", "K", "U3", "IN+", "可选 LM358 放大级; 是否装配待 stage-4 实测(docs/05 §7 #6)", D05 + " §7 #6"))
    A(N("+5V", "+5V", "U3", "V+", "+5V", "-", "LM358 供电(可选级)", D05 + " §7 #6"))

    # ---------------- 8. Battery divider ----------------
    S8 = D05 + " §2.7"
    A(N("VBAT", "VBAT", "BT1", "+", "R_VBAT1", "1", "2S 电池 6.0-8.4V", S8))
    A(N("VBAT_DIV", "VBAT_DIV", "R_VBAT1", "2", "R_VBAT2", "1", "分压中点: 22k 上臂 / 9.1k 下臂", S8))
    A(N("GND", "GND", "R_VBAT2", "2", "GND", "-", "分压下臂接地; 静态电流 270uA", S8))
    A(N("VBAT_DIV", "VBAT_DIV", "R_VBAT1", "2", "R_VBAT3", "1", "分压中点经 1kohm 隔离到 ADC", S8))
    A(N("ADC_VBAT", "ADC_VBAT", "R_VBAT3", "2", "U4", "GPIO3", "源阻抗 R3+(22k//9.1k)=7.4kohm < 10kohm 满足 ESP32-C3 ADC 要求", S8))
    A(N("ADC_VBAT", "ADC_VBAT", "R_VBAT3", "2", "C_VBAT", "1", "0.1uF 滤波, fc 约 245Hz", S8))
    A(N("GND", "GND", "C_VBAT", "2", "GND", "-", "滤波电容地", S8))

    # ---------------- 9. Antenna static discharge ----------------
    A(N("ANT_ESD", "ANT_ESD", "J_ANT", "中心", "R_esd", "1", "天线静电泄放: 1kV 高压电阻 100kohm 到地(或射频专用 GDT)", D04 + " §3.4; hardware/atu-module/README.md §3"))
    A(N("GND", "GND", "R_esd", "2", "GND", "-", "泄放电阻接地", D04 + " §3.4"))

    # ---------------- 10. Power domains (docs/05 §3.3; docs/04 §3.6) ----------------
    S10 = D05 + " §3.3; " + D04 + " §3.6"
    A(N("+12V", "+12V", "U11", "OUT", "+12V", "-", "3.7V->12V 升压模块输出 12-13.8V; 最大 0.5A(发射); 纹波峰峰 <0.5V @2.5W", S10))
    A(N("+12V", "+12V", "U11", "OUT", "U2", "COM", "12V 供 ULN2003A COM(继电器续流)", D05 + " §2.4"))
    A(N("+12V", "+12V", "U11", "OUT", "J1", "12V", "12V 经排针到 PA 漏极与 ATU 继电器线圈", S10))
    A(N("+5V", "+5V", "U9", "OUT", "J1", "5V", "MP2315 同步降压 5V 主轨; 最大 0.3A", S10))
    A(N("+5V", "+5V", "U9", "OUT", "U8", "VCC", "5V 供 244", D05 + " §2.5"))
    A(N("+5V", "+5V", "U9", "OUT", "R1", "1", "5V 供栅极偏置分压", D04 + " §3.2"))
    A(N("+3V3_RF", "+3V3_RF", "U10", "OUT", "U7", "VDD", "MD7673 LDO 3.3V 射频轨(低噪声); 最大 50mA; 专供 Si5351", S10))
    A(N("+3V3_DIG", "+3V3_DIG", "FB1", "OUT", "U4", "3V3", "3.3V 数字轨(独立 pi 型 RC 滤波); 最大 200mA", S10))
    A(N("+3V3_DIG", "+3V3_DIG", "FB1", "OUT", "U5", "VDD", "3.3V 数字轨 -> LCD", S10))
    A(N("+3V3_DIG", "+3V3_DIG", "FB1", "OUT", "U1", "VCC", "3.3V 数字轨 -> TCA9535", S10))
    A(N("VBAT", "VBAT", "BT1", "+", "U9", "VIN", "2S 电池 6.0-8.4V -> MP2315 输入", S10))
    A(N("VBAT", "VBAT", "BT1", "+", "U11", "VIN", "2S 电池 -> 升压模块输入(⚠ 模块标称 3.7V 输入, 需核对)", S10 + "; docs/05 §7 #7"))
    A(N("GND", "GND", "BT1", "-", "GND", "-", "电池负极", S10))

    # ---------------- 11. Grounding strategy ----------------
    A(N("GND", "GND", "GND_DIG", "-", "GND_RF", "-", "🔴 射频地与数字地在底板单点汇接(star ground), 避免功放回流污染 Si5351 与 ADC 参考地", D04 + " §3.1; hardware/core-board/README.md §6"))
    A(N("GND", "GND", "GND_PWR", "-", "GND_DIG", "-", "大电流功放地/电源回路单独回流, 与射频地单点汇集于底板一点", D04 + " §3.1"))

    # ---------------- 12. ATU L 型匹配网络：继电器触点与 L/C 逐脚接法 ----------------
    # 依据：hardware/atu-module/relay-wiring.md（2026-09-26 关闭 pre-fab-checklist C-06）。
    # 拓扑（唯一解，验算见 scripts/verify-atu-lc-combos.py）：
    #   电感三只全部串联，每只被一只继电器「并联旁路」；旁路触点用 COM–NC ⇒ 释放=旁路、吸合=接入
    #   电容三只全部并联，每只经一只继电器「串联接入」；用 COM–NO   ⇒ 释放=断开、吸合=接入
    # 节点：N0=ATU_L_IN  N1=ATU_L1_LO  N2=ATU_L2_LO  N3=ATU_L3_LO(=天线节点/并联C节点)
    SRW = "hardware/atu-module/relay-wiring.md"
    SLC = SRW + " §2.1/§2.4; hardware/atu-module/README.md §2"
    A(N("ATU_L_IN", "ATU_L_IN", "L1", "1", "K1", "COM",
      "K1 旁路触点公共端接 L1 高端（同一节点 N0）", SLC))
    A(N("ATU_L1_LO", "ATU_L1_LO", "L1", "2", "L2", "1", "N1：L1 低端 = L2 高端", SLC))
    A(N("ATU_L1_LO", "ATU_L1_LO", "L1", "2", "K1", "NC",
      "🔴 K1 释放时 COM–NC 闭合 → L1 被旁路(0µH 档的一部分)；吸合 → 12µH 接入。极性契约见 relay-wiring.md §4.3", SLC + "; " + SRW + " §1.5"))
    A(N("ATU_L1_LO", "ATU_L1_LO", "L1", "2", "K2", "COM",
      "K2 旁路触点公共端接 L2 高端（同一节点 N1）", SLC))
    A(N("ATU_L2_LO", "ATU_L2_LO", "L2", "2", "L3", "1", "N2：L2 低端 = L3 高端", SLC))
    A(N("ATU_L2_LO", "ATU_L2_LO", "L2", "2", "K2", "NC",
      "K2 释放时旁路 L2；吸合 → 33µH 接入", SLC))
    A(N("ATU_L2_LO", "ATU_L2_LO", "L2", "2", "K3", "COM",
      "K3 旁路触点公共端接 L3 高端（同一节点 N2）", SLC))
    A(N("ATU_L3_LO", "ATU_L3_LO", "L3", "2", "J_ANT", "中心",
      "🔴 N3 = ATU 输出节点 = 天线座 + 并联电容支路（拓扑 SHUNT_C_AT_LOAD，见 §2.3）。本行取代原 'RF_THRU: J_ATU_IN→J_ANT 直连'",
      SLC + "; §2.3; " + D05 + " §4.1"))
    A(N("ATU_L3_LO", "ATU_L3_LO", "L3", "2", "K3", "NC",
      "K3 释放时旁路 L3；吸合 → 47µH 接入", SLC))
    for _k in ["K4", "K5", "K6"]:
        A(N("ATU_L3_LO", "ATU_L3_LO", "L3", "2", _k, "COM",
          "%s 电容支路触点公共端接 N3（天线节点）；该支路仅在吸合时接入" % _k, SLC))
    A(N("ATU_C3", "ATU_C3", "K4", "NO", "C3", "1",
      "K4 吸合 → 22pF 接入（C3 为硬件位号；固件注释里称 C1）", SLC + "; atu_match.h 组合↔位模式"))
    A(N("GND", "GND", "C3", "2", "GND", "-", "C3 冷端接地", SLC))
    A(N("ATU_C4", "ATU_C4", "K5", "NO", "C4", "1",
      "K5 吸合 → 120pF 接入（固件注释里称 C2）", SLC))
    A(N("GND", "GND", "C4", "2", "GND", "-", "C4 冷端接地", SLC))
    A(N("ATU_C5", "ATU_C5", "K6", "NO", "C5", "1",
      "K6 吸合 → 330pF 接入（固件注释里称 C3）", SLC))
    A(N("GND", "GND", "C5", "2", "GND", "-", "C5 冷端接地", SLC))
    for _k, _o in [("K1", "ATU_L1_LO"), ("K2", "ATU_L2_LO"), ("K3", "ATU_L3_LO")]:
        A(N("ATU_%s_NO_NC" % _k, "ATU_%s_NO_NC" % _k, _k, "NO", "-", "NC",
          "🟠 方案A 未使用触点(%s.NO)悬空：不得接任何网络。仅当改用方案B（吸合=旁路、须同步改固件 atu_match 的电感位语义）时才接 %s" % (_k, _o),
          SRW + " §2.4/§2.6"))
    for _k in ["K4", "K5", "K6"]:
        A(N("ATU_%s_NC_NC" % _k, "ATU_%s_NC_NC" % _k, _k, "NC", "-", "NC",
          "%s 未使用触点(NC)悬空：不得接任何网络" % _k, SRW + " §2.4"))
    # ULN2003A 输入下拉（2026-09-26 新增；见 relay-wiring.md §4.2/§4.4）
    SRLY = SRW + " §4.2/§4.4; 私有固件仓 components/drv_relay/include/drv_relay.h"
    for i, _k in enumerate(["K1", "K2", "K3", "K4", "K5", "K6"]):
        A(N("IOEXP_RELAY_%s" % _k, "IOEXP_RELAY_%s" % _k, "R_RLY%d" % (i + 1), "1", "U2", "IN%d" % (i + 1),
          "🔴 ULN2003A 输入端 10kohm 下拉：TCA9535 上电为输入且带约 100uA 弱上拉电流源，无下拉时 IN 可能被抬到导通阈值附近 → 继电器误吸合",
          SRLY))
        A(N("GND", "GND", "R_RLY%d" % (i + 1), "2", "GND", "-",
          "R_RLY%d 下拉另一端接地（100uA x 10kohm = 1.0V << V_I(on) 2.4V）" % (i + 1), SRLY))

    # ---------------- 13. Unfrozen / to-be-designed ----------------
    A(N("BUZZER_DRV", "BUZZER_DRV", "U1", "IOEXP_SPARE", "LS1", "+", "🟠 蜂鸣器未分配: 挂 TCA9535 空闲位(9 位中选一), 具体位号待定", D05 + " §2.3; hardware/mcu-ui-module/README.md §4"))
    A(N("FB_PULLDOWN", "GPIO12_FB_PD", "R12", "1", "PA_PWR_PWM", "-", "📌 建议未采纳判定: GPIO12 -> 升压 FB 的 10kohm 下拉(docs/05 §7 #7a)", D05 + " §2.10.3, §7 #7a; " + D17 + " §12.6.5"))
    A(N("GND", "GND", "R12", "2", "GND", "-", "同上(采纳后接 GND)", D05 + " §2.10.3"))

    return R


def write_csv(path, rows, header, mapping):
    buf = io.StringIO()
    w = csv.DictWriter(buf, fieldnames=header, lineterminator="\n", extrasaction="ignore")
    w.writeheader()
    for r in rows:
        w.writerow({k: r.get(mapping[k], "") for k in header})
    with open(path, "w", encoding="utf-8-sig", newline="") as f:
        f.write(buf.getvalue())
    return len(rows)


def md_escape(v):
    return str(v).replace("|", "\\|").replace("\n", " ")


def main():
    rows = build()
    os.makedirs(BOM_DIR, exist_ok=True)
    os.makedirs(SCH_DIR, exist_ok=True)

    cn_map = {"网络名": "net", "源器件.引脚": "_src", "目标器件.引脚": "_dst",
              "说明": "note", "依据来源": "source"}
    for r in rows:
        r["_src"] = "%s.%s" % (r["src_ref"], r["src_pin"])
        r["_dst"] = "%s.%s" % (r["dst_ref"], r["dst_pin"])
    n1 = write_csv(os.path.join(BOM_DIR, "netlist.csv"), rows, H_CN, cn_map)
    print("CSV hardware/bom/netlist.csv rows=%d" % n1)

    n2 = write_csv(os.path.join(SCH_DIR, "netlist.csv"), rows, H_EN, {k: k for k in H_EN})
    print("CSV hardware/schematic/netlist.csv rows=%d" % n2)

    nets = []
    for r in rows:
        if r["net"] not in nets:
            nets.append(r["net"])

    md = []
    md.append("# 网表 / 逐脚连接表 · ARDF-MeshTuneFox80（立创EDA 导入包）\n")
    md.append("> 本文件由 `scripts/build-lceda-import-pack.py` 生成，**请勿手工编辑**。")
    md.append("> 每一行都带 `依据来源` 列，指到 `docs/05` / `docs/17` / `docs/04` / 模块 README 的具体小节。\n")
    md.append("## 0. 文件与用法\n")
    md.append("| 文件 | 用途 |")
    md.append("|---|---|")
    md.append("| [hardware/bom/netlist.csv](../bom/netlist.csv) | 中文表头，逐条连接（含说明与依据），给人看 |")
    md.append("| [hardware/schematic/netlist.csv](netlist.csv) | 英文表头（`net,net_label,src_ref,src_pin,dst_ref,dst_pin,note,source`），给脚本/后续原理图生成用 |")
    md.append("")
    md.append("- 编码：**UTF-8 带 BOM + LF**。")
    md.append("- `net_label` 是可安全用作 KiCad/立创EDA **网络标签**的 ASCII 名（`+12V` 之类电源网络用 `+12V` 亦可被两端识别；`net` 列保留原始命名）。")
    md.append("- 🟠 标注「未冻结」的行表示**文档里没有给出完整接法**，需硬件设计补齐后才可作为画图依据。\n")
    md.append("## 1. 覆盖统计\n")
    md.append("| 项 | 数量 |")
    md.append("|---|---|")
    md.append("| 连接行数 | %d |" % len(rows))
    md.append("| 去重网络数 | %d |" % len(nets))
    md.append("")
    md.append("### 1.1 网络名清单（%d 个）\n" % len(nets))
    md.append(", ".join("`%s`" % n for n in nets))
    md.append("")

    md.append("## 2. 子系统覆盖\n")
    cover = [
        ("ESP32-C3 12 个 GPIO 全部去向", "GPIO0/1/3 ADC · GPIO2/8 EC11 · GPIO4/5 I2C · GPIO6/7 SPI2 · GPIO10 LCD_DC · GPIO12 PA_PWR_PWM · GPIO13 EC11_SW（另 GPIO9=BOOT、11=NC、18/19=USB、20/21=UART0）", D05 + " §2.2/§2.8"),
        ("TCA9535 16 位（用 7 + 预留 9）", "P0.0-P0.5=K1-K6 · P1.1=LCD 背光 · 预留 P1.0 + P0.6/P0.7 + P1.2-P1.7 = 9 位", D05 + " §2.3; " + D17 + " §2.1"),
        ("ULN2003A 7 路（6 继电器 + COM 接 +12V）", "IN1-IN6 <- P0.0-P0.5；OUT1-OUT6 -> K1-K6 线圈；COM -> +12V（内部续流二极管）", D05 + " §2.4"),
        ("SPI（SCK/MOSI/DC）", "GPIO6->SCK · GPIO7->MOSI · GPIO10->A0/DC · CS 接 GND · RST 与板复位共用", D05 + " §2.2; ADR-0008 §3.1"),
        ("I2C（SDA/SCL + 上拉）", "GPIO4/GPIO5 + 4.7kohm 上拉；挂 Si5351(0x60) 与 TCA9535(0x20)", D05 + " §2.2/§2.3"),
        ("ADC 三路（分压网络含 R1/R2/R3）", "GPIO0/GPIO1 检波 · GPIO3 电池 22kohm/9.1kohm/1kohm + 0.1uF", D05 + " §2.7/§3.2"),
        ("电源域（+12V / +5V / +3V3_RF / +3V3_DIG / VDD_SPI）", "升压->+12V · MP2315->+5V · MD7673->+3V3_RF · pi 滤波->+3V3_DIG · GPIO11(VDD_SPI) 标 NC 不解锁", D05 + " §3.3; " + D04 + " §3.6"),
        ("Si5351 输出与 PA 键控链（CW 走 CLKx_DIS 而非 GPIO）", "CW = I2C 写 CLKx_DIS · CLK0->244 输入(10kohm 下拉)->244 输出->BS170 栅极(10kohm 下拉)", D05 + " §2.5; ADR-0008 §3.2"),
        ("天线静电泄放", "天线座中心 -> 1kV 100kohm 高压电阻 到地（或 GDT）", D04 + " §3.4"),
        ("地平面/星形地", "射频地与数字地单点汇接于底板一点；四层板地平面完整", D04 + " §3.1; hardware/core-board/README.md §6"),
        ("Tandem Match 耦合器与检波", "T1/T2 FT37-43 · R_sense 1kohm · 1N5711 与 HSMS-2850 并行对照", D05 + " §3.2; hardware/atu-module/README.md §3"),
        ("EC11 与按键", "GPIO2/8 直连(10kohm 上拉) · GPIO13 SW 直连(10kohm 上拉) · GPIO9 BOOT/KEY_USER", D05 + " §2.2/§2.6; ADR-0008 §8.3"),
        ("ATU L 型匹配网络（继电器触点与 L/C 逐脚）", "N0=ATU_L_IN · N1=ATU_L1_LO · N2=ATU_L2_LO · N3=ATU_L3_LO(=天线节点) · K1-K3 用 COM-NC 旁路 L1/L2/L3 · K4-K6 用 COM-NO 接入 C3/C4/C5 · 未使用触点悬空 · ULN 输入 6x10kohm 下拉", "hardware/atu-module/relay-wiring.md §2.1/§2.4/§4.2"),
    ]
    md.append("| 子系统 | 覆盖内容 | 依据 |")
    md.append("|---|---|---|")
    for a, b, c in cover:
        md.append("| %s | %s | %s |" % (md_escape(a), md_escape(b), md_escape(c)))
    md.append("")

    md.append("## 3. 全部连接明细\n")
    md.append("| 网络名 | 源器件.引脚 | 目标器件.引脚 | 说明 | 依据来源 |")
    md.append("|---|---|---|---|---|")
    for r in rows:
        md.append("| `%s` | `%s` | `%s` | %s | %s |" % (
            md_escape(r["net"]), md_escape(r["_src"]), md_escape(r["_dst"]),
            md_escape(r["note"]), md_escape(r["source"])))
    md.append("")

    with open(os.path.join(SCH_DIR, "netlist.md"), "w", encoding="utf-8", newline="\n") as f:
        f.write("\n".join(md))
    print("MD  hardware/schematic/netlist.md nets=%d rows=%d" % (len(nets), len(rows)))


if __name__ == "__main__":
    main()
