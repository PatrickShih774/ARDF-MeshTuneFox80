# KiCad 原理图 —— 决策记录（**已生成 8 份 `.kicad_sch`**）

> 本文取代上一轮的同名记录（上一轮结论是「**不生成**」）。
> 结论：**已生成** 8 份互相独立的 KiCad 6 原理图，放在本目录，可直接拿去立创EDA 试导入，
> 之后由人工细修。生成器 / 自检器 / 导入指引见文末。

---

## 1. 上一轮为什么拒绝，这一轮为什么能做

上一轮的否决理由有 3 条，逐条交代：

| # | 上一轮的理由 | 这一轮的处置 |
|---|---|---|
| ① | 本机没有 KiCad，交付物不可验证 | **部分解决**：写了一个**独立的 s-expression 解析器**做语法/引用/几何自检（§4），并配了「手写最小合法文件必须过、故意写坏的文件必须挂」的对照组。**仍然不是 KiCad 自检**，如实列为残余风险（§5）。 |
| ② | `lib_symbols` 符号定义无法确证，会满屏缺符号 | **已解决**（关键突破）：`.kicad_sch` 允许把符号定义**内嵌在文件自己的 `lib_symbols` 段**。本项目**自绘** 32 个简单符号（矩形本体 + 引脚 + 位号/值），**完全不引用 `Device:R` 等官方库**，打开时**不查任何外部库**，因此「无法确证官方符号定义」这个阻塞点消失。 |
| ③ | 「看着能打开」比「打不开」更危险 | **接受并缓解**：接受「可能需要修」，但把**不可信的部分显式标出来**——每张图底部有 NOTE 文字块，另有 `kicad-build-report.md` 逐行列出「哪些行没能照抄 / 为什么」「哪些引脚号没冻结」。不再需要用户去猜。 |

用户对本次任务的授权原话是「**盲生成后试导入，然后我手动仔细修改**」✅ —— 即明确接受「可能要修」，
前提是**尽量能打开**。上面的 ② 解决 + ①的替代验证 + ③的显式标注，满足这个前提。

---

## 2. 做了什么（成品清单）

| 文件 | 行数 | 字节 | 器件数 | 图幅 |
|---|---|---|---|---|
| [`atu-module.kicad_sch`](atu-module.kicad_sch) | 1716 | 63325 | 29 | A3 |
| [`pa-module.kicad_sch`](pa-module.kicad_sch) | 953 | 35498 | 14 | A3 |
| [`lpf-module.kicad_sch`](lpf-module.kicad_sch) | 256 | 9035 | 6 | A4 |
| [`mcu-ui.kicad_sch`](mcu-ui.kicad_sch) | 1968 | 76143 | 25 | A3 |
| [`power-module.kicad_sch`](power-module.kicad_sch) | 626 | 22751 | 9 | A4 |
| [`core-board.kicad_sch`](core-board.kicad_sch) | 656 | 24344 | 18 | A4 |
| [`interconnect.kicad_sch`](interconnect.kicad_sch) | 222 | 8022 | 6 | A4 |
| [`antenna.kicad_sch`](antenna.kicad_sch) | 179 | 6346 | 2 | A4 |

合计 **109 个器件实例 · 397 个引脚 · 212 个引脚上挂了网络标签 · 73 条有引脚的规范网络**。

产物还包括：

| 文件 | 说明 |
|---|---|
| [`kicad-net-map.csv`](kicad-net-map.csv) | 图上**真实存在**的 `(图页, 位号, 引脚号) → 网络名 + 标签种类`（212 行） |
| [`kicad-row-coverage.csv`](kicad-row-coverage.csv) | `netlist.csv` 全部 181 行的落点与状态 |
| [`kicad-build-report.md`](kicad-build-report.md) | 人看的构建报告（9 节，含逐网络落点、符号库、未冻结引脚号、别名表、Value 来源） |
| [`IMPORT-TO-LCEDA.md`](IMPORT-TO-LCEDA.md) | 给用户的导入指引 + 10 个已知失败点 + 细修清单 |
| [`tests/`](tests/) | 自检器的对照组（1 份手写最小合法 + 5 份故意写坏） |
| [`../../scripts/build-kicad-schematic.py`](../../scripts/build-kicad-schematic.py) | 生成器（幂等） |
| [`../../scripts/check-kicad-schematic.py`](../../scripts/check-kicad-schematic.py) | 自检器 |

