# 05 · 软硬件接口契约

> 状态：已建立（**引脚分配为建议方案，待硬件投板后冻结**）｜适用版本：V3.7｜权威性：**★ 唯一权威**

本文档是**硬件区与软件区的唯一契约点**。任何引脚、连接器、协议边界变更都必须：
1. 在本文件更新；
2. 同步更新**私有固件仓**的 `components/bsp_board/`；
3. 经**硬件与软件双方评审**后才能合入。

> ⚠️ **文档优先级最高**。硬件原理图与固件代码若与本文件冲突，以本文件为准（或先改本文件再改实现）。

---

## 1. GPIO 资源约束分析

### 1.1 ESP32-C3 可用 GPIO

ESP32-C3 标称 22 个 GPIO，但实际可用受限：

| 引脚范围 | 状态 | 说明 |
|---------|------|------|
| GPIO0 – GPIO10 | **11 个可用** | GPIO0–4 为 ADC1_CH0–CH4；GPIO2/GPIO8/GPIO9 为 strapping 引脚 |
| GPIO11 – GPIO17 | **不可用** | 内部连接 SPI Flash / PSRAM |
| GPIO18 – GPIO19 | **2 个可用** | 原生 USB D−/D+ |
| GPIO20 – GPIO21 | **2 个可用** | UART0 TX/RX |
| **合计可用** | **15 个** | — |

**ADC 约束**

| 项 | 说明 |
|----|------|
| ADC1 通道 | GPIO0–GPIO4（5 通道），**可在 WiFi 工作期间使用** |
| ADC2 通道 | GPIO5，**与 WiFi 冲突，本项目不使用** |
| 结论 | → 所有模拟量必须落在 **GPIO0–GPIO4** 上，最多 5 路 |

### 1.2 需求侧引脚统计

| 类别 | 需求 | 数量 |
|------|------|------|
| 模拟输入 | 前向检波、反向检波、电池电压、功放 NTC、（备用：电源电流） | 4–5 |
| I2C | Si5351 + TCA9535 + LCD | 2 |
| 数字输出（慢速） | 继电器 K1–K6、蜂鸣器、PA_EN、LCD RST、LCD 背光 | 11 |
| 数字输入（慢速） | EC11 A/B/SW、按键 ×2 | 5 |
| 快速数字 | CW 键控、功放功率 PWM | 2 |
| 调试 | UART0 或原生 USB | 2 |
| **合计** | — | **26–27** |

**结论**：需求（26–27）远超可用 GPIO（15），**必须使用 I/O 扩展器**，且显示接口必须走少引脚方案。

### 1.3 分配决策

见 [ADR-0004](adr/ADR-0004-lcd12864-on-shared-i2c.md)：

- **LCD 走 I2C**（ST7588i 支持 I2C 模式），与 Si5351、TCA9535 共享总线 → 释放 4 个 GPIO。
- **全部慢速 IO 挂 TCA9535**（16 位 I2C 扩展器）→ 释放 11 个 GPIO。
- **稀缺 GPIO 留给**：ADC（GPIO0–4）、CW 键控（GPIO7）、功放功率 PWM（GPIO8）。

---

## 2. GPIO 分配表（建议方案）

> 状态：**建议（Proposed）**。硬件投板并实测通过后，状态改为**冻结（Frozen）**。
> 修改本表需双方评审，并同步 `bsp_board`。

### 2.1 直接接 ESP32-C3 的引脚

