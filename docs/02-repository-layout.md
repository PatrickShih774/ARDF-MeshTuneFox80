# 02 · 仓库目录规范

> 状态：已建立｜适用版本：V3.7｜权威性：**★ 唯一权威**（文件归属与命名的最终裁定文档）

本文档回答一个问题：**新建一个文件时，它应该放在哪里？**

---

## 1. 顶层分区原则

仓库顶层按**专业域**分区，而不是按文件类型分区。理由见 [ADR-0002](adr/ADR-0002-hardware-software-split-monorepo.md)。

| 顶层目录 | 专业域 | 许可证 | 内容 |
|---------|--------|--------|------|
| `docs/` | 跨专业 | `CC-BY-4.0` | 同时服务硬件与软件的文档、ADR、需求基线 |
| `hardware/` | 硬件 | `CERN-OHL-S-2.0` | 原理图、PCB、Gerber、BOM、结构件、器件手册 |
| `software/` | 软件 | `Apache-2.0`（固件源码在私有仓，不在本仓） | 软件入口与规划（当前仅 `README.md`）；固件源码在私有仓 |
| `validation/` | 验证 | `CC-BY-4.0` | 硬件在环实测方案与报告 |
| `scripts/` | 仓库级 | `Apache-2.0` | 跨域自动化脚本（构建、打包、文档检查） |

四个顶层业务目录**不允许互相包含**，也不允许新增第五个顶层业务目录（新增需先写 ADR）。

**仓库根目录只允许放"社区元文件"与全局配置**（最小必要集）：

| 根目录文件 | 为什么必须在根目录 |
|-----------|------------------|
| `README.md` | GitHub 仓库首页强制渲染（查找顺序：根 → `.github/` → `docs/`） |
| `LICENSING.md` | 多许可仓库的授权入口（见 [08-许可证与合规](08-licensing-and-compliance.md) §1） |
| `LICENSES/` | 各许可全文（REUSE 风格；GitHub 明确"许可文件必须在仓库根目录才能随克隆/下载分发"） |
| `CHANGELOG.md` | 发布工具（git-cliff / standard-version / release-drafter）默认读根目录 |
| `CONTRIBUTING.md` | GitHub 在新建 Issue/PR 页面自动挂链接（查找顺序：`.github/` → 根 → `docs/`） |
| `.editorconfig` / `.gitattributes` / `.gitignore` | Git 与编辑器全局配置，只能放根目录 |

> **需求基线文档不放根目录**：`docs/00-project-upgrade-plan.md`（原根目录 `plan.md`）虽然是项目最重要的文档，但它属于**专业域文档**而非社区元文件，故按第 3 节决策表归入 `docs/`。根目录应当保持"一眼看完"。

### 1.1 三条分区铁律

1. **硬件文档不进 `docs/`，软件文档不进 `docs/`**——除非它同时被硬件与软件引用。模块专属说明写在 `hardware/<模块>/README.md`；固件专属说明写在**私有固件仓**的 `docs/`。
2. **跨域耦合只允许通过契约**——`docs/05-hw-sw-interface-contract.md` 是 GPIO、连接器、协议的唯一事实来源。硬件的引脚分配与软件的 `bsp_board` 必须与该文档一致。
3. **测量数据与源码分离**——原始测量数据（`.csv` / `.s2p` / `.png`）进 `validation/**/raw/`，已被 `.gitignore` 忽略；只提交分析结论与报告。

### 1.2 中英文约定

| 对象 | 约定 | 示例 |
|------|------|------|
| 目录名 | **英文小写**；ESP-IDF 组件用下划线，其余用连字符 | `atu-module/`、`atu_tuner/` |
| 文件名（源码） | 英文小写 + 下划线 | `app_main.c`、`ardf_code.c` |
| 文件名（设计文件） | 英文小写 + 连字符 + 版本号 | `atu-module-V1.0.kicad_pcb` |
| 文档文件名 | 英文小写 + 连字符，可含编号 | `05-hw-sw-interface-contract.md` |
| **文档内容** | **简体中文** | — |
| 代码注释 | 简体中文（面向国内社区），公共 API 用 Doxygen 风格 | — |

