# hardware/ — 硬件设计区

本目录是 **ARDF-MeshTuneFox80** 的硬件设计区，与 `software/` 平级。

- **硬件许可**：CERN-OHL-S v2（CERN Open Hardware Licence Version 2 – Strongly Reciprocal）
- **软件许可**：分层授权（固件二进制 `LicenseRef-ARDF-NC-1.0`，仅限业余无线电非商业用途、不授予源码 / 中控 PC 基础版 `Apache-2.0` / ATU 调谐算法与 Mesh 路由算法商业授权）
- **本目录只放硬件设计资料**：原理图、PCB 源文件、Gerber、BOM、结构件、线束、数据手册索引、外部参考摘录。

---

## 1. 模块化架构

整机采用 **「核心底板 + 可插拔射频模块」** 架构：

```
           ┌──────────────────────────────────────────────┐
           │   核心底板 core-board（130×95mm 四层板）      │
           │   母板/背板：模块插座 + 电源分配 + SMA 互联    │
           └───┬────────┬────────┬────────┬────────┬──────┘
               │        │        │        │        │
            排针+SMA  排针+SMA  排针+SMA  排针    排针
               │        │        │        │        │
        ┌──────┴──┐ ┌───┴────┐ ┌─┴─────┐ ┌┴──────┐ ┌┴──────────┐
        │pa-module│ │lpf-    │ │atu-   │ │power- │ │mcu-ui-    │
        │3×BS170  │ │module  │ │module │ │module │ │module     │
        │E 类功放 │ │三阶椭圆│ │6 继电 │ │5V/3.3V│ │ESP32-C3   │
        │         │ │低通    │ │器 L 型│ │12V    │ │+12864 LCD │
        └─────────┘ └────────┘ └───────┘ └───────┘ └───────────┘
              射频链路：PA → LPF → ATU → 天线（SMA 互联，50Ω）
```

- 射频模块之间通过 **SMA 座 + 短跳线** 互联，同一底板上的信号链为：`Si5351 本振 → PA → LPF → ATU → ANT`。
- 控制/电源通过 **2.54mm 排针排母** 传递（GPIO、PWM、SWR 检波、12V/5V/3.3V、GND）。
- ATU 模块因 HK4100F 继电器封装（DIP 14.5×10.5mm）较大，PCB 单独调整为 **55×65mm**。
- 底板保留 32.768kHz 晶振 DNP 焊盘，用于 Mesh 时钟精度的可选升级。

---

## 2. 目录树

```
hardware/
├── README.md                          # 本文件
├── core-board/                        # 核心底板（130×95mm 四层板）
│   ├── README.md
│   ├── schematic/                     # 原理图源文件
│   ├── pcb/                           # PCB 源文件
│   ├── gerber/                        # 制板 Gerber
│   ├── bom/                           # 物料清单
│   └── mechanical/                    # 结构/安装孔位资料
├── pa-module/                         # 功放模块 3×BS170 并联 E 类
│   ├── README.md
│   ├── schematic/  pcb/  gerber/  bom/  test/
├── lpf-module/                        # 三阶椭圆低通滤波器
│   ├── README.md
│   ├── schematic/  pcb/  gerber/  bom/  test/
├── atu-module/                        # 自动天调 6 继电器 L 型匹配
│   ├── README.md
│   ├── schematic/  pcb/  gerber/  bom/  test/
├── mcu-ui-module/                     # 主控与人机交互
│   ├── README.md
│   ├── schematic/  pcb/  gerber/  bom/
├── power-module/                      # 电源模块
│   ├── README.md
│   ├── schematic/  pcb/  gerber/  bom/
├── antenna/                           # 天线与地线系统
│   ├── README.md
│   ├── design/                        # 天线形态与匹配设计资料
│   └── test/                          # NanoVNA 实测记录
├── enclosure/                         # 外壳与结构
│   ├── README.md
│   ├── 3d-print/                      # 3D 打印模型
│   └── panel/                         # 面板开孔图纸
├── interconnect/                      # 模块互联定义
│   ├── README.md
│   ├── connector/                     # 连接器针脚定义
│   └── harness/                       # 线束图
├── datasheets/                        # 器件数据手册归档索引
│   ├── README.md
│   └── .gitkeep
├── reference/                         # 外部参考设计（只读，不入版本库）
│   ├── README.md
│   └── atu-100/
│       ├── README.md
│       └── .gitkeep
└── archive/                           # 历史版本归档
    ├── README.md
    └── .gitkeep
```

