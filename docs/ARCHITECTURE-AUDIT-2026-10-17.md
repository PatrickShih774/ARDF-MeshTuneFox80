# 硬件仓整体架构审计（ARCHITECTURE-AUDIT-2026-10-17）

> **审计对象**：`ARDF-MeshTuneFox80-hardware`（公开硬件仓）· **基线**：`main` @ `3770717`（2026-10-17 18:19:29 +0800，59 commits）
> **审计方式**：**只读**。本次唯一写入的两个文件是本文与 `docs/README.md` 的一行索引；**未改动任何设计源、派生文件、脚本**（`git status` 前后均干净，见附录 A）。
> **审计范围**：`docs/`（00–08、15、17 + ADR）· `hardware/`（9 个模块目录 + schematic/bom/validation/release）· `scripts/`（5 个 Python + 1 个 PowerShell）
> **对照仓**：私有固件仓 `ARDF-MeshTuneFox80-firmware` @ `90bd63f`（只读引用，用于第 9 章的契约对拍）

## 判定口径（本文严格区分两类句子）

| 标记 | 含义 | 可复现性 |
|---|---|---|
| **【事实】** | 我在本机直接读到 / 跑出来的东西：文件内容、行号、脚本退出码、生成物哈希 | 任何人都能按附录 A 复现 |
| **【判断】** | 我的推论、风险评级、工作量估算、因果解释 | 需要人复核；本文不把它写成事实 |

> 证据引用格式：`路径:行号`，路径相对仓根，行号 = 上述 HEAD 的工作区行号。**没有查证的东西一律写"未核实"**（见附录 C），不猜。

---

## 0. 摘要

### 0.1 一句话结论

**【判断】这个仓的"文档骨架"质量很高，但"单一事实源"不存在**：引脚契约有一份 ★权威（`docs/05`），可是**真正驱动派生文件的是 `scripts/build-netlist.py` 里的内嵌数据表 + `hardware/schematic/kicad-symbol-map.csv`**，这两处既不是权威、也没人声明它们是源；于是 **docs/05 改了、生成器没改**、**ADR 决策了、全仓没落地**、**KiCad 骨架停在 9/26 且不能再生成**。

**【事实】三个可量化的硬伤**：

1. 8 份 `.kicad_sch`（109 个符号实例）里，**12 个实例是已删器件、10 个是错值器件**（合计 22/109 = 20.2%），且生成器现在 **rc=1 且拒绝写任何文件**。
2. 自检器 `check-kicad-schematic.py` **rc=1**，唯一失败项 `row coverage has 181 rows, netlist.csv has 155`（我复核确认，非照抄）。
3. `ADR-0009`（状态 **Accepted**、明确"取代 ADR-0003"）把 ATU 从 **64 组合 3L+3C** 改成 **48 组合 4C+2L**，**全仓零落地**：ADR 索引里没有它、`docs/04/05`、模块 README、BOM、网表、KiCad、验证脚本、固件 `atu_match` 全都还是旧拓扑。

### 0.2 最严重的 5 个问题

| # | 问题 | 一句话 | 关键证据（file:line） |
|---|---|---|---|
| **P0-1** | **ATU 匹配网络存在两套互斥规格，且"新规格"是 Accepted 的 ADR** | ADR-0009 定「串 C 并 L / 4C+2L / 48 组合 / K1–K4 电容、K5–K6 电感抽头」，而全仓仍按「串 L 并 C / 3L+3C / 64 组合 / K1–K3 电感」出图出料出固件；ADR 索引里甚至查不到 0009，ADR-0003 仍标"已接受" | `docs/adr/ADR-0009-atu-4c2l-series-c-shunt-l.md:3-4,29-47,53-54` ↔ `hardware/atu-module/relay-wiring.md:69-77,348-388` · `docs/04-hardware-architecture.md:227` · `docs/adr/README.md:65-74` |
| **P0-2** | **KiCad 骨架是 9/26 的历史快照，含 12 个已删器件，且生成器已被两个数据缺口卡死** | 8 份里 7 份 mtime = 2026-09-26 21:44:50；生成器 rc=1 `netlist refs with no symbol/sheet: ['VCC', 'J17']` 且**退出前不写任何文件**；自检器 rc=1（181 vs 155） | `hardware/schematic/atu-module.kicad_sch:310,1415-1505`（ULN2003A + R_RLY1–6）· `hardware/schematic/mcu-ui.kicad_sch:1276,1623,1723`（TCA9535/LS1/J_UART）· `scripts/build-kicad-schematic.py:1143-1152` |
| **P0-3** | **"docs/05 ↔ 模块 README ↔ 生成器"三方对拍在生成器处断裂** | 引脚号层面 docs/05 与固件 100% 一致，但**生成器仍写 EC11_A=GPIO2、GPIO12=TBD、GPIO20/21=UART0**，且**完全没有 GPIO21（背光）**；docs/05 自己还留着一行反向旧值（GPIO2="未分配/被 EC11_A 占用"） | `scripts/build-netlist.py:56,62,66-67,99-100` · `docs/05-hw-sw-interface-contract.md:517`（vs 同文件 `:106`） |
| **P0-4** | **功放设计点 8.4 V 与 7.4 V 两套数字并存，波及"指标唯一权威"** | docs/04/05 与 BOM 已定 7.4 V（R_opt 12.6 Ω / C1 0.65 nF / L 2.8 µH），但 **docs/00（★指标唯一权威）**、`hardware/README.md`、`pa-module/README.md`、pre-fab A-7 仍写 8.4 V 定点 + 16.3 Ω/0.51 nF/3.7 µH（差约 30%） | `docs/00-project-upgrade-plan.md:16` · `hardware/README.md:9,102` · `hardware/pa-module/README.md:12,19` · `hardware/pre-fab-checklist.md:29` ↔ `docs/04-hardware-architecture.md:85-93` · `docs/05-hw-sw-interface-contract.md:771` |
| **P0-5** | **契约级文档仍以"现行"口吻写着已作废的 12 V / 升压 / PA_PWR_PWM / TCA9535，且有 "幽灵信号"** | `docs/05 §3.1` 写"继电器线圈 12 V/16.7 mA、功放漏极 12–13.8 V（升压可调）"，与同文件 §3.3（5 V/240 mA）直接冲突；`docs/05 §4.2` 的连接器契约里 `PA_EN`/`PA_PWR_PWM` **在网表中没有对应网络**，`CW_KEY` 只有一行 `CW_KEY_SRC`（两端是"U4 的 I²C 写 CLKx_DIS"与 U7）⇒ **不存在 MCU→PA 的键控线** | `docs/05-hw-sw-interface-contract.md:503-505`（vs `:606`）· `:634-639` · `hardware/schematic/netlist.csv`（无 `PA_EN`/`PA_PWR_PWM` 行；仅 `CW_KEY_SRC`，见 `build-netlist.py:121-123`） |

> 另有一个**同等严重但性质不同**的问题，单列于 §3.5：**电池分压 22 kΩ ↔ 30 kΩ 的跨仓漂移**——硬件已定 30 k（比值 0.2327），固件仍按 22 k（0.2926）换算，**满电 8.4 V 会被固件读成 ≈6.68 V，开机即触发"低电告警、禁高功率发射"**（`docs/05:774` ↔ 固件 `components/drv_analog/include/drv_analog_calc.h:66-68`）。

### 0.3 结论分级

| 级别 | 条数 | 说明 |
|---|---|---|
| **P0（阻塞投板 / 会导致做错板或固件不认）** | **6** | P0-1…P0-5 + 电池分压漂移 |
| **P1（架构级不一致，但可在投板前以文档/生成器改动闭环）** | **9** | 见 §10 风险登记表 R-06…R-14 |
| **P2（可制造性/可维护性缺口）** | **7** | 见 R-15…R-21 |
| **P3（记录性/低危）** | **4** | 见 R-22…R-25 |

---

## 1. 模块划分与信号流

### 1.1 物理模块（【事实】）

`docs/04-hardware-architecture.md:44-56` 与 `hardware/README.md:99-112` 给出同一套 9 个模块目录；`hardware/bom/` 下也正好 9 份分模块 BOM（`ls hardware/bom/bom-*.csv`，其中 `bom-summary.csv` 为汇总）。**【判断】架构本身成立**："核心底板 + 可插拔射频模块"（`docs/04:10-28`）与 4 层底板/55×65 mm ATU 的物理约束自洽。

| 模块 | 板/尺寸 | 对外接口（物理） | 电源 | 权威出处 |
|---|---|---|---|---|
| `core-board` | 130×95 mm 四层 | 6 组模块排母 + SMA×3 + 天线座 + 电池座 + 8 个测试点 | 分配 4 轨 | `docs/04:62-67`、`hardware/core-board/README.md:5-33` |
| `pa-module` | 随插槽 | RF in（Si5351 方波）、RF out（SMA）、VCC 漏极、5 V 偏置 | VCC 6.0–8.4 V + 5 V | `docs/04:69-104` |
| `lpf-module` | 随插槽 | SMA in/out，无源无控制 | — | `docs/04:187-194` |
| `atu-module` | 55×65 mm | RF in（SMA）、RF out（SMA→天线）、I²C（0x28）、+5 V 线圈、+3V3 逻辑 | +5V / +3V3_DIG | `docs/05:151-207` |
| `mcu-ui-module` | 随插槽 | I²C0、SPI2、ADC×3(+1 空闲)、GPIO×6、USB | +3V3_DIG | `docs/05:100-121` |
| `power-module` | 随插槽 | 电池入、VCC/+5V/+3V3_RF/+3V3_DIG 出 | — | `docs/04:336-343` |
| `interconnect` / `antenna` / `enclosure` | — | 连接器/线束、天线、结构 | — | `docs/04:478-510` |

### 1.2 模块 ↔ 接口 ↔ 引脚矩阵（【事实】+【判断】混合，逐格标注）

引脚列取 `docs/05 §2.2`（`:104-121`），并在第 9 章与固件逐一对拍（**该表 100% 一致**）。

| 接口 | 总线/类型 | 引脚 | 对端器件（地址/片选） | 该接口的"唯一所有者"（固件） | 一致性 |
|---|---|---|---|---|---|
| ADC1_CH0 | 模拟 | GPIO0 | T1 检波（前向） | `drv_analog` | ✅ |
| ADC1_CH1 | 模拟 | GPIO1 | T2 检波（反向） | `drv_analog` | ✅ |
| ADC1_CH2 | 模拟 | GPIO2 | **无消费者**（本版释放） | `drv_analog`（仅启用时，`docs/05:421`） | ⚠️ 固件**未登记**（`bsp_board_pins.h:45-88` 无 ADC_CH2 项） |
| ADC1_CH3 | 模拟 | GPIO3 | R_VBAT 分压 30k/9.1k | `drv_analog` | 🔴 比值跨仓不一致（§3.5） |
| I²C0 SDA/SCL | 数字双向 | GPIO4/5 | Si5351 `0x60` + **CA-DV8008N `0x28`** | 总线归 `bsp_board` | ✅（但 `docs/05:108` 仍写 TCA9535） |
| SPI2 SCK/MOSI | 数字输出 | GPIO6/7 | ST7567（`CS`=GND、`RST`=板复位） | `drv_lcd12864` | ✅ |
| LCD DC | 数字输出 | GPIO10 | ST7567 A0 | `drv_lcd12864` | ✅ |
| LCD_BL | 数字输出 0/1 | GPIO21 | Q5(2N7002) 低边 + R_BL2 100 kΩ 下拉 | `drv_lcd12864` | ✅（生成器缺此网，§1.4-④） |
| EC11 A/B/SW | 数字输入 | GPIO20 / GPIO8 / GPIO13 | EC11，10 kΩ 上拉×3 | `drv_ec11` | ⚠️ 生成器仍写 A=GPIO2 |
| KEY_USER | 数字输入 | GPIO9 | BOOT 键（strapping） | `drv_keys` | ✅ |
| SCOPE_TRIG | 数字输出（调试） | GPIO12 | 无被控对象 | `bsp_board` 独占 | ⚠️ 命名 `SCOPE_TP`/`SCOPE_TRIG` 并存（`docs/05:114` 已声明以固件为准） |
| 继电器 OC1–OC6 | I²C 从机通道 | —（不占 GPIO） | CA-DV8008N `0x28`，位掩码 `0x3F` | `bsp_io_expander`/`drv_relay` | ✅ 位序与固件一致（§4.3） |
| 功放驱动 | 逻辑 | 无 GPIO（I²C 键控） | SN74ACT244PWR → 3×BS170 栅极 | `drv_pa`、`rf_keyer` | ✅ 无 GPIO（但 `docs/05:634-635` 仍列 `PA_EN`/`CW_KEY` 为连接器信号 → 幽灵，§0.2/P0-5） |
| USB | 差分 | GPIO18/19 | 原生 USB-Serial/JTAG | ESP-IDF 控制台 | ✅ |

**信号流（【事实】按文档串起来，含两处已标注的断点）**：

```
ESP32-C3 ─I²C0(GPIO4/5)─┬─ Si5351(0x60) ─CLK0─ SN74ACT244PWR(5V) ─PA_GATE─ 3×BS170(E类)
                        └─ CA-DV8008N(0x28) ─OC1..OC6─ K1..K6 线圈(+5V)         │
                                                                     PA_DRAIN=VCC(2S)
                                                                                │
   J_PA_OUT ─SMA─ lpf-module(3 阶椭圆) ─SMA─ J_ATU_IN ─ [T1/T2 定向耦合器] ─ L/C 匹配 ─ J_ANT
                                                              │                      │
                                                        D1/D3 + D4/D2           R_esd 100k
                                                              │
                                                     C(10n)-R(68k)-C(10n) → ADC_FWD/ADC_REV
```

**【判断】两处断点**：
1. **耦合器位置在文档里自相矛盾**（输入侧 vs 输出侧），见 §3.3 —— 这决定 `SWR>3 禁发` 到底在保护谁。
2. **`PA_EN` 不存在**：244 的 `1OE` 在网表里没有网络（`hardware/schematic/netlist.csv` 无 `PA_EN` 行），但 `docs/05:634` 把它写成连接器契约。若照 §4.2 做线束，会多引一根无对端的线。`CW_KEY` 同理：网表只有一行 `CW_KEY_SRC`，两端是"U4 的 I²C 写 `CLKx_DIS`"与 U7（`build-netlist.py:121-123`）——**键控根本没有走线**。

### 1.3 三方对拍方法（【事实】）

三方 = ① `docs/05 §2.2/§2.8`（★权威）· ② `hardware/*/README.md`（局部说明）· ③ `scripts/build-netlist.py` + `hardware/schematic/netlist.csv`（派生数据，实际被 KiCad 生成器与 LCEDA 包消费）。

对拍结果（14 个在用引脚 + 4 个不可用引脚 + 2 个 I²C 地址），**逐项列在第 9 章表 9-1**。汇总：

| 对拍对 | 引脚号一致 | 说明 |
|---|---|---|
| ① vs 固件 `board_pins.h` | **16/16 ✅** | 含 4 个"不可用"脚（11/18/19 + 9 特殊） |
| ① vs ② 模块 README | 14/14 ✅（数值/理由 3 处 ❌） | `mcu-ui:36` 22k/9.1k、`pa-module:86` CH2=EC11_A、`mcu-ui:38` SCOPE_TP |
| ① vs ③ 生成器 | **7/11 ❌** | 见 §1.4 |