> 为什么目录名不用中文：ESP-IDF/CMake、KiCad、Gerber 打包工具、CI 环境对非 ASCII 路径存在编码与转义风险，且不利于国际协作。详见 [ADR-0002](adr/ADR-0002-hardware-software-split-monorepo.md)。

---

## 2. 完整目录树

> 图例：`✅` 已建立　`⬜` 规划中（本轮未创建）　`📄` 文档　`🔒` 只读参考　`※` 说明行（非实际目录）

```
ARDF-MeshTuneFox80/
│
├── README.md                                  ✅ 📄 项目总览与导航
├── LICENSING.md                               ✅ 📄 ★ 目录级授权映射（唯一权威）
├── CHANGELOG.md                               ✅ 📄 版本变更记录
├── CONTRIBUTING.md                            ✅ 📄 贡献指南
├── LICENSES/                                  ✅    各许可全文（REUSE 风格）
│   ├── README.md                              ✅ 📄 全文获取方式与校验
│   ├── LicenseRef-ARDF-NC-1.0.txt             ⬜    固件二进制（仅业余无线电非商业用途）
│   ├── CERN-OHL-S-2.0.txt                     ⬜    硬件
│   ├── Apache-2.0.txt                         ⬜    中控 / 协议 / 工具 / 脚本
│   └── CC-BY-4.0.txt                          ⬜    文档 / 验证报告
├── .editorconfig                              ✅    编辑器统一配置
├── .gitattributes                             ✅    Git 属性（LF / 二进制标记）
├── .gitignore                                 ✅    忽略规则
│
├── docs/                                      【跨专业文档】文件名英文，标题与内容中文
│   ├── README.md                              ✅ 📄 文档索引与仲裁规则
│   ├── 00-project-upgrade-plan.md             ✅ 📄 ★ 需求与技术指标基线（原根目录 plan.md）
│   ├── 01-project-overview.md                 ✅ 📄
│   ├── 02-repository-layout.md                ✅ 📄 ★ 本文档
│   ├── 03-software-architecture.md            ✅ 📄 ★
│   ├── 04-hardware-architecture.md            ✅ 📄 ★
│   ├── 05-hw-sw-interface-contract.md         ✅ 📄 ★
│   ├── 06-build-and-dev-environment.md        ✅ 📄
│   ├── 07-coding-standards.md                 ✅ 📄
│   ├── 08-licensing-and-compliance.md         ✅ 📄
│   ├── 09-competition-rules-compliance.md     ⬜ 📄 待补
│   ├── 10-atu-tuning-algorithm-design.md      ⬜ 📄 待补
│   ├── 11-mesh-protocol-and-security.md       ⬜ 📄 待补
│   ├── 12-power-and-endurance-budget.md       ⬜ 📄 待补
│   ├── 13-emc-and-spurious-suppression.md     ⬜ 📄 待补
│   ├── 14-production-and-factory-test.md      ⬜ 📄 待补
│   └── adr/                                   【架构决策记录】7 份
│       ├── README.md                                     ✅ 📄 ADR 索引与模板
│       ├── ADR-0001-adopt-esp-idf-over-arduino.md        ✅ 📄
│       ├── ADR-0002-hardware-software-split-monorepo.md  ✅ 📄
│       ├── ADR-0003-atu-6-relay-l-network.md             ✅ 📄
│       ├── ADR-0004-lcd12864-on-shared-i2c.md            ✅ 📄
│       ├── ADR-0005-console-tech-stack-tbd.md            ✅ 📄
│       ├── ADR-0006-layered-licensing-gpl-isolation.md   ✅ 📄 已被取代（见 ADR-0007）
│       └── ADR-0007-firmware-closed-source-two-repo.md   ✅ 📄 固件闭源与双仓结构
│
├── hardware/                                  【硬件区】CERN-OHL-S-2.0
│   ├── README.md                              ✅ 📄 硬件总览、目录树、放哪里
│   ├── core-board/                            核心底板 130×95 mm 四层板
│   │   ├── README.md                          ✅ 📄
│   │   ├── schematic/                         ✅    原理图源文件
│   │   ├── pcb/                               ✅    PCB 源文件
│   │   ├── gerber/                            ✅    Gerber / 钻孔 / 贴片坐标
│   │   ├── bom/                               ✅    BOM 与成本核算
│   │   └── mechanical/                        ✅    板框、安装孔、结构配合
│   ├── pa-module/                             3× BS170 E 类功放
│   │   ├── README.md                          ✅ 📄
│   │   ├── schematic/ pcb/ gerber/ bom/       ✅
│   │   └── test/                              ✅    功放实测（温度/功率/波形）
│   ├── lpf-module/                            三阶椭圆低通
│   │   ├── README.md                          ✅ 📄
│   │   └── schematic/ pcb/ gerber/ bom/ test/ ✅
│   ├── atu-module/                            6 继电器 L 型自动天调 55×65 mm
│   │   ├── README.md                          ✅ 📄
│   │   └── schematic/ pcb/ gerber/ bom/ test/ ✅
│   ├── mcu-ui-module/                         ESP32-C3 + LCD + EC11 + 按键
│   │   ├── README.md                          ✅ 📄
│   │   └── schematic/ pcb/ gerber/ bom/       ✅
│   ├── power-module/                          5V/3.3V/3.3V-RF/12V 四轨
│   │   ├── README.md                          ✅ 📄
│   │   └── schematic/ pcb/ gerber/ bom/       ✅
│   ├── antenna/                               5 m 导线 + 5 m 地线
│   │   ├── README.md                          ✅ 📄
│   │   ├── design/                            ✅    天线/地线部署设计
│   │   └── test/                              ✅    NanoVNA 实测数据
│   ├── enclosure/                             外壳与 3D 打印件
│   │   ├── README.md                          ✅ 📄
│   │   ├── 3d-print/                          ✅    STL / STEP
│   │   └── panel/                             ✅    面板开孔、丝印
│   ├── interconnect/                          ★ 模块间接口定义
│   │   ├── README.md                          ✅ 📄
│   │   ├── connector/                         ✅    连接器针脚定义
│   │   └── harness/                           ✅    线束图与走线
│   ├── datasheets/                            器件数据手册归档
│   │   ├── README.md                          ✅ 📄
│   │   └── INDEX.md                           ⬜ 📄 手册版本与哈希登记
│   ├── reference/                             🔒 外部参考设计（只读，不入许可）
│   │   ├── README.md                          ✅ 📄
│   │   └── atu-100/                           ✅    ATU-100 参考摘录
│   └── archive/                               历史版本归档
│       └── README.md                          ✅ 📄
│
├── software/                                  【软件区】Apache-2.0
│   └── README.md                              ✅ 📄 软件区总览：软件入口与规划要点
│   ※ 中控 master-console/（规划中，待创建）、共享协议 protocol/（规划中，待创建）、跨子工程工具 tools/（规划中，待创建）；
│     固件源码在私有仓 ARDF-MeshTuneFox80-firmware（本仓不含固件源码，只发布编译产物）
│
├── validation/                                【硬件在环验证区】
│   ├── README.md                              ✅ 📄 十阶段总表与记录规范
│   ├── stage-0-rf-frontend/README.md          ✅ 📄 第 0–1 天
│   ├── stage-1-relay-rf/README.md             ✅ 📄 第 1–3 天
│   ├── stage-2-matching-network/README.md     ✅ 📄 第 4–6 天
│   ├── stage-3-coupler-detector/README.md     ✅ 📄 第 7–9 天
│   ├── stage-4-opamp/README.md                ✅ 📄 第 10–11 天
│   ├── stage-5-tuning-algorithm/README.md     ✅ 📄 第 12–14 天
│   ├── stage-6-antenna-emc/README.md          ✅ 📄 第 15–18 天
│   ├── stage-7-mesh/README.md                 ✅ 📄 第 19–20 天
│   ├── stage-8-cw/README.md                   ✅ 📄
│   ├── stage-9-competition-modes/README.md    ✅ 📄
│   └── reports/                               ✅    汇总报告
│
├── scripts/                                   【仓库级脚本】
│   └── README.md                              ✅ 📄
│
└── .github/                                   【协作与 CI】
    ├── OVERVIEW.md                            ✅ 📄 协作设施规划（Issue / PR / CI / Release）
    ├── workflows/                             ⬜    待创建（见 .github/OVERVIEW.md §5）
    └── ISSUE_TEMPLATE/                        ✅    规划中
```

