# 打样前检查清单（Pre-Fab Checklist）· ARDF-MeshTuneFox80

> 用途：**PCB 投板前逐条勾选**。每条都注明**证据位置**（文档节号或文件路径），
> 勾选前必须打开对应位置确认，不要凭记忆打勾。
>
> - 状态图例：`[x]` 已确认/已完成（**当前全部未确认**，预置为空框，请核对后手改）
>   · `[ ]` 未确认 · `⛔` 阻塞项（不解决就不能投板）
> - 责任方：`HW` 硬件 / `SW` 软件 / `OWNER` 项目所有者（用户拍板）
> - 本清单**只汇总与勾选**，不改变任何契约；冲突时以
>   [`docs/05`](../docs/05-hw-sw-interface-contract.md) 为准。
>
> 生成日期：2026-09 · 对应契约版本：**V3.7**

---

## A. `docs/05 §7 待冻结事项` —— 逐条

> 来源：[`docs/05-hw-sw-interface-contract.md`](../docs/05-hw-sw-interface-contract.md) §7（原文 11 行：1、1a、2–10）

| # | 事项 | 当前状态 | 证据位置 | 责任方 | 投板前动作 |
|---|---|---|---|---|---|
| [ ] A-1 | **GPIO 分配表最终确认** | ✅ 已冻结 2026-09-25：板卡 = 合宙 LuatOS ESP32C3-CORE 新款；GPIO11 不解锁 eFuse | `docs/05` §2.1–§2.6（原文 §7 #1） | HW | 勾选前确认**与 §2.2 引脚表逐行一致** |
| [ ] A-1a | **GPIO 使用审计** | 📋 审计完成，结论「**不改变分配**」 | [`docs/17`](../docs/17-gpio-allocation-audit.md)（原文 §7 #1a）；`docs/17` §12.1 | HW+SW | 若有任何引脚改动，须按 `docs/05` §6 流程重走 |
| [ ] A-2 | ~~⛔ **TCA9535 I²C 地址**~~ → ✅ **已解决（2026-10-11）** | 驱动改为 **CA-DV8008N**（立创 C54557228）；**A0/A1/A2 全部接 GND** ⇒ 7 位地址 **`0x28`**（8 位写 `0x50` / 读 `0x51`）；原 16 位 `IOEXP_*` 与 INT 脚契约作废 | `docs/05` §2.3、§7 #2 | HW | 🔴 画图时把 A0/A1/A2 **显式接 GND**（芯片内部仅弱下拉），并在丝印/网表标注 `0x28`（填 8 位 `0x50` 会左移成 `0xA0` ⇒ 找不到器件） |
| [ ] A-3 | ~~LCD 走 I²C 还是 SPI~~ | ✅ 已定：**SPI 独占**（ST7567 仅 SPI） | [`ADR-0008`](../docs/adr/ADR-0008-st7567-spi-and-pa-keying.md)（原文 §7 #3） | HW+SW | 无需动作 |
| [ ] A-4 | ⛔ **Tandem Match 终端 `R_term` = 50 Ω / 1 W（配对）+ 极性/方向性实测**（2026-10-11 修正） | 🔴 ~~初值 1 kΩ~~ **是错误值**（破坏桥平衡 ⇒ 方向性崩塌；且 `V_det ≈ 22 V` 削顶 ✗）⇒ 改 **50 Ω / 1 W（2512）、两只 1% 配对**（`V_det ≈ 1.12 V @2.5 W` ✅）。**实测**：天线口接 **50 Ω 假负载** 发 1–2 W ⇒ **读数大的一端 = FWD**，另一端应 ≤ −25 dB（方向性）；**反了只需对调标签**；再测开路/短路（两端近似相等 = 全反射参考点） | `docs/05` §3.2.3/§3.2.5、§7 #4；[`validation/stage-3`](../validation/stage-3-coupler-detector/README.md) | HW | 🔴 回填 BOM（`R_sense_F1`/`R1` = 50 Ω/1 W）与原理图；判据同时用于 SWR 标定 |
| [ ] A-5 | ⛔ **检波器件选型**（1N5711 / HSMS-2850 / 并行） | ⚠️ 现方案是**并行对照搭建**，由软件选优/融合；最终选型待实测 | `docs/05` §3.2、§7 #5；[`validation/stage-3`](../validation/stage-3-coupler-detector/README.md) | HW | 🔴 定案后 BOM 才能定量（当前 BOM 按"各 2 只并行"出） |
| [ ] A-6 | ⛔ **是否需要 LM358 运放级** | ⚠️ 未定；BOM 数量写 `0-1` | `docs/05` §7 #6；[`validation/stage-4`](../validation/stage-4-opamp/README.md) | HW | 🔴 定案后 BOM/原理图同步（决定是否预留焊盘） |
| [ ] A-7 | ~~⛔ **12 V 升压模块型号与 FB 网络参数**~~ → ❌ **作废（2026-10-11）** | 本项目**不设升压**：功放直吃 `VCC`（2S 锂电 6.0–8.4 V），E 类按 **7.4 V 标称定点**（🔴 **2026-10-17 用户裁定统一 7.4 V**；8.4 V 那套 `16.3 Ω`/`0.51 nF`/`3.7 µH` 已作废，见 A-11）；该升压模块已从 `bom-power-module.csv` 删除（原 U11） | `docs/05` §7 #7；`docs/04` §3.2 | — | 无需动作；替代项见 **A-11 / A-12** |
| [ ] A-7a | ~~📌 **GPIO12 → 升压 FB 加 10 kΩ 下拉**~~ → ✅ **已关闭（2026-10-11，去向已定）** | **GPIO12 定案 = 示波器打点**（`SCOPE_TP`）：不接任何被控对象，由 `bsp_board` 独占初始化、上电置 0 | `docs/05` §7 #7a **已关闭**、§2.2、§2.10.2 | HW / OWNER | ✅ **无需动作**：`bom-mcu-ui-module.csv` 的 `R12` **保持"作废·数量 0"**（打点脚不需要下拉） |
| [ ] A-11 | 🔴 **PA E 类按 V_CC = 7.4 V（标称）/ 2.5 W 定点重算**（2026-10-11 定稿，取代 8.4 V 版） | 参数：`R_opt ≈ **12.6 Ω**`（按 8.4 V 为 16.3 Ω ⇒ **匹配/LPF 必须按 12.6 Ω 重做**）· 峰值 `V_ds ≈ **26.3 V**`（选 ≥60 V，BS170 余量 2.3×）· `C1 ≈ **0.65 nF**`（扣 C_oss）· 串联 `L ≈ **2.8 µH**`（Q_L≈5）+ RFC · `I ≈ **0.42 A** @7.4 V`；满电 8.4 V → ≈3.2 W（耗散 1.73 W 仍安全）—— ✅ **甲方案：接受、不降驱动**（2026-10-11 用户裁定）；6.0 V → ≈1.64 W | [`docs/04`](../docs/04-hardware-architecture.md) §3.2/§3.2.0/§3.2.1、`docs/05` §7 #7b | HW | 出元件值后才能定 `pa-module` BOM；实测须用假负载 + 功率计逐电压点标定 |
| [ ] A-12 | ✅ **`PA_PWR_PWM`(GPIO12/LEDC) 的去向 —— 已定案（2026-10-11）：示波器打点** | 原为"PWM 调升压 FB"；无升压后失去控制对象 ⇒ 用户拍板 **GPIO12 = 示波器打点（`SCOPE_TP`）**，**不接任何被控对象**（不取"驱动降额使能"、"未来降压调功"、也不"回收悬空"） | `docs/05` §7 #7a（**已关闭**）、§2.2 引脚表（GPIO12 行）、§2.10.2 | HW + SW（**已定**） | ✅ 硬件：`R12` 保持作废·数量 0；固件（另一批次）：`drv_pa` 的 LEDC/PWM 输出**须移除**，改由 `bsp_board` 把 GPIO12 配成打点输出 |
| [ ] A-13 | ❌ ~~"VCC 兼容 12 V"的含义待明确~~ → **作废（2026-10-11 晚：用户取消 12 V 兼容）** | 输入只支持 **2S 锂电 6.0–8.4 V（标称 7.4 V）** ⇒ 12 V 相关的过压/耗散/标定/保护问题**全部不存在**；唯一保留项：满电 8.4 V 输出 ≈3.2 W ⇒ 固件闭环压回 2.5 W ±10 %（`docs/05` §7 #7c） | [`docs/04`](../docs/04-hardware-architecture.md) §3.7 作废声明 | OWNER | 无需动作；`pa-module` 供电 = `VCC` 直供，可按 §3.2 冻结 |
| [ ] A-14 | ⚠️ **输入级保护（已简化）** | 12 V 取消 ⇒ OR-ing / 12 V 过压防护**不需要**；只保留 **2S 电池反接保护（P-MOS）+ 过流 PTC**（BOM `U13` 已降级）；充电 = **成品 2S 充电模块**（`U12`，如 TP5100，8.4 V CC/CV + 2S BMS 保护板） | `docs/05` §7 #7e；BOM `U12`/`U13` | HW | 与 U12/U13 选型一并定；不再需要"源识别" |
| [ ] A-8 | **密钥分发与轮换策略** | ⚠️ 未设计（软件侧，**不阻塞硬件**） | `docs/05` §5.3、§7 #8 | SW | 与本次投板无关，可留待 |
| [ ] A-9 | **Mesh 信道与 peer 上限** | ⚠️ 未设计（软件侧，**不阻塞硬件**） | `docs/05` §7 #9 | SW | 与本次投板无关，可留待 |
| [ ] A-10 | **LCD 可见列窗口 `W0` 与方向位** | ✅ 已定 2026-09-26：**`W0 = 0`**，面板 **180° 安装**，方向位 `0xA0 + 0xC8`，由**同一个宏** `LCD_MOUNT_180 = 1` 驱动（宏在私有固件仓 `components/drv_lcd12864/`，**不在本公开仓**） | `docs/05` §2.2、§7 #10；`docs/17` §12.7 | HW+SW | ⚠️ **换模组或改安装方式必须重定**（画 x=0/x=127 竖线读出）；下单前确认面板安装朝向 |

