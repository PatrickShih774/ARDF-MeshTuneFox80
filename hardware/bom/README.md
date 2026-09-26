# bom/ — 立创EDA 导入包（BOM 与网表）

本目录是**为立创EDA（嘉立创EDA）准备的导入资料**：分模块 BOM、汇总 BOM、逐脚网表。
**只放设计输入，不放任何源码。**

> 本目录的 CSV 全部由脚本生成，**请勿手工编辑**：
> ```powershell
> cd ARDF-MeshTuneFox80-hardware
> python scripts\build-lceda-import-pack.py
> python scripts\build-netlist.py
> ```
> 改数据请改脚本里的行数据表，再重新生成。

---

## 0. 立创EDA 导入能力调研结论（2026-09 核实）

> 调研方式是直接抓取官方文档原文（本机 `web_search` 无 API key，故未走搜索引擎）。
> 每条结论附官方链接与原文摘录；**官方文档没写的，本文明确标注"未找到官方说明"**。

### 0.1 立创EDA 专业版能导入哪些格式

官方文档里**导入是逐格式单页**的，没有一张总表。以下逐页核实：

| 格式 | 官方支持的版本/条件 | 依据（官方文档） |
|---|---|---|
| **KiCad** | 应用内导入：**仅 KiCad 5.1 / 5.9**；迁移助手：见 §0.2 | [导入KiCad](https://prodocs.lceda.cn/cn/import-export/import-kicad/index.html) |
| **Altium Designer** | 基于 **AD17** 格式兼容；需先另存为 ASCII（`*.SchDoc`/`*.PcbDoc`），打包 ZIP | [导入Altium Designer](https://prodocs.lceda.cn/cn/import-export/import-altium-designer/index.html) |
| **EAGLE** | **6.0 及以上**（低于 6.0 是加密二进制，不支持） | [导入EAGLE](https://prodocs.lceda.cn/cn/import-export/import-eagle/index.html) |
| **Protel** | **仅 ASCII 格式的 Protel 99 SE** | [导入Protel](https://prodocs.lceda.cn/cn/import-export/import-protel/index.html) |
| **LTspice** | 仅 **ASCII** `.asc` + 符号 `.asy`，打包 ZIP；加密文件不可导入 | [导入 LTspice](https://prodocs.lceda.cn/cn/import-export/import-ltspice/index.html) |
| **PADS** | 有独立页面 | `/cn/import-export/import-pads/` |
| **Allegro / OrCAD** | 有独立页面 | `/cn/import-export/import-allegro-orcad/` |
| **DipTrace** | 有独立页面 | `/cn/import-export/import-diptrace/` |
| **Pulsonix** | 有独立页面 | `/cn/import-export/import-pulsonix/` |
| **T/DISA 4001** | 有独立页面 | `/cn/import-export/import-tdisa-4001/` |
| **嘉立创EDA 标准版** | 支持（工程迁移或 JSON 导入） | [导入标准版](https://prodocs.lceda.cn/cn/import-export/import-easyeda/index.html) |
| **嘉立创EDA 专业版** | 支持（`.epro`） | `/cn/import-export/import-easyeda-pro/` |

**KiCad 原文摘录**（这是决定本包该按哪个格式生成的关键一句）：

> 「嘉立创EDA专业版支持导入 KiCad **5.1 和 KiCad 5.9** 版本的格式文件。
> 如果是更低版本的 KiCad 文件请在 5.1 保存后重新打包导入。」
> —— <https://prodocs.lceda.cn/cn/import-export/import-kicad/index.html>

也就是说：**应用内的「导入 KiCad」只吃 KiCad 5.x**（KiCad 5.x 是 legacy `.sch`/`.brd`，
不是 KiCad 6+ 的 s-expression `.kicad_sch`/`.kicad_pcb`）。

### 0.2 ⚠️ 但「文件迁移助手」支持 KiCad 6+ 的新格式

官方「[格式转换助手](https://prodocs.lceda.cn/cn/import-export/easyeda-pro-format-converter/index.html)」
页面给出了一张**逐软件的支持格式表**，其中 KiCad 一行原文列出的扩展名是：

> `KICad` — `.zip` / `.lib` / `.mod` / `.kicad_mod` / `.kicad_wks` / `.kicad_sym` / `.pro` `.kicad_pro` / `.sch` / `.kicad_sch` / `.kicad_pcb`
> —— 同一表格，库提取 √，**支持导入 √**

即迁移助手**同时接受 KiCad 5 的 `.sch` 与 KiCad 6+ 的 `.kicad_sch`/`.kicad_pcb`/`.kicad_sym`/`.kicad_pro`**。
同一页的使用教程末尾写明转换后走应用内：
> 「在立创EDA顶部菜单栏选择『文件 - 导入 - 嘉立创EDA（专业版）...』进行文件批量导入。」

同一页还有一条**对"本机没装 EDA"很关键**的说明：

> 「本工具可以直接转换 ASCII 格式的第三方 EDA 工具文档，非 ASCII 格式的，
> **需要选择第三方 EDA 的主执行文件 exe 后才可以进行转换**，所以您需要提前在电脑上安装对应的 EDA 软件。」

**推论（标注为推论，非官方明文）**：KiCad 6+ 的 `.kicad_sch` 是 S-expression **纯文本 ASCII**，
因此按此规则**应属可"直接转换"**、无需本机安装 KiCad；而 KiCad 5 的 `.sch` 同样是纯文本。
但**官方没有明文写"KiCad 不需要装 KiCad"**，实际以迁移助手运行时是否索要 `kicad.exe` 为准。

### 0.3 版本要求汇总（给本项目的操作建议）

| 路径 | 需要的 KiCad 版本 | 是否需要本机装 KiCad | 官方依据 |
|---|---|---|---|
| **A. 应用内「导入 KiCad」** | **5.1 / 5.9**（KiCad 的打包功能把库一起打进 zip） | 需要（在 KiCad 里打包） | [导入KiCad](https://prodocs.lceda.cn/cn/import-export/import-kicad/index.html) |
| **B. 迁移助手（推荐）** | 5.x **或 6+**（含 `.kicad_sch`/`.kicad_pcb`/`.kicad_sym`/`.kicad_pro`） | 官方未明说；按 ASCII 规则倾向"不需要" | [格式转换助手](https://prodocs.lceda.cn/cn/import-export/easyeda-pro-format-converter/index.html) |

⚠️ **应用内 KiCad 导入的三条官方注意事项**（原文要点）：
1. 工程压缩**必须用 KiCad 自带的打包功能**，不要自己在文件夹里 zip（自带打包会连同原理图用的库文件一起打进）；
2. 太低版本支持不好，请在 **v5.1 以上**重新保存一次再打包；
3. **PCB 导入后会自动重建铺铜，铺铜结果会有差异，请仔细检查。**

### 0.4 网表导入能力（与本包直接相关）

官方「[PCB - 导入网表](https://prodocs.lceda.cn/cn/pcb/file-import-netlist/index.html)」原文：

> 「导入网表支持的格式有：**`.tel`、`.enet`、`.asc`、`.net`**」
> 「操作入口：顶部菜单 - 文件 - 导入 - 网表」

导出侧（「[导出网表](https://prodocs.lceda.cn/cn/schematic/export-netlist/index.html)」）原文：
> 「目前支持导出嘉立创EDA，Allegro，PADS 9.5 版本的网表。」

**结论**：立创EDA 的网表导入吃的是 **Protel 系 `.net` / PADS `.asc` / `.tel` / `.enet`**，
**不是通用 CSV**。因此本包提供的 `netlist.csv` **不是**为了直接"导入网表"，
而是作为**画原理图时的逐脚接线依据 + 后续生成网表的源数据**。
`.net` 需要由原理图工具生成，无法由 CSV 直接改名冒充。

### 0.5 BOM 导入能力 —— ⚠️ 未找到官方说明

检索了专业版文档的全部页面（356 个 `/cn/` 页面引用），**没有任何「导入 BOM」页面**。
与 BOM 相关的官方页面只有：

| 页面 | 内容 |
|---|---|
| [原理图 - 导出BOM](https://prodocs.lceda.cn/cn/schematic/export-bill-of-materials-bom/index.html) | 导出物料清单 |
| [PCB - 导出 BOM](https://prodocs.lceda.cn/cn/pcb/export-bill-of-materials-bom/index.html) | 同上（PCB 侧） |
| [导出 - 元件购买](https://prodocs.lceda.cn/cn/schematic/export-order-parts/index.html) | 上传导出的 BOM 到立创商城买元件 |
| [下单 - 元件下单](https://prodocs.lceda.cn/cn/pcb/order-order-parts/index.html) | 按当前 PCB 元件上传 BOM 到立创商城 |

**导出 BOM 的官方可选列/能力**（原文要点）：
- 文件类型：**只支持 XLSX 和 CSV**；
- 范围：可选工程的 PCB 或原理图；
- 「全部属性」区可**勾选需要导出的属性**；「BOM 表头设置」可**双击改列名**、拖动排序；
- 文件类型选 **XLSX** 时可用「嘉立创EDA专业版 BOM 模板」导出；
- 导出界面有「**元件下单**」，跳到立创商城 BOM 匹配界面。

**因此本次结论是**（如实记录，不假设）：
- ❌ **未找到任何"把外部 CSV/Excel 导入成原理图器件或 BOM"的官方功能说明**；
- ⚠️ 立创EDA 的 BOM 流程官方写法是「**导出 → 上传立创商城匹配/下单**」，方向是**导出**而非导入；
- ✅ 所以本目录的 BOM CSV 定位是：**采购/打样清单 + 在立创EDA 内建库时的字段来源**，
  列名按通用 BOM 习惯给出；**若日后官方推出 BOM 导入**，按上表列名映射即可。
- ⚠️ **是否必须 LCSC 编号列：未找到官方说明。** 官方只说明可用「元件下单」跳转立创商城做 BOM 匹配。

### 0.6 标准版 vs 专业版

- 本项目按用户选择走**专业版**（文档里"立创EDA"默认指专业版时，入口记为「开始页 - 导入其他 / 顶部菜单 - 文件 - 导入」；**导出**入口记为专业版的「顶部菜单 - 文件 - 导出」，标准版为「顶部菜单 - 导出」）。
- **标准版导入能力本文未逐一核实**：`docs.lceda.cn`（标准版帮助）首页未能抓到有效导航（仅返回一个 JS chunk 引用），
  故**不对标准版作结论**，标注为"未核实"。

---

## 1. 文件清单

| 文件 | 内容 | 行数 |
|---|---|---|
| [`bom-summary.csv`](bom-summary.csv) | **汇总 BOM**（全模块，便于统一下单） | 82 |
| [`bom-atu-module.csv`](bom-atu-module.csv) | ATU 天调模块 | 15 |
| [`bom-pa-module.csv`](bom-pa-module.csv) | 功放模块 | 7 |
| [`bom-lpf-module.csv`](bom-lpf-module.csv) | 低通滤波模块 | 3 |
| [`bom-mcu-ui-module.csv`](bom-mcu-ui-module.csv) | 主控与人机交互模块 | 24 |
| [`bom-power-module.csv`](bom-power-module.csv) | 电源模块 | 9 |
| [`bom-core-board.csv`](bom-core-board.csv) | 核心底板 | 6 |
| [`bom-interconnect.csv`](bom-interconnect.csv) | 模块互联 | 7 |
| [`bom-enclosure.csv`](bom-enclosure.csv) | 外壳与结构 | 5 |
| [`bom-antenna.csv`](bom-antenna.csv) | 天线与地线系统 | 6 |
| [`bom.md`](bom.md) | 上述 CSV 的 Markdown 呈现（GitHub 上直接看） | — |
| [`netlist.csv`](netlist.csv) | 逐脚连接表（中文表头，含依据来源） | 146 |
| [`../schematic/netlist.csv`](../schematic/netlist.csv) | 逐脚连接表（英文表头，机器可读） | 146 |
| [`../schematic/netlist.md`](../schematic/netlist.md) | 网表说明 + 子系统覆盖 + 全部明细 | — |

## 2. 字段说明

### 2.1 BOM CSV

列顺序：`位号 | 参数 | 封装 | 数量 | 建议型号 | LCSC 编号 | 关键规格 | 模块 | 备注 | 统一数量 | 来源`

| 列 | 含义 |
|---|---|
| 位号 | 参考标号；`-` 表示非板载物料（结构件/线束/天线） |
| 参数 | 电气值或物料类别 |
| 封装 | 封装/形式；`(建议)` 表示**未经来料核实** |
| 数量 | **单机数量**；`0-1`、`待定`、`多只` 表示**未冻结** |
| 建议型号 | 推荐采购型号（来自模块 README / docs/04 / docs/05） |
| **LCSC 编号** | **全部为 `待查`** —— 见 §3 |
| 关键规格 | 设计校核用的硬约束（耐压/电流/材质/线圈参数/功率余量等） |
| 模块 | 所属模块 |
| 备注 | 装配/选型注意；标 🔴 的是安全或强约束项 |
| 统一数量 | 归一化后的数量写法（便于汇总） |
| 来源 | **该行数据的文档依据**（模块 README 小节 / docs 节号） |

### 2.2 网表 CSV

中文表头：`网络名 | 源器件.引脚 | 目标器件.引脚 | 说明 | 依据来源`
英文表头：`net | net_label | src_ref | src_pin | dst_ref | dst_pin | note | source`

`net_label` 是可安全用作网络标签的 ASCII 名；`net` 保留原始命名。

## 3. 🔴 LCSC 编号为什么全部是"待查"

本机**无法核实立创商城编号**，两条路都断了：

1. `web_search` 工具**不可用**（返回：`DeepSeek search has no API key for "DEEPSEEK_API_KEY"`）；
2. 直接访问立创商城搜索接口 **被拒**：
   - `https://list.szlcsc.com/api/pc/search/global?keyword=...` → **403 已禁止**
   - 带会话 Cookie 后 → `{"code":403,"msg":"非法ACL-URL请求，禁止访问！","ok":false}`

按任务纪律「**查不到的就留空并标注"待查"，绝不编造**」，本包**不填任何 LCSC 编号**。
**回填建议**：在立创EDA 里按「建议型号」搜元件（或立创商城搜索），确认在售型号后
用其 **C 开头编号**回填 `LCSC 编号` 列即可。

## 4. 已知缺口与待办（打样前必须处理）

| # | 缺口 | 影响 | 依据 |
|---|---|---|---|
| B-01 | ~~**L 型匹配网络的继电器触点接法未定**~~ → ✅ **已解决（2026-09-26）** | 逐脚接法、真值表与掩码契约见 [`hardware/atu-module/relay-wiring.md`](../atu-module/relay-wiring.md)；同时**新增 6 只 10 kΩ 输入下拉**到本 BOM（`R_RLY1-R_RLY6`） | `hardware/atu-module/relay-wiring.md` §2.4/§4.2 |
| B-02 | **LPF 磁环型号与圈数未给** | `lpf-module` BOM 只能写"待定" | `hardware/lpf-module/README.md` §3 |
| B-03 | **TCA9535 / ULN2003A / MD7673 封装未定** | 影响 PCB 封装与 BOM | 各模块 README 未给封装 |
| B-04 | **12 V 升压模块型号与 FB 网络参数未定** | 影响 +12V 轨、PA 功率与控制 | `docs/05` §7 #7 |
| B-05 | **电池 2S(7.4 V) vs 升压模块标称 3.7 V 输入** | 需核对模块输入范围 | `hardware/power-module/README.md` §2/§3 |
| B-06 | **GPIO12 → 升压 FB 的 10 kΩ 下拉是否采纳未定** | 决定该电阻是否进 BOM | `docs/05` §7 #7a；`docs/17` §12.6.5 |
| B-07 | **π 型 RC vs RC 滤波** | 若真是 RC 会有电阻压降，需确认是否有意为之 | `hardware/power-module/README.md` §3 |
| B-08 | **主控模组名称不一致** | `mcu-ui-module/README.md` 写"ESP32-C3 SuperMini"，`docs/05`/`docs/04` 写"合宙 LuatOS ESP32C3-CORE 新款" | 需统一 |
| B-09 | **TCA9535 的 A2/A1/A0 接法** | 决定 I²C 地址是否真为 0x20 | `docs/05` §7 #2 |
| B-10 | **检波器件选型（1N5711 / HSMS-2850 / 并行）** | 决定检波 BOM 与 LM358 是否需要 | `docs/05` §7 #5、§7 #6 |
| B-11 | **天线阻抗与 R_sense 最终值** | 需 NanoVNA 实测 | `docs/05` §7 #4 |
| B-12 | **外壳/面板/线束图纸为空** | 结构件无法下单 | `enclosure/3d-print/`、`enclosure/panel/`、`interconnect/connector|harness/` 均为空 |
| B-13 | **HK4100F 触点脚的物理命名未核实**（2026-09-26 新发现） | 封装级原理图画不出来；脚位接反即不工作 | [`hardware/atu-module/relay-wiring.md`](../atu-module/relay-wiring.md) §2.5；`datasheets/INDEX.md` 未建立 |
| B-14 | **电容支路开路触点耐压余量未核实**（2026-09-26 新发现） | 谐振高压 816 Vrms vs 250 VAC 额定切换 | [`hardware/atu-module/relay-wiring.md`](../atu-module/relay-wiring.md) §5 R-03 |

> ⚠️ 另：`hardware/README.md` §3 的模块清单**仍写"atu-module 驱动为 6× 2N7002"**，
> 与 `docs/05` §2.4 与 ADR-0008 的现行方案（TCA9535 + ULN2003A）**冲突**。
> 本 BOM 按**现行方案**（TCA9535 + ULN2003A）出，**未**照抄 `hardware/README.md` 的过时行。
> 该处文档需另行修正（见 `docs/17` §4 F-10 的同类问题）。

## 5. 关联文档

- [`hardware/README.md`](../README.md) —— 硬件设计区总说明
- [`docs/05-hw-sw-interface-contract.md`](../../docs/05-hw-sw-interface-contract.md) —— **引脚分配唯一权威来源**
- [`docs/17-gpio-allocation-audit.md`](../../docs/17-gpio-allocation-audit.md) —— GPIO 使用全面审计
- [`docs/04-hardware-architecture.md`](../../docs/04-hardware-architecture.md) —— 硬件架构
- [`docs/adr/ADR-0008`](../../docs/adr/ADR-0008-st7567-spi-and-pa-keying.md) —— ST7567/功放/键控/继电器驱动链
- [`hardware/pre-fab-checklist.md`](../pre-fab-checklist.md) —— **打样前检查清单**