---

## 3. "这个文件放哪里？" 决策表

### 3.1 硬件文件

| 你要新建的东西 | 放这里 |
|---------------|--------|
| 某模块的原理图源文件 | `hardware/<模块>/schematic/` |
| 某模块的 PCB 源文件 | `hardware/<模块>/pcb/` |
| Gerber / 钻孔 / 贴片坐标 | `hardware/<模块>/gerber/` |
| BOM 表、成本核算 | `hardware/<模块>/bom/` |
| 板框图、安装孔、结构配合尺寸 | `hardware/<模块>/mechanical/`（模块无 `mechanical/` 时用 `hardware/enclosure/`） |
| 模块实测报告（功率/温度/波形） | `hardware/<模块>/test/` |
| 3D 打印件 STL / STEP | `hardware/enclosure/3d-print/` |
| 面板开孔图、丝印文件 | `hardware/enclosure/panel/` |
| 连接器针脚定义 | `hardware/interconnect/connector/` |
| 线束图、走线图 | `hardware/interconnect/harness/` |
| 器件数据手册 PDF | `hardware/datasheets/`（**不入 git**，在 `INDEX.md` 登记） |
| 从外部项目抄来的参考原理图/代码 | `hardware/reference/<项目名>/`（**只读**，不纳入本仓库许可） |
| 被替代的旧版本设计 | `hardware/archive/<模块>/<版本>/` |
| 天线部署方案、地线铺设图 | `hardware/antenna/design/` |
| 天线阻抗实测数据 | `hardware/antenna/test/` |

