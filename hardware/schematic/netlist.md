# 网表 / 逐脚连接表 · ARDF-MeshTuneFox80（立创EDA 导入包）

> 本文件由 `scripts/build-lceda-import-pack.py` 生成，**请勿手工编辑**。
> 每一行都带 `依据来源` 列，指到 `docs/05` / `docs/17` / `docs/04` / 模块 README 的具体小节。

## 0. 文件与用法

| 文件 | 用途 |
|---|---|
| [hardware/bom/netlist.csv](../bom/netlist.csv) | 中文表头，逐条连接（含说明与依据），给人看 |
| [hardware/schematic/netlist.csv](netlist.csv) | 英文表头（`net,net_label,src_ref,src_pin,dst_ref,dst_pin,note,source`），给脚本/后续原理图生成用 |

- 编码：**UTF-8 带 BOM + LF**。
- `net_label` 是可安全用作 KiCad/立创EDA **网络标签**的 ASCII 名（`+12V` 之类电源网络用 `+12V` 亦可被两端识别；`net` 列保留原始命名）。
- 🟠 标注「未冻结」的行表示**文档里没有给出完整接法**，需硬件设计补齐后才可作为画图依据。

## 1. 覆盖统计

| 项 | 数量 |
|---|---|
| 连接行数 | 146 |
| 去重网络数 | 74 |

### 1.1 网络名清单（74 个）

`ADC_FWD`, `ADC_REV`, `ADC_VBAT`, `EC11_A`, `EC11_B`, `EC11_SW`, `KEY_USER`, `I2C_SDA`, `I2C_SCL`, `PA_PWR_PWM`, `VDD_SPI_NC`, `USB_DM`, `USB_DP`, `UART0_TX`, `UART0_RX`, `GND`, `TCA9535_INT`, `IOEXP_RELAY_K1`, `IOEXP_RELAY_K2`, `IOEXP_RELAY_K3`, `IOEXP_RELAY_K4`, `IOEXP_RELAY_K5`, `IOEXP_RELAY_K6`, `IOEXP_LCD_BL`, `IOEXP_SPARE_P1_0`, `IOEXP_SPARE_P0_6`, `IOEXP_SPARE_P0_7`, `IOEXP_SPARE_P1_2`, `IOEXP_SPARE_P1_3`, `IOEXP_SPARE_P1_4`, `IOEXP_SPARE_P1_5`, `IOEXP_SPARE_P1_6`, `IOEXP_SPARE_P1_7`, `+12V_RELAY`, `RELAY_K1_COIL`, `RELAY_K2_COIL`, `RELAY_K3_COIL`, `RELAY_K4_COIL`, `RELAY_K5_COIL`, `RELAY_K6_COIL`, `LCD_SCK`, `LCD_MOSI`, `LCD_DC`, `LCD_RST`, `LCD_BL_CTRL`, `LCD_BL_GATE_PD`, `LCD_BL_K`, `+3V3_DIG`, `LCD_V0`, `CW_KEY_SRC`, `RF_SRC_CLK`, `RF_SRC_PD`, `PA_GATE`, `PA_GATE_PD`, `PA_BIAS`, `+5V`, `PA_DRAIN`, `PA_BYPASS`, `DEC244`, `PA_RF_OUT`, `RF_THRU`, `XFWD_SEC`, `DET_FWD`, `XREV_SEC`, `DET_REV`, `LM358_IN`, `VBAT`, `VBAT_DIV`, `ANT_ESD`, `+12V`, `+3V3_RF`, `RELAY_CONTACTS`, `BUZZER_DRV`, `FB_PULLDOWN`

## 2. 子系统覆盖

