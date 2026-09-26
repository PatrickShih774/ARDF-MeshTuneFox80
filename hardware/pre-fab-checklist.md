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
| [ ] A-2 | ⛔ **TCA9535 I²C 地址** | ⚠️ 未确认：需确认 **A2/A1/A0 实际接法**（文档假定 `0x20`） | `docs/05` §2.3、§7 #2 | HW | 🔴 定 A2/A1/A0 接法并在原理图标注；否则固件地址写错就整条扩展器失效 |
| [ ] A-3 | ~~LCD 走 I²C 还是 SPI~~ | ✅ 已定：**SPI 独占**（ST7567 仅 SPI） | [`ADR-0008`](../docs/adr/ADR-0008-st7567-spi-and-pa-keying.md)（原文 §7 #3） | HW+SW | 无需动作 |
| [ ] A-4 | ⛔ **Tandem Match `R_sense` 最终值** | ⚠️ 初值 **1 kΩ**，需 **NanoVNA 微调** | `docs/05` §3.2、§7 #4；[`validation/stage-3`](../validation/stage-3-coupler-detector/README.md) | HW | 🔴 微调后回填 BOM 与原理图；影响 SWR 标定 |
| [ ] A-5 | ⛔ **检波器件选型**（1N5711 / HSMS-2850 / 并行） | ⚠️ 现方案是**并行对照搭建**，由软件选优/融合；最终选型待实测 | `docs/05` §3.2、§7 #5；[`validation/stage-3`](../validation/stage-3-coupler-detector/README.md) | HW | 🔴 定案后 BOM 才能定量（当前 BOM 按"各 2 只并行"出） |
| [ ] A-6 | ⛔ **是否需要 LM358 运放级** | ⚠️ 未定；BOM 数量写 `0-1` | `docs/05` §7 #6；[`validation/stage-4`](../validation/stage-4-opamp/README.md) | HW | 🔴 定案后 BOM/原理图同步（决定是否预留焊盘） |
| [ ] A-7 | ⛔ **12 V 升压模块型号与 FB 网络参数** | ⚠️ 未确认，需确认 **PWM 调压线性度** | `docs/05` §7 #7；`hardware/power-module/README.md` §3 | HW | 🔴 定型号后 `+12V` 轨、PA 功率档、FB 分压一起定 |
| [ ] A-7a | 📌 **GPIO12 → 升压 FB 加 10 kΩ 下拉**（建议） | 📌 **建议采纳，尚未拍板**：PCB 未打样，加一颗电阻近乎零成本 | `docs/05` §2.10.3、§7 #7a；[`docs/17`](../docs/17-gpio-allocation-audit.md) §12.6.5 | HW / OWNER | 采纳 → 加进 BOM（`bom-mcu-ui-module.csv` 的 `R12`）与原理图，并同步 `docs/04`；不采纳 → 删该行 |
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
| [ ] B-06 | **GPIO12 上电安全特例**：BSP 抢先置低 | 硬件建议同时加 10 kΩ 下拉（见 A-7a） | `docs/05` §2.10.2；`docs/17` §12.6.2 | HW+SW |

### B.2 仍需硬件确认的开放项（投板前确认）

| # | 开放项 | 何时确认 | 证据位置 | 责任方 |
|---|---|---|---|---|
| [ ] B-07 | **GPIO12 功能级验证**：LEDC 写占空比 → 量升压模块输出 | PCB 回来后 | `docs/17` §12.3 #1 | HW |
| [ ] B-08 | **TCA9535 输入端口是否采样锁存** | 仅将来走 C.1 方案才需要 | `docs/17` §12.3 #2 | HW |
| [ ] B-09 | **TCA9535 `INT` 触发条件与上拉** | 仅将来走 C.1 方案才需要（本方案 A 不用 INT） | `docs/17` §12.3 #3、§3.5 | HW |
| [ ] B-10 | **`PA_PWR_PWM` 模拟增益与升压模块软起行为** | 硬件调试阶段 | `docs/17` §12.3 #4 | HW |

### B.3 残留风险（须在原理图/PCB 上做缓解）