### 3.2 软件文件

> 本表前 11 行的目标位置全部在**私有固件仓**（`ARDF-MeshTuneFox80-firmware`）内，本公开仓不含固件源码。
> 其余各行的目标位置都在**本公开仓**，但这三块软件内容（中控 PC 软件、共享协议、跨子工程工具）**都还没开始写**，
> 因此路径**规划中，待创建**——路径名只指明未来代码放哪里，目录现在并不存在。本仓 `software/` 当前只有 `README.md`。

| 你要新建的东西 | 放这里 |
|---------------|--------|
| 新的功能模块 | 私有仓 `components/<新组件>/`（需先写组件 README，见下） |
| 应用装配代码 / `app_main()` | 私有仓 `main/` |
| 产品级编译期配置项（Kconfig） | 私有仓 `main/Kconfig.projbuild` |
| 组件级编译期配置项 | 私有仓 `components/<组件>/Kconfig` |
| 公共头文件（对其它组件可见） | 私有仓 `components/<组件>/include/` |
| 私有实现与私有头 | 私有仓 `components/<组件>/src/` |
| 组件级单元测试 | 私有仓 `components/<组件>/test/` |
| 跨组件的集成测试 | 私有仓 `test/main/` |
| 宿主机可跑的算法测试 | 私有仓 `test/`（不依赖硬件） |
| 固件本地脚本（构建/烧录/版本生成） | 私有仓 `tools/` |
| 固件专属文档（状态机图、时序图、调试记录） | 私有仓 `docs/` |
| **通信协议字段定义** | `software/protocol/spec/`（规划中，待创建）、`software/protocol/schema/`（规划中，待创建）——**唯一事实来源**，本仓 |
| 协议生成的 C 头 / Python 类 | `software/protocol/generated/`（规划中，待创建；**禁止手改**，本仓） |
| 中控 PC 软件 | `software/master-console/src/ardf_console/<子模块>/`（规划中，待创建，本仓） |
| 跨子工程工具（协议生成、打包） | `software/tools/`（规划中，待创建，本仓） |
| 同时涉及固件与中控的软件文档 | `docs/`（跨专业文档）或 `software/README.md`（软件规划要点） |