---

## B. `docs/17` 相关决策与开放项

> 来源：[`docs/17-gpio-allocation-audit.md`](../docs/17-gpio-allocation-audit.md)

### B.1 已采纳的决策（须在硬件上体现）

| # | 决策 | 硬件侧要求 | 证据位置 | 责任方 |
|---|---|---|---|---|
| [ ] B-01 | **方案 A 不变**（12/12 引脚用满） | 不得擅自增删引脚 | `docs/17` §12.1、§6.1 | HW |
| [ ] B-02 | ⛔ **`CONFIG_ESPTOOLPY_FLASHMODE_DIO=y` 不得被删/覆盖** | 原理图须标注；**QIO 会让本板无法启动**（flash HD/WP 未接 MCU） | `docs/17` §12.1、§7 R1；`docs/05` §2.6.2；`ADR-0008` §8.4 | HW+SW |
| [ ] B-03 | **取消 NTC 功放温度功能**（2026-09-26） | **PA 模块不装 NTC**；栅极偏置改**纯固定偏置**（分压下端直接接地） | `docs/17` §12.5；`hardware/pa-module/README.md` §8.1 | HW |
| [ ] B-04 | **GPIO 所有权重构**：`bsp_board` 不再配置外设引脚 | 硬件侧无直接影响；**固件侧**须照 §12.6.2 的所有权表 | `docs/17` §12.6；`docs/05` §2.10.1 | SW |
| [ ] B-05 | **LCD 列偏移 `W0 = 0` 与方向位绑成一个宏** | 面板 180° 安装 | `docs/17` §12.7；`docs/05` §2.2 | HW+SW |
| [ ] B-06 | **GPIO12 上电安全特例**：BSP 抢先置低 | ~~硬件建议同时加 10 kΩ 下拉（见 A-7a）~~ → 🔴 **2026-10-11 已定案**：GPIO12 = **示波器打点**（不接被控对象）⇒ **上电安全议题作废**（A-7a 已关闭）；BSP 仍独占初始化（`gpio_reset_pin` → 输出 → 置 0），理由变为"打点脚要确定的电平与干净边沿" | `docs/05` §2.10.2（**已由安全议题降级为调试议题**）；`docs/17` §12.6.2 | HW+SW |

