# hardware/ — 硬件设计区

本目录是 **ARDF-MeshTuneFox80** 的硬件设计区，与 `software/` 平级。

- **硬件许可**：CERN-OHL-S v2（CERN Open Hardware Licence Version 2 – Strongly Reciprocal）
- **软件许可**：分层授权（固件二进制 `LicenseRef-ARDF-NC-1.0`，仅限业余无线电非商业用途、不授予源码 / 中控 PC 基础版 `Apache-2.0` / ATU 调谐算法与 Mesh 路由算法商业授权）
- **本目录只放硬件设计资料**：原理图、PCB 源文件、Gerber、BOM、结构件、线束、数据手册索引、外部参考摘录。

## 方案口径

本目录以 [docs/05](../docs/05-hw-sw-interface-contract.md) §2.3/§2.4 与 §7 、[docs/04](../docs/04-hardware-architecture.md) §3 为现行权威。
历次方案变更（电源拓扑 / 继电器驱动 / GPIO）见 [docs/DECISIONS-2026-10-19.md](../docs/DECISIONS-2026-10-19.md)。

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
| `pa-module` | 随底板插槽 | 3× BS170 并联、10kΩ+2.2kΩ **固定**偏置分压、BZX84-C10（NTC 温度补偿已于 2026-09-26 取消，见 [docs/17 §12.5](../docs/17-gpio-allocation-audit.md)） | E 类功放：**漏极 = `VCC` 输入级原压 6.0–8.4V（默认 2S 锂电，无升压）**，栅极偏置约 2.1V，**输出 2.5W @ V_CC = 7.4V（标称）**（满电 8.4V→**≈3.22W**，✅ 甲方案：接受、不降驱动 / 6.0V→≈1.64W）；🔴 **12V 外部输入时不得直灌**（须禁发或加降压级）；低功率档 0.02–0.5W 改用 **Si5351 驱动强度 + 固定偏置降额**（原"PWM 调升压"作废）。**E 类按 7.4V 标称定点**：`R_opt≈12.6Ω`/峰值 `V_ds≈26.3V`/`C1≈0.65nF`/`L≈2.8µH`/`I≈0.42A`（[docs/04 §3.2](../docs/04-hardware-architecture.md)；🔴 2026-10-17 用户裁定统一 7.4 V，废止 8.4V 那套 16.3Ω/0.51nF/3.7µH） | 规划中 |
| `lpf-module` | 随底板插槽 | 磁环电感 + NP0 电容（三阶椭圆） | 低通滤波：中心 3.55MHz，2f₀（7.1MHz）处衰减 ≥55dB | 规划中 |
| `atu-module` | 55×65mm | 6× **HK4100F-DC5V-SHG**、L1=12µH(T37-6, 约63圈) / L2=33µH(T106-6, 约53圈) / L3=47µH(T106-6, 约64圈)、C=22/120/330pF NP0 1206/1812 ≥630V、**驱动 = CA-DV8008N ×1**（I²C 八通道低边，`0x28`） | L 型匹配网络，3 电感 + 3 电容共 64 种组合；🔴 **2026-10-11 起**：驱动 = **CA-DV8008N**（`COM → +5V`、`OC1–OC6 → K1–K6 线圈`、`A0–A2 → GND`），继电器改 **5V 线圈**（走 +5V，6×40mA=240mA），**删除 `R_RLY1–R_RLY6`**；取代原「TCA9535 + ULN2003A」（`COM → +12V`）方案。⚠️ 下单请按**本行**，不要按历史文档里的 TCA9535/ULN2003A/2N7002 | 规划中 |
| `mcu-ui-module` | 随底板插槽 | 合宙 LuatOS ESP32C3-CORE、12864 LCD（ST7567，SPI）、EC11 旋转编码器（🔴 **A=GPIO20（自 GPIO2 迁来）/ B=GPIO8 / SW=GPIO13**）、~~蜂鸣器~~（❌ **本版不做（2026-10）**，驱动位候选问题随之作废；**OC7/OC8 保持空闲、不预接**） | 主控、显示、参数调节、WiFi/NTP 校时、ESP-NOW Mesh；🔴 **本版新分配**：背光=**GPIO21（0/1）**、示波器打点=**GPIO12**、GPIO2 释放为 **ADC1_CH2**（[docs/05 §2](../docs/05-hw-sw-interface-contract.md)） | 规划中 |
| `power-module` | 随底板插槽 | MP2315（分立）、MD7673、π 型 RC 滤波、2S 500mAh 电池、**成品 2S 充电模块（U12）**、电池反接/PTC 保护（U13） | **三级电源**：**VCC = 输入级（2S 锂电 6.0–8.4V 标称 7.4V，12V 兼容已取消）** → MP2315 同步降压 **+5V**（含 240mA 继电器线圈）→ MD7673 LDO **+3V3**（射频/数字两支）；**不设升压**；充电 = 成品 2S 模块（8.4V CC/CV）；vbat 分压 30k/9.1k/1k（满量程 14.18V，留余量；改回 22k 亦可） | 规划中 |
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
| 原理图 / 工程源文件（**立创EDA 专业版**） | `<模块>/schematic/` | `atu-module/schematic/atu-module-V1.0.epro`（🔴 KiCad 流程已废弃，见 [`schematic/IMPORT-TO-LCEDA.md`](schematic/IMPORT-TO-LCEDA.md)） |
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
| [`hardware/bom/README.md`](bom/README.md) | **立创EDA 导入包**：分模块 BOM + 汇总 BOM + 立创EDA 导入能力调研 |
| [`hardware/bom/bom.md`](bom/bom.md) | 全部 BOM 的 Markdown 呈现（GitHub 直接看） |
| [`hardware/schematic/netlist.md`](schematic/netlist.md) | **逐脚连接表** + 子系统覆盖（12 GPIO / TCA9535 / ULN2003A / SPI / I²C / ADC / 电源域 / CW 键控 / 星形地） |
| [`hardware/schematic/IMPORT-TO-LCEDA.md`](schematic/IMPORT-TO-LCEDA.md) | 🔴 **原理图流程（立创EDA 专业版）** + **KiCad 骨架已于 2026-10-17 整套删除**的说明 |
| [`hardware/pre-fab-checklist.md`](pre-fab-checklist.md) | 🔴 **打样前检查清单**（`docs/05 §7` 全部条目 + `docs/17` 决策 + 本次发现的遗留） |

> 📌 **2026-09 新增**：`hardware/bom/` 与 `hardware/schematic/` 下的 BOM / 网表 / 检查清单
> 由 `scripts/build-lceda-import-pack.py` 与 `scripts/build-netlist.py` 生成，**请勿手工编辑**。
