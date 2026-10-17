# 原理图流程：**立创EDA（LCEDA）** —— 🔴 KiCad 流程已废弃（2026-10-17）

> **状态**：本仓**不再提供任何 KiCad 原理图文件、生成器与自检器**。
> **现行唯一流程 = 立创EDA 专业版**；本文说明「删了什么、为什么删、现在按什么画、按什么核」。
> 文件该放哪见 [`docs/02-repository-layout.md`](../../docs/02-repository-layout.md) §3.1；
> 引脚/连接器契约的唯一权威是 [`docs/05-hw-sw-interface-contract.md`](../../docs/05-hw-sw-interface-contract.md)。

---

## 1. 2026-10-17 裁定：KiCad 骨架整套删除（用户拍板）

**为什么删（不修）**：8 份 `.kicad_sch` 是 **2026-09-26 21:44:50** 的历史快照（其中 `mcu-ui` 于 10-15 被手改），
经审计（[`docs/ARCHITECTURE-AUDIT-2026-10-17.md`](../../docs/ARCHITECTURE-AUDIT-2026-10-17.md) §6）确认：

- **12 个符号实例是已删器件**（ULN2003A · `R_RLY1–R_RLY6` · TCA9535 · LS1 蜂鸣器 · `R12` · `J_UART` · `U11` 升压）；
- **10 个是错值器件**（`K1–K6` = `HK4100F-DC-12V`、`R_sense` = 1 kΩ、`R_BL2` = 10 kΩ、`R_VBAT1` = 22 kΩ …）＋ `+12V` 全局标签 9 处；
- **生成器已跑不动**：`netlist refs with no symbol/sheet: ['VCC', 'J17']`（rc=1，且失败前不写任何文件）；
- 自检器 rc=1：`row coverage has 181 rows, netlist.csv has 155`。

⇒ 用户裁定：**「骨架删了就行，别再修」**。修一套不可重生成、且 20 % 实例是旧器件的图，比不留图更危险。

### 1.1 已删除的文件（`git` 历史里仍可取回）

| 类别 | 文件 |
|---|---|
| 8 份骨架 | `antenna` · `atu-module` · `core-board` · `interconnect` · `lpf-module` · `mcu-ui` · `pa-module` · `power-module`（扩展名 `.kicad_sch`） |
| 派生物 | `kicad-build-report.md` · `kicad-net-map.csv` · `kicad-row-coverage.csv` |
| 输入表 | `kicad-symbol-map.csv`（位号 → 符号 → 图页；只服务于已删的生成器，且含 `R_sense`=1 kΩ、`R_VBAT`=22 kΩ 等已判错的旧值） |
| 决策记录 | `KIcad-skeleton-decision.md`（记录的是已废弃的 KiCad 生成方案，全文指向上述已删文件） |
| 自检对照组 | `tests/`（1 份最小合法 + 5 份故意写坏的 `.kicad_sch`） |
| 脚本 | `scripts/build-kicad-schematic.py`（生成器）· `scripts/check-kicad-schematic.py`（自检器） |

> 🔴 **为什么连脚本一起删**：只删产物、留下生成器 ⇒ **谁跑一次就把整套旧骨架原样长回来**
> （而且生成器内嵌的器件模型本身就是旧的：`SHEETS`/`DERIVED`/`VALUE_FIX` 里还是 ULN2003A、`R_RLY`、12 V 继电器）。
> 自检器同理：它唯一的输入就是那 8 份文件，文件没了只剩 rc=1。

### 1.2 历史记录在哪

- **git 历史**：`git log -- hardware/schematic/ scripts/build-kicad-schematic.py`。
- **审计报告 §6**：[`docs/ARCHITECTURE-AUDIT-2026-10-17.md`](../../docs/ARCHITECTURE-AUDIT-2026-10-17.md)
  逐份列了行数/字节/实例数/问题实例/生成器阻塞点。该报告是 **2026-10-17 时点的只读记录**，
  其中的路径与文件名**现已不存在**——这是刻意的：审计不改历史。

---

## 2. 现在的原理图流程（立创EDA 专业版）

### 2.1 工具与文件格式

| 项 | 说明 |
|---|---|
| EDA | **立创EDA 专业版**（在线版 / 离机客户端） |
| 工程归档 | `.epro` —— 立创EDA专业版 **V1/V2** 的工程归档格式（zip 包）；离机客户端默认用 `.eprj`（SQLite）存储 |
| 格式代际 | 官方说明：**V3 起不再使用 V2 文件格式**，但仍支持 V2 的导入/导出（细节有差异） ⇒ 交付前确认对端版本 |
| 依据 | <https://github.com/easyeda/easyeda-file-format-v2>（官方文件格式说明） |