### B.2 仍需硬件确认的开放项（投板前确认）

| # | 开放项 | 何时确认 | 证据位置 | 责任方 |
|---|---|---|---|---|
| [ ] B-07 | ~~**GPIO12 功能级验证**：LEDC 写占空比 → 量升压模块输出~~ → 🔴 **本项作废（2026-10-11）** | 升压模块已删 + GPIO12 改作示波器打点 ⇒ **无升压输出可量** | `docs/17` §12.3 #1（原条目）；`docs/05` §2.10.2 | HW | 替代验证（若需要）：用示波器看 **打点脚边沿质量**（上升时间/过冲），**不是**功率验证 |
| [ ] B-08 | **TCA9535 输入端口是否采样锁存** | 仅将来走 C.1 方案才需要；🔴 **且 TCA9535 已被 CA-DV8008N 取代**（新器件**无输入端口**）⇒ 本项**对新器件不适用** | `docs/17` §12.3 #2；`docs/05` §2.3 | HW |
| [ ] B-09 | **TCA9535 `INT` 触发条件与上拉** | 仅将来走 C.1 方案才需要；🔴 **CA-DV8008N 无 INT 脚** ⇒ 本项**对新器件不适用** | `docs/17` §12.3 #3、§3.5；`docs/05` §2.3 | HW |
| [ ] B-10 | ~~**`PA_PWR_PWM` 模拟增益与升压模块软起行为**~~ → 🔴 **本项作废（2026-10-11，无升压 + GPIO12 改作打点）** | 硬件调试阶段 | `docs/17` §12.3 #4 | HW |

### B.3 残留风险（须在原理图/PCB 上做缓解）

