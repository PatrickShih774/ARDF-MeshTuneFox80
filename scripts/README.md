# 仓库级脚本区（scripts/）

本目录存放**仓库级**（跨硬件、软件、文档全专业）的辅助脚本。

## 1. 规划内容

| 脚本类别 | 用途 |
| --- | --- |
| 构建辅助 | 一键拉起固件构建、硬件输出检查的统一入口 |
| 发布打包 | 汇总固件 bin + Gerber + BOM + 验证报告为发布包 |
| 文档检查 | 全仓库 Markdown 链接与锚点校验 |
| BOM 成本核算 | 按批次计算硬件成本，输出成本报表 |

## 2. 三方分工边界

| 位置 | 作用域 | 何时放这里 |
| --- | --- | --- |
| **`scripts/`（本目录）** | **仓库级**，跨专业 | 需要同时触及 `hardware/`、`software/`、`docs/`、`validation/` 的流程编排 |
| [`software/tools/`](../software/README.md)（规划中，待创建） | 软件区跨子工程 | 协议生成、软件发布打包、文档检查、BOM 成本核算的**实现体** |
| 私有固件仓的 `tools/` | 仅固件子工程 | 依赖 ESP-IDF 工具链：烧写、分区、日志解析、pytest-embedded 配置（**源码在私有仓，本仓无此目录**） |

判定规则：

1. 需要 ESP-IDF / 硬件 EDA 工具链 → 各自的子工程 `tools/`。
2. 纯宿主机 Python、被两个及以上子工程或 CI 复用 → `software/tools/`（规划中，待创建）。
3. **只是把上面两者串成一条仓库级流水线**（如"构建 + 打包 + 检查"）→ `scripts/`。

`scripts/` 中的脚本应尽量薄：只做编排与调用，具体逻辑放在 `software/tools/`（规划中，待创建）。

> 📌 `software/tools/` 与 `software/master-console/` 均为**规划中，待创建**——软件区三块内容都还没开始写，本仓 `software/` 当前只有 `README.md`（见 [`software/README.md`](../software/README.md)）。

## 3. 约定

- 语言：优先 Python 3.11+；跨平台，避免仅 Windows 可用的写法。
- 每个脚本必须支持 `--help`，并在文件头注释说明用途、依赖与退出码。
- 退出码：`0` 成功，`1` 检查/构建失败，`2` 用法错误。
- 禁止在脚本中硬编码密钥、路径中含有个人信息的路径。

## 4. 当前状态

已实现的脚本（全部纯宿主 Python，无第三方依赖）：

| 脚本 | 用途 | 产物 |
| --- | --- | --- |
| [`build-lceda-import-pack.py`](build-lceda-import-pack.py) | 生成立创EDA 导入包的 BOM 部分 | `hardware/bom/bom-*.csv`、`bom.md` |
| [`build-netlist.py`](build-netlist.py) | 生成逐脚连接表（BOM 导入包的一部分） | `hardware/bom/netlist.csv`、`hardware/schematic/netlist.csv`、`netlist.md` |
| [`build-kicad-schematic.py`](build-kicad-schematic.py) | 生成 8 份互相独立的 **KiCad 6** 原理图骨架（符号内嵌，不依赖任何外部库） | `hardware/schematic/*.kicad_sch`、`kicad-net-map.csv`、`kicad-row-coverage.csv`、`kicad-build-report.md` |
| [`check-kicad-schematic.py`](check-kicad-schematic.py) | 自检上面 8 份文件（括号配平/库引用/标签落点/跨文件唯一性/几何/清单一致性），并跑 `hardware/schematic/tests/` 的对照组 | 无（退出码 0/1） |
| [`verify-atu-lc-combos.py`](verify-atu-lc-combos.py) | 校验 ATU 的 L/C 组合与继电器位模式 | 无 |
| [`check-repo-separation.ps1`](check-repo-separation.ps1) | 校验公开仓/私有仓的分离边界 | 无 |

每个脚本都支持 `--help`；退出码遵循 §3：`0` 成功、`1` 检查/构建失败、`2` 用法错误。
`build-kicad-schematic.py` **幂等**（UUID 由稳定种子导出，不写时间戳），重跑结果逐字节相同。