---

## 3. 模块清单

| 模块目录 | 板卡尺寸 | 核心器件 | 主要功能 | 状态 |
|---------|---------|---------|---------|------|
| `core-board` | 130×95mm 四层板 | 模块排针座 ×6、SMA 母座 ×3、电源分配网络 | 母板/背板，承载各模块插座、电源分配、SMA 互联 | 规划中 |
| `pa-module` | 随底板插槽 | 3× BS170 并联、10kΩ+2.2kΩ **固定**偏置分压、BZX84-C10（NTC 温度补偿已于 2026-09-26 取消，见 [docs/17 §12.5](docs/17-gpio-allocation-audit.md)） | E 类功放：漏极 12–13.8V，栅极偏置约 2.1V，输出 1–2.5W（峰值 3.5W/≤30s）；低功率档 0.02–0.5W 由 PWM 调升压模块实现 | 规划中 |
| `lpf-module` | 随底板插槽 | 磁环电感 + NP0 电容（三阶椭圆） | 低通滤波：中心 3.55MHz，2f₀（7.1MHz）处衰减 ≥55dB | 规划中 |
| `atu-module` | 55×65mm | 6× HK4100F-DC-12V、L1=12µH(T37-6, 约63圈) / L2=33µH(T106-6, 约53圈) / L3=47µH(T106-6, 约64圈)、C=22/120/330pF NP0 1206/1812 ≥630V、6× 2N7002 | L 型匹配网络，3 电感 + 3 电容共 64 种组合；驱动为 2N7002 + 100Ω 栅极电阻 + 10kΩ 下拉 + 1µF 陶瓷电容反峰抑制（可并联 1N4148 冗余） | 规划中 |
| `mcu-ui-module` | 随底板插槽 | 合宙 LuatOS ESP32C3-CORE、12864 LCD（ST7567，SPI）、EC11 旋转编码器（A/B/SW）、蜂鸣器（**未分配，可挂 TCA9535 空闲位**） | 主控、显示、参数调节、WiFi/NTP 校时、ESP-NOW Mesh | 规划中 |
| `power-module` | 随底板插槽 | MP2315、MD7673、π 型 RC 滤波、3.7V→12V 升压模块、2S 500mAh 电池 | 5V 主轨 MP2315 同步降压；3.3V 射频轨 MD7673 LDO；3.3V 数字轨独立 π 型 RC 滤波；12V 功放轨升压模块（PWM 可调） | 规划中 |
| `antenna` | 现场架设 | 5m 垂直导线、≥5m 地线 | 5 米垂直导线（最小 4m，最大 8m）+ 至少 5 米地线（推荐 3 段×2m 辐射状） | 规划中 |
| `enclosure` | 按整机 | 3D 打印件或通用塑料盒 | 整机外壳、面板、散热风道 | 规划中 |
| `interconnect` | — | SMA、2.54mm 排针排母、电池座、天线座 | 模块间连接器定义、线束图、SMA 针脚定义 | 规划中 |
| `datasheets` | — | — | 器件数据手册归档（PDF 不入 git，见 `.gitignore`） | 规划中 |
| `reference` | — | — | 外部参考设计（ATU-100 等），只读参考、不入版本库 | 规划中 |
| `archive` | — | — | 历史版本归档 | 规划中 |

---

## 4. 新增硬件文件放哪里（决策表）