| # | 风险 | 等级 | 硬件缓解动作 | 证据位置 |
|---|---|---|---|---|
| [ ] B-11 | flash 模式改回 QIO → GPIO12/13 方案失效且**板子无法启动** | 🔴 高 | 原理图标注 + 文档三处互引 | `docs/17` §7 R1 |
| [ ] B-12 | strapping：上电/复位瞬间转动旋钮 → ~~GPIO2/~~**GPIO8** 判低 | 🟠 中（🔴 **2026-10-11 风险降为一半**：`EC11_A` 已迁 GPIO20（非 strapping）；**B 仍在 GPIO8**） | **EC11 B 的 10 kΩ 上拉（BOM `R4`）为强制**；GPIO20 的 `EC11_A` 上拉（`R3`）为编码器电气需要 | `docs/17` §7 R2；`docs/05` §2.6（三条缓解全部保留） |
| [ ] B-13 | 每次 `gpio_config()` 前须 `gpio_reset_pin()` 解除 MSPI 簿记 | 🟠 中 | 硬件无关（固件）；原理图无需动作 | `docs/17` §7 R3 |
| [ ] B-14 | MSPI 簿记解除后深睡隔离逻辑会处理 GPIO12/13 | 🟡 低 | 当前不用深睡，无需动作 | `docs/17` §7 R4 |
| [ ] B-15 | `TCA9535 INT` 开漏需外部上拉（**仅 C′ 方案**） | 🟡 低 | 方案 A 不涉及；若改方案则加 10 kΩ 到 3.3 V；🔴 **CA-DV8008N 无 INT 脚** | `docs/17` §7 R6；`docs/05` §2.3 |
| [ ] B-16 | ~~`PA_PWR_PWM` 落 strapping 脚而未反相 FB 极性（**仅 C′ 方案**）~~ → 🔴 **本项作废（2026-10-11）** | `PA_PWR_PWM` 功能已整体作废（无升压）+ GPIO12 改作示波器打点 ⇒ 不存在"PWM 落 strapping 脚"的场景 | `docs/05` §2.6（"LEDC 输出不能放 strapping"这条判据仍保留但无适用对象） | — |
| [ ] B-17 | I²C 失效 = 旋钮完全失效（**仅 C.1 方案**） | 🟠 中 | 方案 A 不涉及 | `docs/17` §7 R9 |

---

## C. 硬件设计文件缺口（🔴 本次发现的"设计文件零"问题）

| # | 缺口 | 现状 | 证据位置 | 责任方 |
|---|---|---|---|---|
| [ ] C-01 | ⛔ **无任何原理图文件** | `hardware/*/schematic/` **只有 `.gitkeep`**；`hardware/schematic/` 下只有**逐脚连接表**（`netlist.csv`/`netlist.md`）与流程说明，**不是原理图源文件**。🔴 **2026-10-17**：8 份 KiCad 骨架已**整套删除**（用户裁定），本条**重新成立**（出图走立创EDA，见 [`schematic/IMPORT-TO-LCEDA.md`](schematic/IMPORT-TO-LCEDA.md)） | 各模块 `schematic/` 目录；[`hardware/schematic/`](schematic/) | HW |
| [ ] C-02 | ⛔ **无任何 PCB 文件** | `hardware/*/pcb/` **只有 `.gitkeep`** | 各模块 `pcb/` 目录 | HW |
| [ ] C-03 | ⛔ **无任何 Gerber** | `hardware/*/gerber/` **只有 `.gitkeep`** | 各模块 `gerber/` 目录 | HW |
| [ ] C-04 | **BOM 已建立（本次新增）** | `hardware/bom/` 分模块 + 汇总 CSV（LCSC 编号待回填） | [`hardware/bom/README.md`](bom/README.md) | HW |
| [ ] C-05 | ⛔ **ATU 模块 BOM 目录与原设计目录并存** | `hardware/atu-module/bom/` 仍为空 `.gitkeep`；新 BOM 在 `hardware/bom/`。**需决定是否合并口径** | 两处 `bom/` | HW/OWNER |
| [ ] C-06 | ~~⛔ **L 型匹配网络触点接法未定**~~ → ✅ **已解决（2026-09-26）** | 逐脚接法、8+8 真值表、64 组合索引、掩码极性全部写入 [`hardware/atu-module/relay-wiring.md`](atu-module/relay-wiring.md)；新增阻塞项转为 **C-15**（HK4100F 脚位命名）与 **D-20/D-21** | [`hardware/atu-module/relay-wiring.md`](atu-module/relay-wiring.md)（§2.4 逐脚表、§3 映射、§4 驱动对齐） | HW | 无需动作，但**画图时必须逐只按 §2.4 接**；方案 A（K1–K3 用 COM–NC 旁路）不得改成方案 B |
| [ ] C-07 | ⛔ **LPF 磁环型号与圈数未定** | `lpf-module/README.md` §3 写"具体见 `schematic/` 与 `bom/`"，**而两者都为空** | `hardware/lpf-module/README.md` §3 | HW |
| [ ] C-08 | **核心底板四层板叠层未定义** | 层序/厚度/阻抗未给；下单前需补 | `hardware/core-board/README.md` §2 | HW |
| [ ] C-09 | **interconnect 针脚定义为空** | `interconnect/connector/`、`harness/` **只有 `.gitkeep`** | 两目录 | HW |
| [ ] C-10 | **外壳与面板图纸为空** | `enclosure/3d-print/`、`panel/` **只有 `.gitkeep`**；面板开孔图纸未出 | `hardware/enclosure/README.md` §5 | HW |
| [ ] C-11 | **datasheets 索引未建立** | `datasheets/INDEX.md` 尚不存在（只有规范） | `hardware/datasheets/README.md` §4 | HW |
| [ ] C-12 | **结构尺寸图未出** | `core-board/mechanical/` 只有 `.gitkeep`（安装孔位/板框/模块间距） | `hardware/core-board/README.md` §5 | HW |
| [ ] C-13 | **线束图未出** | 走向/长度/线径/颜色约定/压接/屏蔽处理均未定义 | `hardware/interconnect/README.md` §5 | HW |
| [ ] C-14 | ⚠️ **`docs/13-emc-and-spurious-suppression.md` 尚不存在（待补）** | 接地与杂散抑制的权威文档缺失；`docs/04` §3.1 与 §5 风险表都指向它 | `docs/04` §3.1、§5（风险 #6） | HW |
| [ ] C-15 | ⛔ **HK4100F 触点脚的物理命名（COM/NO/NC = 第几号脚）未核实**（2026-09-26 新发现） | 本仓**无 HK4100F 数据手册本体**（PDF 走外部归档，而 `hardware/datasheets/INDEX.md` **尚未建立**），`datasheets/` 下只有 `.gitkeep` + `README.md` → **封装级原理图画不出来**，脚位接反即整机不工作 | [`hardware/atu-module/relay-wiring.md`](atu-module/relay-wiring.md) §2.5（含万用表五步核实法）；`hardware/datasheets/README.md` §2/§4 | HW | 🔴 来料后用万用表法核实（先找 720 Ω 线圈脚，再判 COM/NC，再加电判 NO）并把脚号回填 §2.5；同时建立 `datasheets/INDEX.md` |
| [ ] C-16 | 🟠 **电容支路开路触点的耐压余量**（2026-09-26 新发现） | 谐振高压可达 **816 Vrms**，而 HK4100F 额定切换能力仅 250 VAC；电容支路继电器**断开**时开路触点承受该节点全电压 | [`hardware/atu-module/relay-wiring.md`](atu-module/relay-wiring.md) §5 **R-03**；`hardware/atu-module/README.md` §3 | HW | 查数据手册的「触点间介质耐压」与「额定切换电压」的区别；按 `validation/stage-2` §4.8 做谐振高压实测 |

