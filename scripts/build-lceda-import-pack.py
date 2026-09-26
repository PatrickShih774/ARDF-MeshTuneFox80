#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""Generate the LCEDA (JLCEDA) import pack: per-module BOM CSVs + summary CSV + Markdown.

Output encoding rules (see .editorconfig / docs):
  * CSV  -> UTF-8 **with BOM** (utf-8-sig) + LF, so Excel opens Chinese correctly.
  * MD   -> UTF-8 **without BOM** + LF.

Data source of every row is noted in the "来源" column of the summary CSV and in
hardware/bom/README.md. Nothing here is invented: rows come from the module
READMEs, docs/05 and docs/17 of this repository.

Run:  python scripts/build-lceda-import-pack.py
Stdout is ASCII-only on purpose (Windows console is GBK).
"""

from __future__ import annotations

import csv
import io
import os
import sys

REPO = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
BOM_DIR = os.path.join(REPO, "hardware", "bom")

HEADER = [
    "位号", "参数", "封装", "数量", "建议型号", "LCSC 编号",
    "关键规格", "模块", "备注", "统一数量", "来源",
]

TODO = "待查"

# ---------------------------------------------------------------------------
# Rows per module.  Each row: dict with the HEADER keys.
# ---------------------------------------------------------------------------

COMMON_SOURCE = "hardware/{mod}/README.md §3; docs/04 §3"


def row(mod, ref, value, pkg, qty, model, lcsc, spec, note, unit_qty, source):
    return {
        "位号": ref, "参数": value, "封装": pkg, "数量": qty,
        "建议型号": model, "LCSC 编号": lcsc, "关键规格": spec,
        "模块": mod, "备注": note, "统一数量": unit_qty, "来源": source,
    }


def build_rows():
    R = []

    # ===================== atu-module =====================
    m = "atu-module"
    src = COMMON_SOURCE.format(mod=m)
    R += [
        row(m, "K1-K6", "12 V 继电器", "DIP 14.5x10.5mm", "6", "HK4100F-DC-12V", TODO,
            "触点 SPDT(1C) 3A@250VAC/30VDC; 线圈 12VDC/720ohm/16.7mA; 动作6ms/释放4ms; 接触电阻100mohm; 寿命电气10万次/机械1000万次",
            "6只同时吸合约100mA; K1-K3电感位, K4-K6电容位", "6", src),
        row(m, "U1", "16位 I2C I/O 扩展器", "TSSOP-24(建议)", "1", "TCA9535", TODO,
            "I2C 地址 0x20; 3.3V; 16位准双向; 用7位(P0.0-P0.5+P1.1)余9位; INT 未使用(本方案A)",
            "P0.0-P0.5 驱动 ULN2003A; P1.1=LCD背光; 封装需按实际来料确认", "1", src),
        row(m, "U2", "7路达林顿阵列", "SOIC-16/DIP-16", "1", "ULN2003A", TODO,
            "500mA/路; V_CE(sat)约0.9V; COM 必须接 +12V 才能启用内部续流二极管",
            "6路实际16.7mA/路 -> 余量30倍; 线圈得11.1V=92% > 75%吸合阈值", "1", src),
        row(m, "L1", "12 uH 电感", "磁环 T37-6 + 漆包线", "1", "T37-6 磁环", TODO,
            "AL=3.0nH/N^2; 约63圈; 绕组推荐0.5mm漆包线(3.5MHz趋肤深度约35um)",
            "自绕元件; 需实测电感量与SRF", "1", src),
        row(m, "L2", "33 uH 电感", "磁环 T106-6 + 漆包线", "1", "T106-6 磁环", TODO,
            "AL=11.6nH/N^2; 约53圈; T106-6 SRF约6.0MHz(需实测)",
            "自绕元件; 覆盖挂树天线30-34uH需求", "1", src),
        row(m, "L3", "47 uH 电感", "磁环 T106-6 + 漆包线", "1", "T106-6 磁环", TODO,
            "AL=11.6nH/N^2; 约64圈; T106-6 SRF约6.0MHz(需实测)",
            "自绕元件; 覆盖实验室天线35-50uH需求", "1", src),
        row(m, "C3", "22 pF", "1206 或 1812", "1", "NP0/COG 电容 22pF", TODO,
            "NP0(COG) 材质; 耐压 >=630V(谐振高压可达816Vrms); K4吸合时接入",
            "耐压为硬约束, 不得用 X7R 替代", "1", src),
        row(m, "C4", "120 pF", "1206 或 1812", "1", "NP0/COG 电容 120pF", TODO,
            "NP0(COG) 材质; 耐压 >=630V; K5吸合时接入", "同上", "1", src),
        row(m, "C5", "330 pF", "1206 或 1812", "1", "NP0/COG 电容 330pF", TODO,
            "NP0(COG) 材质; 耐压 >=630V; K6吸合时接入", "同上", "1", src),
        row(m, "T1,T2", "Tandem Match 定向耦合器磁芯", "磁环 FT37-43 + 漆包线", "2", "FT37-43 磁环", TODO,
            "初级1匝穿芯 + 次级10匝; 耦合度 20+/-3dB; 方向性>25dB; 带内平坦度<1.0dB",
            "T1/T2 各1只; 43材质 3.5MHz 的 mu'' 需实测(天线README §6)", "2", src),
        row(m, "R_sense", "1 kohm", "0805/1206", "2", "金属膜电阻 1kohm", TODO,
            "初值 1kohm, 需 NanoVNA 微调; 前向/反向各1只", "docs/05 §3.2; docs/05 §7 #4 待冻结",
            "2", "docs/05 §3.2, §7 #4; hardware/atu-module/README.md §3"),
        row(m, "D1,D2", "肖特基检波二极管", "DO-35/DO-7", "2", "1N5711", TODO,
            "与 HSMS-2850 并行对照(同一信号分别检波), 由软件选优或融合",
            "选型待 stage-3 实测对照(docs/05 §7 #5)", "2", "docs/05 §3.2, §7 #5; hardware/atu-module/README.md §3"),
        row(m, "D3,D4", "零偏置肖特基检波二极管", "SOT-23(双管)/SOD-323", "2", "HSMS-2850", TODO,
            "零偏置检波; 与 1N5711 并行对照", "选型待 stage-3 实测对照", "2", "docs/05 §3.2, §7 #5"),
        row(m, "U3", "检波放大器(可选)", "SOIC-8/DIP-8", "0-1", "LM358", TODO,
            "是否需要运放级待 stage-4 实测决定(docs/05 §7 #6); 本行数量标 0-1 表示未定",
            "DO NOT populate until stage-4 verdict", "0-1", "docs/05 §7 #6; hardware/atu-module/README.md §3"),
        row(m, "R_esd", "100 kohm 高压电阻", "轴向高压电阻", "1", "1kV 高压电阻 100kohm", TODO,
            "天线静电泄放到地; 耐压 1kV; 可用射频专用 GDT 替代",
            "二选一: 高压电阻 或 GDT", "1", "docs/04 §3.4; hardware/atu-module/README.md §3"),
    ]

    # ===================== pa-module =====================
    m = "pa-module"
    src = COMMON_SOURCE.format(mod=m)
    R += [
        row(m, "Q1,Q2,Q3", "N 沟道 MOSFET", "TO-92", "3", "BS170", TODO,
            "3管并联 E类开关功放; 总耗散能力约1.05-2.5W; 壳温<85C(2.5W连续30分钟, 热电偶实测)",
            "需 TO-92 散热片/底板铺铜; 无温度传感(无过温保护)", "3", src),
        row(m, "Q4 (备选)", "N 沟道功率 MOSFET", "TO-220", "0-1", "IRF510", TODO,
            "Pd=20W; 需5W输出时的备选; 预留兼容焊盘", "DNP: 仅在壳温实测超限时启用", "0-1", src),
        row(m, "D5 (或 ZD1)", "10V 稳压二极管", "SOT-23", "3", "BZX84-C10", TODO,
            "10V 双向稳压, 栅极保护; 每管1只", "注意寄生电容不得显著劣化方波边沿", "3", src),
        row(m, "R1", "10 kohm", "0805", "1", "电阻 10kohm 1%", TODO,
            "栅极固定偏置分压上臂(自5V LDO取得约2.1V)", "纯固定偏置, 无温度补偿", "1", src),
        row(m, "R2", "2.2 kohm", "0805", "1", "电阻 2.2kohm 1%", TODO,
            "栅极固定偏置分压下臂, 下端直接接地", "NTC 已取消(2026-09-26, docs/17 §12.5)", "1", src),
        row(m, "C6", "100 nF", "0805", "3", "X7R 100nF 50V", TODO,
            "旁路电容, 每管1只", "数量按3管计", "3", src),
        row(m, "C7", "升压输出滤波电容", "电解/钽", "1", "待定", TODO,
            "12V 轨纹波峰峰值 <0.5V @2.5W 发射",
            "型号与容值待 12V 升压模块 P7 定型后确定", "1", "docs/05 §3.3; docs/05 §7 #7"),
    ]

    # ===================== lpf-module =====================
    m = "lpf-module"
    src = COMMON_SOURCE.format(mod=m)
    R += [
        row(m, "L4-L6", "低通滤波电感", "磁环绕制", "3", "磁环 T106-6 (待定)", TODO,
            "三阶椭圆低通; 中心频率 3.55MHz; 通带 3.5-3.6MHz; 7.1MHz 处衰减 >=55dB",
            "磁环型号/圈数待硬件设计后填入(本模块 README 未给值)", "3", src),
        row(m, "C8-C10", "低通滤波电容", "1206/1812", "3", "NP0/COG 电容 (待定)", TODO,
            "NP0 材质; 耐压按谐振点高压留足裕量",
            "容值与耐压待硬件设计后填入", "3", src),
        row(m, "SH1", "金属屏蔽罩", "模块级", "0-1", "定制屏蔽罩", TODO,
            "可选, 抑制辐射耦合", "DNP 可选", "0-1", src),
    ]

    # ===================== mcu-ui-module =====================
    m = "mcu-ui-module"
    src = COMMON_MODULE_SRC = COMMON_SOURCE.format(mod=m)
    R += [
        row(m, "U4 (模组)", "ESP32-C3 主控模组", "2.54mm 排针模组", "1", "合宙 LuatOS ESP32C3-CORE (新款, 原生 USB)", TODO,
            "12个可用GPIO: GPIO0-8,10,12,13; GPIO11 不解锁 eFuse; GPIO18/19 原生USB; GPIO20/21 UART0; flash 必须 DIO 模式",
            "型号待用户确认: 模块README写 ESP32-C3 SuperMini, docs/05/docs/04 写合宙 LuatOS ESP32C3-CORE 新款 -> 需统一(E-01)",
            "1", "docs/05 §2.1-§2.2; docs/04 §3.5; hardware/mcu-ui-module/README.md §2"),
        row(m, "U5", "160 段点阵 LCD 控制器模组", "12864 模组(单排/双排待定)", "1", "ST7567 12864 液晶模组", TODO,
            "128x64; 仅 SPI; CS 接 GND(总线唯一从机); RST 与板复位共用; DC(A0)=GPIO10; 132列驱动/128列可见",
            "面板 180 度安装(W0=0, 方向位0xA0+0xC8); 排线针脚定义待硬件确认", "1", src),
        row(m, "U6", "旋转编码器", "EC11 带按压开关", "1", "EC11 (带SW)", TODO,
            "A/B 相接 GPIO2/GPIO8 (strapping, 须各加 10kohm 上拉, 静止为高); SW 接 GPIO13+GND, 10kohm 上拉, 中断驱动",
            "上电时勿转动旋钮(启动画面提示)", "1", src),
        row(m, "SW1,SW2", "轻触开关", "6x6mm 直插/贴片", "2", "轻触按键", TODO,
            "功能键/返回键; 其中之一复用板载 BOOT(GPIO9, strapping, 上电前不可下拉)",
            "GPIO9 已作 KEY_USER; 另一只为独立轻触键", "2", src),
        row(m, "LS1", "有源蜂鸣器", "12mm 直插", "1", "有源蜂鸣器 3.3V/5V", TODO,
            "有源(自带振荡); 挂 TCA9535 空闲位驱动(未分配, 见 docs/05 §2.3)",
            "GPIO 已用满, 不得直连 MCU; 驱动位待定(IOEXP_SPARE)", "1", src),
        row(m, "U7", "I2C 可编程时钟发生器", "MSOP-10 模块/芯片", "1", "Si5351A (模块或芯片)", TODO,
            "I2C 地址 0x60; 3.3V 射频轨(MD7673, 低噪声); 3.5-3.6MHz, 100Hz 步进",
            "CW 键控走 CLKx_DIS 使能命令, 不占 GPIO", "1", src),
        row(m, "U8", "八路缓冲器/线路驱动器", "TSSOP-20 (PWR)", "1", "SN74ACT244PWR", TODO,
            "5V 供电(ACT 4.5-5.5V); TTL 输入阈值, 3.3V 可直驱; +/-24mA, 输出 0-5V 方波驱动 MOS 栅极",
            "输入侧必须加 10kohm 下拉到 GND, 否则 Si5351 停振时输入悬空 -> 244 振荡 -> PA 自激发射; 每个 Vcc 加 100nF",
            "1", "docs/05 §2.5; ADR-0008 §2; hardware/mcu-ui-module/README.md §4"),
        row(m, "Q5", "N 沟道 MOSFET", "SOT-23", "1", "2N7002", TODO,
            "LCD 背光低边开关; 栅极经 R 1kohm 接 TCA9535 P1.1; Vdss=60V",
            "栅极必须加 10kohm 下拉到 GND: TCA9535 上电为输入高阻, 否则背光状态不定",
            "1", "docs/05 §2.3; hardware/atu-module/README.md §3"),
        row(m, "R_BL", "1 kohm", "0805", "1", "电阻 1kohm", TODO,
            "TCA9535 P1.1 到 2N7002 栅极串联电阻", "", "1", "docs/05 §2.3"),
        row(m, "R_BL2", "10 kohm", "0805", "1", "电阻 10kohm", TODO,
            "2N7002 栅极下拉到 GND(上电安全)", "", "1", "docs/05 §2.3"),
        row(m, "R_BLLED", "背光限流电阻", "0805", "1", "待定", TODO,
            "背光 LED 串限流; 阻值待模组背光电流确定", "待查模组规格", "1", "docs/05 §2.3"),
        row(m, "R3,R4", "10 kohm", "0805", "2", "电阻 10kohm", TODO,
            "EC11 A/B 上拉(strapping 强制要求, 静止为高)", "缓解2/3: 启动提示 + 看门狗重试", "2", "docs/05 §2.6"),
        row(m, "R5", "10 kohm", "0805", "1", "电阻 10kohm", TODO,
            "EC11_SW 上拉到 3.3V, 按下为低(接 GND)", "", "1", "docs/05 §2.2; ADR-0008 §8.3"),
        row(m, "R6,R7", "4.7 kohm", "0805", "2", "电阻 4.7kohm", TODO,
            "I2C0 SDA/SCL 上拉到 3.3V(共享总线: Si5351 + TCA9535)", "", "2", "docs/05 §2.2"),
        row(m, "R8,R9", "10 kohm", "0805", "2", "电阻 10kohm", TODO,
            "SN74ACT244 输入侧下拉到 GND(每路1只, 防悬空振荡)",
            "🔴 强制要求, 见 docs/05 §2.5", "2", "docs/05 §2.5"),
        row(m, "R10", "MOS 栅极下拉电阻", "0805", "3", "电阻 10kohm", TODO,
            "保证 OE/停振时 MOS 可靠截止(docs/05 §2.5 要求2)",
            "数量按 3 只 BS170 计", "3", "docs/05 §2.5"),
        row(m, "R_VBAT1", "22 kohm", "0805", "1", "电阻 22kohm 1%", TODO,
            "VBAT 分压上臂; 备选 24kohm(比值0.294)", "8.4V->2.46V; 6.0V->1.76V", "1", "docs/05 §2.7"),
        row(m, "R_VBAT2", "9.1 kohm", "0805", "1", "电阻 9.1kohm 1%", TODO,
            "VBAT 分压下臂; 备选 10kohm", "源阻抗 R3+(22k//9.1k)=7.4kohm < 10kohm 满足 ADC 要求", "1", "docs/05 §2.7"),
        row(m, "R_VBAT3", "1 kohm", "0805", "1", "电阻 1kohm", TODO,
            "ADC 串联限流/隔离电阻(GPIO3)", "静态电流 270uA", "1", "docs/05 §2.7"),
        row(m, "C_VBAT", "0.1 uF", "0805", "1", "X7R 100nF 50V", TODO,
            "VBAT 分压滤波, fc 约 245Hz", "", "1", "docs/05 §2.7"),
        row(m, "R12", "10 kohm", "0805", "1", "电阻 10kohm", TODO,
            "GPIO12 -> 升压模块 FB 下拉(上电安全硬件兜底)",
            "📌 建议采纳未定(docs/05 §7 #7a); 采纳才计入 BOM(E-03)", "0-1", "docs/05 §2.10.3, §7 #7a; docs/17 §12.6.5"),
        row(m, "X1", "32.768 kHz 晶振", "DNP 焊盘", "0-1", "32.768kHz 晶振", TODO,
            "Mesh 时钟可选升级 DNP; 当前依靠 ESP-NOW 每5分钟重同步", "DNP 不贴", "0-1", src),
        row(m, "R_ADC", "检波负载/分压电阻", "0805", "待定", "待定", TODO,
            "前向/反向检波 ADC 满量程由耦合器与 R_sense 决定; ADC 读数应落量程 20%-80%",
            "P4 R_sense 微调后再定值", "待定", "docs/05 §3.2"),
        row(m, "TP1-TP8", "测试点", "焊盘", "8", "测试点焊盘", TODO,
            "建议: 3.3V/5V/12V/ADC_FWD/ADC_REV/GND/I2C_SDA/I2C_SCL", "便于打样后调试", "8", "推导"),
    ]

    # ===================== power-module =====================
    m = "power-module"
    src = COMMON_SOURCE.format(mod=m)
    R += [
        row(m, "U9", "同步降压 DC-DC", "SOT-23-8/SOIC-8", "1", "MP2315", TODO,
            "5V 主轨; 峰值效率高; 替代原 7805 LDO(原效率约68%, 发热严重)",
            "满载30分钟温升需实测", "1", src),
        row(m, "U10", "LDO 线性稳压器", "SOT-23-5/89", "1", "MD7673E50VC1", TODO,
            "3.3V 射频轨(低噪声, 供 Si5351); 需与数字轨分轨 + pi 型滤波",
            "型号写法以模块README为准(MD7673)", "1", src),
        row(m, "U11", "升压 DC-DC 模块", "成品模块", "1", "3.7V->12V 升压模块 (PWM 可调)", TODO,
            "12V 功放轨; PWM 可调输出; 输出 12-13.8V; 纹波峰峰值 <0.5V @2.5W",
            "🔴 型号与 FB 网络参数未定(docs/05 §7 #7 待冻结); 电池为2S(7.4V)而模块标称3.7V输入需核对(E-02)",
            "1", "docs/05 §3.3, §7 #7; hardware/power-module/README.md §3"),
        row(m, "U12", "自恢复保险丝/保护", "贴片", "1", "待定", TODO,
            "电池保护/充电接口; 具体方案未定", "P8 相关: 电池保护与充电接口方案待设计", "1", src),
        row(m, "BT1", "2S 锂聚合物电池", "2S 500mAh", "1", "2S 500mAh 7.4V 锂电", TODO,
            "续航: 连续发射@2.5W 约38分钟; 竞赛静默释放继电器约100分钟; 待机约150分钟",
            "需配套电池座 + 保护/充电接口", "1", src),
        row(m, "BH1", "电池座", "2S 电池座", "1", "2S 电池座", TODO, "适配所选2S 500mAh电池", "", "1", src),
        row(m, "C11-C13", "输入/输出电容套件", "电解 + 钽 + 陶瓷", "1 套", "电解+钽+陶瓷 套件", TODO,
            "DC-DC 输入/输出电容; 含 100nF X7R 用于 pi 型 RC 滤波(3.3V 数字轨与本振独立滤波)",
            "容值与耐压待 DC-DC 选型确定", "1 套", src),
        row(m, "FB1", "π 型 RC 滤波元件组", "0805/磁珠", "1 套", "pi 型 RC 滤波 (待定)", TODO,
            "3.3V 数字轨独立 pi 型 RC 滤波; 含 100nF X7R",
            "🟠 模块README 写 RC, README 目录树/总表亦写 π 型 RC —— RC 通常靠电阻压降, 需确认是否有意为之(E-04)",
            "1 套", "docs/04 §3.6; hardware/power-module/README.md §3"),
        row(m, "C_3V3RF", "0.1 uF / 10 uF", "0805", "2", "X7R 100nF + 10uF", TODO,
            "3.3V 射频轨去耦(Si5351 就近)", "需实测噪声对本振相噪的影响", "2", src),
    ]

    # ===================== core-board =====================
    m = "core-board"
    src = COMMON_SOURCE.format(mod=m)
    R += [
        row(m, "J1-J6", "模块插座", "2.54mm 排母", "6 组", "2.54mm 排母", TODO,
            "6 组模块插座(pa/lpf/atu/power/mcu-ui 等); 承载 GPIO/PWM/SWR/电源轨",
            "建议用圆孔排母提升插拔寿命", "6 组", src),
        row(m, "J7-J9", "射频连接器", "SMA 母座(PCB 焊接)", "3", "SMA 母座 50ohm", TODO,
            "底板侧射频互联 50ohm; 配合 SMA 公-公短线使用",
            "底板 3 个, 模块侧共 6 个(ATU 模块自带)", "3", src),
        row(m, "J10", "天线座", "SMA 母座(面板)", "1", "SMA 母座", TODO,
            "ATU 输出 -> 天线座", "天线座也计入 interconnect 清单", "1", src),
        row(m, "C14-C20", "高频去耦电容组", "0805", "多只", "X7R 100nF 套件", TODO,
            "每个模块插座旁就近布置", "数量按插座数 x 2 估算, 布线时定", "多只", src),
        row(m, "X1", "32.768 kHz 晶振 DNP 焊盘", "DNP", "1", "32.768kHz 晶振焊盘", TODO,
            "Mesh 时钟可选升级; DNP 不贴", "仅焊盘", "0-1", src),
        row(m, "-", "PCB 四层板", "130x95mm 四层", "1", "四层板 (1.6mm)", TODO,
            "射频链路 50ohm; 电源平面分离: 12V/5V/3.3V射频/3.3V数字; 数字地与射频地单点汇接",
            "🟠 叠层(层序/厚度/阻抗)未定义, 下单前需补(E-05)", "1", src),
    ]

    # ===================== interconnect =====================
    m = "interconnect"
    src = COMMON_SOURCE.format(mod=m)
    R += [
        row(m, "J11-J16", "模块侧 SMA 母座", "SMA 母座", "6", "SMA 母座 50ohm", TODO,
            "射频链路: Si5351->PA->LPF->ATU->ANT; 各环节 50ohm",
            "PA/LPF/ATU 模块各 2 个(输入+输出); 与底板 3 个合计 9 个", "6", src),
        row(m, "W1-W3", "SMA 公-公短线", "SMA 跳线", "3", "SMA 公-公短线", TODO,
            "50ohm 屏蔽线, 长度尽量短; PA->LPF, LPF->ATU 等", "BOM 计 3 根", "3", src),
        row(m, "J17-J22", "模块排针", "2.54mm 排针", "6 组", "2.54mm 排针", TODO,
            "与底板 J1-J6 排母配对; 传递 GPIO/PWM/SWR/12V/5V/3V3/GND",
            "逐脚定义待 interconnect/connector/ 补充(目录现为空)", "6 组", src),
        row(m, "J23", "电池座/电池接口", "2S 电池座", "1", "2S 电池座", TODO,
            "与电源模块电池连接", "与 power-module BT1 配套", "1", src),
        row(m, "J24", "天线座", "SMA 母座", "1", "SMA 母座", TODO,
            "ATU 输出至天线", "与 core-board J10 为同一件, 汇总时避免重复计数", "1", src),
        row(m, "-", "线束材料", "多股软铜线/杜邦线/热缩管/扎带", "1 套", "线束材料套件", TODO,
            "12V 功放轨与 5V 主轨峰值电流下压降需实测; 模拟信号(ADC FWD/REV)建议屏蔽线",
            "线径/颜色约定/压接方式待 harness/ 补充", "1 套", src),
        row(m, "-", "屏蔽线(可选)", "屏蔽双绞/同轴", "可选", "屏蔽线", TODO,
            "用于 SWR 检波模拟信号与 Si5351 I2C 长距离走线", "可选", "可选", src),
    ]

    # ===================== enclosure =====================
    m = "enclosure"
    src = COMMON_SOURCE.format(mod=m)
    R += [
        row(m, "-", "外壳(3D 打印件)", "3D 打印 上下壳+模块支架+LCD压框+电池仓", "1 套", "3D 打印件 (STL/STEP/3MF)", TODO,
            "内部容纳 130x95mm 底板 + 55x65mm ATU + 2S 500mAh 电池; 成本目标约 5 元/套",
            "模型文件尚未建模(3d-print/ 目录为空)", "1 套", src),
        row(m, "-", "通用塑料盒(备选)", "成品盒改制", "0-1", "通用塑料盒", TODO,
            "按底板尺寸选型并手工开孔; 与 3D 打印件二选一", "替代方案", "0-1", src),
        row(m, "-", "M3 铜柱与螺钉", "M3", "1 套", "M3 铜柱 + 螺钉套件", TODO,
            "模块与底板固定; 含自攻螺钉", "长度待结构设计确定", "1 套", src),
        row(m, "-", "面板件", "亚克力或 PCB 材质", "1", "亚克力/PCB 面板", TODO,
            "开孔: LCD 12864 视窗, EC11 旋钮孔, 按键孔, SMA 座孔, 天线座孔, 蜂鸣器出声孔",
            "面板开孔图纸(DXF/PDF)待出(panel/ 目录为空)", "1", src),
        row(m, "-", "散热片/通风栅格(可选)", "成品/打印件", "0-1", "TO-92 散热片 + 通风栅格", TODO,
            "BS170 区域通风; 功放 2.5W 连续30分钟不超温; 壳温判据 <85C",
            "散热片为 PA 模块必需(见 pa-module BOM), 此行指壳体风道", "0-1", src),
    ]

    # ===================== antenna =====================
    m = "antenna"
    src = COMMON_SOURCE.format(mod=m)
    R += [
        row(m, "-", "垂直导线", "多股软铜线/镀锡铜线", "5 m", "多股软铜线 5m", TODO,
            "推荐 5m(最小4m/最大8m); 3.5-3.6MHz; 垂直极化; 远离树干与金属物",
            "无匹配网络时效率极低, 必须配合 ATU", "5 m", src),
        row(m, "-", "地线", "多股软铜线", "5 m", "地线 3 段 x 2m", TODO,
            "至少 5m, 推荐 3 段 x 2m 辐射状铺设", "", "3 x 2 m", src),
        row(m, "-", "地钉", "金属地钉", "3", "地钉", TODO, "固定辐射状地线", "", "3", src),
        row(m, "-", "悬挂件", "绝缘绳/抛绳器/绝缘支撑杆", "1 套", "绝缘绳 + 抛绳器/弹弓 + 绝缘支撑杆", TODO,
            "垂直悬挂; 现场架设与收放", "", "1 套", src),
        row(m, "-", "馈线", "同轴馈线", "1", "同轴馈线 (对接 ATU 输出)", TODO,
            "SMA 座与同轴馈线; 弯曲半径满足要求", "与 interconnect 的 SMA 跳线区分", "1", src),
        row(m, "-", "测量仪器(非 BOM)", "手持矢量网络分析仪", "1", "NanoVNA-F 或同类", TODO,
            "用于实测 3.5MHz 阻抗 R+jX 与匹配轨迹; 属于工具而非装机物料",
            "非装机件, 单独列出以便采购判断", "1", src),
    ]

    return R


def write_csv(path, rows, header):
    # newline="" + explicit lineterminator="\n" => LF only; utf-8-sig => BOM
    buf = io.StringIO()
    w = csv.DictWriter(buf, fieldnames=header, lineterminator="\n", extrasaction="ignore")
    w.writeheader()
    for r in rows:
        w.writerow(r)
    data = buf.getvalue()
    with open(path, "w", encoding="utf-8-sig", newline="") as f:
        f.write(data)
    return len(rows)


def write_md(path, text):
    with open(path, "w", encoding="utf-8", newline="\n") as f:
        f.write(text)


def md_table(rows, header, cols):
    out = ["| " + " | ".join(cols) + " |", "|" + "|".join(["---"] * len(cols)) + "|"]
    for r in rows:
        cells = []
        for c in cols:
            v = str(r.get(c, "")).replace("|", "\\|").replace("\n", " ")
            cells.append(v)
        out.append("| " + " | ".join(cells) + " |")
    return "\n".join(out)


def main():
    rows = build_rows()
    os.makedirs(BOM_DIR, exist_ok=True)

    modules = []
    for r in rows:
        if r["模块"] not in modules:
            modules.append(r["模块"])

    written = []
    for mod in modules:
        sub = [r for r in rows if r["模块"] == mod]
        p = os.path.join(BOM_DIR, "bom-%s.csv" % mod)
        n = write_csv(p, sub, HEADER)
        written.append((p, n))

    p = os.path.join(BOM_DIR, "bom-summary.csv")
    n = write_csv(p, rows, HEADER)
    written.append((p, n))

    # Markdown summary table (same data, readable on GitHub)
    md_cols = ["位号", "参数", "封装", "数量", "建议型号", "LCSC 编号", "关键规格", "模块", "备注"]
    md = []
    md.append("# BOM · ARDF-MeshTuneFox80（立创EDA 导入包）\n")
    md.append("> 本文件由 `scripts/build-lceda-import-pack.py` 生成，**请勿手工编辑**。")
    md.append("> 权威数据源与字段说明见 [bom/README.md](README.md)。\n")
    md.append("## 0. 编码与导入说明\n")
    md.append("- 全部 CSV 为 **UTF-8 带 BOM + LF**，Excel 直接双击打开中文不乱码。")
    md.append("- 列顺序：`位号 | 参数 | 封装 | 数量 | 建议型号 | LCSC 编号 | 关键规格 | 模块 | 备注 | 统一数量 | 来源`。")
    md.append("- 🔴 **`LCSC 编号` 列全部为 `待查`**：本机 `web_search` 无 API key、")
    md.append("  立创商城搜索接口对本机返回 403 / ACL 拒绝，**无法核实真实在售编号**。")
    md.append("  按纪律要求**留空标注待查，绝不编造**。请在立创EDA 内用「建议型号」或立创商城搜索核对后回填。")
    md.append("- 数量列写 `0-1` / `待定` / `多只` 的条目表示**尚未冻结**，不可直接下单。\n")
    md.append("## 1. 按模块汇总\n")
    md.append("| 模块 | 器件行数 | 分模块 CSV |")
    md.append("|---|---|---|")
    for mod in modules:
        sub = [r for r in rows if r["模块"] == mod]
        md.append("| `%s` | %d | [bom-%s.csv](bom-%s.csv) |" % (mod, len(sub), mod, mod))
    md.append("| **合计** | **%d** | [bom-summary.csv](bom-summary.csv) |" % len(rows))
    md.append("")
    md.append("## 2. 逐模块明细\n")
    for mod in modules:
        sub = [r for r in rows if r["模块"] == mod]
        md.append("### 2.%d %s（%d 行）\n" % (modules.index(mod) + 1, mod, len(sub)))
        md.append(md_table(sub, HEADER, md_cols))
        md.append("")
    write_md(os.path.join(BOM_DIR, "bom.md"), "\n".join(md))

    for p, n in written:
        print("CSV %-46s rows=%d" % (os.path.relpath(p, REPO), n))
    print("MD  %-46s modules=%d rows=%d" % (
        os.path.relpath(os.path.join(BOM_DIR, "bom.md"), REPO), len(modules), len(rows)))


if __name__ == "__main__":
    main()