| # | 风险 | 等级 | 硬件缓解动作 | 证据位置 |
|---|---|---|---|---|
| [ ] B-11 | flash 模式改回 QIO → GPIO12/13 方案失效且**板子无法启动** | 🔴 高 | 原理图标注 + 文档三处互引 | `docs/17` §7 R1 |
| [ ] B-12 | strapping：上电/复位瞬间转动旋钮 → GPIO2/8 判低 | 🟠 中 | **EC11 A/B 各 10 kΩ 上拉**（BOM 已有 R3/R4） | `docs/17` §7 R2；`docs/05` §2.6 |
| [ ] B-13 | 每次 `gpio_config()` 前须 `gpio_reset_pin()` 解除 MSPI 簿记 | 🟠 中 | 硬件无关（固件）；原理图无需动作 | `docs/17` §7 R3 |
| [ ] B-14 | MSPI 簿记解除后深睡隔离逻辑会处理 GPIO12/13 | 🟡 低 | 当前不用深睡，无需动作 | `docs/17` §7 R4 |
| [ ] B-15 | `TCA9535 INT` 开漏需外部上拉（**仅 C′ 方案**） | 🟡 低 | 方案 A 不涉及；若改方案则加 10 kΩ 到 3.3 V | `docs/17` §7 R6 |
| [ ] B-16 | `PA_PWR_PWM` 落 strapping 脚而未反相 FB 极性（**仅 C′ 方案**） | 🔴 高（若误用） | 方案 A 不涉及 | `docs/17` §7 R8 |
| [ ] B-17 | I²C 失效 = 旋钮完全失效（**仅 C.1 方案**） | 🟠 中 | 方案 A 不涉及 | `docs/17` §7 R9 |

---

## C. 硬件设计文件缺口（🔴 本次发现的"设计文件零"问题）

| # | 缺口 | 现状 | 证据位置 | 责任方 |
|---|---|---|---|---|
| [ ] C-01 | ⛔ **无任何原理图文件** | `hardware/*/schematic/` **只有 `.gitkeep`** | 各模块 `schematic/` 目录 | HW |
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
| [ ] D-01 | ⛔ **ULN2003A 的 `COM` 必须接 +12 V** | 内部续流二极管靠它生效；不接则继电器反峰无抑制 | `docs/05` §2.4；`hardware/atu-module/README.md` §3 | HW |
| [ ] D-02 | ⛔ **SN74ACT244 输入侧加 10 kΩ 下拉到 GND** | Si5351 停振时 CMOS 输入悬空 → 244 振荡 → **PA 自激发射** | `docs/05` §2.5 要求 1 | HW |
| [ ] D-03 | ⛔ **MOS 栅极加下拉电阻** | 保证 OE/停振时 MOS 可靠截止 | `docs/05` §2.5 要求 2 | HW |
| [ ] D-04 | **244 每个 Vcc 引脚 100 nF 去耦；未用输入接固定电平** | 数据手册常规要求 | `docs/05` §2.5 要求 3 | HW |
| [ ] D-05 | **244 由 5 V 供电** | ACT 系列 4.5–5.5 V；输入 TTL 阈值 | `docs/05` §2.5 要求 4 | HW |
| [ ] D-06 | ⛔ **2N7002 背光驱动栅极加 10 kΩ 下拉到 GND** | TCA9535 上电时 I/O 为**输入高阻**，不加下拉则背光状态不定（可能上电即常亮，耗电且刺眼） | `docs/05` §2.3；`ADR-0008` §8.1 | HW |
| [ ] D-07 | ⛔ **EC11 A/B 各加 10 kΩ 上拉** | strapping 要求（上电须为高）+ 编码器本身需要 | `docs/05` §2.6 缓解 1 | HW |
| [ ] D-08 | **EC11_SW 接 GND + 10 kΩ 上拉** | 常态高、按下低，无需反相 | `docs/05` §2.2；`ADR-0008` §8.3 | HW |
| [ ] D-09 | ⛔ **ST7567 `CS` 接 GND** | LCD 是 SPI2 上唯一从机 → 省 1 脚 | `docs/05` §2.2；`ADR-0008` §3.1 | HW |
| [ ] D-10 | **ST7567 `RST` 与板复位共用** | 上电复位即可 → 省 1 脚与 RC 电路 | `docs/05` §2.2；`ADR-0008` §3.1 | HW |
| [ ] D-11 | **ST7567 `DC`(A0) 必须直连 GPIO10** | 每字节翻转，不可挂 I²C 扩展器 | `docs/05` §2.2；`ADR-0008` §3.1 | HW |
| [ ] D-12 | ⛔ **ADC 走线源阻抗 < 10 kΩ** | ESP32-C3 ADC 要求（现设计 7.4 kΩ ✅） | `docs/05` §2.7 | HW |
| [ ] D-13 | **ATU 电容必须 NP0 + 耐压 ≥630 V** | 谐振高压可达 **816 Vrms** | `hardware/atu-module/README.md` §3 | HW |
| [ ] D-14 | **天线静电泄放：1 kV 高压电阻 100 kΩ 到地（或 GDT）** | 现场天线静电 | `docs/04` §3.4；`hardware/atu-module/README.md` §3 | HW |
| [ ] D-15 | ⛔ **射频地与数字地单点汇接于底板一点（星形地）** | 避免功放回流污染 Si5351 与 ADC 参考地；四层板地平面完整（信号/地/电源/信号） | `docs/04` §3.1；`hardware/core-board/README.md` §6 | HW |
| [ ] D-16 | **12 V 升压轨纹波峰峰值 < 0.5 V @2.5 W 发射** | 干扰本振、杂散超标 | `docs/04` §3.6；`docs/05` §3.3 | HW |
| [ ] D-17 | **Si5351 供电与数字电源分轨 + π 型滤波** | 低噪声，保本振相噪 | `docs/04` §3.6 | HW |
| [ ] D-18 | **I²C SDA/SCL 4.7 kΩ 上拉** | 共享总线（Si5351 + TCA9535） | `docs/05` §2.2 | HW |
| [ ] D-19 | **MOS 管散热：TO-92 散热片 / 底板铺铜** | 本板**无温度传感、无过温保护**，散热设计是唯一热保障 | `hardware/pa-module/README.md` §3、§8.1 | HW |
| [ ] D-20 | ⛔ **ULN2003A `IN1–IN6` 各加 10 kΩ 下拉到 GND（6 只）**（2026-09-26 新发现） | TCA9535 上电时 I/O 为**输入**且带**约 100 µA 弱上拉电流源**；达林顿阵列**不能悬空输入**，无下拉则上电瞬间 ULN 输入被弱上拉抬到导通阈值附近 → **6 只继电器可能同时误吸合**。10 kΩ 下拉把电平钳到 1.0 V ≪ V_I(on) ≈ 2.4 V（固件也在正式初始化前把输出锁存器清 0，构成两道保险） | [`hardware/atu-module/relay-wiring.md`](atu-module/relay-wiring.md) §4.2/§4.4；私有固件仓 `components/drv_relay/include/drv_relay.h` 文件头；BOM 行 `R_RLY1-R_RLY6` | HW | 🔴 加 6 只 10 kΩ（0805）到 BOM 与原理图，位置**尽量靠近 ULN2003A 的 IN 脚** |
| [ ] D-21 | ⛔ **电感旁路触点必须用 `COM–NC`（方案 A）**（2026-09-26 新发现） | 若按 `COM–NO` 跨接电感（"吸合=旁路"），则**上电全释放态 = 92 µH**，与固件 `ATU_MATCH_SAFE_COMBO = 0`（= 0 µH/0 pF 直通）的契约冲突 → 上电安全态、NVS 记忆组合、SWR 判据全部对不上号 | [`hardware/atu-module/relay-wiring.md`](atu-module/relay-wiring.md) §1.5、§2.6；私有固件仓 `components/atu_match/include/atu_match.h` §组合↔位模式 | HW | 🔴 原理图评审时逐只核对 **K1–K3 的 `NC` 脚**是否接在电感另一端；丝印标 `COM/NC/NO`，**不要**只标脚号 |