| GPIO | 功能名（`bsp_board` 宏） | 方向 | 复用/外设 | 备注 |
|------|------------------------|------|----------|------|
| **GPIO0** | `BOARD_ADC_FWD` | AI | ADC1_CH0 | 前向检波（Tandem Match T1 侧）；strapping：需保证上电电平不影响启动 |
| **GPIO1** | `BOARD_ADC_REV` | AI | ADC1_CH1 | 反向检波（T2 侧） |
| **GPIO2** | `BOARD_ADC_VBAT` | AI | ADC1_CH2 | 电池电压分压；**strapping 引脚**，需外部上拉/下拉匹配启动要求 |
| **GPIO3** | `BOARD_ADC_NTC` | AI | ADC1_CH3 | 功放 NTC 温度（10 kΩ B=3950 分压） |
| **GPIO4** | `BOARD_ADC_ISENSE` | AI | ADC1_CH4 | 电源电流检测（**预留**，可省） |
| **GPIO5** | `BOARD_I2C_SDA` | IO | I2C0 SDA | 共享总线：Si5351 + TCA9535 + LCD；**需 4.7 kΩ 上拉至 3.3 V** |
| **GPIO6** | `BOARD_I2C_SCL` | IO | I2C0 SCL | 同上 |
| **GPIO7** | `BOARD_CW_KEY` | O | GPIO / LEDC | **CW 键控输出**：驱动功放键控级；优先用 LEDC 做软起软降（2–5 ms） |
| **GPIO8** | `BOARD_PA_PWR_PWM` | O | LEDC | **功放功率控制**：PWM → 升压模块 FB 网络（400 Hz–20 kHz，经 RC 滤波） |
| **GPIO9** | `BOARD_LCD_SPI_ALT_SCK` | O | SPI2 | **备选**：若 LCD 改用 SPI 模式则启用；否则预留（strapping 引脚，需注意上电电平） |
| **GPIO10** | `BOARD_LCD_SPI_ALT_MOSI` | O | SPI2 | **备选**：同上 |
| **GPIO18** | `BOARD_USB_DM` | IO | USB Serial/JTAG | 原生 USB-CDC：日志 / 中控串口 / 固件下载 |
| **GPIO19** | `BOARD_USB_DP` | IO | USB Serial/JTAG | 同上 |
| **GPIO20** | `BOARD_UART_TX` | O | UART0 TX | 备用串口：日志 / 中控 |
| **GPIO21** | `BOARD_UART_RX` | I | UART0 RX | 同上 |

**占用统计**：ADC 5（其中 1 预留）+ I2C 2 + 快速数字 2 + USB 2 + UART 2 + LCD 备选 2 = **15**

### 2.2 TCA9535 I2C 扩展器分配

**器件**：TCA9535（16 位 I2C GPIO 扩展器），I2C 地址 `0x20`（A2/A1/A0 全接地；`bsp_board` 中需明确定义）

| 端口 | 功能名（`bsp_board` 宏） | 方向 | 连接对象 | 备注 |
|------|------------------------|------|---------|------|
| P0.0 | `IOEXP_RELAY_K1` | O | L1 = 12 µH | 经 2N7002 驱动 HK4100F |
| P0.1 | `IOEXP_RELAY_K2` | O | L2 = 33 µH | 同上 |
| P0.2 | `IOEXP_RELAY_K3` | O | L3 = 47 µH | 同上 |
| P0.3 | `IOEXP_RELAY_K4` | O | C3 = 22 pF | 同上 |
| P0.4 | `IOEXP_RELAY_K5` | O | C4 = 120 pF | 同上 |
| P0.5 | `IOEXP_RELAY_K6` | O | C5 = 330 pF | 同上 |
| P0.6 | `IOEXP_PA_EN` | O | 功放使能 | 关断功放供电/偏置 |
| P0.7 | `IOEXP_BUZZER` | O | 有源蜂鸣器 | 提示音 / 告警 |
| P1.0 | `IOEXP_EC11_A` | I | EC11 A 相 | 轮询（建议 100–200 Hz）或用 P1.0 中断 |
| P1.1 | `IOEXP_EC11_B` | I | EC11 B 相 | 同上 |
| P1.2 | `IOEXP_EC11_SW` | I | EC11 按键 | — |
| P1.3 | `IOEXP_KEY1` | I | 轻触按键 1 | — |
| P1.4 | `IOEXP_KEY2` | I | 轻触按键 2 | — |
| P1.5 | `IOEXP_LCD_RST` | O | LCD 复位 | — |
| P1.6 | `IOEXP_LCD_BL` | O | LCD 背光使能 | 若需调光则改接 LEDC 引脚 |
| P1.7 | `IOEXP_SPARE` | O | **预留** | 可扩展：天线静电泄放继电器、散热风扇、状态 LED |