---

## 3. 格式版本：选 `(version 20211123)`（KiCad 6.0）

**依据**（两路交叉确证）：

1. **立创EDA 侧能吃哪个版本**（决定我们该产出哪个版本）
   - 立创EDA专业版**应用内**「导入 KiCad」：**只支持 KiCad 5.1 / 5.9**
     —— <https://prodocs.lceda.cn/cn/import-export/import-kicad/index.html>
     （原文摘录：「嘉立创EDA专业版支持导入 KiCad 5.1 和 KiCad 5.9 版本的格式文件。」）
   - 立创EDA **格式转换助手**：支持 **KiCad 5.x 与 6+** 的 `.kicad_sch`
     —— <https://prodocs.lceda.cn/cn/import-export/easyeda-pro-format-converter/index.html>
   - ⇒ 要用 s-expression 的 `.kicad_sch`，**必须走迁移助手**；而 KiCad 6 是 s-expression 的**最低**版本，
     兼容面最广（KiCad 6/7/8/9 都能读 6 的格式并自动升级）。
2. **KiCad 官方文件格式规范**（决定语法怎么写）
   - 概览与头部/各段定义：<https://dev-docs.kicad.org/en/file-formats/sexpr-schematic/>
     该页开宗明义：「This documents the s-expression schematic file format for **all versions of KiCad
     from 6.0**」，并规定 `(kicad_sch (version VERSION) (generator GENERATOR) …)`，
     `version` 用 **YYYYMMDD** 格式。
   - 符号定义/引脚/属性：<https://dev-docs.kicad.org/en/file-formats/sexpr-intro/>
     （`lib_symbols` 里的 `symbol` / `pin` / `property` / `rectangle` / `effects` 等）。
   - 于是：**version = 20211123**（KiCad 6.0 的格式号）。

**刻意不用的新语法**（KiCad 7/8/9 才有，不确定就不写）：
- 不用 `(exclude_from_sim …)`（KiCad 8）、`(generator_version …)`（KiCad 8）；
- 不用符号实例内的 `(instances (project …))`（KiCad 7 取代了 KiCad 6 的 `symbol_instances`），
  本文件按 **KiCad 6 写法**：文件尾部用 `(symbol_instances …)` + `(sheet_instances …)`；
- 不用 `(fields_autoplaced yes)`（KiCad 8 改成了带参数的写法），本文件只在 `global_label`
  上用 KiCad 6 的无参 `(fields_autoplaced)`；
- 不用 `(dnp yes)`（KiCad 7）。DNP 器件（`Q4`、`X1`）用 **`(in_bom no)`** + 值里带 `-DNP` 表示。
- 每行 `(property "…" … (id N) …)` 保留 KiCad 6 的 `id` 字段（KiCad 7 才删除它）。

**语法的保守选择**（不确定就选更简单/更笨的写法）：
- 图面文字**不用 `\n` 转义**：一段多行说明被拆成**多个单行 `(text …)` 对象**，彻底避开字符串转义问题；
- **不画任何导线**（`wire` 段为空），引脚之间靠网络标签连接——KiCad 与立创EDA 都认，且没有画错导线的可能；
- 坐标全部落在 **2.54 mm 网格**上（引脚端点落在 1.27 mm 网格），不用分数/科学计数法；
- 文件里**没有半角引号/反斜杠**需要转义（生成时断言）。

---

## 4. 自检（没有 KiCad 时能做的**最强**验证）