---

## D. 电气与安全硬约束（每个都要在原理图上看得见）

| # | 约束 | 为什么 | 证据位置 | 责任方 |
|---|---|---|---|---|
| [ ] D-01 | ⛔ **CA-DV8008 的 `COM` 必须接 `+5 V`**（2026-10-11 改写） | 内部续流钳位二极管**共阴**端，必须接继电器线圈电源；不接则反峰无抑制 | `docs/05` §2.3/§2.4；[`hardware/atu-module/relay-wiring.md`](atu-module/relay-wiring.md) CHANGELOG | HW | 🔴 接 **`+5 V`**（与线圈同源、就近走线），**不是** `+12 V`/`VCC` |
| [ ] D-02 | ⛔ **SN74ACT244 输入侧加 10 kΩ 下拉到 GND** | Si5351 停振时 CMOS 输入悬空 → 244 振荡 → **PA 自激发射** | `docs/05` §2.5 要求 1 | HW |
| [ ] D-03 | ⛔ **MOS 栅极加下拉电阻** | 保证 OE/停振时 MOS 可靠截止 | `docs/05` §2.5 要求 2 | HW |
| [ ] D-04 | **244 每个 Vcc 引脚 100 nF 去耦；未用输入接固定电平** | 数据手册常规要求 | `docs/05` §2.5 要求 3 | HW |
| [ ] D-05 | **244 由 5 V 供电** | ACT 系列 4.5–5.5 V；输入 TTL 阈值 | `docs/05` §2.5 要求 4 | HW |
| [ ] D-06 | ⛔ **2N7002 背光驱动栅极加 100 kΩ 下拉到 GND**（🔴 2026-10-11：原 10 kΩ → **100 kΩ** 按用户口径） | **驱动源已定案 = GPIO21**（0/1 输出，不用 PWM）；GPIO21 在复位默认态/固件未初始化时为**高阻**，不加下拉则背光状态不定（可能上电即常亮，耗电且刺眼） ⇒ 下拉保证 **上电默认低 = 背光关** | `docs/05` §2.3/§2.4；`ADR-0008` §8.1 | HW |
| [ ] D-07 | ⛔ **EC11 B 加 10 kΩ 上拉（强制）· EC11 A 亦加 10 kΩ（电气需要）** | ~~strapping 要求（上电须为高）+ 编码器本身需要~~ → 🔴 **2026-10-11 起**：`EC11_A` 已迁 **GPIO20（非 strapping）** ⇒ 只有 **B（GPIO8）** 仍受 strapping 强制；**A 的上拉保留但理由变为编码器电气需要** | `docs/05` §2.6 缓解 1 | HW |
| [ ] D-06b | ⛔ **背光驱动源接 `GPIO21`**（`R_BL` 1 kΩ 串到 Q5 栅极） | 🔴 **2026-10-11 定案**（原"待定/候选另加 CA-DV8008 `0x29`"作废） | `docs/05` §2.2/§2.3；§7 #2a **已关闭** | HW |
| [ ] D-06c | ⛔ **OC7 / OC8 保持空闲、不预接**：原理图上**标 NC**，不得接任何负载 | 🔴 **2026-10-11 用户明确要求"不要动，空着"**；固件侧对应位**不得配置、不得写入** | `docs/05` §2.3/§2.4 | HW + SW |
| [ ] D-08 | **EC11_SW 接 GND + 10 kΩ 上拉** | 常态高、按下低，无需反相 | `docs/05` §2.2；`ADR-0008` §8.3 | HW |
| [ ] D-09 | ⛔ **ST7567 `CS` 接 GND**（本版） | LCD 是 SPI 上唯一从机 → 省 1 脚。🔴 **下一版改为独立 GPIO**（硬接 GND 让片选不可观测/不可控），见 [docs/NEXT-PCB-RULES-2026-10-18.md](../docs/NEXT-PCB-RULES-2026-10-18.md) 第①条 | `docs/05` §2.2；`ADR-0008` §3.1 | HW |
| [ ] D-10 | 🔴 **ST7567 `RST` 必须由 MCU 驱动 = `GPIO12`**（**2026-10-18 更正**） | 原"与板复位共用"**已作废**：该接法下屏从未被 MCU 复位到确定状态 ⇒ **背光亮、屏幕全黑**（只发 `0xE2` 实测 20 次 0/20 亮）。现行：`RST` → GPIO12，固件发 **高 5 ms → 低 5 ms → 高 5 ms** 三段脉冲 | `docs/05` §2.2；[`docs/NEXT-PCB-RULES-2026-10-18.md`](../docs/NEXT-PCB-RULES-2026-10-18.md) 第③条；[`docs/LCD-NO-DISPLAY-ROOTCAUSE-2026-10-18.md`](../docs/LCD-NO-DISPLAY-ROOTCAUSE-2026-10-18.md) | HW |
| [ ] D-11 | **ST7567 `DC`(A0) 必须直连 GPIO10** | 每字节翻转，不可挂 I²C 扩展器 | `docs/05` §2.2；`ADR-0008` §3.1 | HW |
| [ ] D-12 | ⛔ **ADC 走线源阻抗 < 10 kΩ** | ESP32-C3 ADC 要求（现设计 7.4 kΩ ✅） | `docs/05` §2.7 | HW |
| [ ] D-13 | **ATU 电容必须 NP0 + 耐压 ≥630 V** | 谐振高压可达 **816 Vrms** | `hardware/atu-module/README.md` §3 | HW |
| [ ] D-14 | **天线静电泄放：1 kV 高压电阻 100 kΩ 到地（或 GDT）** | 现场天线静电 | `docs/04` §3.4；`hardware/atu-module/README.md` §3 | HW |
| [ ] D-15 | ⛔ **射频地与数字地单点汇接于底板一点（星形地）** | 避免功放回流污染 Si5351 与 ADC 参考地；四层板地平面完整（信号/地/电源/信号） | `docs/04` §3.1；`hardware/core-board/README.md` §6 | HW |
| [ ] D-16 | **5 V 主轨与 3.3 V 数字轨纹波 < 50 mVpp；继电器吸合瞬间跌落不干扰本振/ADC**（2026-10-11 改写） | 功放轨 = `VCC` 电池直供（**无升压 ⇒ 无开关纹波源**）；风险转移到 5 V 轨（新增 240 mA 脉冲线圈负载）与 3.3 V 数字轨 | `docs/04` §3.6；`docs/05` §3.3 | HW |
| [ ] D-17 | **Si5351 供电与数字电源分轨 + π 型滤波** | 低噪声，保本振相噪 | `docs/04` §3.6 | HW |
| [ ] D-18 | **I²C SDA/SCL 4.7 kΩ 上拉到 3.3 V** | 共享总线：Si5351（`0x60`）+ **CA-DV8008（`0x28`）**；🔴 总线上**不得**再出现 TCA9535（`0x20`，已移除） | `docs/05` §2.2/§2.3 | HW |
| [ ] D-19 | **MOS 管散热：TO-92 散热片 / 底板铺铜** | 本板**无温度传感、无过温保护**，散热设计是唯一热保障 | `hardware/pa-module/README.md` §3、§8.1 | HW |
| [ ] D-20 | ~~⛔ **ULN2003A `IN1–IN6` 各加 10 kΩ 下拉（6 只）**~~ → ✅ **作废（2026-10-11）** | CA-DV8008 上电寄存器 = 0 ⇒ 8 路输出**高阻** ⇒ 线圈无电流，**不依赖逻辑侧下拉**；`R_RLY1–R_RLY6` 已从 BOM 删除 | `docs/05` §2.3；[`hardware/atu-module/relay-wiring.md`](atu-module/relay-wiring.md) CHANGELOG | HW | 不再需要这 6 只电阻 |
| [ ] D-22 | 🔴 **继电器线圈只许接 `+5 V`，严禁接 `VCC`**（2026-10-11 新增） | 5 V 线圈上限 = 130% 额定 = **6.5 V**；`VCC` = 2S 原压 6.0–8.4 V ⇒ 误接将达 **148 %–168 %** 额定功耗 ⇒ 超规发热、寿命骤降（不会立刻烧毁） | `docs/05` §2.4；`bom-atu-module.csv` 的 `K1-K6` 行 | HW | 🔴 **J17 不引 VCC**（pin1 只给 `+5 V`）⇒ 从物理上杜绝误接 |
| [ ] D-23 | 🔴 **继电器型号必须是 `HK4100F-DC5V-SHG`**（立创 **C12072**，125 Ω / 200 mW）（2026-10-11 新增） | `DC12V` 型吸合需 **≥9.0 V**，而 2S 最高 8.4 V ⇒ **全程吸不动**；`DC6V` 型上限 7.8 V 又低于满电 8.4 V ✗ | `bom-atu-module.csv`；`docs/05` §2.4 | HW | 来料核对丝印 `DC5V`；不得用 DC12V / DC9V / DC6V 替代 |
| [ ] D-24 | **J17 针脚定义**：`1=+5V` · `2,4=GND` · `3=+3V3_DIG` · `5=I2C_SDA` · `6=I2C_SCL` · `7=ADC_FWD` · `8=ADC_REV`（2026-10-11 新增） | **不引 `VCC`**；`+3V3_DIG` **必须保留** —— CA-DV8008 逻辑侧 `V_IH = 0.7×VCC`，若接 5 V 则门限 3.5 V > I²C 总线高电平 3.3 V ⇒ **读不到高电平** | [`hardware/atu-module/relay-wiring.md`](atu-module/relay-wiring.md) CHANGELOG；`docs/05` §2.3 | HW | 与 interconnect 的 **C-09**（针脚定义未冻结）一起冻结 |
| [ ] D-25 | **上电安全态 = 全释放直通**（2026-10-11 新增） | CA-DV8008 上电 8 路高阻 ⇒ K1–K6 全释放 ⇒ 0 µH / 0 pF；与固件 `ATU_MATCH_SAFE_COMBO = 0` 天然一致 | `docs/05` §2.3；私有固件仓 `components/atu_match/include/atu_match.h` | HW | 上电瞬间用电流表确认 `+5 V` 线圈支路**无电流**；再逐位写寄存器核对吸合表 |
| [ ] D-21 | ⛔ **电感旁路触点必须用 `COM–NC`（方案 A）**（2026-09-26 新发现） | 若按 `COM–NO` 跨接电感（"吸合=旁路"），则**上电全释放态 = 92 µH**，与固件 `ATU_MATCH_SAFE_COMBO = 0`（= 0 µH/0 pF 直通）的契约冲突 → 上电安全态、NVS 记忆组合、SWR 判据全部对不上号 | [`hardware/atu-module/relay-wiring.md`](atu-module/relay-wiring.md) §1.5、§2.6；私有固件仓 `components/atu_match/include/atu_match.h` §组合↔位模式 | HW | 🔴 原理图评审时逐只核对 **K1–K3 的 `NC` 脚**是否接在电感另一端；丝印标 `COM/NC/NO`，**不要**只标脚号 |