### 2.2 设计输入（都在本仓，且都有唯一权威）

| 你要什么 | 查哪里 | 可否手改 |
|---|---|---|
| 引脚分配 / 连接器 / 电平 / 协议边界 | [`docs/05-hw-sw-interface-contract.md`](../../docs/05-hw-sw-interface-contract.md)（★唯一权威） | 走 `docs/05` §6 流程 |
| **逐脚连接表**（位号.引脚 ↔ 网络） | [`netlist.csv`](netlist.csv) · [`netlist.md`](netlist.md) | ❌ **派生文件**，由 `scripts/build-netlist.py` 生成 |
| 物料与位号 | [`hardware/bom/`](../bom/) 的 `bom-*.csv` | ❌ 派生文件 |
| 电源域 / 功耗契约 | `docs/05` §3.3、`docs/04` §3.6 | — |
| 打样前检查 | [`pre-fab-checklist.md`](../pre-fab-checklist.md) | — |

> ⚠️ 本目录**只剩** `netlist.csv` / `netlist.md` / 本文：它们不是原理图源文件，是**逐脚连接表**。

### 2.3 流程（六步）

1. 先定契约：任何引脚/网络变更 **先改 `docs/05`**，再改 `scripts/build-netlist.py` 的内嵌数据表，重跑
   `python scripts\build-netlist.py` 让它产出新的 `netlist.csv` / `netlist.md`。
2. 在立创EDA 里建**一个工程**，按模块建图页（`core-board` / `pa-module` / `lpf-module` / `atu-module` /
   `mcu-ui-module` / `power-module` / `interconnect` / `antenna`）。
3. 画图时**以 `netlist.csv` 逐行为准**，以 `docs/05` 判对错；两者冲突 ⇒ 停下改文档，不要在图上"猜一个"。
4. 器件值/封装按 `hardware/bom/bom-*.csv` 选型（BOM 的 LCSC 列仍多为"待查"，见 `hardware/bom/README.md`）。
5. 电源域、上电安全态、极性这些**硬要件**逐条核对：`docs/05` §2.3–§2.5、§2.10，`pre-fab-checklist` 的 A/D 组。
6. 导出：原理图 PDF、Gerber、贴片坐标、BOM 分别放 `hardware/<模块>/{schematic,gerber,bom}/`（命名规范见 `docs/02` §4.1）。

> 🔴 **图页归属**：按 [`docs/02`](../../docs/02-repository-layout.md) §3.1，源文件放 `hardware/<模块>/schematic/`；
> **不再**集中放在 `hardware/schematic/`（旧骨架放错目录本身就是审计的 G-6 项）。

---

## 3. 关于"从 KiCad 导入立创EDA"

**本仓已无任何 `.kicad_sch`，本文旧版那份"8 份骨架逐份导入"的指引随之全部作废。**

若将来确实需要把**第三方** KiCad 文件导入立创EDA（例如参考设计），按立创EDA 官方两条路走：

| 路线 | 吃什么 | 官方文档 |
|---|---|---|
| 应用内「文件 → 导入 → KiCad」 | **KiCad 5.1 / 5.9** 的 legacy `.sch`（需在 KiCad 里用自带打包功能连库一起打包） | <https://prodocs.lceda.cn/cn/import-export/import-kicad/index.html> |
| 格式转换助手（迁移助手，独立工具） | KiCad **5.x 与 6+**（`.sch` / `.kicad_sch` / `.kicad_pcb` / `.kicad_sym` / `.kicad_mod` / `.kicad_pro` / `.lib`） | <https://prodocs.lceda.cn/cn/import-export/easyeda-pro-format-converter/index.html> |

> 立创EDA **BOM** 导入能力的调研仍在 [`hardware/bom/README.md`](../bom/README.md) §0.2（那部分与本目录无关，仍然有效）。

---

## 4. 相关文档

| 文档 | 用途 |
|---|---|
| [`docs/05-hw-sw-interface-contract.md`](../../docs/05-hw-sw-interface-contract.md) | 引脚/连接器/协议**唯一权威** |
| [`docs/04-hardware-architecture.md`](../../docs/04-hardware-architecture.md) | 模块划分、电源域、射频链设计点 |
| [`docs/02-repository-layout.md`](../../docs/02-repository-layout.md) | 文件该放哪 + 命名规范 |
| [`hardware/pre-fab-checklist.md`](../pre-fab-checklist.md) | 打样前逐条勾选 |
| [`hardware/bom/README.md`](../bom/README.md) | BOM / 立创EDA 导入能力调研 |
| [`docs/ARCHITECTURE-AUDIT-2026-10-17.md`](../../docs/ARCHITECTURE-AUDIT-2026-10-17.md) | 审计报告（含已删骨架的量化记录，§6） |