### 3.3 文档与验证文件

| 你要新建的东西 | 放这里 |
|---------------|--------|
| 同时服务硬件与软件的文档 | `docs/NN-标题.md` |
| 项目需求与技术指标基线 | `docs/00-project-upgrade-plan.md`（**不要**放仓库根目录） |
| 多许可仓库的授权映射 / 许可全文 | `LICENSING.md`、`LICENSES/`（**必须**在根目录） |
| 影响目录/选型/许可的决策记录 | `docs/adr/ADR-NNNN-标题.md` |
| 某硬件的实测方案与报告 | `validation/stage-N-*/` |
| 某软件的单元测试 | 私有仓 `test/`（**不是** `validation/`） |
| 跨域自动化脚本（打包发布、文档检查） | `scripts/` |
| 版本变更记录 | `CHANGELOG.md` |
| Issue / PR 模板 | `.github/ISSUE_TEMPLATE/` |

> **`validation/` 与私有固件仓 `test/` 的区别**：前者是**硬件在环实测**（需要仪器、需要真板子），后者是**代码级单元测试**（可在宿主机或 CI 跑）。不要混淆。

---

## 4. 命名规范

### 4.1 硬件设计文件

```
<模块名>-<板号>-<版本>.<扩展名>
```

| 示例 | 说明 |
|------|------|
| `atu-module-V1.0.kicad_sch` | ATU 模块原理图 V1.0 |
| `atu-module-V1.0.kicad_pcb` | ATU 模块 PCB V1.0 |
| `pa-module-V1.1-gerber.zip` | 功放模块 V1.1 的 Gerber 包 |
| `core-board-V1.0-bom.xlsx` | 核心底板 V1.0 BOM |
| `atu-module-V1.0-asm.pdf` | ATU 模块装配图 |

- 版本号格式 `V<主>.<次>`：**主版本**变更 = 板框/接口/关键器件变更（不兼容）；**次版本**变更 = 布局优化、元件替换（兼容）。
- 同一模块的多板号（如主板有 A/B 面分板）用 `-A` / `-B` 后缀。
- **禁止**在文件名中出现"最终版""新版""测试2""副本"等字样；不确定的版本放 `hardware/archive/` 或先不提交。

### 4.2 ESP-IDF 组件与源码

> 本节的组件与源码命名规范**适用于私有固件仓**中的固件代码；本公开仓内不含固件源码。

| 对象 | 规范 | 示例 |
|------|------|------|
| 组件目录 | `snake_case`，带层前缀 | `bsp_board`、`drv_si5351`、`atu_tuner` |
| 层前缀 | `bsp_` / `drv_` / `rf_` / `atu_` / `ardf_` / `net_` / `mesh_` / `utils_` | — |
| 公共头文件 | `include/<组件名>.h` | `include/atu_tuner.h` |
| 私有头文件 | `src/<模块名>_internal.h` | `src/search_table.h` |
| 源文件 | `src/<模块名>.c` | `src/atu_tuner.c` |
| 公共类型/宏前缀 | 组件短名 + `_` | `atu_`、`swr_`、`ardf_` |
| FreeRTOS 任务名 | `task_<职责>` | `task_rf_ctrl`、`task_mesh` |

### 4.3 文档文件

- 跨专业文档带两位序号：`NN-标题.md`。
- ADR 用四位序号 + 标题：`ADR-NNNN-标题.md`。
- 其余文档不加序号，用有意义的英文连字符名：`atu-module-tuning-notes.md`。
- 报告类文件带日期：`report-20260925.md`。