---

## E. 文档一致性（先修文档再投板）

| # | 问题 | 证据位置 | 责任方 |
|---|---|---|---|
| [ ] E-01 | ~~⛔ **`hardware/README.md` §3 仍写"atu-module 驱动 = 6× 2N7002"，与现行方案（TCA9535 + ULN2003A）冲突**~~ → ✅ **已修正（2026-10-18）**：`hardware/README.md` §3 现写 **CA-DV8008N**；原"现行方案 = TCA9535 + ULN2003A"这句本身也已过期 | `hardware/README.md` §3（atu-module 行）；`docs/05` §2.3/§2.4 | HW |
| [ ] E-02 | **`docs/04` §3.5 过时内容已逐条修正**（可用 GPIO 数 / LCD 接口 / IO 扩展器归属 / 驱动方案）：2026-10-18 复查时已改为 **14 个可用 GPIO、LCD 串行独占+RST=GPIO12、扩展器=CA-DV8008N、驱动=CA-DV8008N** | `docs/17` §4 **F-10**；`docs/04` §3.5 | HW |
| [ ] E-03 | **主控模组名称不一致**：`mcu-ui-module/README.md` 写 "ESP32-C3 SuperMini"，`docs/05`/`docs/04` 写 "合宙 LuatOS ESP32C3-CORE 新款" → **现行板卡已由 `docs/17` §13 逐脚核实为合宙 LuatOS ESP32C3-CORE 新款（15 脚引出）**；`mcu-ui-module/README.md` §2/§3 的 "SuperMini" 字样属**过时**，须改为现行板卡 | `hardware/mcu-ui-module/README.md` §2、§3；`docs/05` §2；`docs/04` §3.5；**`docs/17` §13.2/§13.6(a)** | HW/OWNER |
| [ ] E-04 | **`docs/17 §4 F-10` 的过时项未闭环**（审计已列出但未修） | `docs/17` §4 F-10、§12.6 | HW |
| [ ] E-05 | **`docs/05` §1.2 结论仍写"远超可用 GPIO（15）"**，而同文 §1.1 已统一为 12 | `docs/05` §1.2（L52）vs §1.1 | SW/HW |
| [ ] E-06 | 📌 **开发板选型（SuperMini vs LuatOS）对照已完成，决策待项目所有者拍板**：结论是 **SuperMini 缺 GPIO12/13（`PA_PWR_PWM`/`EC11_SW` 必须换到 GPIO20/21）、GPIO8 有板载 LED 冲突、余量 +2→0**；推荐**留在 LuatOS**。**若决定换 SuperMini，必须先闭环 §13.7 的 P-1（拆/断 GPIO8 的 LED）、P-2（重排 pin map 并走 `docs/05` §6 流程）、P-3（确认控制台全在原生 USB-Serial/JTAG）** —— 三条缺一不可，否则不能投板<br>🔴 **2026-10-11 追加**：**GPIO20/21 在本版已被 `EC11_A` / `LCD_BL` 用掉** ⇒ 该换板路径若启用，**必须先重排 pin map**（`PA_PWR_PWM` 功能本身也已作废 ⇒ P-2 的两条映射已失效其一）。本版**不做**换板 | `docs/17` §13（§13.1 结论、§13.4 缺口、§13.7 前置条件）；`docs/05` §2.2 | HW/OWNER |
| [ ] E-07 | 🔴 **"外接 WiFi 天线"这个换板动机已被证伪（2026-09-27）**：**合宙 LuatOS ESP32C3-CORE 与 ESP32-C3 SuperMini 都没有 IPEX/U.FL 座** —— LuatOS 是**板载 PCB 蛇形天线**（官方硬件资源清单原文「2.4G PCB板载天线」，官方原理图 `CORE-ESP32-A12.kicad_sch` 全图无 `ANT`/`IPEX`/`U.FL` 位号）；SuperMini 是**陶瓷贴片天线 `CrossAir CA-C03`**，厂家"外接天线"一节的配图是「**屏蔽层 + 线芯**」= **焊一条线**，也不是插座。⇒ 外接天线在两块板上都是**同样的改板动作**（断开串联匹配器件 → 同轴线芯焊到 `LNA_IN` 侧焊盘 → 屏蔽层就近接地），**换板不带来任何天线便利**；且 SuperMini 的陶瓷天线开箱**更弱**。<br>⇒ **E-06 的决策不应再把"能外接天线"计入 SuperMini 的收益**；若确需外接天线，按 [`docs/17`](../docs/17-gpio-allocation-audit.md) **§13.11.4 方案 E-1** 单独立项（需 VNA + A/B 实测） | [`docs/17` §13.11](../docs/17-gpio-allocation-audit.md)（T-1/T-2/T-4 一手证据、T-5/T-6 厂家资料） | HW/OWNER |