| 子系统 | 覆盖内容 | 依据 |
|---|---|---|
| ESP32-C3 12 个 GPIO 全部去向 | GPIO0/1/3 ADC · GPIO2/8 EC11 · GPIO4/5 I2C · GPIO6/7 SPI2 · GPIO10 LCD_DC · GPIO12 PA_PWR_PWM · GPIO13 EC11_SW（另 GPIO9=BOOT、11=NC、18/19=USB、20/21=UART0） | docs/05-hw-sw-interface-contract.md §2.2/§2.8 |
| TCA9535 16 位（用 7 + 预留 9） | P0.0-P0.5=K1-K6 · P1.1=LCD 背光 · 预留 P1.0 + P0.6/P0.7 + P1.2-P1.7 = 9 位 | docs/05-hw-sw-interface-contract.md §2.3; docs/17-gpio-allocation-audit.md §2.1 |
| ULN2003A 7 路（6 继电器 + COM 接 +12V） | IN1-IN6 <- P0.0-P0.5；OUT1-OUT6 -> K1-K6 线圈；COM -> +12V（内部续流二极管） | docs/05-hw-sw-interface-contract.md §2.4 |
| SPI（SCK/MOSI/DC） | GPIO6->SCK · GPIO7->MOSI · GPIO10->A0/DC · CS 接 GND · RST 与板复位共用 | docs/05-hw-sw-interface-contract.md §2.2; ADR-0008 §3.1 |
| I2C（SDA/SCL + 上拉） | GPIO4/GPIO5 + 4.7kohm 上拉；挂 Si5351(0x60) 与 TCA9535(0x20) | docs/05-hw-sw-interface-contract.md §2.2/§2.3 |
| ADC 三路（分压网络含 R1/R2/R3） | GPIO0/GPIO1 检波 · GPIO3 电池 22kohm/9.1kohm/1kohm + 0.1uF | docs/05-hw-sw-interface-contract.md §2.7/§3.2 |
| 电源域（+12V / +5V / +3V3_RF / +3V3_DIG / VDD_SPI） | 升压->+12V · MP2315->+5V · MD7673->+3V3_RF · pi 滤波->+3V3_DIG · GPIO11(VDD_SPI) 标 NC 不解锁 | docs/05-hw-sw-interface-contract.md §3.3; docs/04-hardware-architecture.md §3.6 |
| Si5351 输出与 PA 键控链（CW 走 CLKx_DIS 而非 GPIO） | CW = I2C 写 CLKx_DIS · CLK0->244 输入(10kohm 下拉)->244 输出->BS170 栅极(10kohm 下拉) | docs/05-hw-sw-interface-contract.md §2.5; ADR-0008 §3.2 |
| 天线静电泄放 | 天线座中心 -> 1kV 100kohm 高压电阻 到地（或 GDT） | docs/04-hardware-architecture.md §3.4 |
| 地平面/星形地 | 射频地与数字地单点汇接于底板一点；四层板地平面完整 | docs/04-hardware-architecture.md §3.1; hardware/core-board/README.md §6 |
| Tandem Match 耦合器与检波 | T1/T2 FT37-43 · R_sense 1kohm · 1N5711 与 HSMS-2850 并行对照 | docs/05-hw-sw-interface-contract.md §3.2; hardware/atu-module/README.md §3 |
| EC11 与按键 | GPIO2/8 直连(10kohm 上拉) · GPIO13 SW 直连(10kohm 上拉) · GPIO9 BOOT/KEY_USER | docs/05-hw-sw-interface-contract.md §2.2/§2.6; ADR-0008 §8.3 |

## 3. 全部连接明细

