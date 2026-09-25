# docs/ — 跨专业文档索引

本目录存放**同时服务于硬件与软件**的文档。硬件专属文档在 `hardware/<模块>/README.md`，软件相关规划在 [`software/README.md`](../software/README.md)（中控 PC 软件 / 共享协议 / 工具均规划中，待创建）；固件专属文档在**私有固件仓**（`ARDF-MeshTuneFox80-firmware`）。

> 文档语言：简体中文。目录与文件名：英文小写 + 连字符（见 [ADR-0002](adr/ADR-0002-hardware-software-split-monorepo.md)）。

---

## 文档清单

| 编号 | 文档 | 回答什么问题 | 权威性 |
|------|------|-------------|--------|
| **00** | [**项目升级计划书**](00-project-upgrade-plan.md) | **需求基线**：技术方案、指标、成本、验证方案 | ★ 指标唯一权威 |
| 01 | [项目概述](01-project-overview.md) | 这个项目是什么、要解决什么、边界在哪 | 概述性 |
| 02 | [仓库目录规范](02-repository-layout.md) | **某个文件应该放在哪里** | ★ 唯一权威 |
| 03 | [软件架构](03-software-architecture.md) | 固件如何分层、组件如何划分、任务如何调度 | ★ 唯一权威 |
| 04 | [硬件架构](04-hardware-architecture.md) | 硬件如何分模块、模块如何互联、如何版本管理 | ★ 唯一权威 |
| 05 | [软硬件接口契约](05-hw-sw-interface-contract.md) | **GPIO 怎么分配、连接器如何定义、协议边界在哪** | ★ 唯一权威 |
| 06 | [构建与开发环境](06-build-and-dev-environment.md) | 怎么装工具链、怎么编译、怎么烧录、怎么调试 | 操作性 |
| 07 | [编码规范](07-coding-standards.md) | 代码怎么写、命名怎么做、注释怎么加 | ★ 唯一权威 |
| 08 | [许可证与合规](08-licensing-and-compliance.md) | 各区域适用什么协议、商用合规路径 | ★ 唯一权威 |
| **15** | [**用 DSH 插件机制集成 ESP-IDF 开发与调试**](15-dsh-esp-idf-integration.md) | DSH 插件架构实测、技能/MCP 路径、ESP-IDF 工具集设计 | 开发工具 |

### 优先级仲裁规则

当文档之间出现冲突时，按以下顺序裁定：

```
05-hw-sw-interface-contract.md   ← 引脚、连接器、协议（硬件与软件都不许私自改）
        ↓
02-repository-layout.md          ← 文件归属与命名
        ↓
03-software-architecture.md      ← 软件分层与组件划分
04-hardware-architecture.md      ← 硬件模块与互联
        ↓
00-project-upgrade-plan.md       ← 需求与技术指标基线
        ↓
各模块 README.md                  ← 局部说明
```

**例外**：技术指标（功率、频率、SWR 判据、成本等）冲突时以 [00-project-upgrade-plan.md](00-project-upgrade-plan.md) 为准，禁止在模块 README 中私自修改指标。

---

## 架构决策记录（ADR）

`adr/` 目录记录**为什么这样决策**。任何影响目录结构、技术选型、许可边界的变更都必须新增或更新一份 ADR。

| 编号 | 决策 | 状态 |
|------|------|------|
| [ADR-0001](adr/ADR-0001-adopt-esp-idf-over-arduino.md) | 采用 ESP-IDF 而非 Arduino | 已接受 |
| [ADR-0002](adr/ADR-0002-hardware-software-split-monorepo.md) | 软硬件分区的单仓结构 | 已接受 |
| [ADR-0003](adr/ADR-0003-atu-6-relay-l-network.md) | ATU 采用 6 继电器 L 型匹配网络 | 已接受 |
| [ADR-0004](adr/ADR-0004-lcd12864-on-shared-i2c.md) | 12864 液晶走 I2C 共享总线 | ⚠️ 已被取代 |
| [**ADR-0008**](adr/ADR-0008-st7567-spi-and-pa-keying.md) | **液晶改 ST7567(SPI)、功放驱动与键控、继电器驱动链** | **已接受** |
| [ADR-0005](adr/ADR-0005-console-tech-stack-tbd.md) | 中控 PC 软件技术栈待定 | **提议** |
| [ADR-0006](adr/ADR-0006-layered-licensing-gpl-isolation.md) | 原分层授权方案（**已被取代**，见 ADR-0007） | **已被取代** |
| [ADR-0007](adr/ADR-0007-firmware-closed-source-two-repo.md) | **固件闭源与双仓结构** | 已接受 |