**占用统计**：**16/16 全部使用**（含 1 路预留）

### 2.3 引脚冲突与注意事项

| 项 | 说明 |
|----|------|
| Strapping 引脚 | GPIO2 / GPIO8 / GPIO9 在复位时有特殊功能，外部电路不得在复位期间强制错误电平 |
| GPIO8 板载 LED | 部分 ESP32-C3 SuperMini 板在 GPIO8 挂 WS2812。**投板前必须确认所用模组版本**；若冲突，把 `BOARD_PA_PWR_PWM` 移到 GPIO10，并启用 LCD 的 I2C 方案（GPIO9 保持未用） |
| ADC 线性度 | ESP32-C3 ADC 非线性明显，`drv_analog` 必须做**多点校准**（至少 3 点）并存储校准系数到 NVS |
| I2C 总线速率 | 建议 400 kHz（快速模式）。LCD 全屏刷新 1024 字节约 25 ms，需局部刷新 |
| I2C 总线互斥 | Si5351 / TCA9535 / LCD 共享总线，**必须加互斥量**；LCD 长传输不得阻塞 CW 键控 |
| CW 键控实时性 | 若使用 TCA9535 经 I2C 键控，延迟约 100 µs 量级，对 12 WPM（点长 100 ms）可接受；但**推荐直接使用 GPIO7 + LEDC** 以获得确定性 |
| 功放 PWM 滤波 | `BOARD_PA_PWR_PWM` 需经 RC 低通（建议截止频率 ≪ PWM 频率）后接入升压模块 FB；滤波时间常数会成为功率切换的响应时间，需在 `drv_pa` 中补偿 |

---

## 3. 电气参数契约

### 3.1 逻辑电平

| 项 | 数值 |
|----|------|
| 数字逻辑电平 | 3.3 V（**所有扩展器、驱动器、LCD 均须 3.3 V 兼容**） |
| 继电器线圈驱动 | 12 V，16.7 mA/只，6 只同时吸合 <110 mA |
| 功放漏极 | 12–13.8 V（升压可调） |
| 栅极偏置 | ≈2.1 V 直流 |

### 3.2 ADC 通道标定

| 通道 | 物理量 | 满量程 | 分压/增益 | 说明 |
|------|--------|--------|----------|------|
| GPIO0 | 前向功率 | 由耦合器决定 | Tandem Match 20±3 dB，R_sense 初值 1 kΩ（NanoVNA 微调） | 2 W 下 ADC 读数应落在量程 **20%–80%** |
| GPIO1 | 反向功率 | 同上 | 同上 | SWR=2.0 @2 W 时读数应 **≥量程 5%** |
| GPIO2 | 电池电压 | 2S 锂电 6.0–8.4 V | 分压至 ≤3.3 V | 需校准 |
| GPIO3 | 功放温度 | NTC 10 kΩ B=3950 | 分压 | 需查表或 Steinhart-Hart |
| GPIO4 | 电源电流 | 预留 | 采样电阻 + 放大 | 预留 |

**检波器件**：1N5711 与 HSMS-2850 **并行对照**搭建（同一信号分别检波），由软件选择更优通道或做融合。

### 3.3 功耗契约

| 轨 | 电压 | 最大电流 | 说明 |
|----|------|---------|------|
| 12 V 功放轨 | 12–13.8 V | 0.5 A（发射） | 纹波峰峰值 **<0.5 V**（2.5 W 发射时） |
| 5 V 主轨 | 5 V | 0.3 A | 继电器线圈、偏置分压 |
| 3.3 V 射频轨 | 3.3 V | 50 mA | Si5351，低噪声 LDO（MD7673） |
| 3.3 V 数字轨 | 3.3 V | 200 mA | ESP32-C3、LCD、TCA9535 |