| 网络名 | 源器件.引脚 | 目标器件.引脚 | 说明 | 依据来源 |
|---|---|---|---|---|
| `ADC_FWD` | `U4.GPIO0` | `T1.1 (次级)` | ADC1_CH0 前向检波输入; 满量程由耦合器与 R_sense 决定; 2W 下读数应落量程 20%-80% | docs/05-hw-sw-interface-contract.md §2.2/§2.8; §3.2 |
| `ADC_REV` | `U4.GPIO1` | `T2.1 (次级)` | ADC1_CH1 反向检波输入; SWR=2.0@2W 时读数应 >=量程 5% | docs/05-hw-sw-interface-contract.md §2.2/§2.8; §3.2 |
| `ADC_VBAT` | `U4.GPIO3` | `R_VBAT3.2` | ADC1_CH3 电池电压(经 22k/9.1k/1k 分压 + 0.1uF); 6.0V->1.76V, 8.4V->2.46V | docs/05-hw-sw-interface-contract.md §2.2/§2.8; §2.7 |
| `EC11_A` | `U4.GPIO2` | `U6.A` | strapping 脚: 必须有 10kohm 上拉(R3), 静止为高; 上电时勿转动旋钮 | docs/05-hw-sw-interface-contract.md §2.2/§2.8; §2.6 |
| `EC11_B` | `U4.GPIO8` | `U6.B` | strapping 脚: 必须有 10kohm 上拉(R4), 静止为高 | docs/05-hw-sw-interface-contract.md §2.2/§2.8; §2.6 |
| `EC11_SW` | `U4.GPIO13` | `U6.SW` | 按下接 GND + 10kohm 上拉(R5), 中断驱动; GPIO13 = SPIWP, 固件须先 gpio_reset_pin 撤销 MSPI 保留 | docs/05-hw-sw-interface-contract.md §2.2/§2.8; docs/17-gpio-allocation-audit.md §12.6.3 |
| `KEY_USER` | `U4.GPIO9` | `SW2.1` | BOOT 按键(strapping): 上电前不可下拉; 启动后可作 KEY_USER | docs/05-hw-sw-interface-contract.md §2.2/§2.8; §2.6 |
| `I2C_SDA` | `U4.GPIO4` | `R6.1` | I2C0 SDA, 开漏; 4.7kohm 上拉到 3.3V; 共享总线 Si5351 + TCA9535 | docs/05-hw-sw-interface-contract.md §2.2/§2.8 |
| `I2C_SCL` | `U4.GPIO5` | `R7.1` | I2C0 SCL, 开漏; 4.7kohm 上拉到 3.3V | docs/05-hw-sw-interface-contract.md §2.2/§2.8 |
| `PA_PWR_PWM` | `U4.GPIO12` | `U11.FB` | LEDC PWM -> 升压模块 FB 网络; 低=最低功率; 高阻/高=有推向满功率风险 | docs/05-hw-sw-interface-contract.md §2.2/§2.8; §2.10.2 |
| `VDD_SPI_NC` | `U4.GPIO11` | `-.NC` | 🔴 不可用: VDD_SPI, 已决定不解锁 eFuse; 原理图上标注 NC/保留, 不得接任何网络 | docs/05-hw-sw-interface-contract.md §2.2/§2.8 §2.1 |
| `USB_DM` | `U4.GPIO18` | `J_USB.D-` | 原生 USB Serial/JTAG: 日志/中控/下载 | docs/05-hw-sw-interface-contract.md §2.2/§2.8 §2.2 |
| `USB_DP` | `U4.GPIO19` | `J_USB.D+` | 同上 | docs/05-hw-sw-interface-contract.md §2.2/§2.8 §2.2 |
| `UART0_TX` | `U4.GPIO20` | `J_UART.TX` | UART0 备用串口(板载 USB-UART 桥) | docs/05-hw-sw-interface-contract.md §2.2/§2.8 §2.2 |
| `UART0_RX` | `U4.GPIO21` | `J_UART.RX` | 同上 | docs/05-hw-sw-interface-contract.md §2.2/§2.8 §2.2 |
| `EC11_A` | `R3.2` | `+3V3_DIG.-` | EC11_A 上拉 10kohm(strapping 强制要求) | docs/05-hw-sw-interface-contract.md §2.2/§2.8 §2.6 |
| `EC11_B` | `R4.2` | `+3V3_DIG.-` | EC11_B 上拉 10kohm(strapping 强制要求) | docs/05-hw-sw-interface-contract.md §2.2/§2.8 §2.6 |
| `EC11_SW` | `R5.2` | `+3V3_DIG.-` | EC11_SW 上拉 10kohm | docs/05-hw-sw-interface-contract.md §2.2; ADR-0008 §8.3 |
| `GND` | `U6.SW2 (另一端)` | `GND.-` | EC11_SW 按下时把 EC11_SW 拉低 | docs/05-hw-sw-interface-contract.md §2.2; ADR-0008 §8.3 |
| `I2C_SDA` | `R6.2` | `+3V3_DIG.-` | I2C SDA 上拉 4.7kohm | docs/05-hw-sw-interface-contract.md §2.2/§2.8 |
| `I2C_SCL` | `R7.2` | `+3V3_DIG.-` | I2C SCL 上拉 4.7kohm | docs/05-hw-sw-interface-contract.md §2.2/§2.8 |
| `I2C_SDA` | `U7.SDA` | `U4.GPIO4` | Si5351 I2C 数据(地址 0x60) | docs/05-hw-sw-interface-contract.md §2.3/§2.5; docs/04-hardware-architecture.md §3.5 |
| `I2C_SCL` | `U7.SCL` | `U4.GPIO5` | Si5351 I2C 时钟 | docs/05-hw-sw-interface-contract.md §2.3/§2.5 |
| `I2C_SDA` | `U1.SDA` | `U4.GPIO4` | TCA9535 I2C 数据(地址 0x20; A2/A1/A0 接法待确认) | docs/05-hw-sw-interface-contract.md §2.3, §7 #2 |
| `I2C_SCL` | `U1.SCL` | `U4.GPIO5` | TCA9535 I2C 时钟 | docs/05-hw-sw-interface-contract.md §2.3 |
| `TCA9535_INT` | `U1.INT` | `-.NC` | 本方案 A 不使用 INT; 若日后走 C/C-prime 方案需 10kohm 上拉到 3.3V | docs/17-gpio-allocation-audit.md §3.5, §7 R6 |
| `IOEXP_RELAY_K1` | `U1.P0.0` | `U2.IN1` | TCA9535 P0.0 -> ULN2003A IN1(3.3V 并行, 6 根) | docs/05-hw-sw-interface-contract.md §2.3; docs/17-gpio-allocation-audit.md §2.1 |
| `IOEXP_RELAY_K2` | `U1.P0.1` | `U2.IN2` | TCA9535 P0.1 -> ULN2003A IN2(3.3V 并行, 6 根) | docs/05-hw-sw-interface-contract.md §2.3; docs/17-gpio-allocation-audit.md §2.1 |
| `IOEXP_RELAY_K3` | `U1.P0.2` | `U2.IN3` | TCA9535 P0.2 -> ULN2003A IN3(3.3V 并行, 6 根) | docs/05-hw-sw-interface-contract.md §2.3; docs/17-gpio-allocation-audit.md §2.1 |
| `IOEXP_RELAY_K4` | `U1.P0.3` | `U2.IN4` | TCA9535 P0.3 -> ULN2003A IN4(3.3V 并行, 6 根) | docs/05-hw-sw-interface-contract.md §2.3; docs/17-gpio-allocation-audit.md §2.1 |
| `IOEXP_RELAY_K5` | `U1.P0.4` | `U2.IN5` | TCA9535 P0.4 -> ULN2003A IN5(3.3V 并行, 6 根) | docs/05-hw-sw-interface-contract.md §2.3; docs/17-gpio-allocation-audit.md §2.1 |
| `IOEXP_RELAY_K6` | `U1.P0.5` | `U2.IN6` | TCA9535 P0.5 -> ULN2003A IN6(3.3V 并行, 6 根) | docs/05-hw-sw-interface-contract.md §2.3; docs/17-gpio-allocation-audit.md §2.1 |
| `IOEXP_LCD_BL` | `U1.P1.1` | `R_BL.1` | 背光开关: P1.1 -> R 1kohm -> 2N7002 栅极 | docs/05-hw-sw-interface-contract.md §2.3 |
| `IOEXP_SPARE_P1_0` | `U1.P1.0` | `-.NC` | 预留(原 EC11 按键, 已释放) | docs/05-hw-sw-interface-contract.md §2.3; docs/17-gpio-allocation-audit.md §2.1 |
| `IOEXP_SPARE_P0_6` | `U1.P0.6` | `-.NC` | 预留 9 位之一(蜂鸣器/状态灯/散热风扇/天线泄放等) | docs/05-hw-sw-interface-contract.md §2.3; docs/17-gpio-allocation-audit.md §2.1 |
| `IOEXP_SPARE_P0_7` | `U1.P0.7` | `-.NC` | 预留 9 位之一(蜂鸣器/状态灯/散热风扇/天线泄放等) | docs/05-hw-sw-interface-contract.md §2.3; docs/17-gpio-allocation-audit.md §2.1 |
| `IOEXP_SPARE_P1_2` | `U1.P1.2` | `-.NC` | 预留 9 位之一(蜂鸣器/状态灯/散热风扇/天线泄放等) | docs/05-hw-sw-interface-contract.md §2.3; docs/17-gpio-allocation-audit.md §2.1 |
| `IOEXP_SPARE_P1_3` | `U1.P1.3` | `-.NC` | 预留 9 位之一(蜂鸣器/状态灯/散热风扇/天线泄放等) | docs/05-hw-sw-interface-contract.md §2.3; docs/17-gpio-allocation-audit.md §2.1 |
| `IOEXP_SPARE_P1_4` | `U1.P1.4` | `-.NC` | 预留 9 位之一(蜂鸣器/状态灯/散热风扇/天线泄放等) | docs/05-hw-sw-interface-contract.md §2.3; docs/17-gpio-allocation-audit.md §2.1 |
| `IOEXP_SPARE_P1_5` | `U1.P1.5` | `-.NC` | 预留 9 位之一(蜂鸣器/状态灯/散热风扇/天线泄放等) | docs/05-hw-sw-interface-contract.md §2.3; docs/17-gpio-allocation-audit.md §2.1 |
| `IOEXP_SPARE_P1_6` | `U1.P1.6` | `-.NC` | 预留 9 位之一(蜂鸣器/状态灯/散热风扇/天线泄放等) | docs/05-hw-sw-interface-contract.md §2.3; docs/17-gpio-allocation-audit.md §2.1 |
| `IOEXP_SPARE_P1_7` | `U1.P1.7` | `-.NC` | 预留 9 位之一(蜂鸣器/状态灯/散热风扇/天线泄放等) | docs/05-hw-sw-interface-contract.md §2.3; docs/17-gpio-allocation-audit.md §2.1 |
| `+12V_RELAY` | `U2.COM` | `+12V.-` | 🔴 COM 必须接 +12V: 内部续流二极管靠它生效(不接则继电器反峰无抑制) | docs/05-hw-sw-interface-contract.md §2.4 |
| `RELAY_K1_COIL` | `U2.OUT1` | `K1.线圈+` | ULN2003A OUT1 低边吸合 K1 线圈; 16.7mA/只, 6 只同吸 <110mA | docs/05-hw-sw-interface-contract.md §2.4 |
| `+12V_RELAY` | `K1.线圈-` | `+12V.-` | K1 线圈另一端接 +12V 功放轨; 线圈得电压 12-0.9=11.1V=92% (>75% 吸合阈值) | docs/05-hw-sw-interface-contract.md §2.4 |
| `RELAY_K2_COIL` | `U2.OUT2` | `K2.线圈+` | ULN2003A OUT2 低边吸合 K2 线圈; 16.7mA/只, 6 只同吸 <110mA | docs/05-hw-sw-interface-contract.md §2.4 |
| `+12V_RELAY` | `K2.线圈-` | `+12V.-` | K2 线圈另一端接 +12V 功放轨; 线圈得电压 12-0.9=11.1V=92% (>75% 吸合阈值) | docs/05-hw-sw-interface-contract.md §2.4 |
| `RELAY_K3_COIL` | `U2.OUT3` | `K3.线圈+` | ULN2003A OUT3 低边吸合 K3 线圈; 16.7mA/只, 6 只同吸 <110mA | docs/05-hw-sw-interface-contract.md §2.4 |
| `+12V_RELAY` | `K3.线圈-` | `+12V.-` | K3 线圈另一端接 +12V 功放轨; 线圈得电压 12-0.9=11.1V=92% (>75% 吸合阈值) | docs/05-hw-sw-interface-contract.md §2.4 |
| `RELAY_K4_COIL` | `U2.OUT4` | `K4.线圈+` | ULN2003A OUT4 低边吸合 K4 线圈; 16.7mA/只, 6 只同吸 <110mA | docs/05-hw-sw-interface-contract.md §2.4 |
| `+12V_RELAY` | `K4.线圈-` | `+12V.-` | K4 线圈另一端接 +12V 功放轨; 线圈得电压 12-0.9=11.1V=92% (>75% 吸合阈值) | docs/05-hw-sw-interface-contract.md §2.4 |
| `RELAY_K5_COIL` | `U2.OUT5` | `K5.线圈+` | ULN2003A OUT5 低边吸合 K5 线圈; 16.7mA/只, 6 只同吸 <110mA | docs/05-hw-sw-interface-contract.md §2.4 |
| `+12V_RELAY` | `K5.线圈-` | `+12V.-` | K5 线圈另一端接 +12V 功放轨; 线圈得电压 12-0.9=11.1V=92% (>75% 吸合阈值) | docs/05-hw-sw-interface-contract.md §2.4 |
| `RELAY_K6_COIL` | `U2.OUT6` | `K6.线圈+` | ULN2003A OUT6 低边吸合 K6 线圈; 16.7mA/只, 6 只同吸 <110mA | docs/05-hw-sw-interface-contract.md §2.4 |
| `+12V_RELAY` | `K6.线圈-` | `+12V.-` | K6 线圈另一端接 +12V 功放轨; 线圈得电压 12-0.9=11.1V=92% (>75% 吸合阈值) | docs/05-hw-sw-interface-contract.md §2.4 |
| `GND` | `U2.GND` | `GND.-` | ULN2003A 地(e 脚) | docs/05-hw-sw-interface-contract.md §2.4 |
| `LCD_SCK` | `U4.GPIO6` | `U5.SCK/CLK` | SPI2 SCK -> ST7567 | docs/05-hw-sw-interface-contract.md §2.2; ADR-0008 §3.1 |
| `LCD_MOSI` | `U4.GPIO7` | `U5.MOSI/SI` | SPI2 MOSI -> ST7567 | docs/05-hw-sw-interface-contract.md §2.2; ADR-0008 §3.1 |
| `LCD_DC` | `U4.GPIO10` | `U5.A0/DC` | 命令/数据选择, 必须直连(每字节翻转, 不可挂 I2C 扩展器) | docs/05-hw-sw-interface-contract.md §2.2; ADR-0008 §3.1; §3.1 |
| `GND` | `U5.CS` | `GND.-` | 🔴 CS 接 GND: ST7567 是 SPI2 上唯一从机 -> 省 1 个 GPIO | docs/05-hw-sw-interface-contract.md §2.2; ADR-0008 §3.1 |
| `LCD_RST` | `U5.RST` | `RESET_BOARD.-` | 🔴 RST 与板复位共用: 上电复位即可 -> 省 1 脚与 RC 电路 | docs/05-hw-sw-interface-contract.md §2.2; ADR-0008 §3.1 |
| `LCD_BL_CTRL` | `R_BL.2` | `Q5.G` | P1.1 经 1kohm 到 2N7002 栅极 | docs/05-hw-sw-interface-contract.md §2.3 |
| `LCD_BL_GATE_PD` | `R_BL2.1` | `Q5.G` | 🔴 栅极 10kohm 下拉到 GND: TCA9535 上电为输入高阻, 否则背光状态不定 | docs/05-hw-sw-interface-contract.md §2.3 |
| `GND` | `R_BL2.2` | `GND.-` | 背光 MOS 栅极下拉另一端 | docs/05-hw-sw-interface-contract.md §2.3 |
| `LCD_BL_K` | `Q5.D` | `U5.LED-` | 2N7002 漏极接背光 LED 阴极串 | docs/05-hw-sw-interface-contract.md §2.3 |
| `GND` | `Q5.S` | `GND.-` | 2N7002 源极 | docs/05-hw-sw-interface-contract.md §2.3 |
| `+3V3_DIG` | `R_BLLED.1` | `U5.LED+` | 背光 LED 阳极经限流电阻(R_BLLED 阻值待模组规格确定) | docs/05-hw-sw-interface-contract.md §2.3 |
| `+3V3_DIG` | `U5.VDD/VDDIO` | `U5.VDD/VDDIO` | LCD 逻辑供电 3.3V | docs/05-hw-sw-interface-contract.md §2.2; ADR-0008 §3.1 |
| `LCD_V0` | `U5.V0/VOUT` | `LCD_BIAS.-` | 对比度偏置网络: 模组自带或外接可调(未冻结) | docs/05-hw-sw-interface-contract.md §2.3 |
| `GND` | `U5.VSS` | `GND.-` | LCD 地 | docs/05-hw-sw-interface-contract.md §2.2; ADR-0008 §3.1 |
| `CW_KEY_SRC` | `U4.I2C 写 CLKx_DIS` | `U7.CLKx_CONTROL` | 🔴 CW 键控 = Si5351 使能命令(I2C 写 CLKx_DIS 位), 不占任何 GPIO; 无插入损耗/无开关损耗/无静态电流 | docs/05-hw-sw-interface-contract.md §2.5; ADR-0008 §3.2 |
| `RF_SRC_CLK` | `U7.CLK0` | `U8.1A` | Si5351 3.3V CMOS 方波 -> 244 输入 | docs/05-hw-sw-interface-contract.md §2.5; ADR-0008 §3.2 |
| `RF_SRC_PD` | `R8.1` | `U8.1A` | 🔴 244 输入侧 10kohm 下拉到 GND: Si5351 停振时输入悬空会使 244 振荡 -> PA 自激发射 | docs/05-hw-sw-interface-contract.md §2.5; ADR-0008 §3.2 |
| `GND` | `R8.2` | `GND.-` | 输入下拉另一端 | docs/05-hw-sw-interface-contract.md §2.5; ADR-0008 §3.2 |
| `PA_GATE` | `U8.1Y` | `Q1.G` | 244 输出 0-5V 方波(+/-24mA) -> BS170 栅极(Class-E 开关) | docs/05-hw-sw-interface-contract.md §2.5; ADR-0008 §3.2 |
| `PA_GATE` | `U8.1Y` | `Q2.G` | 3 管并联: 栅极共连 | docs/05-hw-sw-interface-contract.md §2.5; ADR-0008 §3.2 |
| `PA_GATE` | `U8.1Y` | `Q3.G` | 3 管并联: 栅极共连 | docs/05-hw-sw-interface-contract.md §2.5; ADR-0008 §3.2 |
| `PA_GATE_PD` | `R10.1` | `Q1.G` | 🔴 MOS 栅极下拉: 保证 OE/停振时 MOS 可靠截止 | docs/05-hw-sw-interface-contract.md §2.5; ADR-0008 §3.2 |
| `PA_GATE_PD` | `R10.1` | `Q2.G` | 🔴 MOS 栅极下拉: 保证 OE/停振时 MOS 可靠截止 | docs/05-hw-sw-interface-contract.md §2.5; ADR-0008 §3.2 |
| `PA_GATE_PD` | `R10.1` | `Q3.G` | 🔴 MOS 栅极下拉: 保证 OE/停振时 MOS 可靠截止 | docs/05-hw-sw-interface-contract.md §2.5; ADR-0008 §3.2 |
| `GND` | `R10.2` | `GND.-` | 栅极下拉另一端(3 管共用描述) | docs/05-hw-sw-interface-contract.md §2.5; ADR-0008 §3.2 |
| `PA_BIAS` | `R1.2` | `R2.1` | 栅极固定偏置分压中点 约2.1V(纯固定偏置, 无温度补偿) | docs/05-hw-sw-interface-contract.md §3.1; docs/17-gpio-allocation-audit.md §12.5 |
| `+5V` | `R1.1` | `+5V.-` | 偏置分压上臂接 5V 主轨 | docs/04-hardware-architecture.md §3.6 |
| `GND` | `R2.2` | `GND.-` | 偏置分压下臂直接接地(NTC 已取消) | docs/17-gpio-allocation-audit.md §12.5 |
| `PA_BIAS` | `R1.2` | `Q1.G` | 固定栅极偏置到各管栅极 | docs/04-hardware-architecture.md §3.2 |
| `GND` | `D5_prot.A` | `Q1.G` | BZX84-C10 10V 稳压管栅极保护(每管1只) | docs/04-hardware-architecture.md §3.2 |
| `PA_DRAIN` | `+12V.-` | `Q1.D` | BS170 漏极 12-13.8V(升压可调); 3 管并联 | docs/05-hw-sw-interface-contract.md §3.1 |
| `GND` | `Q1.S` | `GND.-` | BS170 源极 | docs/04-hardware-architecture.md §3.2 |
| `PA_BYPASS` | `C6.1` | `Q1.D` | 100nF 旁路电容(每管1只) | docs/04-hardware-architecture.md §3.2 |
| `PA_BIAS` | `R1.2` | `Q2.G` | 固定栅极偏置到各管栅极 | docs/04-hardware-architecture.md §3.2 |
| `GND` | `D5_prot.A` | `Q2.G` | BZX84-C10 10V 稳压管栅极保护(每管1只) | docs/04-hardware-architecture.md §3.2 |
| `PA_DRAIN` | `+12V.-` | `Q2.D` | BS170 漏极 12-13.8V(升压可调); 3 管并联 | docs/05-hw-sw-interface-contract.md §3.1 |
| `GND` | `Q2.S` | `GND.-` | BS170 源极 | docs/04-hardware-architecture.md §3.2 |
| `PA_BYPASS` | `C6.1` | `Q2.D` | 100nF 旁路电容(每管1只) | docs/04-hardware-architecture.md §3.2 |
| `PA_BIAS` | `R1.2` | `Q3.G` | 固定栅极偏置到各管栅极 | docs/04-hardware-architecture.md §3.2 |
| `GND` | `D5_prot.A` | `Q3.G` | BZX84-C10 10V 稳压管栅极保护(每管1只) | docs/04-hardware-architecture.md §3.2 |
| `PA_DRAIN` | `+12V.-` | `Q3.D` | BS170 漏极 12-13.8V(升压可调); 3 管并联 | docs/05-hw-sw-interface-contract.md §3.1 |
| `GND` | `Q3.S` | `GND.-` | BS170 源极 | docs/04-hardware-architecture.md §3.2 |
| `PA_BYPASS` | `C6.1` | `Q3.D` | 100nF 旁路电容(每管1只) | docs/04-hardware-architecture.md §3.2 |
| `+5V` | `U8.VCC` | `+5V.-` | 🔴 244 必须 5V 供电(ACT 系列 4.5-5.5V, TTL 输入阈值) | docs/05-hw-sw-interface-contract.md §2.5; ADR-0008 §3.2 |
| `GND` | `U8.GND` | `GND.-` | 244 地 | docs/05-hw-sw-interface-contract.md §2.5; ADR-0008 §3.2 |
| `DEC244` | `C244.1` | `U8.VCC` | 🔴 244 每个 Vcc 引脚 100nF 去耦 | docs/05-hw-sw-interface-contract.md §2.5; ADR-0008 §3.2 |
| `PA_RF_OUT` | `Q1.D (并联)` | `J_PA_OUT.中心` | PA 输出 -> LPF, 经 SMA 50ohm | docs/05-hw-sw-interface-contract.md §4.1 |
| `RF_THRU` | `J_ATU_IN.中心` | `J_ANT.中心` | ATU 输出侧 Tandem Match 主线(50ohm) | docs/05-hw-sw-interface-contract.md §4.1; docs/04-hardware-architecture.md §3.4 |
| `XFWD_SEC` | `T1.次级+` | `R_sense_F.1` | T1 次级(初级1匝穿芯 + 次级10匝; 耦合度 20+/-3dB) | docs/05-hw-sw-interface-contract.md §3.2; hardware/atu-module/README.md §3 |
| `GND` | `R_sense_F.2` | `GND.-` | 前向 R_sense 1kohm 初值, 需 NanoVNA 微调 | docs/05-hw-sw-interface-contract.md §3.2, §7 #4 |
| `DET_FWD` | `R_sense_F.1` | `D1.A` | 1N5711 检波(前向) | docs/05-hw-sw-interface-contract.md §3.2; hardware/atu-module/README.md §3 |
| `DET_FWD` | `R_sense_F.1` | `D3.A` | HSMS-2850 零偏置检波, 与 1N5711 并行对照 | docs/05-hw-sw-interface-contract.md §3.2; hardware/atu-module/README.md §3 |
| `ADC_FWD` | `D1.K` | `U4.GPIO0` | 检波输出 -> ADC1_CH0(两条检波支路由固件选优/融合) | docs/05-hw-sw-interface-contract.md §3.2; hardware/atu-module/README.md §3 |
| `ADC_FWD` | `D3.K` | `U4.GPIO0` | 同上(并行对照) | docs/05-hw-sw-interface-contract.md §3.2; hardware/atu-module/README.md §3 |
| `XREV_SEC` | `T2.次级+` | `R_sense_R.1` | T2 次级(反向) | docs/05-hw-sw-interface-contract.md §3.2; hardware/atu-module/README.md §3 |
| `GND` | `R_sense_R.2` | `GND.-` | 反向 R_sense 1kohm 初值 | docs/05-hw-sw-interface-contract.md §7 #4 |
| `DET_REV` | `R_sense_R.1` | `D2.A` | 1N5711 检波(反向) | docs/05-hw-sw-interface-contract.md §3.2; hardware/atu-module/README.md §3 |
| `DET_REV` | `R_sense_R.1` | `D4.A` | HSMS-2850 并行对照 | docs/05-hw-sw-interface-contract.md §3.2; hardware/atu-module/README.md §3 |
| `ADC_REV` | `D2.K` | `U4.GPIO1` | 检波输出 -> ADC1_CH1 | docs/05-hw-sw-interface-contract.md §3.2; hardware/atu-module/README.md §3 |
| `ADC_REV` | `D4.K` | `U4.GPIO1` | 同上(并行对照) | docs/05-hw-sw-interface-contract.md §3.2; hardware/atu-module/README.md §3 |
| `LM358_IN` | `D1.K` | `U3.IN+` | 可选 LM358 放大级; 是否装配待 stage-4 实测(docs/05 §7 #6) | docs/05-hw-sw-interface-contract.md §7 #6 |
| `+5V` | `U3.V+` | `+5V.-` | LM358 供电(可选级) | docs/05-hw-sw-interface-contract.md §7 #6 |
| `VBAT` | `BT1.+` | `R_VBAT1.1` | 2S 电池 6.0-8.4V | docs/05-hw-sw-interface-contract.md §2.7 |
| `VBAT_DIV` | `R_VBAT1.2` | `R_VBAT2.1` | 分压中点: 22k 上臂 / 9.1k 下臂 | docs/05-hw-sw-interface-contract.md §2.7 |
| `GND` | `R_VBAT2.2` | `GND.-` | 分压下臂接地; 静态电流 270uA | docs/05-hw-sw-interface-contract.md §2.7 |
| `VBAT_DIV` | `R_VBAT1.2` | `R_VBAT3.1` | 分压中点经 1kohm 隔离到 ADC | docs/05-hw-sw-interface-contract.md §2.7 |
| `ADC_VBAT` | `R_VBAT3.2` | `U4.GPIO3` | 源阻抗 R3+(22k//9.1k)=7.4kohm < 10kohm 满足 ESP32-C3 ADC 要求 | docs/05-hw-sw-interface-contract.md §2.7 |
| `ADC_VBAT` | `R_VBAT3.2` | `C_VBAT.1` | 0.1uF 滤波, fc 约 245Hz | docs/05-hw-sw-interface-contract.md §2.7 |
| `GND` | `C_VBAT.2` | `GND.-` | 滤波电容地 | docs/05-hw-sw-interface-contract.md §2.7 |
| `ANT_ESD` | `J_ANT.中心` | `R_esd.1` | 天线静电泄放: 1kV 高压电阻 100kohm 到地(或射频专用 GDT) | docs/04-hardware-architecture.md §3.4; hardware/atu-module/README.md §3 |
| `GND` | `R_esd.2` | `GND.-` | 泄放电阻接地 | docs/04-hardware-architecture.md §3.4 |
| `+12V` | `U11.OUT` | `+12V.-` | 3.7V->12V 升压模块输出 12-13.8V; 最大 0.5A(发射); 纹波峰峰 <0.5V @2.5W | docs/05-hw-sw-interface-contract.md §3.3; docs/04-hardware-architecture.md §3.6 |
| `+12V` | `U11.OUT` | `U2.COM` | 12V 供 ULN2003A COM(继电器续流) | docs/05-hw-sw-interface-contract.md §2.4 |
| `+12V` | `U11.OUT` | `J1.12V` | 12V 经排针到 PA 漏极与 ATU 继电器线圈 | docs/05-hw-sw-interface-contract.md §3.3; docs/04-hardware-architecture.md §3.6 |
| `+5V` | `U9.OUT` | `J1.5V` | MP2315 同步降压 5V 主轨; 最大 0.3A | docs/05-hw-sw-interface-contract.md §3.3; docs/04-hardware-architecture.md §3.6 |
| `+5V` | `U9.OUT` | `U8.VCC` | 5V 供 244 | docs/05-hw-sw-interface-contract.md §2.5 |
| `+5V` | `U9.OUT` | `R1.1` | 5V 供栅极偏置分压 | docs/04-hardware-architecture.md §3.2 |
| `+3V3_RF` | `U10.OUT` | `U7.VDD` | MD7673 LDO 3.3V 射频轨(低噪声); 最大 50mA; 专供 Si5351 | docs/05-hw-sw-interface-contract.md §3.3; docs/04-hardware-architecture.md §3.6 |
| `+3V3_DIG` | `FB1.OUT` | `U4.3V3` | 3.3V 数字轨(独立 pi 型 RC 滤波); 最大 200mA | docs/05-hw-sw-interface-contract.md §3.3; docs/04-hardware-architecture.md §3.6 |
| `+3V3_DIG` | `FB1.OUT` | `U5.VDD` | 3.3V 数字轨 -> LCD | docs/05-hw-sw-interface-contract.md §3.3; docs/04-hardware-architecture.md §3.6 |
| `+3V3_DIG` | `FB1.OUT` | `U1.VCC` | 3.3V 数字轨 -> TCA9535 | docs/05-hw-sw-interface-contract.md §3.3; docs/04-hardware-architecture.md §3.6 |
| `VBAT` | `BT1.+` | `U9.VIN` | 2S 电池 6.0-8.4V -> MP2315 输入 | docs/05-hw-sw-interface-contract.md §3.3; docs/04-hardware-architecture.md §3.6 |
| `VBAT` | `BT1.+` | `U11.VIN` | 2S 电池 -> 升压模块输入(⚠ 模块标称 3.7V 输入, 需核对) | docs/05-hw-sw-interface-contract.md §3.3; docs/04-hardware-architecture.md §3.6; docs/05 §7 #7 |
| `GND` | `BT1.-` | `GND.-` | 电池负极 | docs/05-hw-sw-interface-contract.md §3.3; docs/04-hardware-architecture.md §3.6 |
| `GND` | `GND_DIG.-` | `GND_RF.-` | 🔴 射频地与数字地在底板单点汇接(star ground), 避免功放回流污染 Si5351 与 ADC 参考地 | docs/04-hardware-architecture.md §3.1; hardware/core-board/README.md §6 |
| `GND` | `GND_PWR.-` | `GND_DIG.-` | 大电流功放地/电源回路单独回流, 与射频地单点汇集于底板一点 | docs/04-hardware-architecture.md §3.1 |
| `RELAY_CONTACTS` | `K1..K6.触点` | `L1..L3/C3..C5.L 型网络` | 🟠 未冻结: 6 只继电器触点如何串并出 8 电感组合(0/12/33/45/47/59/80/92uH)与 8 电容组合(0/22/120/142/330/352/450/472pF)在文档中未给出逐脚接法, 只有组合值表 | hardware/atu-module/README.md §2; docs/05 §7 #1 已冻结分配但网络未出图 |
| `BUZZER_DRV` | `U1.IOEXP_SPARE` | `LS1.+` | 🟠 蜂鸣器未分配: 挂 TCA9535 空闲位(9 位中选一), 具体位号待定 | docs/05-hw-sw-interface-contract.md §2.3; hardware/mcu-ui-module/README.md §4 |
| `FB_PULLDOWN` | `R12.1` | `PA_PWR_PWM.-` | 📌 建议未采纳判定: GPIO12 -> 升压 FB 的 10kohm 下拉(docs/05 §7 #7a) | docs/05-hw-sw-interface-contract.md §2.10.3, §7 #7a; docs/17-gpio-allocation-audit.md §12.6.5 |
| `GND` | `R12.2` | `GND.-` | 同上(采纳后接 GND) | docs/05-hw-sw-interface-contract.md §2.10.3 |
