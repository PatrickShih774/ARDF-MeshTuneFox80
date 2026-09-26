# KiCad 原理图骨架 —— 决策记录（**决定：不生成 `.kicad_sch` / `.sch` 文件**）

> 本文回答任务 ③：「KiCad 原理图骨架：做了没有？若没做，为什么？」
> 结论：**没有生成任何 KiCad 原理图文件**。理由与替代交付物见下。

---

## 1. 调研结论（决定这件事的关键事实）

| 路径 | 支持哪个 KiCad 版本 | 依据 |
|---|---|---|
| 立创EDA 专业版**应用内**「导入 KiCad」 | **仅 KiCad 5.1 / 5.9** | <https://prodocs.lceda.cn/cn/import-export/import-kicad/index.html> |
| 立创EDA **格式转换助手**（迁移助手） | KiCad 5.x **与 6+**：`.sch` / `.kicad_sch` / `.kicad_pcb` / `.kicad_sym` / `.kicad_mod` / `.kicad_pro` / `.lib` | <https://prodocs.lceda.cn/cn/import-export/easyeda-pro-format-converter/index.html> |

**原文摘录（应用内导入页）**：
> 「嘉立创EDA专业版支持导入 KiCad **5.1 和 KiCad 5.9** 版本的格式文件。」

即：**应用内导入只吃 KiCad 5.x**（legacy `.sch`/`.brd`），
**KiCad 6/7/8/9 的 s-expression `.kicad_sch` 必须走迁移助手**。

同时，迁移助手页有一条关键限制：
> 「本工具可以直接转换 ASCII 格式的第三方 EDA 工具文档，非 ASCII 格式的，
> **需要选择第三方 EDA 的主执行文件 exe 后才可以进行转换**，所以您需要提前在电脑上安装对应的 EDA 软件。」

**推论（非官方明文）**：KiCad 的 `.sch`（5.x）与 `.kicad_sch`（6+）都是**纯文本 ASCII**，
因此按此规则倾向"可直接转换、无需本机装 KiCad"。但**官方未明文写"KiCad 不需要装 KiCad"**。

> ⚠️ 另外注意：本项目 `hardware/README.md` §4/§5 的命名规范与示例**已假定 KiCad**
> （示例：`atu-module-V1.0.kicad_sch`、`atu-module-V1.0.kicad_pcb`），
> 且 `.gitattributes` 已把 `*.kicad_sch` / `*.kicad_pcb` 标为 `binary`。
> 即**仓库的既有约定是 KiCad 6+ 的 s-expression 命名**，与"应用内只支持 5.1/5.9"存在落差。

---

## 2. 为什么**不**生成 KiCad 文件

三个理由，任一成立即足以否决：

### 2.1 本机没有 KiCad，无法自检 → 交付物不可验证

任务纪律明确要求**不要生成打不开的文件**。手写 `.kicad_sch` / `.sch` 的风险点：
- 版本格式差异（KiCad 5 legacy 与 KiCad 6/7/8/9 s-expression 是**两套完全不同的语法**）；
- KiCad 9 的 s-expression 与 6/7 之间仍有差异（例如版本标记、部分 token）；
- 语法任何一处不合法 → **整个文件打不开或静默丢图元**，而本机**没有 KiCad 可以打开验证**。

### 2.2 符号库定义（`lib_symbols`）无法确证

这是任务里已经点明的红线：
> 「**符号库定义（`lib_symbols`）必须内嵌**，否则打开时缺符号 ❌
> → **若你无法确证符号定义**，**只生成"器件清单 + 网络标签"的骨架**并**明确说明**需要用户在 EDA 里补符号」

实际情况：
- KiCad 6+ 的 `.kicad_sch` 要求把用到的**每一个**符号的完整图形定义**内嵌**在 `lib_symbols` 段里，
  包括 `symbol` / `pin` / `polyline` / `rectangle` / `property` / `unit` 等一大票子节点；
- 这些定义必须**与 KiCad 官方 `Device` 等库逐字一致**才能正常显示与更新；
- 本机**没有 KiCad，也没有 KiCad 官方符号库**（无 `Device.kicad_sym` 等）→ **无法确证任何一条符号定义**。

按任务给出的降级指令，这正是"应只做器件清单 + 网络标签"的情形。

### 2.3 生成出来的东西"看着能打开"比"打不开"更危险

