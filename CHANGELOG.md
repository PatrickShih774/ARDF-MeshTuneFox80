# 更新日志

本文件记录本项目所有值得注意的变更。
格式参考 [Keep a Changelog](https://keepachangelog.com/zh-CN/1.1.0/)，
版本号遵循 [语义化版本](https://semver.org/lang/zh-CN/)。

分类约定：`新增`（Added）、`变更`（Changed）、`弃用`（Deprecated）、
`移除`（Removed）、`修复`（Fixed）、`安全`（Security）。

---

## [Unreleased]

> **本轮仅建立架构骨架与文档，不含任何实现代码。**

### 新增

- 建立**专业域分区**的仓库骨架：顶层划分 `hardware/`、`software/`、`docs/`、
  `validation/`、`scripts/`、`.github/`，并配套 `.editorconfig`、`.gitattributes`、
  `CONTRIBUTING.md`、`CHANGELOG.md`。
- 建立 **docs 文档体系**：`docs/00` ~ `docs/08` 共 9 份规范文档，
  以及 `docs/adr/` 下 **7 份**架构决策记录（ADR-0001 ~ ADR-0007）。
- 建立 **validation 十阶段验证目录**：`stage-0-rf-frontend` ~
  `stage-9-competition-modes` 与 `reports/`，每阶段含验证计划 `README.md`。
- 建立 **许可结构（REUSE 风格）**：根目录 [`LICENSING.md`](LICENSING.md)（目录级授权映射，唯一权威）
  与 [`LICENSES/`](LICENSES/README.md)（许可全文目录 + 获取与校验说明）。
  根目录**不放置单一 `LICENSE`**，避免 GitHub 与扫描工具把整仓（含硬件）判定为单一许可。
  理由见 [docs/08-licensing-and-compliance.md](docs/08-licensing-and-compliance.md) §1。
- 新增**固件自定义许可** [`LicenseRef-ARDF-NC-1.0`](LICENSES/LicenseRef-ARDF-NC-1.0.txt)
  （ARDF 业余无线电非商业许可 1.0）。
- 建立 **GitHub 协作设施占位**：`.github/ISSUE_TEMPLATE/` 含 `.gitkeep`，**未配置真实 CI**。
  `.github/workflows/` **暂不入库**：Git 不跟踪空目录，而向该路径推送要求
  Personal Access Token 具备 `workflow` scope，故等真正编写 CI YAML 时再一并创建
  （见 [.github/OVERVIEW.md](.github/OVERVIEW.md) §5）。
- 建立**仓库级脚本区占位**：`scripts/`（构建辅助、发布打包、文档检查、BOM 成本核算）。
- **放入四份许可全文**（REUSE 风格 `LICENSES/`）：`CERN-OHL-S-2.0.txt`（官方 ohwr 源，13708 B）、
  `Apache-2.0.txt`（11358 B）、`CC-BY-4.0.txt`（18657 B）、`LicenseRef-ARDF-NC-1.0.txt`（本工程自撰，8084 B）。
  SHA-256 已登记到 [LICENSES/README.md](LICENSES/README.md) §四，并加 `.gitattributes` 规则
  `LICENSES/*.txt -text` 保证**许可全文逐字节不被行尾转换**。
- 新增 **[`NOTICE`](NOTICE)**：第三方组件声明台账（ESP-IDF Apache-2.0、FreeRTOS MIT、
  mbedTLS Apache-2.0、Unity MIT），并明确 **`NOTICE` 必须随固件二进制一并分发**——
  闭源不等于可以省略第三方声明。
- 新增 **[`.gitignore`](.gitignore) 防泄漏护栏**：`software/firmware/`、`**/components/*/src/*.c`、
  `main/app_main.c`、`sdkconfig.defaults`、`partitions.csv` 及 `hardware/reference/**` 下的
  第三方源码/图纸类型一律不入库，作为固件源码误入公开仓的最后一道保险。

### 变更

- **改为双仓库结构**：公开仓只保留硬件、文档、共享协议、中控软件与**固件二进制（Releases）**；
  固件源码迁入私有仓 `ARDF-MeshTuneFox80-firmware`。决策见
  [ADR-0007](docs/adr/ADR-0007-firmware-closed-source-two-repo.md)。
- **固件许可由 `GPL-3.0-or-later` 改为 `LicenseRef-ARDF-NC-1.0`**：
  新许可**只覆盖编译后的二进制**，仅限业余无线电非商业用途，**不授予源代码、不要求公开源码**。
  由此 [ADR-0006](docs/adr/ADR-0006-layered-licensing-gpl-isolation.md)
  （分层授权与 GPL 隔离方案）**整体作废**，状态改为「已被取代」；
  [docs/03-software-architecture.md](docs/03-software-architecture.md) 分区表中的
  独立算法分区（`algo`）随之删除。
- **`plan.md` 迁入 `docs/00-project-upgrade-plan.md`，并删除根目录副本**：需求与技术指标基线
  属专业域文档，按 [docs/02-repository-layout.md](docs/02-repository-layout.md) 归入 `docs/`，
  使仓库根目录只保留社区元文件（README / LICENSING / LICENSES / CHANGELOG / CONTRIBUTING）。
  迁移保真性已校验：79 个标题锚点行号偏移恒为 +6，10 项关键硬指标数值一致，
  字节数差值与元信息块长度吻合。
- **`docs/` 与 `docs/adr/` 的文件名全部改为英文小写 + 连字符**（共 15 个文件，如
  `01-项目概述.md` → `01-project-overview.md`、`ADR-0001-采用ESP-IDF而非Arduino.md` →
  `ADR-0001-adopt-esp-idf-over-arduino.md`）。**文件名英文、文件内 H1 标题与正文仍为简体中文**，
  中文索引表保留在 [docs/README.md](docs/README.md)。理由是落实
  [ADR-0002](docs/adr/ADR-0002-hardware-software-split-monorepo.md) 的「目录与文件名英文」方针：
  非 ASCII 路径会导致 `git status`/`git log` 输出八进制转义、GitHub 分享链接被百分号编码、
  CI 日志与压缩包文件名乱码。同步替换全仓 **80 个文件、360 处**引用。
- **许可标识统一改用 SPDX**：`CERN-OHL-S-2.0` / `Apache-2.0` / `CC-BY-4.0` / `LicenseRef-ARDF-NC-1.0`，
  与 [docs/07-coding-standards.md](docs/07-coding-standards.md) 的源文件 SPDX 头要求对齐。
- **`.github/README.md` 改名为 `.github/OVERVIEW.md`**：消除 GitHub 的 README 语义歧义——
  GitHub 会把子目录的 `README.md` 渲染在该目录页面上，并且在根 `README.md` 缺失时
  **静默**将其用作仓库首页 README（查找顺序：根 → `.github/` → `docs/`）。改名后不再参与回退。
- **撤回中文名「狐网天调80」**：新中文名尚未确定，故从所有对外文档中移除。
  `README.md` 副标题改为「中文名：**待定**」。
  `docs/00-project-upgrade-plan.md` 作为 V3.7 **需求基线快照**，正文**保持逐字原样**
  （其中 3 处仍含该名称），改为在文件头部元信息中声明该名称已作废、新名待定。
- **`docs/README.md`**：新增「命名约定」「关联区域」两节，并补充
  「为什么 `validation/` 不并入 `docs/`」的判定依据（证据 vs 规范）。
- **`CONTRIBUTING.md`**：许可章节改为引用 `LICENSING.md`；新增安全红线
  「**固件源码严禁出现在本公开仓的任何文件、Issue 或 PR 中**」。
- 补充 `docs/02-repository-layout.md` 的「仓库根目录允许放什么」表与判定依据
  （GitHub 社区健康文件的查找顺序、发布工具约定）。

### 移除

- **固件源码迁出本仓**：`software/firmware/` 的 94 个文件移至私有仓
  `ARDF-MeshTuneFox80-firmware`，本公开仓不再包含任何固件源码。
- **`software/` 目录大幅简化（21 → 1 个文件）**：删除 `software/master-console/`、
  `software/protocol/`、`software/tools/`、`software/docs/` 四套骨架。
  这四套骨架共 20 个文件，其中 15 个是**空的 `.gitkeep` 占位**——它们是为"将来要写的代码"
  预留的目录，而固件源码迁走后已无承载对象。**不为不存在的代码预建目录**；
  将来真正开始写时，按 [docs/02-repository-layout.md](docs/02-repository-layout.md) §3.2
  的文件归属决策表创建即可。现 `software/` 只保留
  [`README.md`](software/README.md)（软件入口，含各部分的规划要点）。
- **`LICENSES/GPL-3.0-or-later.txt`**：固件不再使用 GPL，全文随之删除。
- **修正 7 处相对路径断链**：`software/firmware/README.md`（迁移前）的 6 处 `../../../docs/`
  层级多了一层（应为 `../../docs/`），`hardware/reference/README.md` 的 `../LICENSING.md`
  应为 `../../LICENSING.md`。

### 决策记录

- **[ADR-0007](docs/adr/ADR-0007-firmware-closed-source-two-repo.md) 固件闭源与双仓结构**：
  源码保密与公开仓库在技术上不可兼得（GitHub 可见性是仓库级的，历史提交同样公开）；
  且 GPL 下"只发布二进制"在法理上不成立。故拆分为公开仓 + 私有固件仓，
  固件改用只覆盖二进制的自定义非商业许可。
  代价写实：失去社区贡献、用户无法审计固件（缓解措施为公开行为规格与实测报告，
  做到"可验证不可修改"）、需重写公开仓历史。
- **[ADR-0006](docs/adr/ADR-0006-layered-licensing-gpl-isolation.md) 已被 ADR-0007 取代**：
  整体闭源后 copyleft 传染问题不存在，「独立可执行程序 + 独立分区 + 进程间通信」
  的隔离设计失去意义，徒增复杂度与法律不确定性。
- **`validation/` 保持顶层目录，不并入 `docs/`**：它是**实测证据**而非**规范文档**，
  产物含原始二进制数据（`.s2p`/`.csv`/`.png`），生命周期与工具链均不同，
  且并入会违反 ADR-0002 的「顶层按专业域分区」原则。判定依据见
  [docs/README.md](docs/README.md) 末节。

### 说明

- 本轮**不含任何实现代码**：无 `.py/.c/.h/.ino/.ts/.js/.yml` 业务实现。
- 硬件设计与固件实现由后续迭代补齐。
- 公开仓历史已重写为单一提交，以彻底移除固件源码与 GPL 全文。

### 待办（本轮未完成）

- **首次固件构建并发布 Release**（在私有仓执行）：`ardf-node.bin` + 分区表 + `SHA256SUMS`，
  并在 Release 页面**附 [`NOTICE`](NOTICE) 与固件许可全文**（Apache-2.0/MIT 的硬性要求）。
- 自定义许可 `LicenseRef-ARDF-NC-1.0` 的「商业性使用」边界需律师复核（**商业化前必须**）。
- 按 [docs/README.md](docs/README.md) 的待补清单补齐 `09` ~ `14` 号文档。
- 各源文件添加 SPDX 标识符（随实现推进）。

### 已完成（本轮收尾）

- ✅ 四份许可全文放入 `LICENSES/` 并登记 SHA-256。
- ✅ 创建 [`NOTICE`](NOTICE) 第三方声明台账。
- ✅ **核对 ATU-100 原始许可** → 结论：`Dfinitski/N7DDC-ATU-100-*` **无许可（保留所有权利）**，
  原版仓库 `n7ddc/ATU-100` **链接已失效（HTTP 404）**。据此：
  - 明确「**只借鉴思想/方法/电路拓扑，严禁复制任何内容**」的处理规则；
  - `hardware/reference/` 改为**只放本工程自撰说明**，不放任何上游材料；
  - 结论写入 [hardware/reference/README.md](hardware/reference/README.md) §2、
    [docs/08](docs/08-licensing-and-compliance.md) §4.1、[LICENSING.md](LICENSING.md) §7.1。
- ✅ `.gitignore` 加防泄漏护栏，并修正其中已过时的内容
  （已撤回的中文名、`docs/02-仓库目录规范.md` 旧文件名、`software/firmware` 旧路径）。

---

## 版本命名约定

- `MAJOR`：软硬件接口契约发生不兼容变更（如 GPIO 分配、协议主版本）。
- `MINOR`：向后兼容的新功能（新报文、新赛事模式、新工具）。
- `PATCH`：向后兼容的缺陷修复与文档更正。

发布时须与本仓库 tag 对应，并在 Release 中附带固件 bin、Gerber、BOM 与验证报告。