ADR 索引与模板见 [adr/README.md](adr/README.md)。

---

## 待补文档（Backlog）

| 文档 | 内容 | 触发时机 |
|------|------|----------|
| `09-competition-rules-compliance.md` | 6 种模式 × 规则条款 × 实现方式 × 验证证据 的可追溯矩阵 | 固件实现启动时 |
| `10-atu-tuning-algorithm-design.md` | ATU-100 算法移植说明、搜索空间、收敛性分析、仿真验证 | `atu_tuner` 实现前 |
| `11-mesh-protocol-and-security.md` | 帧格式、路由策略、HMAC 密钥管理、重放窗口 | `mesh_router` 实现前 |
| `12-power-and-endurance-budget.md` | 各工作模式电流分解与续航核算（对接 00-project-upgrade-plan.md 3.4 节） | 电源模块设计时 |
| `13-emc-and-spurious-suppression.md` | 2f₀ 衰减、PCB 布局接地策略、屏蔽 | PCB 布线前 |
| `14-production-and-factory-test.md` | 产测固件、测试工装、校准流程 | 小批量试产前 |

新增文档时请同步更新本索引，并在 `docs/02-repository-layout.md` 的文件归属决策表中登记（如涉及新类别）。

---

## 命名约定（重要）

`docs/` 下的文件**文件名用英文小写 + 连字符**，而**文件内的 H1 标题与正文全部是简体中文**。上面第 1 节的中文索引表就是中英对照映射。

| 层 | 用什么语言 | 例子 |
|----|-----------|------|
| 目录名、文件名 | **英文** | `05-hw-sw-interface-contract.md` |
| H1 标题、正文、表格 | **简体中文** | `# 05 · 软硬件接口契约` |

原因见 [02-repository-layout.md](02-repository-layout.md) §1.2：非 ASCII 路径会让 `git status`/`git log` 输出八进制转义、让 GitHub 分享链接变成百分号编码、让 CI 日志与压缩包文件名乱码。

---

## 关联区域（不在本目录，不要混放）

本目录**只放跨专业的规范与决策文档**。以下内容各有归属，请勿移入 `docs/`：

| 区域 | 放什么 | 为什么不并入 `docs/` |
|------|--------|---------------------|
| [`../hardware/`](../hardware/README.md) | 原理图、PCB、Gerber、BOM、结构件 | 专业域，且含二进制设计文件 |
| [`../software/`](../software/README.md) | 软件入口与规划要点（当前仅 `README.md`）；中控软件、共享协议、工具均**规划中，待创建**（**固件源码在私有仓**） | 专业域，参与构建 |
| [`../validation/`](../validation/README.md) | **硬件在环实测**方案、报告与原始数据 | 见下方说明 |
| [`../LICENSING.md`](../LICENSING.md)、[`../LICENSES/`](../LICENSES/README.md) | 授权映射与许可全文 | GitHub 只在仓库根识别许可 |

### 为什么 `validation/` 不并入 `docs/`

`validation/` 与 `docs/` 是**证据 vs 规范**的区别，不是"文件类型"的区别：

| | `docs/` | `validation/` |
|---|---------|---------------|
| 性质 | **规范**：应该是什么 | **证据**：实测到了什么 |
| 权威性 | 多份文档是「★ 唯一权威」 | 无权威性，是实测记录 |
| 产物 | 纯 Markdown | Markdown **+ 原始二进制数据**（`.s2p`/`.csv`/`.png`） |
| 何时用 | 设计阶段阅读 | 实验台上执行（NanoVNA / SDR / 示波器） |
| 与谁对应 | 架构与契约 | 计划书第八章 10 个验证阶段 |

如果把 `validation/` 并入 `docs/`：

1. `docs/` 将不再是「纯文档目录」，[`.gitignore`](../.gitignore) 里按 `validation/**` 写的整节忽略规则需要重写；
2. 实测报告会与标注「★ 唯一权威」的规范文档相邻，破坏本文档第 2 节的仲裁规则语义；
3. 会违反 [ADR-0002](adr/ADR-0002-hardware-software-split-monorepo.md) 确立的「顶层按**专业域**分区，不按文件类型分区」原则——验证/测量是独立专业域；
4. `validation/`（硬件在环）与私有固件仓的 `test/`（单元测试）之间那条有价值的边界会被掩盖。