---

## F. 投板放行判据（全部满足才可下单）

| # | 判据 | 证据位置 |
|---|---|---|
| [ ] F-01 | **A. 组全部 ⛔ 项已闭环**（A-2 / A-4 / A-5 / A-6 / A-7） | 本清单 A 组 |
| [ ] F-02 | **C. 组 C-01 / C-02 / C-07 / C-15 已闭环**（原理图、PCB、LPF 参数、HK4100F 脚位核实）—— **C-06 已于 2026-09-26 闭环**（[`relay-wiring.md`](atu-module/relay-wiring.md)） | 本清单 C 组 |
| [ ] F-03 | **D. 组 ⛔ 项在原理图上逐条可见并已复核** | 本清单 D 组 |
| [ ] F-04 | **E. 组 E-01 已修正**（`hardware/README.md` 的驱动方案过时行；此项 2026-10-18 复查已闭环） | `hardware/README.md` §3 |
| [ ] F-05 | **BOM 的 `LCSC 编号` 列已回填**（当前全部 `待查`） | [`hardware/bom/README.md`](bom/README.md) §3 |
| [ ] F-06 | **设计规则检查（DRC）通过**：线宽/间距/孔径/铜箔到边距 | 投板前在 EDA 内执行 |
| [ ] F-07 | **射频链路 50 Ω 阻抗连续性已复核**（PA→LPF→ATU→ANT，SMA 互联） | `docs/05` §4.1 |
| [ ] F-08 | **Gerber 已生成并按厂商要求复核**（层数、钻孔、阻焊、丝印） | 投板前在 EDA 内执行 |