| 我要放的东西 | 目标目录 | 示例 |
|-------------|---------|------|
| 原理图源文件 | `<模块>/schematic/` | `atu-module/schematic/atu-module-V1.0.kicad_sch` |
| PCB 源文件 | `<模块>/pcb/` | `atu-module/pcb/atu-module-V1.0.kicad_pcb` |
| Gerber / 制板包 | `<模块>/gerber/` | `pa-module/gerber/pa-module-V1.1-gerber.zip` |
| 物料清单 BOM | `<模块>/bom/` | `core-board/bom/core-board-V1.0-bom.csv` |
| 结构件、安装孔位、面板 | `<模块>/mechanical/` 或 `enclosure/` | `core-board/mechanical/core-board-V1.0-dims.pdf`、`enclosure/panel/panel-V1.0.dxf` |
| 测试报告、实测数据、截图 | `<模块>/test/` | `atu-module/test/atu-module-V1.0-relay-loss.md` |
| 器件数据手册 | `datasheets/`（外部归档 + `INDEX.md` 登记） | 见 `datasheets/README.md` |
| 外部参考设计摘录 | `reference/<项目名>/` | `reference/atu-100/` |
| 被替代的旧版本 | `archive/<模块>/<版本>/` | `archive/atu-module/V1.0/` |

---

## 5. 命名规范

统一格式：**`<模块>-<板号>-<版本>.<扩展名>`**

- 版本号格式：`V<主>.<次>`，例如 `V1.0`、`V1.1`、`V2.0`。
- 板号用于同一模块的多张板卡区分，可省略；省略时写作 `<模块>-<版本>.<扩展名>`。

示例：

| 文件 | 说明 |
|------|------|
| `atu-module-V1.0.kicad_pcb` | ATU 模块 V1.0 的 PCB 源文件 |
| `pa-module-V1.1-gerber.zip` | 功放模块 V1.1 的 Gerber 制板包 |
| `core-board-V1.0-bom.csv` | 核心底板 V1.0 的 BOM |
| `lpf-module-V1.0-sch.pdf` | 低通模块 V1.0 原理图导出 |

约束：

- 目录名一律 **英文小写 + 连字符**（`kebab-case`），不使用中文、空格、下划线、大写。
- 文档内容使用 **简体中文**。
- 任何二进制大文件（Gerber 压缩包、PDF、3D 模型、STEP）需先确认 `.gitignore` 规则再入库。

---

## 6. 与软件的关系

- **引脚分配、寄存器映射、通信协议以 [`docs/05-hw-sw-interface-contract.md`](../docs/05-hw-sw-interface-contract.md) 为唯一权威来源**，硬件设计必须与该文档保持一致；如有冲突，先改契约文档再改硬件。
- 硬件侧的 GPIO/PWM/ADC 需求（继电器驱动、SWR 检波 ADC、升压模块 PWM、Si5351 I²C、LCD SPI）应在 `interconnect/` 中登记为接口清单。
- ATU 调谐算法在软件侧实现在**私有固件仓**的 `components/atu_tuner/`，硬件只需保证 6 路继电器独立可控、SWR 前向/反射双通道可读。
- 固件对硬件的安全联锁要求（SWR>3.0 禁止发射）由硬件检波通道的可用量程决定，检波电路设计需满足 ADC 量程 20%–80% 的读数要求。

---

## 7. 相关文档

| 文档 | 说明 |
|------|------|
| [项目升级计划书](../docs/00-project-upgrade-plan.md) | 项目升级计划书 V3.7（技术方案权威来源） |
| [`docs/05-hw-sw-interface-contract.md`](../docs/05-hw-sw-interface-contract.md) | 软硬件接口契约（引脚分配唯一权威来源） |
| [`hardware/README.md`](README.md) | 本文件 |
| [`hardware/interconnect/README.md`](interconnect/README.md) | 连接器与线束定义 |
| [`hardware/datasheets/README.md`](datasheets/README.md) | 数据手册归档规范 |
| [`hardware/reference/README.md`](reference/README.md) | 外部参考设计说明 |
| [`hardware/archive/README.md`](archive/README.md) | 历史版本归档规则 |