`scripts/check-kicad-schematic.py` 里**自己写了一个 s-expression 解析器**（不是括号计数），
逐文件跑下面 7 组检查，并附带一组**对照组**证明检查器不是空转：

| 组 | 检查内容 | 本次结果 |
|---|---|---|
| A | 编码：无 BOM、只有 LF、**纯 ASCII**（字节 `>127` 计数必须为 0） | 8/8 通过（`>127` 字节数均为 **0**，CR 均为 0，均无 BOM） |
| B | 语法：真解析（**括号必须严格配平**）、根 token 是 `kicad_sch`、`version` = `20211123`、无 KiCad 7/8 专属 token | 8/8 通过 |
| C | 库：每个实例的 `lib_id` 都能在本文件 `lib_symbols` 里找到；实例声明的**引脚集合与符号定义逐个相同**；四个标准属性齐全 | 8/8 通过（109 个实例、`lib_id` 引用零悬空） |
| D | 连接：每个 `label`/`global_label` **必须精确落在某个引脚的连接点上**（或导线端点）——否则那个网络会静默丢失；**一个引脚上不允许出现两个不同标签**（那等于短路）；uuid 全局唯一 | 8/8 通过（212 个标签全部落在引脚上，0 个悬空，0 个双重标签） |
| E | 跨文件：位号全局唯一、uuid 全局唯一；**跨图页的网络必须在所有图页上都是 `global_label`**；6 条电源网络必须全局 | 8/8 通过（17 条跨页网络全部 global） |
| F | 清单一致性：`kicad-net-map.csv` 必须与文件里**真实**的引脚→网络映射逐行相同（212 行）；`kicad-row-coverage.csv` 必须覆盖 `netlist.csv` 全部 181 行且无 `SKIPPED`；**清单里声称「某引脚挂了某网络」的 278 处必须逐个在文件里找到**，且 `DRAWN` 行的网络名必须与文件里一致 | 通过（212 行逐行一致；181 行 = 162 `DRAWN` + 16 `PARTIAL` + 3 `NOTE`；278 处挂载全部回查命中） |
| G | 几何：109 个器件包围盒**两两不重叠**；所有引脚/标签/文字都在图幅内 | 8/8 通过（0 处重叠、0 个越界） |

**对照组（证明检查器不空转）** —— 这是任务要求的「最小可开文件对照」：
`hardware/schematic/tests/` 下有一份**手写**的最小合法 `.kicad_sch`（1 个电阻 + 1 个标签，
`minimal-1r-1label.kicad_sch`），检查器必须让它 **PASS**；另有 5 份**故意写坏**的文件必须被
**分别以预期的那一类错误**抓住：

| 对照文件 | 故意制造的问题 | 期望且实际命中的错误码 |
|---|---|---|
| `minimal-1r-1label.kicad_sch` | ——（合法的基准） | **PASS**（0 问题） |
| `bad-01-unbalanced-paren.kicad_sch` | 少了 1 个右括号 | `B01` 解析失败（括号不配平） |
| `bad-02-missing-lib-symbol.kicad_sch` | 实例引用 `ARDF:C`，但 `lib_symbols` 里只有 `ARDF:R` | `C02` lib_id 悬空 |
| `bad-03-dangling-label.kicad_sch` | 标签被挪到空白处（99.06, 99.06） | `D01` 标签不在任何引脚/导线上 |
| `bad-04-pin-not-in-symbol.kicad_sch` | 实例多声明一个 `(pin "3")`，符号里没有 3 号脚 | `C03` 引脚集合不匹配 |
| `bad-05-nonascii.kicad_sch` | 值字段里塞了一个中文字 | `A03` 非 ASCII 字节 |

⇒ 正反两个方向都被验证：**合法的过、非法的按类别挂**。
运行：`python scripts\check-kicad-schematic.py`（退出码 0 = 全过）。

