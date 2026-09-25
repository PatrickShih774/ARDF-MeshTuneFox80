# LICENSING — 本项目如何授权

> **本文件是许可归属的唯一权威映射表。**
> 状态：已建立（双仓结构版）｜适用版本：V3.7
> 相关文档：[docs/08-licensing-and-compliance.md](docs/08-licensing-and-compliance.md)、[ADR-0007 固件闭源与双仓结构](docs/adr/ADR-0007-firmware-closed-source-two-repo.md)

---

## 一、项目结构：两个仓库

本项目采用**双仓库**结构，因为**源码保密与公开仓库在技术上不可兼得**——GitHub 的可见性是仓库级的，只要仓库是 public，`git ls-files` 里的每个文件（含历史提交）都可公开读取。

| 仓库 | 可见性 | 内容 |
|------|--------|------|
| [`ARDF-MeshTuneFox80`](https://github.com/PatrickShih774/ARDF-MeshTuneFox80) | **公开** | 硬件设计、文档、**编译后的固件二进制（GitHub Releases）**；共享协议与中控 PC 软件（规划中，待创建） |
| `ARDF-MeshTuneFox80-firmware` | **私有** | ESP32-C3 固件的**全部源码**，不对外公开 |

---

## 二、为什么根目录没有单一的 `LICENSE`

本仓库同时包含四类性质不同的资产，授权意图各不相同：

| 资产 | 期望的授权行为 |
|------|---------------|
| 硬件设计（原理图 / PCB / 结构件） | **强互惠**：衍生设计必须同样开源 |
| 中控软件 / 协议定义 / 工具（规划中，待创建） | **宽松**：允许闭源集成与二次开发 |
| 文档 / 验证报告 | **便于引用**：允许转载与改编 |
| **固件二进制** | **仅限业余无线电非商业使用**；源码在私有仓 |

如果在根目录放**一个** `LICENSE`，GitHub 以及绝大多数代码扫描工具会把**整个仓库**判定为那一种许可，直接掩盖上面的区分。

因此本项目采用 [REUSE](https://reuse.software/) 风格的**按目录分层授权**：各许可全文放在 [`LICENSES/`](LICENSES/)，逐目录映射见下方第三节，源文件头部带 **SPDX 标识符**。

> **已知代价**：GitHub 仓库侧边栏会显示 *"no license"*。对多许可仓库而言，这比错误地显示单一许可**更准确**。

---

## 三、目录级授权映射表

| 路径 | 许可证（SPDX） | 全文 | 商业含义 |
|------|---------------|------|---------|
| `hardware/` | `CERN-OHL-S-2.0` | [`LICENSES/CERN-OHL-S-2.0.txt`](LICENSES/CERN-OHL-S-2.0.txt) | 强互惠。可商业制造销售，但**修改后的设计必须同样以 CERN-OHL-S v2 开源** |
| `docs/` | `CC-BY-4.0` | [`LICENSES/CC-BY-4.0.txt`](LICENSES/CC-BY-4.0.txt) | 可自由转载改编，需署名 |
| `validation/` | `CC-BY-4.0` | [`LICENSES/CC-BY-4.0.txt`](LICENSES/CC-BY-4.0.txt) | 报告可自由引用，需署名 |
| `software/master-console/`（规划中，待创建） | `Apache-2.0` | [`LICENSES/Apache-2.0.txt`](LICENSES/Apache-2.0.txt) | 允许闭源分发、商业使用 |
| `software/protocol/`（规划中，待创建） | `Apache-2.0` | [`LICENSES/Apache-2.0.txt`](LICENSES/Apache-2.0.txt) | 协议规范公开，鼓励第三方实现 |
| `software/tools/`（规划中，待创建）、`scripts/` | `Apache-2.0` | [`LICENSES/Apache-2.0.txt`](LICENSES/Apache-2.0.txt) | 工具链不进入固件镜像 |
| **固件二进制**（GitHub Releases） | **`LicenseRef-ARDF-NC-1.0`** | [`LICENSES/LicenseRef-ARDF-NC-1.0.txt`](LICENSES/LicenseRef-ARDF-NC-1.0.txt) | **仅限业余无线电非商业用途**；不授予源代码、不要求公开源码 |
| **固件源码**（私有仓） | 同上（私有仓内另有 `LICENSE`） | 不在本仓库 | 不对外授权 |
| **例外**：`hardware/reference/` | **各原始项目许可** | 不在本仓库 | **只读参考，不纳入本仓库任何许可范围** |

---

## 四、固件：为什么源码不公开，以及许可覆盖什么

### 4.1 覆盖范围

`LicenseRef-ARDF-NC-1.0`（[ARDF 业余无线电非商业许可 1.0](LICENSES/LicenseRef-ARDF-NC-1.0.txt)）**只覆盖编译后的二进制形式**：

| | 说明 |
|---|---|
| **授予** | 为**业余无线电用途**安装、运行、使用固件；制作个人备份；**非商业性**再分发完整原始副本 |
| **不授予** | 对**源代码**的任何权利 |
| **不要求** | 权利人**没有义务**提供源代码；本许可**不要求**任何人公开源码 |
| **禁止** | 商业性使用、修改与逆向工程、移除版权标识 |

这与 GPL 等 copyleft 许可有**实质区别**：GPL 下分发二进制即触发源码公开义务，本许可下不存在该义务。

### 4.2 「业余无线电用途」包括什么

- 持有效业余无线电操作证书的个人，为学习、实验、训练或通联使用
- 业余无线电测向（ARDF）竞赛与训练
- 非营利组织、学校或无线电管理机构举办的公益性活动

**不包括**：销售设备、商业培训、收费技术支持、以营利为目的的竞赛等。

> 完整的商业性使用定义见许可正文第 1.4 条。

### 4.3 与 GPL 的历史关系（重要）

本项目的固件**曾**声明为 `GPL-3.0-or-later`。该声明**已作废**，原因见
[ADR-0007](docs/adr/ADR-0007-firmware-closed-source-two-repo.md)。

由此产生的连带变化：

- [ADR-0006](docs/adr/ADR-0006-layered-licensing-gpl-isolation.md) 的「GPL 传染性隔离 / 独立 `algo` 分区 / 进程间通信」设计**整体作废**——没有 GPL 就没有传染问题。
- [docs/03-software-architecture.md](docs/03-software-architecture.md) 的分区表中不再有 `algo` 分区。
- 公开仓的历史已重写，以彻底移除固件源码与 GPL 全文。

---

## 五、`LICENSES/` 目录

| 文件 | SPDX 标识符 | 用途 |
|------|------------|------|
| `LICENSES/CERN-OHL-S-2.0.txt` | `CERN-OHL-S-2.0` | 硬件 |
| `LICENSES/Apache-2.0.txt` | `Apache-2.0` | 中控软件 / 协议 / 工具 / 脚本 |
| `LICENSES/CC-BY-4.0.txt` | `CC-BY-4.0` | 文档 / 验证报告 |
| `LICENSES/LicenseRef-ARDF-NC-1.0.txt` | `LicenseRef-ARDF-NC-1.0` | **固件二进制**（自定义许可） |
| `LICENSES/README.md` | — | 全文获取方式与校验方法 |

> 🔴 标准许可（前三份）全文必须**逐字节原样**放置，禁止改写、精简或重排版；获取方式与校验方法见 [`LICENSES/README.md`](LICENSES/README.md)。
> `LicenseRef-*` 是本项目的**自定义许可**（REUSE 规范允许），正文由本项目自行撰写，可直接编辑，但改动需同步更新本文件与 [docs/08](docs/08-licensing-and-compliance.md)。

---

## 六、源文件 SPDX 头（强制）

每个源文件顶部必须声明其许可：

```c
/*
 * ARDF-MeshTuneFox80 - <模块中文名>
 * ...
 * SPDX-License-Identifier: Apache-2.0
 * Copyright (c) 2026 ARDF-MeshTuneFox80 Contributors
 */
```

对应关系：

| 文件所在路径 | `SPDX-License-Identifier` |
|-------------|--------------------------|
| `software/master-console/**`（规划中，待创建）、`software/protocol/**`（规划中，待创建）、`software/tools/**`（规划中，待创建）、`scripts/**` | `Apache-2.0` |
| `hardware/**`（源设计文件、BOM、结构件） | `CERN-OHL-S-2.0` |
| **私有固件仓** `**` | `LicenseRef-ARDF-NC-1.0` |

> ⚠️ **固件源码的任何片段都不得提交到本公开仓**——包括 Issue 与 PR 描述。见 [CONTRIBUTING.md](CONTRIBUTING.md) 安全红线。

---

## 七、第三方内容与依赖

### 7.1 外部参考设计（不适用本项目许可）

`hardware/reference/` 下的内容来自外部项目，**版权归各自原作者**：

| 来源 | 链接 | 状态 |
|------|------|------|
| N7DDC-ATU-100-mini-and-extended-boards (Dfinitski) | https://github.com/Dfinitski/N7DDC-ATU-100-mini-and-extended-boards | ⚠️ **许可待核对** |
| ATU-100 by N7DDC | https://github.com/n7ddc/ATU-100 | ⚠️ 待核对 |

> ⚠️ **待办**：投板与实现前必须逐文件确认原始许可条款；若无明确许可，默认"保留所有权利"。本项目**只借鉴算法思想与公开电路拓扑**，禁止逐行复制代码或设计文件。详见 [docs/08](docs/08-licensing-and-compliance.md) §4.1。

### 7.2 第三方依赖

| 依赖 | 许可 | 说明 |
|------|------|------|
| ESP-IDF | Apache-2.0 | 固件框架 |
| FreeRTOS（随 ESP-IDF） | MIT | — |
| mbedTLS（随 ESP-IDF） | Apache-2.0 | — |
| Unity（随 ESP-IDF） | MIT | 仅测试用，不进固件镜像 |

> ⚠️ **注意**：ESP-IDF 为 `Apache-2.0`，其**版权声明与 NOTICE 必须随固件二进制一并提供**。本项目采用闭源固件时，仍需在 Release 页面或固件的「关于」信息中保留这些声明。`NOTICE` 文件待创建。

---

## 八、贡献者许可约定

本公开仓的贡献按下表授权：

| 贡献区域 | 授权协议 |
|---------|---------|
| `hardware/` | `CERN-OHL-S-2.0` |
| `software/master-console/`（规划中，待创建）、`software/protocol/`（规划中，待创建）、`software/tools/`（规划中，待创建）、`scripts/` | `Apache-2.0` |
| `docs/`、`validation/` | `CC-BY-4.0` |
| **固件源码** | **不接受外部贡献**（私有仓，非公开） |

- 贡献者**保留版权**，当前不要求签署 CLA。
- 若未来为支持双许可模式而引入 CLA，须提前在 [CONTRIBUTING.md](CONTRIBUTING.md) 中公告。

---

## 九、常见问题

**Q：我只想用硬件设计做板卖套件，可以吗？**
A：可以。CERN-OHL-S v2 允许商业制造与销售。但如果你**修改了设计**，必须把修改后的**源设计文件**（原理图 / PCB 源文件，不只是 Gerber）同样以 CERN-OHL-S v2 公开，并在交付物中附带许可声明。

**Q：固件源码会公开吗？**
A：不会。固件源码存放在**私有仓**，不对外发布。公共发布的只有编译后的二进制（GitHub Releases）。

**Q：我能把固件二进制装在自己做的设备上卖吗？**
A：不能。`LicenseRef-ARDF-NC-1.0` 禁止商业性使用。卖搭载本固件的设备属于商业性使用，无论硬件是否由你自行按 CERN-OHL-S 设计。

**Q：我能把固件二进制放到自己的网站供人下载吗？**
A：可以，但必须**非商业**、提供**完整未修改**的副本、附随完整许可文本、保留全部版权标识，且不得收费（复制介质成本除外）。建议直接链接到本仓 Releases。

**Q：为什么 GitHub 显示 "no license"？**
A：因为本仓库是多许可仓库，根目录没有单一 `LICENSE`。这是**有意为之**，见第二节。

**Q：ESP-IDF 是 Apache-2.0，我的闭源固件用了它，需要开源吗？**
A：不需要。Apache-2.0 不是 copyleft，不要求衍生作品开源。但你**必须**保留其版权声明、许可文本与 NOTICE——分发固件二进制时同样适用。

---

## 十、关联文档

| 文档 | 用途 |
|------|------|
| [docs/08-licensing-and-compliance.md](docs/08-licensing-and-compliance.md) | 分层授权完整说明、射频合规、落地清单 |
| [ADR-0007 固件闭源与双仓结构](docs/adr/ADR-0007-firmware-closed-source-two-repo.md) | 本次结构的决策背景 |
| [ADR-0006 分层授权与 GPL 隔离方案](docs/adr/ADR-0006-layered-licensing-gpl-isolation.md) | **已被 ADR-0007 取代** |
| [docs/07-coding-standards.md](docs/07-coding-standards.md) | 源文件 SPDX 头规范 |
| [software/README.md](software/README.md) | 软件入口与规划要点（中控 PC 软件 / 共享协议 / 工具均规划中，待创建） |
| [LICENSES/README.md](LICENSES/README.md) | 许可全文获取与校验 |
| [CONTRIBUTING.md](CONTRIBUTING.md) | 贡献者许可约定与安全红线 |