---

## 4. 连接器契约（模块间互联）

> 详细针脚定义在 `hardware/interconnect/connector/`。本节定义**契约级要求**。

### 4.1 射频互联

| 链路 | 连接器 | 阻抗 | 要求 |
|------|--------|------|------|
| Si5351 → PA | 底板走线 / 排针 | 50 Ω | 短走线，避免与数字信号并行 |
| PA → LPF | **SMA** | 50 Ω | 屏蔽线，长度尽量短 |
| LPF → ATU | **SMA** | 50 Ω | 同轴短线 |
| ATU → 天线座 | **SMA** | 50 Ω | 底板到面板 |
| ATU → SWR 耦合器 | 板内 | 50 Ω | Tandem Match 位于 ATU 输出侧 |

**线缆**：SMA 公-公短线（BOM 计 3 根）。

### 4.2 控制与电源互联

必须定义（**待硬件设计后冻结**）：

| 信号 | 电平 | 方向 | 说明 |
|------|------|------|------|
| `PA_EN` | 3.3 V | MCU → PA | 功放使能 |
| `CW_KEY` | 3.3 V | MCU → PA | 键控（软起软降） |
| `PA_PWR_PWM` | 3.3 V PWM | MCU → Power | 升压调压 |
| `FWD_DET` | 0–3.3 V | SWR → MCU(ADC) | 前向检波 |
| `REV_DET` | 0–3.3 V | SWR → MCU(ADC) | 反向检波 |
| `+12V` / `+5V` / `+3V3` / `GND` | — | Power → 各模块 | 电源分配 |

**验证要点**：连接器插拔寿命、SMA 力矩、线束压降。

---

## 5. 通信协议契约

### 5.1 协议分层

| 层 | 适用范围 | 定义位置 |
|----|---------|---------|
| **Mesh 帧** | 设备之间（ESP-NOW），含时钟同步、状态回传、中继转发 | `software/protocol/spec/`（规划中，待创建） |
| **Console 帧** | 设备 ↔ 中控 PC（USB-CDC / UART / WiFi） | `software/protocol/spec/`（规划中，待创建） |
| **遥测字段** | 从机状态上报 | `software/protocol/spec/`（规划中，待创建） |

> ⚠️ **协议尚未定义**：`software/protocol/`（规划中，待创建）目录**现在并不存在**，上表的「定义位置」只是未来放规范的地方；具体的帧格式、报文字段与安全方案都还没有编写。

> **唯一事实来源**：`software/protocol/`（规划中，待创建）。协议一旦开始编写，固件的 `comm_console`、`net_espnow` 与中控软件都必须使用由 `software/protocol/generated/`（规划中，待创建）生成的代码，**禁止各自手写帧结构**。

### 5.2 遥测字段契约（必须全部实现）

| 字段 | 类型 | 单位 | 说明 |
|------|------|------|------|
| 设备 ID | uint16 | — | 台号 / 节点编号 |
| UTC 时间 | uint32 | s | 自 Unix 纪元 |
| 发射状态 | uint8 | 枚举 | 待机 / 长音 / 识别码 / 间隔 |
| 频率 | uint32 | Hz | 当前发射频率 |
| 功放温度 | int16 | 0.1 °C | NTC 换算 |
| 电池电压 | uint16 | mV | — |
| ATU 调谐状态 | uint8 | 枚举 | 未调谐 / 命中记忆 / 调谐中 / 调谐成功 / 失败 |
| SWR | uint16 | 0.01 | 驻波比 ×100 |

### 5.3 安全契约

| 机制 | 要求 |
|------|------|
| 链路层 | ESP-NOW 原生 CCMP 加密 |
| 应用层 | HMAC-SHA256 消息认证 |
| 应用层 | MAC 地址白名单 |
| 应用层 | 序列号防重放（滑动窗口） |