**幂等性**：连续跑两次生成器，11 个产物文件的 SHA-256 **逐字节相同**
（UUID 由 `sha1("ardf-meshtunefox80:" + 稳定种子)` 导出，文件里不写时间戳）。

---

## 5. 已知限制 / 残余风险（**没有**验证的东西）

1. **没有任何 KiCad 打开过这些文件**。本机没有 KiCad，任务纪律也禁止安装任何 EDA 工具。
   语法正确性来自自检器**自己写的解析器**；它证明「括号配平、token 合法、引用完整」，
   **不能**证明「KiCad 的解析器会接受」。
2. **立创EDA 的格式转换助手从未运行过**。[`IMPORT-TO-LCEDA.md`](IMPORT-TO-LCEDA.md) §3 的 10 个失败点
   是**从格式差异推断**的，不是实测报错文案。
3. **物理引脚号有一部分是功能名占位**，这是**故意**的：
   `HK4100F` 的 COM/NO/NC 物理脚号，
   [`hardware/atu-module/relay-wiring.md`](../atu-module/relay-wiring.md) §2.5 明确要求
   「**待来料核实（不得凭猜画图）**」，所以脚本的继电器符号里，引脚号**就是功能名**（`COM`/`NO`/`NC`/`COIL+`/`COIL-`）。
   同类情况还有：ESP32-C3 模组（`GPIO4` 之类）、ST7567 模组（`VDD/VDDIO` 之类）、`J1–J6` 模块排针（C-09 待定）、
   `Si5351A`/`MP2315`/`MD7673` 的脚号、`EC11`、SMA 座。**用真实数据手册脚号**的只有：
   `ULN2003A`(16)、`TCA9535`(24)、`SN74ACT244`(20)、`LM358`(8)、`BS170`/`IRF510`/`2N7002`(3)、`BZX84`(3)。
   报告 §5 逐符号列了这个状态。
4. **符号图形好不好看没验证**：只做了包围盒不重叠。**长引脚名的文字宽度没有建模**，
   可能压到相邻器件上（只影响观感，不影响网络）。
5. **电气正确性没验证**：图上的连接**完全照抄** [`netlist.csv`](netlist.csv)，
   没做 ERC，没算过电流/电压/阻抗，也没有独立复核 `netlist.csv` 本身对不对。
6. **两个元件位号在源数据里不一致，脚本按别名合并并记录在案**：
   `D5_prot → D5`、`C_decout → C244`（见 `REF_ALIAS`）。
7. **Value 字段是 ASCII 转写**（`.kicad_sch` 必须纯 ASCII，而 BOM 的值是中文）。
   转写规则与每个位号的来源写在报告 §8。
8. **`symbol_instances` / `sheet_instances` 段是否被转换器使用**，未验证（KiCad 6 根图的标准写法）。
9. **`paper` 是自动选的**（A4/A3），依据是「器件包围盒 + 注释块」的实测尺寸；
   如果转换器不认 A3，把脚本里 `PAPERS` 第一项改成 `A4` 即可。

---

## 6. 生成器做了什么（可重复、可审计的规则）

数据源与用法（**不自己发明连接**）：

| 输入 | 用途 |
|---|---|
| [`netlist.csv`](netlist.csv)（181 行） | **唯一**连接来源：每行的两端引脚各挂一个该行的网络标签 |
| [`kicad-symbol-map.csv`](kicad-symbol-map.csv)（47 行） | 位号 → 符号类别 → **图页** → 建议库符号；并决定「放了但 netlist 里没有」的器件（LPF 的 L4–L6/C8–C10、升级件 C11–C13、`Q4` DNP、`X1` DNP、`SW1`、`J2–J10`、`J11–J16`、`TP1–TP8`） |
| [`hardware/bom/bom-summary.csv`](../bom/bom-summary.csv) | 器件的 **Value**（ASCII 转写，来源逐条记录） |
| [`hardware/atu-module/relay-wiring.md`](../atu-module/relay-wiring.md) | ATU 的逐脚接法（**电感旁路用 COM–NC**、电容支路用 COM–NO、未用触点悬空），已在 `netlist.csv` 第 144–167 行体现 |