---

## G. 关联文档

| 文档 | 说明 |
|---|---|
| [`docs/05-hw-sw-interface-contract.md`](../docs/05-hw-sw-interface-contract.md) | 软硬件接口契约（**唯一权威**）；§7 待冻结事项 |
| [`docs/17-gpio-allocation-audit.md`](../docs/17-gpio-allocation-audit.md) | GPIO 使用全面审计；§7 残留风险、§12 决策记录 |
| [`docs/04-hardware-architecture.md`](../docs/04-hardware-architecture.md) | 硬件架构（⚠️ §3.5 有过时内容，见 E-02） |
| [`docs/adr/ADR-0008`](../docs/adr/ADR-0008-st7567-spi-and-pa-keying.md) | ST7567 / PA 驱动 / CW 键控 / 继电器驱动链 |
| [`hardware/bom/README.md`](bom/README.md) | 立创EDA 导入包与 BOM 说明、LCSC 待查原因 |
| [`hardware/atu-module/relay-wiring.md`](atu-module/relay-wiring.md) | 🔴 **ATU 继电器逐脚接法规格**（C-06 的关闭文档；D-20/D-21/C-15/C-16 的来源） |
| [`hardware/README.md`](README.md) | 硬件设计区总说明（⚠️ §3 有过时行，见 E-01） |