### 1.4 三方不一致清单（本节的核心产出）

| # | 项 | docs/05（权威）写什么 | 生成器/派生写什么 | 严重度 |
|---|---|---|---|---|
| ① | **EC11_A** | GPIO20（`:116`、`:422`） | **GPIO2**，且注"strapping 脚必须有 10k 上拉"（`scripts/build-netlist.py:56`；`netlist.csv:4`） | 🔴 会导致 A/B 相读错脚 |
| ② | **GPIO12** | `SCOPE_TRIG` 定案（`:114`、`:429`；§7 #7a 已关闭 `:770`） | `GPIO12_TBD`，"去向待定（①驱动降额 ②未来降压调功 ③回收）… 未定前硬件不接"（`build-netlist.py:62`） | 🔴 与"已定案"矛盾；且派生网表里这根脚悬空 |
| ③ | **GPIO20/21** | 回收为 EC11_A / LCD_BL（`:121`） | 仍作 **UART0_TX/RX → J_UART**（`build-netlist.py:66-67`） | 🔴 两个功能凭空多出 2 个对端 |
| ④ | **LCD_BL 驱动源** | GPIO21（`:117`、`:428`） | `LCD_BL_DRV` 的源是 **`-` / TBD**，注"背光驱动位待定（候选另加 CA-DV8008 @0x29）"（`build-netlist.py:99-100`） | 🔴 整条背光链在网表里没有驱动端 |
| ⑤ | **R_sense（Tandem Match 终端）** | **50 Ω / 1 W 配对**，并明写"旧文档 1 kΩ 是错误值"（`:566`、`:766`） | **1 kΩ 初值，需 NanoVNA 微调**（`build-netlist.py:156,162`；`netlist.csv`；BOM `hardware/bom/bom-atu-module.csv:11`；`kicad-symbol-map.csv:31`） | 🔴 按 1 kΩ 做板 ⇒ 桥不平衡、方向性崩塌 |
| ⑥ | **5 V 主轨最大电流** | 0.54 A（原 0.3 + 线圈 0.24，`:606`） | "MP2315 同步降压 5V 主轨; 最大 0.3A"（`build-netlist.py:190`） | 🟠 派生数据低估 80% |
| ⑦ | **背光栅极下拉 R_BL2** | 100 kΩ（`:175`） | netlist 100 kΩ ✅，但 KiCad 实例 `R_BL2 = 10 kohm`（`hardware/schematic/mcu-ui.kicad_sch` 实例表） | 🟠 图与料不一致 |
| ⑧ | **电池分压上臂** | 30 kΩ（`:774` #7d） | netlist 30k ✅、BOM 30k ✅，但 **KiCad 实例 `R_VBAT1 = 22 kohm`**、`kicad-symbol-map.csv:30` "22k/9.1k/1k"、`mcu-ui-module/README.md:36` "22k/9.1k" | 🔴 三处旧值 + 固件也按 22k（§3.5） |

> **【判断】根因**：`build-netlist.py` 把连接关系**硬编码在 Python 里**（`build()` 函数，`:47-257`），而不是从 `docs/05` 或任何机器可读契约生成。所以"docs/05 改一处、生成器要人肉改第二处"，而改第二处没有检查、没有 CI、也没人声明它是事实源（`scripts/README.md:45-57` 只说"已实现"，没说数据从哪来）。

---

## 2. 电源域

### 2.1 电压域表（【事实】，以 `docs/04:336-343` + `docs/05:601-608` + `hardware/power-module/README.md:7-14` 为准）

| 域 | 电压 | 谁产生 | 谁消费 | 电流上限（文档） | 保护 |
|---|---|---|---|---|---|
| **VCC（输入级）** | 2S 锂电 6.0–8.4 V（标称 7.4 V） | 电池 BT1 直供 | ① PA 漏极（E 类）② MP2315 输入 ③ vbat 分压 | ≈0.42 A（7.4 V/2.5 W，η≈80%） | 反接 P-MOS + PTC（`U13`，已降级）+ 2S BMS（`U12` 充电模块） |
| **+5 V 主轨** | 5 V | MP2315 同步降压（输入 4.5–24 V） | ① **ATU 6×线圈 240 mA** ② 栅极偏置分压 ③ LCD 背光 ④ 244 供电 ⑤ CA-DV8008 `COM` | 0.54 A（`docs/05:606`） | 无独立保护；靠 MP2315 自身限流 |
| **+3V3_RF** | 3.3 V | MD7673 LDO（由 +5 V 供电） | Si5351 | 50 mA | π 滤波 |
| **+3V3_DIG** | 3.3 V | π 型 RC 滤波 | ESP32-C3、LCD、EC11、**CA-DV8008 逻辑侧** | 200 mA | — |
| ~~+12 V~~ | ❌ 已取消 | ~~U11 升压~~ | — | — | — |

**【判断】要点**：
- **VCC 是"直供"而不是"稳压"**，因此功率随电量平方下滑（`docs/04:95-104`）；这与"2.5 W 额定"的口径绑定在 7.4 V（§0.2 P0-4 的另一半）。
- **+5 V 轨是本次改版后新增的真实负载热点**：继电器从 12 V/16.7 mA 改为 5 V/40 mA ⇒ 同 6 只线圈的 5 V 侧电流从 100 mA 涨到 **240 mA**，且是**脉冲负载**（调谐时 6 只同吸）。`docs/04:476` 与 pre-fab D-16（`hardware/pre-fab-checklist.md:123`）已把它列为纹波/跌落风险项 ✅；但 **`docs/04:469-472` 的续航表仍按 0.100 A 计算** ⇒ 见下。
- **续航表已过期（【事实】+【判断】计算）**：`docs/04:469` 用"ATU 继电器 0.100 A"，与同文件 `:341`（240 mA）矛盾。按 240 mA 重算（500 mAh 2S，7.4 V 3.7 Wh）：连续发射 `0.5+0.2+0.24 = 0.94 A` ⇒ **≈32 min**（原写 38）；继电器常吸的竞赛档 `0.1+0.2+0.24 = 0.54 A` ⇒ **≈56 min**（原写 75）；静默释放档不变（≈100 min）。**这是计算推断，未实测**。

### 2.2 上电时序（【事实】只有部分被文档化）

| 阶段 | 谁负责 | 状态 | 文档 |
|---|---|---|---|
| 电池插入 → 5 V/3.3 V 建立 | 硬件 | 无时序约束文件（**未核实**是否有软启动/浪涌要求；`docs/04:401-409` 的输入级保护候选已随 12 V 取消而作废） | `docs/04:345-349` |
| 3.3 V 建立 → MCU 复位释放 | ESP32-C3 内部 POR + 板复位（LCD `RST` 共用） | ✅ 有说明 | `docs/05:128` |
| 复位 → `bsp_board_init()` | 全部引脚高阻 | GPIO21 由 **R_BL2 100 kΩ 硬件下拉**保证背光关；GPIO12 悬空无害；CA-DV8008 输出寄存器=0 ⇒ 继电器全释放（0 µH/0 pF 直通） | `docs/05:175,454-460,167` |
| `bsp_board_init()` 之后 | 各所有者 | 一引脚一所有者（`docs/05:416-434`） | ✅ 契约完整 |

**【判断】**：上电安全链是这份设计里最结实的部分——**"MOS 栅极硬件下拉 + 扩展器上电全高阻 + 固件 SAFE_COMBO=0"三重一致**，且三处文档互相引用（`docs/05:167,175,429`；固件 `board_pins.h:196-200`）。这条应保留为范式。

**但有一处缺口**：`docs/05:632-634` 说"CA-DV8008 的 OC7/OC8 保持空闲、不得预接"，而 **CA-DV8008 的 I²C 总线在上电瞬间是否可能被其它主设备拉低**未讨论；`docs/05:259` 仅对 strapping 场景提了一句"I²C 空闲被上拉 ⚠️ 可以，但复位瞬间若总线被占则危险"——**没有落到具体缓解**（未核实是否真风险）。

### 2.3 保护（TVS / 保险 / 反接）

| 保护对象 | 现状 | 证据 | 判定 |
|---|---|---|---|
| 电池反接 | P-MOS + PTC（`U13`） | `hardware/bom/bom-power-module.csv:4`；`docs/05:775` #7e | ✅ 已登记 |
| 过流 | 自恢复 PTC（2 A 保持/4 A 跳闸） | `docs/04:408` | ✅ |
| 过压 / 浪涌 | ❌ **无**（TVS 随 12 V 取消而删） | `docs/04:347-349` | 🟠 2S 电池场景合理；但**充电模块 U12 输入 5–18 V**（`bom-power-module.csv:5`）⇒ 充电口误插 12–18 V 时无 TVS，**未核实**是否可接受 |
| 天线静电 | R_esd 100 kΩ/1 kV 到地（或 GDT） | `docs/04:316-322`；`bom-atu-module.csv:15` | ✅ 文档化最好的一项 |
| 继电器线圈反峰 | 靠 CA-DV8008 `COM→+5V` 内部钳位 | `docs/05:160,192` | ✅（无外部续流管，**依赖器件内部**，属单点依赖） |
| 功放过温 | ❌ **无传感器、无联锁** | `pa-module/README.md:105-113` | 🟠 已知并如实登记为功能缺口 |
| 功放过驻波 | 固件 `SWR>3.0` 禁发 | `docs/05:676-680` | ⚠️ 依赖"耦合器位置"这一未定项（§3.3） |

### 2.4 已删项残留扫描（【事实】，按文件计数）

扫描词：`TCA9535` / `ULN2003` / `+12V` / `12 V` / `升压` / `PA_PWR_PWM` / `HK4100F-DC-12` / `R_RLY` / `LS1`，覆盖 `docs/**.md`、`hardware/**.md|csv|kicad_sch`、`scripts/*.py`、根 `*.md`（不含 `release/`）。**44 个文件命中**，前 12 名：

| 文件 | 命中数 | 构成 | 是否有"历史方案"总声明 |
|---|---|---|---|
| `docs/17-gpio-allocation-audit.md` | 131 | PA_PWR_PWM 53 / TCA9535 50 / 升压 18 | ✅ 有（`:8-22` 两条取代声明） |
| `docs/04-hardware-architecture.md` | 73 | "12 V" 45 / 升压 12 / TCA9535 5 | 🔴 **无**（只有 §3.7 局部作废声明） |
| `hardware/atu-module/relay-wiring.md` | 68 | ULN2003 22 / TCA9535 19 | ✅ 有（`:10-13` CHANGELOG 总声明） |
| `docs/05-hw-sw-interface-contract.md` | 67 | 升压 21 / TCA9535 17 / 12 V 14 | 🔴 **无**（散落多处，部分已标作废、部分没有） |
| `hardware/schematic/kicad-row-coverage.csv` | 65 | +12V 31 / R_RLY 24 | ❌ 派生文件（就是旧数据本身） |
| `docs/00-project-upgrade-plan.md` | 52 | 升压 13 / ULN2003 12 / TCA9535 11 | ✅ 有（`:13-20`） |
| `hardware/schematic/atu-module.kicad_sch` | 38 | +12V 7 / R_RLY 12 / ULN2003 7 | ❌ 派生文件（旧数据本身） |
| `hardware/pre-fab-checklist.md` | 38 | 升压 13 / 12 V 8 / TCA9535 7 | 🟠 逐条标作废，但 **A-7 仍写 8.4 V 定点**（`:29`）、**E-01 已失效**（`:140`） |
| `docs/adr/ADR-0008-...md` | 38 | TCA9535 23 | 🟠 部分标注（§8.2 已标"被 §8.3 取代"） |
| `scripts/build-kicad-schematic.py` | 36 | TCA9535 11 / ULN2003 8 / R_RLY 8 | ❌ **输入数据**（`SHEETS`/`DERIVED`/`VALUE_FIX`） |
| `README.md`（根） | 31 | TCA9535 6 / ULN2003 6 | 🟠 未见总声明（未逐行核） |
| `hardware/schematic/mcu-ui.kicad_sch` | 19 | TCA9535 10 / PA_PWR_PWM 5 / LS1 4 | ❌ 派生文件 |

**【判断】三类残留，处置优先级不同**：
- **(a) 派生文件里的旧数据**（kicad_sch / kicad-row-coverage.csv / kicad-net-map.csv / kicad-build-report.md / kicad-symbol-map.csv）：**不要手改**，随生成器重跑自然消失 —— 但生成器现在跑不动（§6.3），所以这是**被 P0-2 连带阻塞**的。
- **(b) 权威文档里"以现行口吻"写的旧方案**：`docs/05:503-505`（12 V 线圈/功放轨）、`docs/05:108`（Si5351 + TCA9535 共享总线）、`docs/04:51`（模块清单 6×DC-12V + ULN2003A）、`docs/04:261-301`（§3.4 继电器 12 V + "当前方案 = TCA9535+ULN2003A"）、`docs/04:500`（控制互联列"功率 PWM"）、`docs/04:567`（风险 #9 写 TCA9535）、`interconnect/README.md:15,36,40,42,55`、`core-board/README.md:14,22,29,31`。这些**没有总声明遮挡**，读文档的人会照着做。
- **(c) 模块 README / 验证方案里把旧方案当"现行"**：`atu-module/README.md:22-33`（6×DC-12V、12VDC/720Ω/16.7 mA）、`:55-77`（"驱动电路：TCA9535 → ULN2003A 达林顿链"标题就是现行口吻，其下 `:57-62` 的取代声明只否掉了 2N7002，**没否掉它自己**）、`:73`（"ULN2003A 的 COM 必须接 +12V"）、`:88`（R_sense 1 kΩ）、`:144`（BOM 行写 TCA9535+ULN2003A）、`:154-155`（验证项要求量 ULN2003A 反峰与温升）、`:165`（关联文档把 ADR-0008 描述成"继电器驱动 = TCA9535 + ULN2003A 的决策依据"）；`validation/stage-1-relay-rf/README.md:8,13-14,19,23-24,30,41-42,44,60`（把 TCA9535+ULN2003A 当"现行方案/下单口径/验收项"）。**这一类最危险**：它是"照着做会买错料、测错项"的入口。

**特别项（蜂鸣器）**：`LS1` 在 `bom-mcu-ui-module.csv:6` 已标"本版移除/数量 0"✅，`docs/05:179-181,779` 与固件一致 ✅，但 `mcu-ui-module/README.md:58` 的"目录内容"仍写 BOM 含"蜂鸣器"、`hardware/schematic/mcu-ui.kicad_sch:1623/1945` 仍有 `LS1=BUZZER-3V3` 实例。⇒ **文档层已清，派生物未清**。

---

## 3. 射频链

### 3.1 逐级器件（【事实】）