---

## E. 文档一致性（先修文档再投板）

| # | 问题 | 证据位置 | 责任方 |
|---|---|---|---|
| [ ] E-01 | ⛔ **`hardware/README.md` §3 仍写"atu-module 驱动 = 6× 2N7002"**，与现行方案（TCA9535 + ULN2003A）冲突 | `hardware/README.md` §3（atu-module 行）；`docs/05` §2.4；`ADR-0008` §3.3 | HW |
| [ ] E-02 | **`docs/04` §3.5 仍有过时内容**（15 个可用 GPIO / LCD 走 I²C / IO 扩展器含 LCD RST / 2N7002 分立） | `docs/17` §4 **F-10**（明确"未改，超出授权范围"）；`docs/04` §3.5 | HW |
| [ ] E-03 | **主控模组名称不一致**：`mcu-ui-module/README.md` 写 "ESP32-C3 SuperMini"，`docs/05`/`docs/04` 写 "合宙 LuatOS ESP32C3-CORE 新款" | `hardware/mcu-ui-module/README.md` §2；`docs/05` §2；`docs/04` §3.5 | HW/OWNER |
| [ ] E-04 | **`docs/17 §4 F-10` 的过时项未闭环**（审计已列出但未修） | `docs/17` §4 F-10、§12.6 | HW |
| [ ] E-05 | **`docs/05` §1.2 结论仍写"远超可用 GPIO（15）"**，而同文 §1.1 已统一为 12 | `docs/05` §1.2（L52）vs §1.1 | SW/HW |

---

## F. 投板放行判据（全部满足才可下单）

| # | 判据 | 证据位置 |
|---|---|---|
| [ ] F-01 | **A. 组全部 ⛔ 项已闭环**（A-2 / A-4 / A-5 / A-6 / A-7） | 本清单 A 组 |
| [ ] F-02 | **C. 组 C-01 / C-02 / C-07 / C-15 已闭环**（原理图、PCB、LPF 参数、HK4100F 脚位核实）—— **C-06 已于 2026-09-26 闭环**（[`relay-wiring.md`](atu-module/relay-wiring.md)） | 本清单 C 组 |
| [ ] F-03 | **D. 组 ⛔ 项在原理图上逐条可见并已复核** | 本清单 D 组 |
| [ ] F-04 | **E. 组 E-01 已修正**（`hardware/README.md` 的 2N7002 过时行） | `hardware/README.md` §3 |
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