三条把「原始网表」变成「可画图」的显式规则（都在报告里逐条列出，可审计）：

1. **别名表 `NET_ALIAS`（9 条）**：`netlist.csv` 里两个网络名落在**同一个器件引脚**上 ⇒ 它们本来就是同一个节点，
   合并成一个规范名。例：`PA_GATE_PD → PA_GATE`（数据行 75/78 共用 `Q1.G`）、`ANT_ESD → ATU_L3_LO`
   （数据行 126/150 共用 `J_ANT.CENTER`）、`XFWD_SEC → DET_FWD`（数据行 105/107 共用 `R_sense_F.1`）。
   每条的判据（哪两行共用哪个脚）写在报告 §7。
   > 本文/报告里的「行号」= `netlist.csv` 的**数据行号**（1 起，与 `kicad-row-coverage.csv` 的 `row` 列一致），
   > 即 CSV 文件行号减 1。
2. **尾部占位网络名当锚点**：`R3.2 → +3V3_DIG` 这种「一端是器件引脚、另一端写的是电源网名」的行，
   把引脚钉到那条网络上。**但只当占位名出现在目标端**；`+12V → Q1.D`（该行声明的网络是 `PA_DRAIN`）
   不能这么处理，因为 +12V 是经射频扼流圈到的漏极，**不是同一个节点**。
   当锚点网络名与该行 `net_label` 列**不一致**时（6 行：16/17/18/20/21/180），
   引脚按锚点落，同时把该行标成 `PARTIAL` 并写明原因，等你确认。
3. **同一个引脚被多条网络声明时，只保留第一条**（按文件顺序），其余记入
   `node_alt` → 写进图面 NOTE 和报告 §6。**宁可少连，不可乱连**：
   少连是可见的、可修的；乱连（把两条网络短在一起）是危险的、且很难发现。
   例：`Q1.G` 被 `PA_GATE`/`PA_GATE_PD`/`PA_BIAS`/`GND` 四条声明 → 保留 `PA_GATE`，
   `D5` 的阳极留在 `GND` 上（阴极悬空，等人接栅极）——这恰好是正确拓扑。

**布局**：按模块的信号流顺序从左到右、从上到下排（RF 链 `J_ATU_IN → T1 → … → L1 → L2 → L3 → K1…K6`
就是从左到右），器件包围盒之间的水平间隙 **17.78 mm**、行距 **15.24 mm**（均 ≥ 要求的 10 mm），
全部坐标落在 2.54 mm 网格上。

**两个标签种类**：模块内网络用局部 `label`（112 处），跨图页网络与 6 条电源网络用 `global_label`（100 处）。
若立创EDA 转换器丢掉局部标签，跑 `python scripts\build-kicad-schematic.py --all-global` 让**全部**网络
都变成 `global_label` 再导一次（该模式同样能过自检）。

---

## 7. 关联文档

- [`IMPORT-TO-LCEDA.md`](IMPORT-TO-LCEDA.md) —— **导入步骤 + 10 个已知失败点 + 手动细修清单**
- [`kicad-build-report.md`](kicad-build-report.md) —— 构建报告（逐网络落点 / 符号库 / 未照抄的行）
- [`netlist.csv`](netlist.csv) / [`netlist.md`](netlist.md) —— 逐脚连接表（数据源）
- [`kicad-symbol-map.csv`](kicad-symbol-map.csv) —— 位号 → 符号 → 图页
- [`hardware/bom/README.md`](../bom/README.md) §0 —— 立创EDA 导入能力的完整调研
- [`hardware/atu-module/relay-wiring.md`](../atu-module/relay-wiring.md) §2.4/§2.5 —— ATU 逐脚接法与
  「HK4100F 物理脚号待核实（不得凭猜画图）」