| 级 | 器件/网络 | 关键参数 | 文档位置 | 是否有器件级依据 |
|---|---|---|---|---|
| 0 源 | Si5351A（`U7`，0x60） | 3.5–3.6 MHz，100 Hz 步进；CLK0 输出 | `docs/05:212`、`bom-mcu-ui-module.csv:7` | ✅ |
| 1 整形/驱动 | **SN74ACT244PWR（`U8`）**，5 V 供电 | ±24 mA，0–5 V 方波；输入侧 10 kΩ 下拉**强制** | `docs/05:212-235`、pre-fab D-02（`:107`） | ✅（含"不加下拉→244 自激→PA 自激发射"的失效论证） |
| 1b 栅极网络 | 3×BS170 栅极并联 + 10 kΩ 下拉（R10）+ BZX84-C10 | ≈2.1 V 固定偏置（R1 10k / R2 2.2k） | `docs/04:166-174`、`bom-pa-module.csv:4-6` | ✅ |
| 2 功放 | 3×BS170 并联 E 类 | 7.4 V / 2.5 W 设计点；R_opt 12.6 Ω；C1 0.65 nF；L 2.8 µH | `docs/04:85-93` | ✅（但 8.4 V 旧口径仍在多处，§0.2 P0-4） |
| 3 低通 | 3 阶椭圆 LPF | 3.55 MHz，2f₀ ≥55 dB，插损"实测登记" | `docs/04:187-194`、`lpf-module/README.md:9-16` | 🟠 **器件值缺失**：`lpf-module.kicad_sch` 里 L4/L5/L6/C8/C9/C10 = `TBD-T106-6`/`TBD-NP0`（实例表）；pre-fab C-07（`:89`）已登记 |
| 4 定向耦合器 | **Tandem Match**：T1/T2 各 1:10 穿同一主线，次级串接，两端各 50 Ω/1 W 终端 | 耦合 20±3 dB，方向性 >25 dB | `docs/05:549-573`、`atu-module/README.md:97-126` | ✅ 拓扑/器件/RC 选值都文档化（**这是全仓文档质量最高的一节**） |
| 4b 检波 | D1/D3（1N5711）+ D2/D4（HSMS-2850 占位）并行 | V_F 0.15–0.3 V，平方律 | `docs/05:567`；`bom-atu-module.csv:12-13` | ⚠️ 选型未定（`docs/05:767` #5，待 stage-3） |
| 4c 滤波 | C(10n)–R(68k)–C(10n) C0G | τ=0.68 ms；3.55 MHz 抑制 −83.6 dB | `docs/05:575-586` | ✅（有对比表与选值理由） |
| 5 匹配网络 | 6 只 HK4100F + 3L/3C（**或** ADR-0009 的 4C+2L） | 64 组合（**或** 48） | `docs/04:227`、`relay-wiring.md:329-390`、`ADR-0009:39-47` | 🔴 双规格（§4.5） |
| 6 天线 | 5 m 垂直导线 + ≥5 m 地线 | 挂树 115–134 −j990…−j1180 Ω | `docs/04:478-488`、`hardware/antenna/test/2026-10-field-measurements.md:6-30` | ✅ 有 11 点实测（但频率/高度未记录，`:42-45`） |

### 3.2 驻波桥拓扑是否文档化？（【事实】）

**结论：拓扑与元件级细节已文档化，但"位置"未定，且"器件级 BOM 未跟上"。**

已文档化（✅）：正向/反向检波各由一只 50 Ω 终端 + 双二极管并行 + 两级 C-R-C 组成；FWD/REV 是"两端串接后的和/差"而不是单只变压器出来的（`docs/05:565` 明写）；极性必须实测（`:588-599` 给了六步法）。

未文档化 / 未定（❌）：
1. **耦合器在主线的哪一侧**（§3.3）。
2. **ADC 分压与偏置**：`docs/05:569` 只有"ADC 节点泄放 100 kΩ（建议）"，**没有**任何"分压比/偏置电压/满量程对应 dBm"的表；`bom-mcu-ui-module.csv:24` 的 `R_ADC` 数量写"待定"、值写"待定"。
3. **BOM 缺检波滤波件**：`bom-atu-module.csv` 全 14 行里**没有 68 kΩ / 10 nF / 100 kΩ 泄放**任何一行（我逐行核过 `:2-15`）。⇒ 照 BOM 下单，检波器只有二极管，没有 RC。

### 3.3 耦合器位置：`docs/05` 内部矛盾（【事实】）

| 出处 | 说法 |
|---|---|
| `docs/05-hw-sw-interface-contract.md:624` | "ATU → SWR 耦合器 · 板内 · 50 Ω · **Tandem Match 位于 ATU 输出侧**" |
| `docs/05-hw-sw-interface-contract.md:550-561`（§3.2.3 图） | `RF_IN ─T1─T2─ 主线 → LC 匹配网络 → 天线` ⇒ **在匹配网络之前（输入侧）** |
| `hardware/atu-module/relay-wiring.md:200` | N0（L 链入口）="`J_ATU_IN.中心`、`L1.1`、`K1.COM`"，且 N0 注释为"来自 lpf-module / **耦合器主线**" ⇒ **输入侧** |
| `scripts/build-netlist.py:152-154` | `ATU_L_IN`："输入 SMA →(Tandem Match 耦合器主线)→ L 链第一只电感" ⇒ **输入侧** |

**【判断】这是架构级歧义，不是文字瑕疵**：输入侧测得的是"PA 看到的阻抗"（保护 PA 正确，但调谐判据是"让 PA 满意"）；输出侧测得的是"天线侧的 SWR"（能直接反映天线失配，但 PA 保护是间接的）。两者对 `SWR>3.0 禁发`（`docs/05:676`）、`ATU_MATCH_SAFE_COMBO` 的判据、以及 §3.2.5 的极性实测步骤（"RF_OUT 接假负载、RF_IN 接发射机"）都会给出**不同的验收数字**。4 处文档里 3 处指向输入侧、1 处写"输出侧" ⇒ **建议按输入侧收敛并改 `:624`**。

### 3.4 与固件的契约：`BOARD_ADC_FWD/REV` 的电压范围与 dBm/W 映射有标定依据吗？

**结论（【事实】）：没有。当前是"占位标定"。**

- 硬件侧只给"目标区间"而非映射：`docs/05:514-515`「2 W 下 ADC 读数应落量程 **20%–80%**」「SWR=2.0 @2 W 时读数 ≥量程 5%」；`:572` 给了一个电平估算（N=10、R=50 Ω、2.5 W ⇒ `V_det ≈ 1.12 V`）。
- 标定表**尚未产生**：`docs/05:598` 第⑥步"记录 0.5/1/2/2.5 W 各点 FWD 读数 ⇒ 建功率标定表"；`docs/05:766`（§7 #4）仍把"用 50 Ω 假负载实测方向性 >25 dB + 两电阻配对"列为**待做**；`validation/reports/` 只有 `.gitkeep`（无任何实测报告）。
- 固件明确承认是占位：`ARDF-MeshTuneFox80-firmware/components/rf_swr/include/rf_swr.h:106`「缺省值只是**占位**，必须用实测两点标定覆盖」、`:171-175`「缺省检波器模型（**占位值**）/ 缺省耦合器标定（门限按 1N5711 量级取**占位值**）」。
- 唯一的数值不变量是 `SWR 门限 3.0`（`docs/05:674-680` 与固件 `rf_swr.h:77` 一致 ✅）。

**【判断】** 这是"如实的占位"，不是错误；但**风险在于硬件仓没有任何地方登记"标定数据缺失 ⇒ 功率读数不可信"**。`docs/05:570` 只说"需功率 + SWR 双标定"，`pre-fab-checklist` 的 A-4（`:26`）只要求方向性与电阻配对，**没有一条要求"投板后必须产出功率标定表并回填 BOM/固件"**。建议补一条放行判据（§11-⑦）。

### 3.5 🔴 电池分压的跨仓漂移：22 kΩ vs 30 kΩ（【事实】+【判断】影响）

| 侧 | 取值 | 比值 | 8.4 V 时引脚电压 | 6.0 V 时引脚电压 | 证据 |
|---|---|---|---|---|---|
| **硬件（现行）** | R1=30k / R2=9.1k / R3=1k | **0.2327** | 1.95 V | 1.40 V | `docs/05:774`（#7d 定稿）、`hardware/bom/bom-mcu-ui-module.csv:18-20`、`build-netlist.py:55,172-176` |
| **固件（现行代码）** | `DRV_ANALOG_BATT_R1_OHM = 22000` | **0.292605** | 2.46 V | 1.76 V | 固件 `components/drv_analog/include/drv_analog_calc.h:43-48,66-68` |
| 硬件老写法（仍存） | 22k/9.1k | 0.2926 | 2.46 V | 1.76 V | `hardware/schematic/mcu-ui.kicad_sch`（R_VBAT1=22 kohm）、`kicad-symbol-map.csv:30`、`mcu-ui-module/README.md:36` |

**【判断】影响可算**：固件按 `VBAT = V_pin × 3.4176` 换算，而板上实际比值 0.2327 ⇒ 上报值 ≈ 真值 × **0.795**。满电 8.4 V 会被读成 **≈6.68 V**；而 `docs/05:355` 的"低电告警 ≤6.80 V"意味着 **满电电池一开机就落在告警区**，按同一条款"不得发起高功率发射"。⇒ **接线完全正确、固件也不报错，但电池永远显示没电** —— 这正是任务里点名的"接线正确但固件不认"那一类。

**【事实】责任划分**：`docs/05:774` 已明写"🔴 **固件阈值按 0.2327 标定**"，所以这是**已下达但未执行的固件侧变更**；硬件仓这边的问题是 **`mcu-ui-module/README.md:36` 仍写 22k/9.1k**，等于给固件方提供了错的参照。

---

## 4. ATU 继电器模块

### 4.1 契约现状（【事实】，三方一致的部分）

| 契约项 | 值 | 证据 |
|---|---|---|
| 驱动器件 | CA-DV8008N（立创 C54557228），SOIC-16N/TSSOP-16 | `docs/05:153`、`bom-atu-module.csv:3` |
| I²C 地址 | **0x28**（A0/A1/A2 全 GND；8 位写 0x50 / 读 0x51） | `docs/05:154`、`relay-wiring.md:18`、固件 `board_pins.h:66` ✅ |
| 通道映射 | OC1↔K1 … OC6↔K6；**OC7/OC8 空闲、不预接** | `docs/05:158-159,205`、`relay-wiring.md:28`、固件 `board_pins.h:181-190` ✅ |
| 线圈电源 | **+5 V**（HK4100F-DC5V-SHG，125 Ω/40 mA，6 只同吸 240 mA） | `docs/05:190,199`、`bom-atu-module.csv:2`、固件 `board_pins.h:202-204` ✅ |
| COM | **+5 V**（内部续流钳位共阴） | `docs/05:160,192`、pre-fab D-01（`:106`） ✅ |
| VCC（逻辑） | **+3V3_DIG**（V_IH=0.7×VCC，接 5 V 会读不到高电平） | `docs/05:161`、`bom-atu-module.csv:3` ✅ |
| 上电安全态 | 寄存器=0 ⇒ 8 路高阻 ⇒ 全释放 = 0 µH/0 pF 直通 | `docs/05:167`、固件 `atu_match.h:66`、`drv_relay.h:23-33` ✅ |
| 位掩码 | 只用 `0x3F`，OC7/OC8 绝不触碰 | `docs/05:205,434`、固件 `drv_relay.h:86`、`atu_match.h:63` ✅ |

**【判断】这一层是全仓跨仓一致性最好的部分**：地址、通道、极性、安全态、掩码在 4 份文档 + 3 份固件头文件里逐字对齐。

### 4.2 与 `relay-wiring.md` 的 CHANGELOG 对拍（【事实】）

`relay-wiring.md:10-31` 的 CHANGELOG（2026-10-11）写了 10 条差异并给了总声明（`:12`）："凡出现 TCA9535 / ULN2003A / IOEXP_RELAY_K1..K6 / R_RLY1..R_RLY6 / +12V（线圈电源）之处，均为历史方案"。

对拍结果：

| CHANGELOG 条目 | 是否落地 | 证据 |
|---|---|---|
| 驱动改 CA-DV8008N ×1 | ✅（BOM/docs/固件） | `bom-atu-module.csv:3` |
| 地址 0x20 → 0x28 | ✅ | `docs/05:154` |
| 继电器 DC12V → DC5V-SHG | ✅ 文档/BOM；❌ **KiCad** | `bom-atu-module.csv:2` vs `atu-module.kicad_sch`（K1–K6 值 = `HK4100F-DC-12V`/`12 V`） |
| 线圈电源 +12 V → +5 V | ✅ 文档/BOM；❌ **KiCad**（`+12V` 全局标签 7 处） | `atu-module.kicad_sch:539,564,589,619,649,679,807` |
| 删除 R_RLY1–6 | ✅ 文档/BOM/pre-fab D-20；❌ **KiCad**（6 个实例）＋ ❌ **本文 TL;DR 仍在要求"必须补"** | `atu-module.kicad_sch:1415-1505`；`relay-wiring.md:76`（TL;DR："⛔ 必须补的硬件 ‖ ULN2003A IN1–IN6 各加 10 kΩ 下拉"）vs `hardware/pre-fab-checklist.md:127`（D-20 已作废） |
| COM → +5 V | ✅ 文档/KiCad 都对（`U2.COM` 在旧图里接 +12 V，属旧器件） | — |

**【判断】两个仍然会误导人的点**：
1. **`relay-wiring.md:76`**：TL;DR 表格里"必须补的硬件 = 6 只 10 kΩ 下拉"，与 pre-fab D-20（已作废）**直接冲突**。总声明说"凡出现 R_RLY 者均为历史"，但这一行没有出现 `R_RLY` 字样，只有"10 kΩ 下拉"——**总声明盖不住它**。
2. **`relay-wiring.md:436-456`（§4.2）** 整节仍在论证"必须补 6 只下拉"，并写"这条此前不在 BOM…本轮新增（见 pre-fab D-20）"——叙述时态是现在时，且给出的 BOM 依据已被删除。

### 4.3 L/C 网络与固件 `atu_match` 的一致性（【事实】逐项）

| 契约项 | 硬件仓 | 固件 | 判定 |
|---|---|---|---|
| 组合数 | 64（2^6） | `ATU_MATCH_COMBO_COUNT 64u` | ✅ |
| 索引编码 | `index = ind_bits | (cap_bits << 3)`，且 `index == relay_mask` | `index = ind_bits | (cap_bits << 3)`，注释"index 与 relay_mask 数值相同" | ✅ |
| 位序 | bit0=K1=L1 12µH · bit1=K2=L2 33µH · bit2=K3=L3 47µH · bit3=K4=**C3** 22pF · bit4=K5=**C4** 120pF · bit5=K6=**C5** 330pF | bit0..bit2 同 · bit3=K4=**C1** 22pF · bit4=K5=**C2** 120pF · bit5=K6=**C3** 330pF | ⚠️ **位序对、位号错**（硬件 C3/C4/C5 ↔ 固件注释 C1/C2/C3） |
| 拓扑 | 电感串联求和、电容并联求和；`SHUNT_C_AT_LOAD`（电容在天线侧） | "电感串联求和、电容并联求和" | ✅（但固件注释承认"合成方式与元件↔继电器对应关系必须由硬件实测确认"，`atu_match.h:29-30`） |
| 安全态 | `ATU_MATCH_SAFE_COMBO = 0` | 同 | ✅ |
| 极性 | 位=1 ⇔ 吸合 ⇔ 元件接入 | 位=1 ⇔ 吸合 | ✅（`drv_relay.h:23`） |