---

## 5. 新增内容的标准流程

### 5.1 新增一个 ESP-IDF 组件（6 步）

> 以下步骤**在私有固件仓中执行**（需先取得私有仓访问权）。

1. 确认它不属于现有 28 个组件（见 [03-软件架构](03-software-architecture.md) 组件清单）。
2. 创建目录：私有仓 `components/<新组件>/{include,src}`。
3. 写 `README.md`（职责 / 分层与依赖 / 对外接口 / 设计约束 / 测试要点 / 关联文档）。
4. 在私有仓 `components/README.md` 的组件清单表中登记。
5. 在 [docs/03-software-architecture.md](03-software-architecture.md) 的分层图中登记。
6. 实现代码时补 `CMakeLists.txt`（`idf_component_register`）与 `Kconfig`（如需要）。

### 5.2 新增一个硬件模块

1. 在 `hardware/` 下建 `<模块名>/`，含 `schematic/ pcb/ gerber/ bom/`（按需加 `mechanical/`、`test/`）。
2. 写模块 `README.md`（定位 / 关键指标 / 核心器件 / 接口 / 目录内容 / 验证要点 / 关联文档）。
3. 在 `hardware/README.md` 的模块清单表中登记。
4. **必须**在 [docs/05-hw-sw-interface-contract.md](05-hw-sw-interface-contract.md) 中登记该模块的连接器与引脚占用。
5. 在 `hardware/interconnect/` 中更新互联定义。

### 5.3 新增一份架构文档

1. 判断它属于「跨专业」（`docs/`）、「硬件」（`hardware/<模块>/README.md`）、「软件」（软件架构与规范归 `docs/`，规划要点归 `software/README.md`；软件子工程规划中，尚无专属文档目录）还是「验证」（`validation/`）。
2. 建文件并写内容。
3. 在对应的 `README.md` 索引中登记。
4. 若该文档成为某一领域的**唯一权威**，必须在本规范的第 3 节决策表中补充条目，并在 [docs/README.md](README.md) 的仲裁规则中体现优先级。

---

## 6. 禁止事项清单

| ❌ 禁止 | 原因 |
|--------|------|
| 在仓库根目录随手放文件 | 根目录只允许 README / LICENSING / LICENSES/ / CHANGELOG / CONTRIBUTING / 点文件（见 §1 表格） |
| 在 `docs/` 放模块专属说明 | 模块说明归模块目录 |
| 手改 `software/protocol/generated/`（规划中，待创建） | 该目录由脚本生成，改动会被覆盖 |
| 提交 `hardware/datasheets/*.pdf` | 体积大；用 `INDEX.md` 登记外部归档位置与哈希 |
| 提交 `validation/**/raw/` 原始数据 | 已被 `.gitignore` 忽略；只提交结论与报告 |
| 提交密钥、呼号个人信息 | 安全红线，见 [CONTRIBUTING.md](../CONTRIBUTING.md) |
| 在文件名中使用中文或空格 | 工具链兼容性风险 |
| 使用"最终版""新版""副本"等文件名 | 无法判断版本关系 |
| 在组件之间直接跨层调用 | 破坏分层，见 [03-软件架构](03-software-architecture.md) |
| 私自修改 `docs/05-hw-sw-interface-contract.md` 中的引脚分配 | 需硬件与软件双方评审 |

---

## 7. 关联文档

| 文档 | 用途 |
|------|------|
| [ADR-0002 软硬件分区的单仓结构](adr/ADR-0002-hardware-software-split-monorepo.md) | 为什么这样分区 |
| [03-软件架构](03-software-architecture.md) | 软件区内部结构 |
| [04-硬件架构](04-hardware-architecture.md) | 硬件区内部结构 |
| [05-软硬件接口契约](05-hw-sw-interface-contract.md) | 跨域契约 |
| [CONTRIBUTING.md](../CONTRIBUTING.md) | 提交流程与评审要求 |
| [07-编码规范](07-coding-standards.md) | 代码怎么写 |