- 一个没有 `lib_symbols` 的 `.kicad_sch` 在 KiCad 里**会打开，但满屏是红框缺符号**；
- 用户可能误以为"文件没问题，只是要补符号"，于是**在一个错误基座上继续画图**，
  后续引脚号/网络名一旦错位，错误会一路带到 PCB。

结论：**不生成**。宁可把同等信息以**可逐条核对**的形式交付（见 §3），
也不产生一个**看似可用、实则不可信**的原理图文件。

---

## 3. 替代交付物（"器件清单 + 网络标签"骨架，可直接在立创EDA 里落地）

| 交付物 | 内容 | 为什么它是可用的替代 |
|---|---|---|
| [`hardware/bom/bom-summary.csv`](../bom/bom-summary.csv) 及分模块 CSV | **器件清单**：位号 / 参数 / 封装 / 数量 / 建议型号 / 关键规格 / 依据来源 | 逐行可在立创EDA 里按位号放器件 |
| [`hardware/bom/bom.md`](../bom/bom.md) | 同上，Markdown 呈现 | GitHub 上直接看 |
| [`hardware/schematic/netlist.csv`](netlist.csv) | **网络标签 + 逐脚连接**（英文表头，机器可读；含 `net_label` 列） | `net_label` 就是**可直接用作网络标签的 ASCII 名** |
| [`hardware/schematic/netlist.md`](netlist.md) | 同上 + **子系统覆盖表**（12 GPIO / TCA9535 16 位 / ULN2003A 7 路 / SPI / I²C / ADC / 电源域 / CW 键控 / 静电泄放 / 星形地） | 画图时的逐脚依据，每条带文档节号 |
| [`hardware/bom/netlist.csv`](../bom/netlist.csv) | 同上，中文表头（含"依据来源"列） | 给人看 |
| [`hardware/schematic/kicad-symbol-map.csv`](kicad-symbol-map.csv) | **位号 → 建议 KiCad 标准库符号名 → 所在图页 → 网络标签** 映射表 | 用户若先画 KiCad 再迁移立创EDA，可直接照此放符号；**符号图形由 EDA 自带库提供，不需要我们瞎编** |

### 3.1 层次化拆分建议（供用户在立创EDA 里建 7 个图页）

| 图页 | 对应模块 | 位号范围（见 `kicad-symbol-map.csv`） |
|---|---|---|
| `root` | 层次根页 + 电源域/地平面 | 电源网络、GND 汇接 |
| `atu` | 自动天调 | K1–K6、L1–L3、C3–C5、T1/T2、D1–D4、U2（ULN2003A） |
| `pa` | 功放 | Q1–Q3、D5、R1/R2、C6、U8（244） |
| `core` | 核心底板 | J1–J6、J7–J9、去耦电容组 |
| `power` | 电源 | U9（MP2315）、U10（MD7673）、U11（升压）、BT1、电容套件 |
| `lpf` | 低通滤波 | L4–L6、C8–C10 |
| `mcu-ui` | 主控与交互 | U4（ESP32-C3）、U5（ST7567）、U6（EC11）、U1（TCA9535）、U7（Si5351）、LS1、SW1/SW2、全部上拉/下拉 |
| `interconnect` | 互联 | SMA 座、排针排母、天线座、电池座 |

---

## 4. 如果日后确实需要 KiCad 文件：建议的生成路径

1. **优先在立创EDA 里直接画**（用户本来就选立创EDA），完成后用「导出」得到立创EDA 自家格式；
   不需要 KiCad 这一步。
2. 若坚持先生成 KiCad 文件，请在**装了 KiCad 的机器**上：
   - 用 KiCad 建工程 → 放置符号（图形由 KiCad 自带库提供）→ 用**网络标签**连线；
   - 保存为 **KiCad 5.1** 格式可直接走应用内导入；保存为 6+ 格式则走迁移助手。
3. 若要把本包升级成可运行的生成器：需要一个**能访问 KiCad 官方符号库**的环境，
   由脚本把 `Device.kicad_sym` 等库中对应符号的定义**原样复制**进 `lib_symbols`，
   并**在 KiCad 里打开自检**后才能交付。**当前机器不具备该条件。**

---

## 5. 关联文档

- [`hardware/bom/README.md`](../bom/README.md) §0 —— 立创EDA 导入能力完整调研
- [`hardware/schematic/netlist.md`](netlist.md) —— 逐脚连接表与子系统覆盖
- [`hardware/bom/bom.md`](../bom/bom.md) —— 器件清单
- [`hardware/pre-fab-checklist.md`](../pre-fab-checklist.md) —— 打样前检查清单