**位号冲突的证据**：硬件 `relay-wiring.md:363-372`（C3/C4/C5）· `atu-module/README.md:47-51`（C3/C4/C5）· `bom-atu-module.csv:7-9`（C3/C4/C5）↔ 固件 `atu_match.h:22-24`（C1/C2/C3）。生成器的 netlist 甚至为此写了注释："C3 为硬件位号；固件注释里称 C1"（`scripts/build-netlist.py:233,236,239`）。

**【判断】** 功能上不致命（位序才是契约），但它会让"照固件注释点料"的人把 22 pF 装到 C1 位（硬件 C1 不存在于 ATU BOM）——属于**命名债**，建议固件改注释（一行改动），而不要改硬件位号（会动 BOM/丝印/网表）。

### 4.4 `atu-module/**` 的残留（【事实】）

| 位置 | 残留 | 是否被总声明覆盖 |
|---|---|---|
| `atu-module/README.md:22-33` | 6× HK4100F-DC-**12V**、12VDC/720Ω/16.7 mA/6 只 100 mA | ❌ 无总声明 |
| `atu-module/README.md:53-55` | "全部选用 NP0 1206/1812，耐压 ≥630 V"（✅ 有效） | — |
| `atu-module/README.md:55-77` | "**驱动电路：TCA9535 → ULN2003A 达林顿链**" + 链路图 + `COM 必须接 +12V` + "元件数 2 颗" | 🟠 局部声明只否掉 2N7002（`:57-62`），**没有否掉 TCA9535+ULN2003A** |
| `atu-module/README.md:79-84` | 2N7002 推演（已标"原（已废）"） | ✅ |
| `atu-module/README.md:88` | "R_sense 初始 **1 kΩ**" | ❌ 与同文件 `:106,118`（50 Ω）**自相矛盾** |
| `atu-module/README.md:144` | BOM 行写"TCA9535 + ULN2003A" | ❌ |
| `atu-module/README.md:154-155` | 验证项要求"ULN2003A 关断反峰/温升" | ❌ |
| `atu-module/README.md:165` | 关联文档称 ADR-0008 是"继电器驱动 = TCA9535 + ULN2003A 的决策依据" | ❌（ADR-0008 §3.3 已被 2026-10-11 方案取代） |
| `relay-wiring.md:412-499`（§4 整节） | TCA9535→ULN2003A 极性/上电/校核 | ✅ 总声明覆盖（`:12` 明确列了这 5 个词） |
| `relay-wiring.md:76` | TL;DR "必须补 6 只下拉" | ⚠️ **盖不住**（见 §4.2） |
| `relay-wiring.md:400` | "6 只线圈同时通电（约 100 mA）" | ❌ 应为 240 mA（同文件 `:21` 已写 240 mA） |

### 4.5 🔴 ADR-0009：一个"已接受但零落地"的拓扑决策（【事实】）

`docs/adr/ADR-0009-atu-4c2l-series-c-shunt-l.md`：

- `:3` 状态 **✅ Accepted（2026-10-11）**；`:4` "**取代 ADR-0003**（6 继电器 L 型网络：串联 L 旁路 + 并联 C，64 组合）"。
- `:27-47` 决定：**③ 串 C 并 L（负载侧）+ 4C+2L**；电容 **68/390/470/1000 pF**（K1–K4 旁路型）；电感 = **单只 T68-6 双抽头 59/63 匝 ⇒ 19.8/22.6 µH**（K5/K6）；**48 组合**。
- `:53-54` 明写后果："`relay_mask` 位定义**重排**（K1–K4 = 电容旁路、K5/K6 = 电感抽头）"、"`relay-wiring.md` 的 64 组合表 ✗ → **48 组合表**；BOM 删 `L1/L2/L3`、加 `L_tap`"。

**全仓引用情况（我 grep 了所有 `*.md/*.py/*.csv`）**：除 ADR-0009 自身与 `hardware/antenna/test/2026-10-field-measurements.md`（`:4,32-40,46`）外，**零引用**。具体地：

| 应当被 ADR-0009 改变的地方 | 实际内容 | 证据 |
|---|---|---|
| ADR 索引 | **没有 ADR-0009 这一行**；ADR-0003 仍标"已接受" | `docs/adr/README.md:65-74` |
| `docs/04` ATU 节 | 3L+3C、64 组合、"L1 12µH / L2 33µH / L3 47µH" | `docs/04:227-247` |
| `docs/05` ATU 节 | 6 继电器、OC1–OC6、64 组合 | `docs/05:386,582` |
| `atu-module/README.md` | 3 电感 + 3 电容、64 组合、C3/C4/C5=22/120/330 pF | `:13-15,37-51` |
| `relay-wiring.md` | 64 组合全表（附录 A 64 行） | `:556-627` |
| BOM | L1=12µH、L2=33µH、L3=47µH、C3/C4/C5=22/120/330 pF | `bom-atu-module.csv:4-9` |
| KiCad 骨架 | L1/L2/L3、C3/C4/C5 | `atu-module.kicad_sch` 实例表 |
| 验证脚本 | 8+8=64、`SHUNT_C_AT_LOAD` | `scripts/verify-atu-lc-combos.py`（rc=0） |
| 固件 | `ATU_MATCH_COMBO_COUNT 64u`、3+3、`index=mask` | 固件 `atu_match.h:59-63` |

**【判断】这是本次审计发现的最严重的单点问题**，理由有三：
1. **它是 Accepted 状态**（按 `docs/adr/README.md:29`「已接受：已达成一致，所有后续实现必须遵守」⇒ 现在全仓都在违反一条 Accepted ADR）。
2. **它同时改固件契约**（位定义重排 + 组合数 64→48）⇒ 一旦实施，`atu_match` 的 `index/mask` 语义、NVS 记忆、丝印、调谐搜索全要跟着改；一旦不实施，就必须显式把 ADR-0009 标成"未采纳/撤回"，否则后来者无法判断。
3. **旧拓扑已被自己的验证脚本证伪**：`verify-atu-lc-combos.py` 运行到底（rc=0）但对 README 的判据点给出 `[NOTE] README '50-j1110 / 47uH / SWR<1.8' is NOT reachable with any of the 64 combinations`——这正是 ADR-0009 要解决的问题。**旧方案有已知达不到的指标，新方案没落地**。

### 4.6 旧拓扑的覆盖能力（【事实】来自验证脚本实跑）

`python scripts/verify-atu-lc-combos.py` → **rc=0**，关键数字：
- `tree 120-j1050`：`SHUNT_C_AT_LOAD` 最优 SWR **2.193** @ L=33 µH/C=22 pF（README 判据 <2.5 ✅）。
- `lab A 88-j1030`：最优 **1.870** @ 47 µH/0 pF（判据 <2.0 ✅）。
- `lab B 50-j1110`：最优 **3.209**（`SHUNT_C_AT_LOAD`）/ 1.838（`SERIES_L_AT_LOAD`+120 pF）⇒ **判据 <1.8 在任何 64 组合下都达不到**（脚本自记为 open item）。
- 解析解校验：树天线 `L = 30.502 µH / C = 23.395 pF` ✅ 与文档 31 µH/25 pF 吻合。

**【判断】** 这说明 64 组合表本身是**可信的**（数字可复现），问题不在算术，而在**选型覆盖不足**——而 ADR-0009 正是那个"覆盖不足"的解答，却停在纸上。

---

## 5. 可制造性

### 5.1 BOM 完整性（【事实】）

| 指标 | 数值 | 证据 |
|---|---|---|
| 分模块 BOM 文件 | 9（+ `bom-summary.csv` + `bom.md`） | `hardware/bom/` |
| 分模块 BOM 数据行 | **81** | 逐文件 `DictReader` 统计 |
| 有真实 LCSC 编号的行 | **2 / 81**（`K1-K6`=C12072、`U1`=C54557228） | `bom-atu-module.csv:2-3`；其余全为 `待查` |
| `统一数量` 非整数的行 | **20 / 81**（`0-1`、`待定`、`6 组`、`多只`、`1 套`、`可选`、`5 m`…） | 例：`bom-atu-module.csv:14`（U3 `0-1`）、`bom-mcu-ui-module.csv:24`（R_ADC `待定`） |
| 汇总 BOM 是否去重 | ❌ **没有**：81 行 = 各模块简单拼接；`X1` 出现 **2 次**（core + mcu-ui）、`位号 = "-"` 的行 **14** 行 | `hardware/bom/bom-summary.csv` |

**LCSC 全"待查"是已说明的**：`hardware/bom/README.md:177-188` 如实写了"立创搜索 API 403 ⇒ 不编造，留待查"。**【判断】这不算缺陷，算正确的诚实**；但它使 `pre-fab-checklist F-05`（`:158`"BOM 的 LCSC 编号列已回填（当前全部待查）"）成为**投板的硬阻塞项**，而这条目前无任何进展记录。

### 5.2 BOM ↔ 网表的位号覆盖（【事实】）

**任务里提到的"row coverage 181 vs netlist 155"不是 BOM 与网表的差异，而是 `kicad-row-coverage.csv`（9/26 快照）与 `netlist.csv`（10/17 重生成）的差异** —— 我在 §6.4 单独量化。**BOM 与网表**的独立比对结果是另一组问题：

| 现象 | 例证 |
|---|---|
| BOM 用**范围写法**，网表用**逐位号** | BOM `K1-K6` / `J1-J6` / `J7-J9` / `TP1-TP8` / `C11-C13`；网表 `K1`…`K6`、`J1`、`J17` |
| 于是自动比对必然"Missing" | 我实测：网表 64 个非伪引用中，**17 个**在 BOM 里查不到（`C244`、`D5_prot`、`J1`、`J17`、`J_ANT`、`J_ATU_IN`、`J_PA_OUT`、`J_UART`、`J_USB`、`K1`…`K6`、`R_sense_F`、`R_sense_R`）；其中 `K1..K6`、`J1` 是范围写法造成，`C244`/`D5_prot` 是**别名**（BOM 写 `C6,C_decout` / `D5`） |
| 真正缺的 | `J_ANT`/`J_ATU_IN`/`J_PA_OUT`（模块侧 SMA，BOM `J11-J16` 覆盖一部分）、`J_USB`、`J17`（见 5.3）、`R_sense_F/R`（BOM 只有一行 `R_sense`）、`C244` |

**【判断】** 这不是"BOM 少了 17 个件"，而是**BOM 与网表没有共同的位号命名空间**（范围 vs 单体、别名、伪引用）。它使得"BOM 与网表行数对不上"这类检查无法自动化，只能人肉。**建议**：BOM 的"位号"列改为**逐位号 + 逗号分隔**（生成器已能展开 `expand_refs`，见 `build-kicad-schematic.py:665`），这是一次生成器改动可覆盖的。

### 5.3 关键错误/缺口（【事实】，按危害排序）

| # | 问题 | 证据 | 后果（【判断】） |
|---|---|---|---|
| M-1 | **`R_sense` 仍是 1 kΩ** | `bom-atu-module.csv:11`（"1 kohm…初值，需 NanoVNA 微调"）、`build-netlist.py:156,162`、`kicad-symbol-map.csv:31` | 桥终端≠Z₀ ⇒ 方向性崩塌、`V_det` 达 22 V 削顶。`docs/05:566` 已判"1 kΩ 是错误值"，但**派生文件没改** ⇒ 照 BOM 下单必错 |
| M-2 | **BOM 缺检波 C-R-C（68 kΩ/10 nF×2）与 100 kΩ 泄放** | `bom-atu-module.csv:2-15` 无相应行 | 检波器只有二极管；ADC 读数纹波/放电不可控 |
| M-3 | **`J17` 位号双重定义** | pre-fab D-24（`:130`）把 J17 定义为"ATU 继电器/控制连接器（8 pin：+5V/GND/+3V3/I2C/ADC）"；`bom-interconnect.csv:4` 把 **J17-J22** 定义为"模块排针（2.54 mm，传 GPIO/PWM/SWR/**12V**/5V/3V3）" | 采购/画图/接线三方各按一套；也是 KiCad 生成器 `J17` 无符号的直接原因（§6.3） |
| M-4 | **`U8`（SN74ACT244）模块归属不一致** | `bom-mcu-ui-module.csv:8` 归 `mcu-ui-module`；而 `pa-module.kicad_sch` 实例含 `U8=SN74ACT244PWR`、`build-netlist.py:142` 的 `+5V→U8.VCC` 在 PA 段 | 插件板该把 244 装在哪块？两份 BOM 都可自洽，合起来冲突 |
| M-5 | **`X1` 重复出现在两份模块 BOM** | `bom-core-board.csv:6` + `bom-mcu-ui-module.csv:23`（都是 32.768 kHz DNP） | 汇总不去重 ⇒ 可能多买/多贴 |
| M-6 | **测试点定义含 12 V** | `bom-mcu-ui-module.csv:25`（"3.3V/5V/**12V**/ADC_FWD/…"）、`bom-summary.csv:49` | 板上没有 12 V 轨，测试点清单是旧的 |
| M-7 | **LPF 器件值仍 TBD** | `lpf-module.kicad_sch`（`TBD-T106-6`/`TBD-NP0`）、pre-fab C-07（`:89`） | LPF 无法下单；而 `lpf-module/README.md:20` 把"具体型号见 schematic/bom"指向空目录 |

### 5.4 装配顺序 / 测试点（【事实】）

- **装配顺序：文档里没有**。最接近的是 `docs/04:539-551`（发布产物清单）与 `hardware/README.md:116-128`（文件归属表），**都不是装配工艺**。`hardware/pre-fab-checklist.md` 是"打样前检查"，不含"先贴哪一面/哪些 DNP"。
- **DNP 清单散落**：`Q4`/`X1`（`build-kicad-schematic.py:654`）、`U3`（BOM `0-1`）、`R12`/`LS1`/`C7`（数量 0）。**没有一份"本版 DNP/不贴清单"**。**【判断】** 这是投板前的实际风险点（贴片厂按 BOM 数量 0 处理即可，但 0-1/待定的 5 行会卡住）。
- **测试点**：`core-board.kicad_sch` 有 `TP1..TP8` 实例（18 个实例里 8 个是 TP），但**没有一份"测试点 ↔ 网络 ↔ 期望值"表**；BOM 的建议清单（`bom-mcu-ui-module.csv:25`）还含 12 V。`docs/05:307` 提到"实测三重确认"但没连到测试点。

### 5.5 `pre-fab-checklist.md` 与当前设计的一致性（【事实】）

**整体质量高**：A 组对齐 `docs/05 §7`（含 A-2/A-4/A-7/A-7a/A-12/A-13/A-14 的 2026-10-11 更新）、D 组新增 D-22/D-23/D-24/D-25（`:128-131`）都是本轮真实变更。**但有 4 处已失效**：