**密钥管理**：密钥存储于 NVS 的 `nvs_keys` 分区（预留），**禁止硬编码在源码中**。轮换策略待定。

### 5.4 固件侧实现映射

> 下表组件均**在私有固件仓中实现**，目录为 `components/<组件名>/`；本公开仓不含固件源码。

| 契约项 | 固件组件 |
|--------|---------|
| GPIO 分配表 | `bsp_board` |
| TCA9535 端口分配 | `bsp_io_expander` |
| ADC 通道与标定 | `drv_analog` |
| Mesh 帧 | `net_espnow`、`mesh_router`、`mesh_security`、`net_timesync` |
| Console 帧与遥测 | `comm_console` |
| SWR / 功率换算 | `rf_swr` |
| 功率控制与联锁 | `rf_power`、`drv_pa` |
| 继电器组合 | `drv_relay`、`atu_match` |

---

## 6. 变更流程

任何涉及本契约的变更，必须按以下流程：

```
1. 修改 docs/05-hw-sw-interface-contract.md（提出变更，标注状态为「提议」）
2. 硬件方确认：原理图/PCB/BOM 影响评估
3. 软件方确认：bsp_board / 相关组件影响评估
4. 双方评审通过 → 本文件状态改为「冻结」
5. 同步提交：原理图变更 + bsp_board 变更（同一 PR 或关联 PR）
6. 更新 CHANGELOG.md
```

**禁止事项**

| ❌ 禁止 | 原因 |
|--------|------|
| 在组件中硬编码 GPIO 号 | 破坏 `bsp_board` 单一来源 |
| 硬件改引脚但不改本文件 | 软件将驱动错误引脚 |
| 固件与中控各自定义帧结构 | 协议漂移，无法互通 |
| 把密钥硬编码进源码 | 安全红线 |

---

## 7. 待冻结事项清单

| # | 事项 | 阻塞原因 | 责任方 |
|---|------|---------|--------|
| 1 | GPIO 分配表最终确认 | 需确认 SuperMini 模组 GPIO8 是否挂 WS2812 | 硬件 |
| 2 | TCA9535 I2C 地址 | 需确认 A2/A1/A0 实际接法 | 硬件 |
| 3 | LCD 走 I2C 还是 SPI | 需实测 I2C 刷新率是否满足 UI 需求 | 硬件 + 软件 |
| 4 | Tandem Match `R_sense` 最终值 | 需 NanoVNA 微调（初值 1 kΩ） | 硬件 |
| 5 | 检波器件选型（1N5711 / HSMS-2850 / 并行） | 需 [stage-3](../validation/stage-3-coupler-detector/README.md) 实测对照 | 硬件 |
| 6 | 是否需要 LM358 运放级 | 需 [stage-4](../validation/stage-4-opamp/README.md) 对照验证 | 硬件 |
| 7 | 12 V 升压模块型号与 FB 网络参数 | 需确认 PWM 调压线性度 | 硬件 |
| 8 | 密钥分发与轮换策略 | 未设计 | 软件 |
| 9 | Mesh 信道与 peer 上限 | 未设计 | 软件 |

---

## 8. 关联文档

| 文档 | 用途 |
|------|------|
| [ADR-0004 12864 液晶走 I2C 共享总线](adr/ADR-0004-lcd12864-on-shared-i2c.md) | GPIO 分配决策依据 |
| [03-软件架构](03-software-architecture.md) | 固件组件与 `bsp_board` |
| [04-硬件架构](04-hardware-architecture.md) | 硬件模块与互联 |
| [hardware/interconnect/README.md](../hardware/interconnect/README.md) | 连接器针脚定义 |
| 共享协议（规划中，见 `software/README.md`） | 协议唯一事实来源 |
| [ESP32-C3 数据手册](https://documentation.espressif.com/esp32-c3_datasheet_en.html) | 引脚复用与 strapping |