| 项 | 写什么 | 现状 | 证据 |
|---|---|---|---|
| **C-01**（`:83`） | "⛔ 无任何原理图文件 —— `hardware/*/schematic/` 只有 `.gitkeep`" | **8 份 `.kicad_sch` 已存在**（在 `hardware/schematic/`，不在各模块目录） | `hardware/schematic/*.kicad_sch` |
| **A-7**（`:29`） | "E 类按 **8.4 V 定点**" | docs/04/05 已改 7.4 V | `docs/04:85`、`docs/05:771` |
| **E-01**（`:140`） | "`hardware/README.md §3` 仍写 6×2N7002，与**现行方案（TCA9535 + ULN2003A）**冲突" | 前半句已修（`hardware/README.md:104` 现写 CA-DV8008N），后半句"现行方案"本身已过期 ⇒ **整条应关闭/改写** | `hardware/README.md:104` |
| **E-06**（`:145`） | "开发板选型决策**待项目所有者拍板**" | `docs/05:780`（§7 #12）与 `docs/17:132` 已定"留在 LuatOS、本版不做换板" ⇒ 决策已闭 | `docs/05:780` |

**【判断】** 这 4 条会让"按清单放行"的人做无效工作（找不存在的缺口 / 追已关闭的决策）。建议在重开清单时一并修正——**但本次审计不改**。

---

## 6. KiCad 骨架问题量化

### 6.1 逐份清单（【事实】）

`python scripts/check-kicad-schematic.py` 输出（逐份 PASS，唯一 FAIL 是行覆盖）：

| 文件 | 行数 | 字节 | 符号实例 | 图幅 | mtime | 含已删器件 | 含错值器件 |
|---|---|---|---|---|---|---|---|
| `atu-module.kicad_sch` | 1716 | 63325 | **29** | A3 | **2026-09-26 21:44:50** | 7（U2 + R_RLY1–6） | 8（K1–K6 12 V；R_sense_F/R 1 kΩ） |
| `pa-module.kicad_sch` | 953 | 35498 | 14 | A3 | 2026-09-26 21:44:50 | 0 | 0 ✅ |
| `lpf-module.kicad_sch` | 256 | 9035 | 6 | A4 | 2026-09-26 21:44:50 | 0 | 6 个 TBD（值未定，非作废） |
| `mcu-ui.kicad_sch` | 1976 | 76641 | **25** | A3 | **2026-10-15 21:53:05**（**手工改过**） | 4（U1=TCA9535、LS1、R12、J_UART） | 2（R_BL2=10 kΩ、R_VBAT1=22 kΩ） |
| `power-module.kicad_sch` | 626 | 22751 | 9 | A4 | 2026-09-26 21:44:50 | 1（U11=BOOST-12V-MODULE） | 0 |
| `core-board.kicad_sch` | 656 | 24344 | 18 | A4 | 2026-09-26 21:44:50 | 0（但含 `+12V` 标签） | 0 |
| `interconnect.kicad_sch` | 222 | 8022 | 6 | A4 | 2026-09-26 21:44:50 | 0 | 0 |
| `antenna.kicad_sch` | 179 | 6346 | 2 | A4 | 2026-09-26 21:44:50 | 0 | 0 |
| **合计** | 6584 | — | **109** | — | — | **12** | **10** |

> 附：自检器汇总行 `SUMMARY files=8 instances=109 pins=397 labels=212 nets=73 netlist_rows=181 attached=278 problems=1`。

### 6.2 22 个问题实例逐项（【事实】）

| # | 文件 | 位号 | 现值 | 应为 | 依据 |
|---|---|---|---|---|---|
| 1 | atu | `U2` | `ULN2003A` | **删除** | `docs/05:195`（1 颗 CA-DV8008N 替代 ULN2003A+TCA9535） |
| 2–7 | atu | `R_RLY1`…`R_RLY6` | `10 kohm` | **删除** | `docs/05:167,200`；pre-fab D-20（`:127`） |
| 8–13 | atu | `K1`…`K6` | `HK4100F-DC-12V`（K1）/`12 V`（K2–K6） | `HK4100F-DC5V-SHG` | `docs/05:158`；`relay-wiring.md:20` |
| 14–15 | atu | `R_sense_F`/`R_sense_R` | `1 kohm` | `50 Ω / 1 W` | `docs/05:566,766` |
| 16 | mcu-ui | `U1` | `TCA9535` | `CA-DV8008N` | `docs/05:153`；`VALUE_FIX["U1"]="CA-DV8008N"`（`build-kicad-schematic.py:621`，**值表已改、符号未改**） |
| 17 | mcu-ui | `LS1` | `BUZZER-3V3` | **删除** | `docs/05:179-181,779` |
| 18 | mcu-ui | `R12` | `10 kohm` | **删除（数量 0）** | `docs/05:474`；`bom-mcu-ui-module.csv:22` |
| 19 | mcu-ui | `J_UART` | `Conn_01x04` | **删除** | `docs/05:121`（UART0 备用串口取消） |
| 20 | mcu-ui | `R_BL2` | `10 kohm` | `100 kΩ` | `docs/05:175`；`bom-mcu-ui-module.csv:11` |
| 21 | mcu-ui | `R_VBAT1` | `22 kohm` | `30 kΩ` | `docs/05:774`；`bom-mcu-ui-module.csv:18` |
| 22 | power | `U11` | `BOOST-12V-MODULE` | **删除** | `docs/05:772`（#8："该升压模块已从 bom-power-module.csv 删除（原 U11）"） |

**另有网络标签级残留**（同样会让 ERC/网表出错）：
- `+12V` 全局标签 **9 处**：`atu-module.kicad_sch:539,564,589,619,649,679,807`、`core-board.kicad_sch:132`、`power-module.kicad_sch:334`。
- `IOEXP_*` 标签 **16 个**（`mcu-ui.kicad_sch` 标签表）：`IOEXP_LCD_BL`、`IOEXP_RELAY_K1..K6`、`IOEXP_SPARE_P0_6/P0_7/P1_0/P1_2/P1_3/P1_4/P1_5/P1_6/P1_7`、`TCA9535_INT`。
- `PA_PWR_PWM` 2 处（`mcu-ui.kicad_sch:770,1168`）、`BUZZER_DRV` 1、`UART0_TX/RX` 2、`GPIO12_FB_PD` 1。
- **反向缺失**：`mcu-ui.kicad_sch` 里**没有** `GPIO20`、`GPIO21`、`GPIO12` 作为网络——它在符号里保留了引脚名（`:120-125`），但没有任何连到 `EC11_A`/`LCD_BL_CTRL` 的网。

### 6.3 生成器为什么不能重跑（【事实】+【判断】修复点）

**实测**（在 `%TEMP%` 的整仓副本里跑，未污染工作区，见附录 A）：
```
$ python scripts/build-kicad-schematic.py
netlist refs with no symbol/sheet: ['VCC', 'J17']
RC=1
```
且 **rc=1 时一个文件都没写**（跑前跑后 8 份 .kicad_sch + 4 份 CSV/MD 的 SHA-256 全部不变）。

**两个阻塞的精确成因**（【事实】代码级）：

1. **`VCC` 不是伪引用**：`build-kicad-schematic.py:614-616` 的 `PSEUDO_REFS` 列了 `"-", "GND", "+12V", "+5V", "+3V3_DIG", "+3V3_RF", "VBAT", "PA_PWR_PWM", "RESET_BOARD", "LCD_BIAS", "GND_DIG", "GND_RF", "GND_PWR"` —— **没有 `VCC`**。而现行网表有 2 行以 `VCC` 为端点：`PA_DRAIN: VCC → Q1.D`（`netlist.csv` 对应 `build-netlist.py:139`）、`VCC: BT1.+ → VCC`（`build-netlist.py:186`）。⇒ `:1143-1152` 的 `unplaced` 收集到 `VCC` 就 `SystemExit`。
2. **`J17` 没有任何符号/图页**：`kicad-symbol-map.csv` 只映射到 `J1..J6`（`:43`，core）与 `J7..J16`（`:44`，SMA），`J17` 只在 `bom-interconnect.csv:4`（`J17-J22` 模块排针）和 pre-fab D-24 里出现。`sheet_of_ref()` 虽把 `J17..J24` 硬编码到 `interconnect`（`:760-762`），但**前提是 ref 已在 `ref_symbol` 里**——它不在，所以仍判 unplaced。

**【判断】修这两个阻塞本身是小改动**（1 行 `PSEUDO_REFS` + 1 行符号表），但**修完重跑会立刻把整套 22 个问题实例写进新图**，因为生成器的"器件模型"本身还是旧的（见 §6.6）。

### 6.4 `row coverage 181 vs 155` 量化（【事实】）

`kicad-row-coverage.csv` = 181 行（`status`: DRAWN 162 / PARTIAL 16 / NOTE 3）；`netlist.csv` = 155 行。差额 26 行的构成（按网名比对，我实跑）：

| 只在旧快照（9/26）里 | 行数 |
|---|---|
| `+12V_RELAY` | 7 |
| `+12V` | 3 |
| `IOEXP_RELAY_K1..K6` | 12（每个 2 行） |
| `IOEXP_SPARE_P0_6 / P0_7 / P1_0 / P1_2 / P1_3 / P1_4 / P1_5 / P1_6 / P1_7` | 9 |
| `FB_PULLDOWN` | 1 |
| `PA_PWR_PWM` | 1 |
| `TCA9535_INT` | 1 |
| **小计** | **35** |
| **只在新网表（10/17）里** | `+5V_RELAY` 7 · `GPIO12_TBD` 1 · `LCD_BL_DRV` 1 · `VCC` 2 = **11** |
| 同名网行数变化（净减） | `GND` 34→30（−4）· `+5V` 6→8（+2）· `+3V3_DIG` 5→6（+1）· `VBAT` 3→2（−1） ⇒ **−2** |
| **核对** | **181 − 35 + 11 − 2 = 155** ✅ |

**16 个 PARTIAL 行（=画了但没画对）里最要命的 3 类**：
1. `row 1/2`（`ADC_FWD`/`ADC_REV`）：`T1/T2` 的次级引脚在符号里不存在（"row pin token '1 (次级)' is not a pin of T1 (XFMR)"）⇒ **两条 SWR 检波网在原理图上没有真正连上**。
2. `row 16–21`（EC11_A/B/SW、I2C_SDA/SCL）：上拉行被合并到 `+3V3_DIG`，**上拉电阻的网络名丢失**（"the other end is net name +3V3_DIG"）。
3. `row 179/180`（`BUZZER_DRV`/`GPIO12_FB_PD`）：引用了 **`IOEXP_SPARE`（TCA9535 的脚）** 与 `PA_PWR_PWM` —— 两条网在现行网表里不存在。

**另外 3 个 NOTE 行**（`row 71` CW_KEY_SRC、`141/142` GND）是"标签级、无器件引脚"的合法记录 ✅。

### 6.5 手工改动的硬证据（【事实】）

`kicad-build-report.md:13` 记 `mcu-ui.kicad_sch` = **1968 行 / 76143 字节**；磁盘实际 = **1976 行 / 76641 字节**（mtime 2026-10-15 21:53:05）。⇒ 这份文件在**生成之后被人手改过**，而报告没重生成（因为生成器跑不动）。

手改的内容是什么？grep 显示 `mcu-ui.kicad_sch:13` 与 `:1745` 各有一条**文本注记**："2026-10-11 REV: EC11_A GPIO2→GPIO20 | LCD_BL=GPIO21 | GPIO12=SCOPE_TP … BUZZER LS1 REMOVED (not in this version)"。**但**：`U1=TCA9535`（`:1276,1862`）、`LS1`（`:1623,1945`）、`J_UART`（`:1723,1970`）、`PA_PWR_PWM`（`:770,1168`）**一个都没改**。

**【判断】这是最坏的一种"改"**：图面上写着"已改版"，图体里还是旧电路 ⇒ 谁打开这份图都会得到矛盾信息，而且 git 只显示 `Bin 76143 -> 76641 bytes`（`git show --stat 3770717`），review 时完全看不出改了什么。

### 6.6 要修好需要做什么（按工作量排序，【判断】）

> 前置：**所有对 `.kicad_sch` 的手改都应停止**，一律回到"改源 → 重跑"。

| # | 动作 | 工作量 | 前置 | 说明 |
|---|---|---|---|---|
| 1 | `PSEUDO_REFS` 加 `"VCC"`（`build-kicad-schematic.py:614`） | **10 分钟** | — | 1 行 |
| 2 | 解决 `J17` 的**双重身份**：把 ATU 控制连接器改名（如 `J_ATU_CTRL`），把 `J17-J22` 保留给模块排针；或反之 | **0.5 天** | 先定 D-24 与 BOM 哪个是准 | 这是 §5.3 M-3，属设计决策不是脚本 bug |
| 3 | 给 `J17`（或改名后的连接器）在 `kicad-symbol-map.csv` 补一行符号 + 图页 | **10 分钟** | #2 | 依赖 #2 |
| 4 | 清 `kicad-symbol-map.csv` 的旧器件行：`U1→CA-DV8008N 符号`、删 `U2`(ULN2003A)、删 `U11`(Boost)、删 `LS1`、删 `J_UART`、删 `R12`、删 `K1..K6` 的 `DC-12V` 型号、`R_sense` 改 50 Ω/1 W、`R_VBAT` 改 30k、删 `+12V`/`PA_PWR_PWM`/`IOEXP_*` 标签 | **0.5–1 天** | — | 30 行表，**这是真正的"源"** |
| 5 | 同步生成器内嵌模型：`SHEETS` 删 `U2`/`R_RLY*`/`U11`/`LS1`/`J_UART`/`R12`（`:524-545`）、`DERIVED` 删 `R_RLY1..6`（`:579-581`）、`VALUE_FIX` 删 `R_sense_F: "1kohm"`（`:625`）、`VALUE_EXTRA` 删 `R_sense_R`（`:640`） | **0.5 天** | #4 | 与 #4 一起做，否则重跑会崩在"符号不存在" |
| 6 | 新增 `CA-DV8008N` 的内嵌符号（8 通道低边 + COM/VCC/A0-A2/GND），并把继电器符号改为 `HK4100F-DC5V-SHG`（线圈 5 V/125 Ω） | **0.5 天** | — | 现在 `SYMBOLS` 里根本没有 CA-DV8008（`defsym` 列表 `:281-472`） |
| 7 | 修 `build-netlist.py` 的 4 处旧值 + 补 GPIO21/GPIO12 网（`:56,62,66-67,99-100`） | **0.5 天** | — | 与 §1.4 同一批 |
| 8 | 重跑 `build-netlist.py` → `build-kicad-schematic.py` → `check-kicad-schematic.py` 三连，直到 `rc=0` | **2 小时** | #1–#7 | 行覆盖会自动回到 155=155 |
| 9 | 处理 16 个 PARTIAL：给 `XFMR` 符号补"次级"引脚、拆开上拉行的网络名、删 `BUZZER_DRV`/`GPIO12_FB_PD` 行 | **1–2 天** | #8 | 这些是**生成器建模缺陷**，不是数据问题 |
| 10 | 把 8 份 `.kicad_sch` 从 `hardware/schematic/` 迁到各模块 `schematic/`（或反过来改 `docs/02` 与 `hardware/README §4` 的归属规则） | **0.5 天** | — | 现位置**违反** `docs/02:190,259` 与 `hardware/README.md:120` 的"`<模块>/schematic/`"规则 |
| 11 | 加 CI（GitHub Actions 或 pre-commit）跑 3 个 build + 2 个 check | **0.5 天** | #8 | 见 §7.3 |

**合计约 4–6 人日**（不含 #2 的设计决策时间）。**【判断】若只做 #1+#3（20 分钟）强行让生成器跑通，结果会是一次"把 22 个旧器件写死在全新图里"的重生成——比现在更糟**，因为现在的旧图至少 mtime 能提示"这是旧货"。

---

## 7. 生成器健康度

### 7.1 脚本清单（【事实】）

| 脚本 | 行数 | 输入 | 输出 | 依赖 | 自检 | 实测 rc |
|---|---|---|---|---|---|---|
| `build-netlist.py` | 355 | **Python 内嵌数据**（`build()` `:47-257`，含 docs 章节号作为"来源"字段） | `hardware/bom/netlist.csv`、`hardware/schematic/netlist.csv`、`netlist.md` | 标准库（csv/io/os） | ❌ 仅打印行数 | **0** ✅ |
| `build-lceda-import-pack.py` | 412 | **Python 内嵌数据**（`build_rows()` `:49-326`） | 9 份 `bom-*.csv` + `bom-summary.csv` + `bom.md` | 标准库 | ❌ | **0** ✅ |
| `build-kicad-schematic.py` | 1440 | `hardware/schematic/netlist.csv` + `kicad-symbol-map.csv` + `hardware/bom/bom-*.csv` | 8 份 `.kicad_sch` + `kicad-net-map.csv` + `kicad-row-coverage.csv` + `kicad-build-report.md` | 标准库（含 hashlib 做稳定 UUID） | ⚠️ 内部一致性断言（`:1143-1152`，即当前阻塞点） | **1** 🔴 |
| `check-kicad-schematic.py` | 571 | 8 份 `.kicad_sch` + 4 份清单 + `tests/` 6 个 fixture | 无（退出码） | 标准库 | ✅ 有对照组（`check_control_group()` `:379-400`，5 个 bad fixture 各自期望错误码） | **1** 🔴 |
| `verify-atu-lc-combos.py` | 302 | 无（纯计算 + 与 README 判据对照） | 无 | 标准库（cmath/itertools/math） | ✅ 42 项 check | **0** ✅ |
| `check-repo-separation.ps1` | — | 两仓路径 | 无 | PowerShell | ✅ | 未跑（见附录 C） |

**关键耦合缺失（【事实】）**：`build-netlist.py:20` 的 docstring 写 *"Run: python scripts/build-lceda-import-pack.py (this file is imported by it)"*，但 `build-lceda-import-pack.py` 里**没有任何 `netlist` 字样、没有 subprocess、没有 import**。⇒ **"一条命令生成全套"是假的**：必须按 `build-netlist` → `build-kicad-schematic` → `build-lceda` 的隐式顺序手工跑，且没人强制这个顺序（`scripts/README.md:45-57` 也没写顺序）。

### 7.2 幂等性实测（【事实】，在 `%TEMP%` 副本里跑）

| 脚本 | 跑前 → 跑后 | 结论 |
|---|---|---|
| `build-netlist.py` | 21 个派生文件 SHA-256 **全部不变** | ✅ **逐字节幂等** |
| `build-lceda-import-pack.py` | 同上，全部不变 | ✅ **逐字节幂等** |
| `build-kicad-schematic.py` | rc=1，**一个文件都没写**（含 `kicad-build-report.md` 不变） | ⚠️ 幂等但**不可用**：失败即"无操作"，不会留下半成品 ✅（这点做得好） |

**【判断】** 幂等性设计是合格的（UUID 用稳定种子、不写时间戳，`scripts/README.md:57` 的声明我实测成立）。**问题不在幂等，在"输入源已经过期"**。

### 7.3 结构性缺陷（【判断】，每条附事实依据）

| # | 缺陷 | 事实依据 | 影响 |
|---|---|---|---|
| G-1 | **没有单一事实源（SSOT）**：连接关系与 BOM 都是 Python 内嵌字面量 | `build-netlist.py:47-257`、`build-lceda-import-pack.py:49-326` | docs/05 改一处要人肉改两处脚本；实测已漂移 4 处（§1.4） |
| G-2 | **没有 CI**：`.github/` 只有 `ISSUE_TEMPLATE/.gitkeep` 与 `OVERVIEW.md` | `ls .github` | rc=1 的自检器可以长期红灯而无人知；HEAD 提交（10/17）正是"改了生成器、没跑、也没人拦"的样本 |
| G-3 | **派生文件与生成器不同步被 git 掩盖** | `git show --stat 3770717`：`mcu-ui.kicad_sch` 显示 `Bin 76143 -> 76641 bytes` | 二进制化的 `.kicad_sch`（单行 S-expr）让 diff 不可读 ⇒ review 失效 |
| G-4 | **生成器报告的汇总表自相矛盾** | `kicad-build-report.md:23-26`：DRAWN 162 + DRAWN_PARTIAL 0 + NOTE 3 = **165 ≠ total 181**；而同文件 `:168-186` 逐行表里有 **16 个 PARTIAL** | 报告不可信；`DRAWN_PARTIAL` 应为 16 |
| G-5 | **生成器 docstring 谎报耦合** | `build-netlist.py:20` vs `build-lceda-import-pack.py`（无 netlist 引用） | 新手会以为跑一个就够 |
| G-6 | **8 份骨架放错目录** | 在 `hardware/schematic/`；而 `docs/02:190,259`、`hardware/README.md:120`、`docs/04:545` 都要求 `<模块>/schematic/` | 与"目录归属唯一权威"冲突；也让"每模块自包含"的模块化承诺落空 |
| G-7 | **无第三方依赖 ✅** | 5 个 py 全部只用标准库（import 清单见附录 A） | 好事：任何装了 Python 3 的机器可跑；但也意味着**没借用任何 KiCad 官方库**，符号全靠内嵌 15 个 `defsym`（`build-kicad-schematic.py:281-472`），覆盖不了真实器件 |

---

## 8. 文档体系：权威源地图与矛盾清单

### 8.1 权威源地图（【事实】依据 `docs/README.md:14-40` 的表格与仲裁规则）

| 你要查什么 | 查哪里 | 权威性 | 现状 |
|---|---|---|---|
| **引脚 / 连接器 / 协议边界** | `docs/05-hw-sw-interface-contract.md` | ★ 唯一权威 | 🟠 §1.2/§1.3/§3.1/§3.2/§4.2/§8 有多处过期（§8.3 矛盾表） |
| **技术指标（功率/频率/SWR/成本）** | `docs/00-project-upgrade-plan.md` | ★ 指标唯一权威 | 🔴 **功放设计点已过期**（`:16` 8.4 V/16.3 Ω，vs `docs/04:85-93` 7.4 V/12.6 Ω） |
| **硬件模块划分与互联** | `docs/04-hardware-architecture.md` | ★ 唯一权威 | 🟠 §2 模块清单、§3.4 继电器 12 V、§3.7.6 降驱动、§5 风险 #9 均过期 |
| **文件该放哪** | `docs/02-repository-layout.md` | ★ 唯一权威 | ✅（但 8 份骨架违反它，§6.6 #10） |
| **固件分层/组件** | `docs/03-software-architecture.md` | ★ 唯一权威 | 本次未逐章核（超出硬件审计范围） |
| **许可** | `docs/08-licensing-and-compliance.md` + `LICENSING.md` + `LICENSES/` | ★ 唯一权威 | 本次未核 |
| **为什么这样决策** | `docs/adr/`（10 份） | 决策史 | 🔴 索引缺 ADR-0009；ADR-0003 状态未改 |
| **GPIO 分配的独立复核** | `docs/17-gpio-allocation-audit.md` | 审计（**非权威**） | ✅ 自身有"2026-10-11 二次取代声明"（`:8-22`）；但 131 处旧词、§13 换板评估已过期 |
| **ATU 逐脚接法 / 掩码极性** | `hardware/atu-module/relay-wiring.md`（自声明 `:54-61`） | 模块级权威（本文范围内） | 🟠 与 ADR-0009 冲突；TL;DR `:76` 未标作废 |
| **继电器组合 ↔ 固件掩码** | **私有固件仓** `drv_relay.h` / `atu_match.h`（`relay-wiring.md:59` 已如此声明） | ★ 跨仓权威 | ✅ 与硬件位序一致（位号命名不同，§4.3） |
| **现场天线阻抗** | `hardware/antenna/test/2026-10-field-measurements.md` + `impedance-table.md` | 实测 | ✅（但频率/高度未记录，`:42-45`） |
| **打样前检查** | `hardware/pre-fab-checklist.md` | 操作清单（非权威） | 🟠 4 条失效（§5.5） |
| **派生数据（禁手改）** | `hardware/bom/*.csv`、`hardware/schematic/netlist.*`、`kicad-*.csv`、`kicad-build-report.md` | ❌ 派生 | 🔴 与源不同步（§1.4、§6） |
| **真正的"源"（但无人声明）** | `scripts/build-netlist.py` 内嵌表 + `hardware/schematic/kicad-symbol-map.csv` | ⚠️ 事实上是源 | 🔴 无权威标签、无评审流程、含旧器件 |

**【判断】这张表暴露的结构问题**：仓里有 **3 个不同的"事实源"**（`docs/05`、`build-netlist.py`、`kicad-symbol-map.csv`），而 `docs/README.md:26-36` 的仲裁规则**只覆盖前两个中的文档层**，**完全没有提到生成器数据与 `kicad-symbol-map.csv` 的权威地位**。⇒ 建议在 `docs/README.md` 的仲裁表里补一行："派生数据的源 = 生成器内嵌表与符号映射表，二者必须由 `docs/05` 驱动"，并把它纳入 §6 变更流程。

### 8.2 派生文件清单（【事实】，**本次审计只记录不修**）

| 文件 | 由谁生成 | 当前 mtime | 备注 |
|---|---|---|---|
| `hardware/bom/bom-*.csv`（9）、`bom-summary.csv`、`bom.md` | `build-lceda-import-pack.py` | 10-17 | ✅ 与脚本同步 |
| `hardware/bom/netlist.csv`、`hardware/schematic/netlist.csv`、`netlist.md` | `build-netlist.py` | 10-17 | ✅ 与脚本同步（但脚本数据过期） |
| `hardware/schematic/*.kicad_sch`（8） | `build-kicad-schematic.py` | 7 份 09-26 / 1 份 10-15（手改） | 🔴 不可重生成 |
| `hardware/schematic/kicad-net-map.csv`、`kicad-row-coverage.csv` | 同上 | 09-26 | 🔴 旧快照 |
| `hardware/schematic/kicad-build-report.md` | 同上 | 10-15 | 🔴 与磁盘不符（§6.5） |
| `hardware/schematic/kicad-symbol-map.csv` | **手写**（不是派生！） | 09-26 20:49 | ⚠️ 被生成器当输入，实为"隐形的源" |
| `hardware/schematic/IMPORT-TO-LCEDA.md` | 半派生（10-17 改过） | 10-17 | 引用了 LCEDA 导入能力调研 |

### 8.3 互相矛盾清单（【事实】，双方均给 file:line）

| # | A 方说 | B 方说 | 严重度 |
|---|---|---|---|
| X-1 | `docs/05:503` "继电器线圈驱动 **12 V**，16.7 mA/只，6 只同吸 <110 mA" | `docs/05:606` "5 V 主轨…**继电器线圈 0.24 A**"（同文件 100 行后） | 🔴 |
| X-2 | `docs/05:517` "GPIO2 **未分配**…该脚被 `EC11_A` 占用" | `docs/05:106` "GPIO2 = `BOARD_ADC_CH2`（2026-10-11 释放）"（同文件 411 行前） | 🔴 |
| X-3 | `docs/05:521-524` "ADC1 的 5 通道已用 3 个…**没有任何可用的模拟输入余量**" | `docs/05:370` "**ADC 余量 2**（ADC1_CH2）" | 🟠 |
| X-4 | `docs/04:73` "E 类按 **8.4 V 定点**设计" | `docs/04:85` "E 类设计点…**由 8.4 V 改为 7.4 V 标称**"（同文件 12 行后） | 🔴 |
| X-5 | `docs/04:349`／`docs/04:442` "④ 满电 8.4 V 的功率超限**由固件降 Si5351 驱动**处理" | `docs/04:104,126` "✅ **甲方案：接受 ≈3.22 W、不降驱动**" | 🔴 |
| X-6 | `docs/00:16`（★指标权威）"E 类按 **8.4 V 定点**（R_opt≈16.3Ω/C1≈0.51nF/L≈3.7µH）" | `docs/04:89-92` "R_opt **12.6 Ω**/C1 **0.65 nF**/L **2.8 µH** @7.4 V" | 🔴 |
| X-7 | `relay-wiring.md:76`（TL;DR）"⛔ **必须补的硬件**：ULN2003A IN1–IN6 各加 10 kΩ 下拉" | `pre-fab-checklist.md:127` "D-20 → ✅ **作废（2026-10-11）**…不再需要这 6 只电阻" | 🔴 |
| X-8 | `atu-module/README.md:88` "R_sense **初始 1 kΩ**" | 同文件 `:106,118` "`R_term` = **50 Ω / 1 W**（≠50 Ω 则方向性崩塌）" | 🔴 |
| X-9 | `mcu-ui-module/README.md:36` "电池电压分压（GPIO3，**22k/9.1k**）" | `docs/05:774`（#7d）"**R1 = 30k**"＋`bom-mcu-ui-module.csv:18` 30k | 🔴 |
| X-10 | `pre-fab-checklist.md:83`（C-01）"⛔ **无任何原理图文件**" | `hardware/schematic/*.kicad_sch` ×8 存在（09-26 起） | 🟠 |
| X-11 | `pre-fab-checklist.md:140`（E-01）"与**现行方案（TCA9535 + ULN2003A）**冲突" | `docs/05:153` "改用 **CA-DV8008N**" | 🟠 |
| X-12 | `docs/adr/README.md:69` "ADR-0003 … **已接受**" | `ADR-0009:4` "**取代 ADR-0003**" | 🟠 |
| X-13 | `docs/05:108` "共享总线：Si5351 + **TCA9535**" | `docs/05:371` "I²C（Si5351 + **CA-DV8008N `0x28`**）" | 🟠 |
| X-14 | `docs/01:149-150`（项目概述）"继电器 HK4100F-DC-**12V**…驱动 **TCA9535→ULN2003A（COM 接 +12V）**" | `docs/05:153-160` | 🟠 |
| X-15 | `docs/04:469` 续航表"ATU 继电器 **0.100 A**" | `docs/04:341` "继电器线圈（**6×40 mA = 240 mA**）" | 🟠 |
| X-16 | `build-netlist.py:190` "5V 主轨…**最大 0.3A**" | `docs/05:606` "**0.54 A**" | 🟠 |

> 只列 16 条（要求 ≥3）。**其中 X-1/X-4/X-5/X-6 是同一类错误**（2026-10-11 的方案变更只改了一半），**X-2/X-9/X-11/X-13/X-16 是"改了权威没改派生/引用"**。

### 8.4 文档编号完整性（【事实】）

`docs/` 实有：`00,01,02,03,04,05,06,07,08,15,17` + `CONSISTENCY-FIXES.md` + `README.md`（13 份），ADR 10 份（9 条 + README）。
**缺号**：`09,10,11,12,13,14,16`（7 个）。已知被正文引用的缺号：`docs/13-emc-and-spurious-suppression.md`（`docs/04:67,564` 与 pre-fab C-14 `:96` 都指向它，**文件不存在**）。**【判断】** 建议在 `docs/README.md` 里给缺号一个"未计划/已废弃"的说明，否则每个新读者都会去 `ls docs/13*`。

---

## 9. 与固件的契约对拍（`docs/05` ⇄ `board_pins.h`）

### 9.1 逐引脚矩阵（【事实】）

固件侧唯一权威：`ARDF-MeshTuneFox80-firmware/components/bsp_board/include/board_pins.h`（`:44-137`）+ 引脚表 `src/bsp_board_pins.c:62-88`。

| GPIO | 硬件仓 `docs/05 §2.2` | 固件 `board_pins.h` | 一致？ | 备注 |
|---|---|---|---|---|
| 0 | `BOARD_ADC_FWD` ADC1_CH0（`:104`） | `BOARD_ADC_FWD GPIO_NUM_0`（`:44`） | ✅ | |
| 1 | `BOARD_ADC_REV` ADC1_CH1（`:105`） | `BOARD_ADC_REV GPIO_NUM_1`（`:45`） | ✅ | |
| 2 | `BOARD_ADC_CH2`（备用，本版释放）（`:106`） | `BOARD_ADC_CH2 GPIO_NUM_2`（`:49`）；**未进 `s_pin_map`**（`:46-48` 注释） | ✅（功能）／⚠️ 未登记 | `docs/05:421` 说"owner=drv_analog 仅启用时"，固件 `BSP_PIN_*` 枚举**无 ADC_CH2**（`bsp_board_pins.h:45-51`） |
| 3 | `BOARD_ADC_VBAT`（`:107`） | `BOARD_ADC_VBAT GPIO_NUM_3`（`:50`） | ✅ | 但比值跨仓不一致（§3.5） |
| 4 | `BOARD_I2C_SDA`（`:108`） | `BOARD_I2C_SDA GPIO_NUM_4`（`:56`） | ✅ | 硬件文档仍写"Si5351 + TCA9535" |
| 5 | `BOARD_I2C_SCL`（`:109`） | `BOARD_I2C_SCL GPIO_NUM_5`（`:57`） | ✅ | |
| 6 | `BOARD_LCD_SCK`（`:110`） | `BOARD_LCD_SCK GPIO_NUM_6`（`:71`） | ✅ | |
| 7 | `BOARD_LCD_MOSI`（`:111`） | `BOARD_LCD_MOSI GPIO_NUM_7`（`:72`） | ✅ | |
| 8 | `BOARD_EC11_B`（strapping，10 kΩ）（`:112`） | `BOARD_EC11_B GPIO_NUM_8`（`:134`） | ✅ | |
| 9 | 保留 BOOT，启动后 `KEY_USER`（`:118`） | `BOARD_KEY_USER GPIO_NUM_9`（`:155`） | ✅ | |
| 10 | `BOARD_LCD_DC`（`:113`） | `BOARD_LCD_DC GPIO_NUM_10`（`:73`） | ✅ | |
| 11 | ❌ 不可用（VDD_SPI）（`:119`） | 未定义（注释 `:167`） | ✅ | |
| 12 | `BOARD_SCOPE_TRIG`（示波器打点）（`:114`） | `BOARD_SCOPE_TRIG GPIO_NUM_12`（`:103`） | ✅ | ⚠️ 文档正文另用旧名 `BOARD_SCOPE_TP`（`:286,300,429,446`；`docs/05:114` 已声明以固件名为准） |
| 13 | `BOARD_EC11_SW`（`:115`） | `BOARD_EC11_SW GPIO_NUM_13`（`:137`） | ✅ | |
| 18/19 | 原生 USB（`:120`） | 未定义（注释 `:167`） | ✅ | |
| 20 | `BOARD_EC11_A`（`:116`） | `BOARD_EC11_A GPIO_NUM_20`（`:133`） | ✅ | 生成器仍写 GPIO2 |
| 21 | `BOARD_LCD_BL`（`:117`） | `BOARD_LCD_BL GPIO_NUM_21`（`:84`）+ `_POWER_ON_LEVEL 0`（`:86`） | ✅ | 生成器/网表缺此网 |
| — | Si5351 `0x60`：**`docs/05` 全文未写这个地址**（我 grep 过，只有 `mcu-ui-module/README.md:32` 写了） | `BOARD_SI5351_ADDR 0x60`（`board_pins.h:60`） | ✅（值）／🟠 权威文档缺载 | 建议 `docs/05 §2.3` 补一行 |
| — | CA-DV8008N `0x28`（`:154`） | `BOARD_CA_DV8008_ADDR 0x28`（`:66`） | ✅ | |
| — | 通道 OC1..OC6 ↔ K1..K6（`:158`） | `IOEXP_RELAY_K1..K6 = 0..5`（`:181-186`） | ✅ | |

**统计：16 个物理引脚 + 2 个 I²C 地址 + 6 个通道映射，引脚号/地址/位序层面 0 处不一致。**

### 9.2 契约面上的 5 处不一致（【事实】+【判断】）

| # | 位置 | 硬件仓 | 固件仓 | 性质 |
|---|---|---|---|---|
| F-1 | GPIO12 名称 | `BOARD_SCOPE_TP`（`docs/05:286,300,429,446`）；`SCOPE_TRIG`（`:114`） | `BOARD_SCOPE_TRIG`（`board_pins.h:103`） | **命名债**（脚号一致，文档已声明以固件为准） |
| F-2 | GPIO2（ADC1_CH2） | 列为 `drv_analog` 的所有物（`docs/05:421`） | **未登记**（无 `BSP_PIN_ADC_CH2`） | **契约多于实现**；将来启用要改固件枚举 |
| F-3 | **hw_rev=2 网关板（SuperMini）** | 硬件仓**无任何 rev2 引脚文档**（我 grep 了 `docs/05`/`04`/`17` 的 `rev2|hw_rev|网关|SuperMini`，只有 `docs/17 §13` 的"未采纳换板评估"） | 固件有完整的 rev2 维度：`BOARD_EC11_A_REV2 = GPIO2`、`BOARD_EC11_SW_REV2 = GPIO4`（`board_pins.h:148-149`）、`s_pin_map` 每项带 `gpio_rev2` 与 `valid_mask`（`bsp_board_pins.c:40-88`）、能力矩阵（`bsp_board_caps.h:17-20`） | **固件单方面存在的硬件版本** ⇒ 网关板的引脚契约在硬件仓查不到 |
| F-4 | 电池分压比值 | 30k/9.1k = 0.2327（`docs/05:774`） | `R1 = 22000`（`drv_analog_calc.h:66`） | **数值不一致**（§3.5）⇒ 功能性 bug |
| F-5 | ATU 电容位号 | C3/C4/C5（`relay-wiring.md:363-372`） | C1/C2/C3（`atu_match.h:22-24`） | **命名债**（位序一致） |

### 9.3 另外 3 处"固件有、硬件没有"的契约面（【判断】，只记录）

1. **`BSP_CAP_*` 能力矩阵**（`bsp_board_caps.h:126-150`）把"板子有哪些外设"分成 6 类能力，硬件仓没有对应表述 ⇒ 将来出 hw_rev=3 时无硬件侧依据。
2. **遥测帧 16 字节布局**（`docs/05:682-693`）已与固件 `comm_console.h` 对齐 ✅，但 **NTC 温度字段删除后的"无过温保护"**（`pa-module/README.md:107`）在硬件仓的 §7 待冻结清单里**没有条目**（只在模块 README 里）。
3. **`SWR` 门限 3.0（线上 300）/ 滞回解除 2.5（线上 250）**（`docs/05:674-680`）与固件 `rf_swr.h:77` 一致 ✅ —— 这是**做得最好的一条跨仓契约**（连"中控端不要拿 2.5 当告警线"都写了）。

---

## 10. 风险登记表

> 严重度：**P0** = 不修就会做错板/固件不认/整机不出图；**P1** = 架构不一致，投板前必须定；**P2** = 可制造性/可维护性缺口；**P3** = 记录性。
> "证据"列均为 file:line；"影响"列是【判断】。

| ID | 严重度 | 风险 | 证据 | 影响 | 建议 |
|---|---|---|---|---|---|
| R-01 | **P0** | ATU 拓扑双规格（ADR-0009 Accepted 但零落地） | `ADR-0009:3-4,29-47,53-54` ↔ `relay-wiring.md:69-77,348-388`、`docs/04:227`、`bom-atu-module.csv:4-9`、固件 `atu_match.h:14-28,59-63` | 出图/出料/固件三方各按一套；投板即锁定错误拓扑 | **先裁定**：采纳 ADR-0009（则 §6.6 全表 + BOM + 固件契约都要改）或显式撤回（把 ADR-0009 改"已废弃"并在索引登记）。**在此之前不得投板** |
| R-02 | **P0** | KiCad 骨架含 22/109 问题实例且不可重生成 | §6.1–6.3 | 无法出图；照现图打样会装 ULN2003A/TCA9535/12 V 继电器 | 按 §6.6 的 #1–#8 顺序修 |
| R-03 | **P0** | 生成器/派生网表的 4 处旧引脚（EC11_A、GPIO12、GPIO20/21、LCD_BL） | `build-netlist.py:56,62,66-67,99-100` | 照网表接线会把 EC11_A 接到 ADC 脚、背光无驱动、GPIO12 悬空 | 与 R-02 同批修（#7） |
| R-04 | **P0** | 功放设计点 8.4 V/7.4 V 两套数字 | `docs/00:16`、`hardware/README.md:9,102`、`pa-module/README.md:12,19`、`pre-fab:29` ↔ `docs/04:85-93`、`docs/05:771` | 匹配网络/LPF/C1 的取值差 ~30%，无法出图 | 以 `docs/04:85` 为准，逐处改（含 ★指标权威 `docs/00:16`） |
| R-05 | **P0** | 电池分压 22 kΩ ↔ 30 kΩ 跨仓漂移 | `docs/05:774` ↔ 固件 `drv_analog_calc.h:66-68`；`mcu-ui-module/README.md:36`、`kicad-symbol-map.csv:30` | 满电读成 6.68 V ⇒ 开机即低电告警、禁高功率发射 | 固件改 `DRV_ANALOG_BATT_R1_OHM 30000`；硬件仓同步 3 处旧值 |
| R-06 | **P0** | `R_sense` 仍 1 kΩ（BOM/网表/符号表） | `bom-atu-module.csv:11`、`build-netlist.py:156,162`、`kicad-symbol-map.csv:31` | 桥不平衡、方向性崩塌、`V_det` 削顶 | 三处改 50 Ω/1 W（派生物随生成器） |
| R-07 | P1 | 契约级 12 V / 升压 / PA_PWR_PWM 残留（§2.4-b/c） | `docs/05:503-505,634-639`、`docs/04:51,261-301,469,500,567`、`interconnect/README.md:15,36,40,42,55`、`core-board/README.md:14,22,29,31`、`atu-module/README.md:22-77,144,154-155,165`、`validation/stage-1:8-60` | 买错料/画错图/测错项 | 按"权威 → 模块 → 验证"三层清，给 `atu-module/README.md §3` 加总声明（照 relay-wiring 的做法） |
| R-08 | P1 | `J17` 位号双重定义 | pre-fab D-24（`:130`）↔ `bom-interconnect.csv:4` | 采购/画图/接线各按一套；也是生成器阻塞源 | 改名或合并，二者取一 |
| R-09 | P1 | 耦合器位置（输入侧 vs 输出侧）未定 | `docs/05:624` ↔ `docs/05:550-561`、`relay-wiring.md:200`、`build-netlist.py:152` | `SWR>3 禁发` 的判据与标定基准不明 | 定为输入侧（3 处已如此），改 `:624` 一句话 |
| R-10 | P1 | 文档/派生文件互相矛盾 16 条（§8.3） | 见 §8.3 | 读者无法判断现行方案 | 先修 🔴 的 8 条（X-1/2/4/5/6/7/8/9） |
| R-11 | P1 | ADR 索引缺 ADR-0009、ADR-0003 状态未更 | `docs/adr/README.md:65-74` | 违反"已接受即必须遵守"（`README.md:29`） | 补索引 + 改状态 |
| R-12 | P1 | KiCad 骨架目录违反 `docs/02` | `hardware/schematic/*.kicad_sch` ↔ `docs/02:190,259`、`hardware/README.md:120` | 模块化承诺落空 | 迁移或改规则（§6.6 #10） |
| R-13 | P1 | 无 CI，自检可长期红灯 | `.github/`（无 workflows） | 本次"改了生成器没跑"的提交就是证据 | 加 GH Actions：3 build + 2 check |
| R-14 | P1 | `docs/00`（指标权威）过期 | `docs/00:16,18` | 所有"以 00 为准"的仲裁都会得出 8.4 V | 改 `:16`（7.4 V 口径）与 `:18`（30k 的理由） |
| R-15 | P2 | BOM LCSC 全待查（2/81 已填） | `bom-*.csv`；`bom/README.md:177-188` | 无法下单 | 人工回填（F-05） |
| R-16 | P2 | BOM 缺检波 C-R-C / 100 kΩ 泄放 | `bom-atu-module.csv:2-15` | 检波器不完整 | 补 3 行（2×10 nF、1×68 kΩ、1×100 kΩ） |
| R-17 | P2 | BOM 用范围写法、与网表无共同命名空间 | §5.2 | 自动覆盖检查失效 | 生成器展开逐位号 |
| R-18 | P2 | `X1` 重复、汇总不去重、14 行无位号 | `bom-core-board.csv:6` + `bom-mcu-ui-module.csv:23`；`bom-summary.csv` | 多买/漏买 | 生成器去重 + 位号必填校验 |
| R-19 | P2 | `U8`（244）模块归属冲突 | `bom-mcu-ui-module.csv:8` ↔ `pa-module.kicad_sch` | 插件位置不明 | 定为 pa-module（它在 PA 驱动链上） |
| R-20 | P2 | LPF 器件值 TBD | `lpf-module.kicad_sch`、pre-fab C-07（`:89`） | LPF 无法下单 | 按 `docs/04:187-194` 的判据算出 3 阶椭圆参数 |
| R-21 | P2 | 无装配顺序/DNP 清单/测试点表 | §5.4 | 贴片与产测无依据 | 新增 1 份 `hardware/assembly-order.md`（**本次不做**） |
| R-22 | P3 | 生成器报告汇总表算错（165≠181） | `kicad-build-report.md:23-26` | 报告不可信 | 随重生成自动修 |
| R-23 | P3 | `build-netlist.py:20` docstring 谎报被 import | 同 | 误导 | 1 行 |
| R-24 | P3 | `docs/13` 被引用但不存在 | `docs/04:67,564`、pre-fab C-14 | 每条引用都指向空洞 | 补号或改指向 |
| R-25 | P3 | `pre-fab` C-01/E-01/E-06 已失效 | §5.5 | 无效工作 | 清单重开时修 |

---

## 11. 建议的下一步（按性价比排序）

> 排序判据 = **"消除的风险 ÷ 工作量"**。每项都标了前置与预估。

| 序 | 动作 | 消除风险 | 工作量 | 前置 |
|---|---|---|---|---|
| **①** | **裁定 ADR-0009**（采纳 or 撤回），并按裁定在 `docs/adr/README.md` 补索引、改 ADR-0003 状态 | R-01、R-11 | **0.5 h（裁定）+ 0.5 h（落索引）** | 需项目所有者拍板（拓扑变更属决策，不是文档修正） |
| **②** | **统一功放设计点为 7.4 V**：改 `docs/00:16`（★权威）+ `hardware/README.md:9,102` + `pa-module/README.md:12,19` + `pre-fab:29` + `docs/04:73` | R-04、R-14（部分） | **2 h** | 无（`docs/04:85-93` 已有完整算式） |
| **③** | **修 §8.3 里 8 条 🔴 矛盾**：`docs/05:503-505`、`:517`、`:634-639`、`:108`；`docs/04:51,469,500`；`atu-module/README.md:55-77,88,144,154-155`；`relay-wiring.md:76`；`mcu-ui-module/README.md:36` | R-07、R-10 | **4–6 h** | ①（ATU 相关条目要等裁定） |
| **④** | **让生成器活过来**：`PSEUDO_REFS += "VCC"`、`J17` 改名/补符号、清 `kicad-symbol-map.csv` 旧行、清生成器内嵌旧器件、修 `build-netlist.py` 4 处旧引脚 | R-02、R-03 | **1.5–2 人日** | ③（数据先对，再重生成） |
| **⑤** | **重跑三连并让自检回绿**（netlist → kicad → check），把 16 个 PARTIAL 作为独立工单（生成器建模缺陷） | R-02、R-22 | **2–3 人日**（含 PARTIAL） | ④ |
| **⑥** | **加 CI**（3 build + 2 check + “派生文件与生成器一致”断言） | R-13 | **0.5 人日** | ⑤（先绿再上锁） |
| **⑦** | **补标定与放行判据**：在 `pre-fab-checklist` F 组加一条“功率/SWR 标定表已产出并回填固件” | §3.4 的“占位标定”风险 | **0.5 h（写判据）+ 实测另计** | 需真机 |
| **⑧** | **修 BOM**：`R_sense` 50 Ω、补 3 行检波 RC、`U8` 归属、`X1` 去重、逐位号展开 | R-06、R-16~R-19 | **0.5 人日**（多数随生成器） | ①（ATU 拓扑定了才不会白改） |
| **⑨** | **补 `docs/02` 的生成器权威声明**：仲裁表加一行“派生数据源 = 生成器内嵌表 + 符号映射表，受 `docs/05` 驱动”；并把 `hardware/schematic/` 的位置规则写进 `docs/02` | §8.1 的结构性缺陷、R-12 | **1 h** | 无 |
| **⑩** | **把网关板（hw_rev=2）的引脚契约补进硬件仓**：或在 `docs/05` 加一节“rev2 变体”，或声明“rev2 不在本仓范围” | F-3（固件单方面的硬件版本） | **2 h（写）** | 需确认网关板是否仍要维护 |

> **不建议现在做的事**：① 手工修 `.kicad_sch`（会被下次重生成覆盖，且是二进制 diff）；② 逐条清理 `docs/17` 的 131 处旧词（它已有自己的取代声明，属低收益）；③ 改 `docs/01`（概述性、非权威，改与不改都不影响决策）。

---

## 附录 A · 复核记录（可复现）

**A.1 只读声明与 git 状态**
```
审计前： git status --short  →（空）
         git rev-parse --abbrev-ref HEAD → main
         git log --oneline -1 → 3770717 docs(hw): BOM/网表生成器数据向 docs/05 同步…
           git rev-list --count HEAD → 59
审计中： 只运行了：读文件 / grep / Select-String / 2 个只读脚本 / 1 次 %TEMP% 副本内的写入
审计后： git status --short  →（空）
```
**工作区在审计前后均干净；本次只新增本文与 `docs/README.md` 的一行索引。**

**A.2 脚本实跑（只读脚本，直接在工作区跑）**
| 命令 | rc | 输出要点 |
|---|---|---|
| `python scripts/check-kicad-schematic.py` | **1** | 8 份逐份 PASS；`FAIL row coverage has 181 rows, netlist.csv has 155`；对照组 6/6 PASS；`SUMMARY … problems=1` |
| `python scripts/verify-atu-lc-combos.py` | **0** | `RESULT: all checks passed`；附 `[NOTE] README '50-j1110 / 47uH / SWR<1.8' is NOT reachable with any of the 64 combinations` |

**A.3 生成器实跑（在 `%TEMP%\hw-audit-copy` 整仓副本里，robocopy 排除 `release/ .git __pycache__`，150 个文件）**
| 命令 | rc | 输出要点 | 跑前=跑后？ |
|---|---|---|---|
| `python scripts/build-netlist.py` | 0 | `rows=155`（bom + schematic）、`nets=68` | ✅ 21 个派生文件 SHA-256 全同 |
| `python scripts/build-lceda-import-pack.py` | 0 | 9 份模块 BOM + summary（81 行）+ bom.md | ✅ 全同 |
| `python scripts/build-kicad-schematic.py` | **1** | `netlist refs with no symbol/sheet: ['VCC', 'J17']` | ✅ 全同（**失败即不写**） |

> 说明：我没有在工作区跑任何 `build-*.py`，因此工作区派生文件未被任何脚本覆盖；上述哈希比对证明这三个脚本在当前输入下是幂等的（kicad 是"失败-无写入"式幂等）。

**A.4 依赖清单（5 个 py 的全部 import）**
`csv, io, os, sys, re, hashlib, cmath, itertools, math` + `from __future__ import annotations` ⇒ **纯标准库，无第三方、无 KiCad 依赖**（`build-kicad-schematic.py:38-45` 等）。

**A.5 数据统计口径**
- BOM：`csv.DictReader`(utf-8-sig) 逐文件统计，9 份模块 BOM = 81 数据行；`LCSC 编号` 非"待查"者 2 行；`统一数量` 非纯整数 20 行。
- 网表：`hardware/schematic/netlist.csv` = 156 行（含表头）⇒ **155 数据行**。
- 行覆盖：`kicad-row-coverage.csv` = 182 行（含表头）⇒ **181 数据行**；status 分布 DRAWN 162 / PARTIAL 16 / NOTE 3。
- KiCad 实例：按 `(symbol (lib_id "…")` 抓取，再在后续 4 KB 内取 `Reference`/`Value`；与自检器的 `instances=` 计数逐份吻合（29/14/6/25/9/18/6/2）。
- 残留词扫描：全文 `str.count`，覆盖 `docs/**/*.md`、`hardware/**/*.{md,csv,kicad_sch}`、`scripts/*.py`、根 `*.md`，排除 `release/`。

---

## 附录 B · 新发现 vs 已在册

> "在册"= 该问题已被仓内某份清单/审计登记（给出条目号）。**只有标"已在册"的才算重复。**

| 发现 | 状态 | 在册位置（若有） |
|---|---|---|
| ADR-0009 零落地（拓扑双规格） | 🆕 **首次发现** | 无（ADR 索引都没有它） |
| ADR 索引缺 0009 / ADR-0003 状态未改 | 🆕 首次发现 | 无 |
| 生成器 4 处旧引脚（EC11_A/GPIO12/UART0/LCD_BL） | ⚠️ **会话内已知，仓内未登记** | 无 |
| KiCad 生成器 rc=1（VCC/J17） | ⚠️ 会话内已知，仓内未登记 | 无（`kicad-build-report.md` 未记） |
| 行覆盖 181 vs 155 | ⚠️ 会话内已知，仓内未登记 | 无 |
| 22 个问题实例（12 删 + 10 错值） | 🟡 部分在册 | "含已作废器件"在会话内已知；**具体 22 项清单首次给出** |
| `mcu-ui.kicad_sch` 被手改（76641 vs 报告 76143） | 🆕 首次发现 | 无 |
| `R_sense` 1 kΩ 在 BOM/网表/符号表 | 🟡 判据在册 | `docs/05:566`、§7 #4（`docs/05:766`）已判"错误值"，**但派生文件未改首次指出** |
| BOM 缺检波 C-R-C / 100 kΩ | 🆕 首次发现 | 无 |
| `J17` 位号双重定义 | 🆕 首次发现 | 无（D-24 与 BOM 各自都没错，合起来冲突） |
| `U8` 模块归属冲突 | 🆕 首次发现 | 无 |
| `X1` 重复 / summary 不去重 / 14 行无位号 | 🆕 首次发现 | 无 |
| 电池分压 22k↔30k 跨仓漂移 | 🆕 首次发现 | 需求侧在册（`docs/05:774`"固件按 0.2327 标定"），**固件未执行首次指出** |
| 耦合器位置（输入/输出侧）矛盾 | 🆕 首次发现 | 无 |
| 功放 8.4 V 残留在 docs/00 等 5 处 | 🟡 部分在册 | `docs/04` 已自更新；**docs/00（★权威）未改首次指出** |
| 契约级 12 V / PA_PWR_PWM / TCA9535 残留（20+ 处） | 🟡 部分在册 | pre-fab E-02 只登记 `docs/04 §3.5`；`docs/00:13-20`、`hardware/README.md:9-11`、`relay-wiring.md:12` 有总声明；**其余 20+ 处未登记** |
| `relay-wiring.md:76` TL;DR 仍要求补 6 只下拉 | 🆕 首次发现 | 与 pre-fab D-20 直接冲突 |
| `pre-fab` C-01/E-01/E-06 失效 | 🆕 首次发现 | 无 |
| `docs/02` 未覆盖生成器权威 / 骨架放错目录 | 🆕 首次发现 | 无 |
| `build-netlist.py:20` docstring 谎报 import | 🆕 首次发现 | 无 |
| 无 CI | 🆕 首次发现 | 无 |
| 生成器报告汇总表 165≠181 | 🆕 首次发现 | 无 |
| LPF 器件值 TBD | ✅ **已在册** | pre-fab C-07（`:89`） |
| LCSC 全待查 | ✅ 已在册 | `bom/README.md:177-188`；pre-fab F-05（`:158`） |
| HK4100F 脚位未核实 | ✅ 已在册 | pre-fab C-15（`:97`）、`relay-wiring.md §2.5` |
| 电容支路开路触点耐压 816 Vrms | ✅ 已在册 | pre-fab C-16（`:98`）、`relay-wiring.md §5 R-03` |
| 无过温保护 | ✅ 已在册 | `pa-module/README.md:105-113`；`docs/17:725` 起（§12.5） |
| 天线实测缺频率/高度 | ✅ 已在册 | `2026-10-field-measurements.md:42-45` |
| `docs/13` 缺失 | ✅ 已在册 | pre-fab C-14（`:96`） |

**新发现计数（【判断】口径：仓内任何清单都没有、且不是会话内已知的）**：
- **P0 级 3 条**：ADR-0009 零落地、电池分压跨仓漂移、R_sense 派生文件未同步（含 BOM 缺滤波件）。
- **P1 级 6 条**：耦合器位置、`J17` 双定义、`U8` 归属、mcu-ui 手改、ADR 索引缺项、`docs/02` 未覆盖生成器权威。
- **P2/P3 级 6 条**：X1 重复、`relay-wiring:76`、pre-fab 3 条失效、docstring 谎报、无 CI、报告汇总算错。
- **合计 15 条新发现**；另有 **7 条属"部分在册/会话已知"**（已在表里标注）。

---

## 附录 C · 未核实项（如实说明，不猜）

| # | 项 | 为什么没核 | 建议怎么核 |
|---|---|---|---|
| U-1 | **CA-DV8008N 的真实寄存器/时序**（是否有上电复位延时、单字节读回的确切格式） | 仓内无数据手册（`hardware/datasheets/` 只有 `.gitkeep` + README，`INDEX.md` 不存在；pre-fab C-11 `:93` 已登记） | 来料后按 `datasheets/README.md` 建立 INDEX，逐项核对 `docs/05:164` 的寄存器模型 |
| U-2 | **HK4100F 触点物理脚号**（COM/NC/NO = 第几脚） | 同上，无手册 | pre-fab C-15（`:97`）的五步万用表法 |
| U-3 | **真实功率标定表**（0.5/1/2/2.5 W 对应的 ADC 码） | 需要真机 + 假负载 | `docs/05:598` 的六步法 + stage-3/4 |
| U-4 | **+5 V 轨在 240 mA 脉冲下的实际跌落** | 需实测 | pre-fab D-16（`:123`） |
| U-5 | **耦合器实际方向性**（>25 dB 是否达到） | 需实测 | `docs/05:766`（#4） |
| U-6 | **`check-repo-separation.ps1`** 是否通过 | 它会读私有仓路径，跨仓约束不明确；属"公开/私有边界"检查，超出本次架构审计范围 | 由 Lead 在双仓环境跑 |
| U-7 | **docs/03/06/07/08/15 的内部一致性** | 本次聚焦硬件仓；这 5 份与硬件架构弱相关（03 为固件分层、06 为环境、07 为代码风格、08 为许可、15 为工具链） | 若需要，另开文档审计 |
| U-8 | **`.github/OVERVIEW.md`、`CHANGELOG.md`、根 `README.md` 与现行设计的一致性** | 只做了关键词扫描（根 README 命中 31 处旧词，未逐行判定是"历史记录"还是"现行口述"） | 建议下一轮按 §2.4 的三分类逐行判 |
| U-9 | **`release/v0.1.0` 三档 `.bin` 与当前引脚契约的关系** | 二进制不可读；`release/v0.1.0/README.md` 与 `docs/README.md:12` 都说"构建基线早于该功能" | 不属架构审计范围；按 release notes 处理 |
| U-10 | **ADR-0009 的"2026-10-11 Accepted"与提交日期（2026-10-17）的差异** | git 只显示它随 HEAD 提交入库（`git show --stat 3770717`），无法判断"何时真正拍板" | 问项目所有者；不影响"它现在是 Accepted 且未落地"这个事实 |

---

## 附录 D · 审计边界（本次刻意**没有**做的事）

1. **没有修改任何设计源**（`docs/0*.md`、`hardware/**`、`scripts/**`、`docs/adr/**`）。
2. **没有重生成任何派生文件**：`build-*.py` 只在 `%TEMP%` 副本里跑过，工作区未被写。
3. **没有 `git checkout / restore / reset`**，没有用 PowerShell 做文本往返改文件。
4. **没有对 `.kicad_sch` 做任何手工修补**（那是 §6.6 的工单，不是审计动作）。
5. **没有修改固件仓**（只读引用 4 个头文件：`board_pins.h`、`bsp_board_pins.c/h`、`drv_analog_calc.h`、`atu_match.h`、`rf_swr.h`）。
6. **唯一的写入**：本文 + `docs/README.md` 索引一行。

---

*审计完成时间：2026-10-17 · 审计基线：`3770717` · 本文所有行号均为该基线工作区行号。*
