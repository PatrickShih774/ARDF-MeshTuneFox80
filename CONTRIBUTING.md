# 贡献指南（CONTRIBUTING）

感谢参与 **ARDF-MeshTuneFox80** 项目！
本文件说明协作流程与硬性规则。提交任何改动前请先读完。

---

## 1. 代码托管与分支模型

| 分支 | 用途 | 规则 |
| --- | --- | --- |
| `main` | **稳定分支**，只接受已发布或即将发布的代码 | 禁止直接推送；只能由 PR 合入；每次合入需可构建 |
| `develop` | 集成分支，日常开发的汇聚点 | PR 默认目标分支；构建与测试必须全绿 |
| `feature/*` | 新功能 | 从 `develop` 切出，例：`feature/mesh-router-neighbor-table` |
| `fix/*` | 缺陷修复 | 从 `develop` 切出，例：`fix/atu-relay-release-time` |
| `hw/*` | **硬件改动**（原理图 / PCB / BOM / 结构件） | 从 `develop` 切出，例：`hw/atu-relay-footprint` |
| `docs/*` | 文档与 ADR | 从 `develop` 切出，例：`docs/adr-0007-...` |

流程：

```text
切分支 → 本地自检（见 §3） → PR 到 develop → 评审 → 合入
→ 发布前由 develop 合并到 main 并打 tag
```

- 分支名全小写，用连字符分词。
- 一个 PR 只做一件事；混装软硬件改动的 PR 会被要求拆分。
- 合并前请**变基（rebase）**到最新 `develop`，保持线性历史。

---

## 2. 提交信息规范

采用 **Conventional Commits**：

```text
<type>(<scope>): <简短描述>

<可选正文：为什么改、怎么验证的>

<可选脚注：关联 Issue / ADR 编号>
```

**type** 取值：`feat`、`fix`、`docs`、`refactor`、`test`、`build`、`chore`、`perf`。

**scope** 取值（本项目允许的集合）：

| scope | 含义 |
| --- | --- |
| `fw` | 固件（**私有仓**） |
| `hw` | 硬件（`hardware/`） |
| `docs` | 文档与 ADR（`docs/`、各 `README.md`） |
| `protocol` | 通信协议定义（`software/protocol/`，规划中，待创建） |
| `console` | 中控 PC 软件（`software/master-console/`，规划中，待创建） |
| `ci` | CI、构建与仓库级脚本（`.github/`、`scripts/`） |

> ⚠️ **固件改动不在本仓提交**：固件全部源码位于私有仓 `ARDF-MeshTuneFox80-firmware`，
> 其提交规范沿用本节约定；本公开仓只接收共享协议、中控软件、工具、硬件与文档改动。

**中文示例**：

1. `feat(fw): 增加 ESP-NOW 邻居表过期淘汰逻辑`
   （正文：邻居超过 30 秒未收到心跳即标记失效，避免路由表无限膨胀；已用两台设备验证。）
2. `fix(hw): 修正 ATU 继电器驱动 1µF 反峰电容封装错误`
   （正文：原封装 0805 耐压不足，改为 1206/50V；BOM 同步更新，成本 +0.03 元/台。）
3. `docs(protocol): 明确 TELEMETRY 帧 SWR 字段为 ×100 定点`
   （正文：此前未写定量纲，双端实现出现 100 倍歧义；已同步 update schema。）

要求：

- 标题行 **不超过 72 字符**，用中文祈使句，句末不加句号。
- 一次提交只包含一个逻辑改动。
- 破坏性变更必须在脚注写 `BREAKING CHANGE:`，并说明对软硬件接口的影响。
- 提交信息中**禁止**出现呼号、真实姓名、密钥等个人信息。

---

## 3. 评审要求（按改动类型）

### 3.1 软件改动

必须满足：

- [ ] `idf.py build` 通过（固件，**在私有固件仓内执行**）；中控/工具侧对应的测试命令通过。
- [ ] **单元测试通过**：固件侧 Unity / pytest-embedded（**在私有固件仓内执行**）；中控侧纯逻辑单元测试。
- [ ] 新增或修改的逻辑有对应测试；缺陷修复附**能复现原问题的测试**。
- [ ] 不引入新的编译告警；`-Werror` 下可构建。
- [ ] 若改动了协议或接口，**先改 `software/protocol/`（规划中，待创建）**，再重新生成代码。
- [ ] 未手改 `software/protocol/generated/`（规划中，待创建）中的任何文件。
- [ ] 编码规范符合 [docs/07-coding-standards.md](docs/07-coding-standards.md)。

### 3.2 硬件改动

必须随 PR 附带：

- [ ] **原理图 / PCB 变更说明**：改了哪一页、哪个网络、为什么改。
- [ ] **BOM 影响**：新增/删除/替换的元件、单价变化、单台成本影响。
- [ ] 若涉及软硬件接口（GPIO、电平、时序）→ 同步更新
      [docs/05-hw-sw-interface-contract.md](docs/05-hw-sw-interface-contract.md)，并**在 PR 中显式提醒评审人**。
- [ ] 若涉及既有 ADR 的约束（如继电器型号、LCD 总线），需说明是否与 ADR 冲突；
      冲突则先提出新 ADR。
- [ ] 输出文件（Gerber/钻孔）如需入库，确认未混入临时文件。
- [ ] 影响验证判据的改动，需同步更新对应的 `validation/stage-*/README.md`。

### 3.3 文档改动

- [ ] 相对链接可解析（本地用 Markdown 预览或链接检查工具过一遍）。
- [ ] ADR 改动遵守 [docs/adr/README.md](docs/adr/README.md)：**已接受的 ADR 不得改结论**，
      要变更请新建 ADR 并声明取代关系。

---

## 4. 目录归属规则

新增文件请按下表放置，完整规范见 [docs/02-repository-layout.md](docs/02-repository-layout.md)。

| 你要新增的东西 | 放这里 |
| --- | --- |
| 固件功能组件 | **私有固件仓**的 `components/<组件名>/` |
| 固件单元测试 | **私有固件仓**的 `test/` |
| 固件专用脚本（依赖 ESP-IDF 工具链） | **私有固件仓**的 `tools/` |
| 中控软件源码 | `software/master-console/src/ardf_console/<子包>/`（规划中，待创建） |
| 中控单元测试 | `software/master-console/tests/`（规划中，待创建） |
| 协议人读规范 | `software/protocol/spec/`（规划中，待创建） |
| 协议机器可读定义 | `software/protocol/schema/`（规划中，待创建） |
| 协议抓包/十六进制样例 | `software/protocol/examples/`（规划中，待创建） |
| 跨子工程工具（纯宿主机） | `software/tools/<工具名>/`（规划中，待创建） |
| 仓库级流水线脚本 | `scripts/` |
| 原理图 / PCB / Gerber / BOM / 结构件 | `hardware/<模块名>/` |
| 跨专业文档（目录规范、架构、接口契约、编码规范、许可） | `docs/` |
| 架构决策记录 | `docs/adr/ADR-XXXX-标题.md` |
| 硬件在环验证计划与报告 | `validation/stage-N-*/` |
| 跨阶段验证汇总 | `validation/reports/` |
| CI / Issue / PR 模板 | `.github/` |

判定要点：

1. **跨子工程才上移**：只服务固件的放**私有固件仓**的 `tools/`，被两个以上子工程复用的放 `software/tools/`（规划中，待创建）。
2. **原始数据不入库**：实测 `.csv`/`.s2p`/大图放 `validation/**/raw/`（已被忽略）。
3. **不确定就问**：在 Issue 中提出，不要自行新建一级目录。

> 📌 上表末尾几行的 `software/**` 路径**都还没开始写**，三块软件内容（中控 PC 软件、共享协议、工具）均为**规划中，待创建**；本仓 `software/` 当前只有 `README.md`（软件入口与规划要点）。

---

## 5. 编码规范

统一入口：[docs/07-coding-standards.md](docs/07-coding-standards.md)。要点：

- 语言版本：固件 C99（ESP-IDF 风格）、中控 Python 3.11+（PEP 8 + 类型标注）。
- 格式与换行由 [.editorconfig](.editorconfig) 约束：UTF-8、LF、文件末尾换行。
- 命名：组件与文件用 `snake_case`；宏用 `UPPER_SNAKE`；常量禁止魔法数字，
  必须在组件头文件中具名定义。
- 注释用中文，说明"为什么"而非"是什么"。
- 禁止提交注释掉的大段代码；历史交给 Git。

---

## 6. 许可证与贡献者协议

本项目采用**分层授权**。目录级授权映射的**唯一权威**是 [`LICENSING.md`](LICENSING.md)（各许可全文在 [`LICENSES/`](LICENSES/README.md)），决策背景见 [ADR-0007 固件闭源与双仓结构](docs/adr/ADR-0007-firmware-closed-source-two-repo.md)：

| 目录 | 许可（SPDX） |
| --- | --- |
| `hardware/` | `CERN-OHL-S-2.0` |
| 固件（私有仓源码 + Releases 二进制） | `LicenseRef-ARDF-NC-1.0`：仅限业余无线电非商业用途 |
| `software/master-console/`（规划中，待创建）、`software/protocol/`（规划中，待创建）、`software/tools/`（规划中，待创建）、`scripts/` | `Apache-2.0` |
| `docs/`、`validation/` | `CC-BY-4.0` |
| ATU 调谐算法、Mesh 路由算法 | 商业授权（闭源，不在本仓库公开部分） |
| `hardware/reference/` | 各原始项目许可（**不纳入本仓库授权范围**） |

> 本仓库根目录**没有单一 `LICENSE`**：多许可仓库放根许可会让工具把整仓判定为单一协议。这是有意为之，说明见 [`LICENSING.md`](LICENSING.md) 第一节。

**提交即表示你同意**：你的贡献将按上述对应目录的许可发布，
且你有权这样做（不得提交来源不明或与许可冲突的第三方代码）。

- 新增源文件必须带 **SPDX 标识符**（规范见 [docs/07-coding-standards.md](docs/07-coding-standards.md) §2.2）。
- 引入第三方代码/库前，必须先在 PR 中说明其许可证，并登记到
  [docs/08-licensing-and-compliance.md](docs/08-licensing-and-compliance.md) 的许可证台账。
- **禁止**把私有固件源码的任何片段提交到本公开仓——包括源码、头文件、构建文件与注释。
- **

### 🔴 双仓分离纪律（机器校验）

| 内容 | 归属仓库 |
|------|---------|
| 硬件设计、文档、验证报告、许可 | **公开仓** `ARDF-MeshTuneFox80` |
| **固件源码、构建文件、工具** | **私有仓** `ARDF-MeshTuneFox80-firmware` |

**提交前请运行：**

```powershell
pwsh -File scripts/check-repo-separation.ps1
```

脚本用 `git ls-files` 扫描两个仓库的**已入库文件**，发现越界即退出码 1：

- 公开仓禁止出现：`.c/.h/.cpp` 源码、`CMakeLists.txt`、`sdkconfig*`、
  `partitions.csv`、`Kconfig*`、`version.txt`、`*.bin/.elf/.map/.hex`
- 私有仓禁止出现：KiCad/EDA 源文件、Gerber、`step/stl/dxf`、PDF、BOM 表
- 公开仓 `software/` 只允许 `README.md`（双仓结构说明）

> ⚠️ **一旦越界并已推送，仅 `git rm` 不够**——历史里仍有该文件，
> 必须**删除并重建公开仓**（本项目已因此重建过一次，见
> [docs/08](docs/08-licensing-and-compliance.md) §6）。固件源码严禁出现在本公开仓的任何文件、Issue 或 PR 中**；确需讨论固件行为时，
  只描述**接口与可观测行为**，附协议或日志层面的证据，不贴源码。
- **禁止**把 `hardware/reference/` 下的第三方内容复制进本项目的 `hardware/` 或 `software/`。
- 闭源算法的实现细节不得出现在本仓库的任何公开文件中（包括 Issue 与 PR 描述）。
- 上述隔离为工程措施，**不构成法律意见**；商业化前需律师复核。

---

## 7. 安全红线

以下内容**任何情况下都不得提交**：

1. **密钥与凭据**：HMAC 密钥、WiFi/ESP-NOW 密钥、OTA 签名私钥、设备出厂密钥。
2. **呼号与个人信息**：真实呼号、姓名、电话、住址、身份证号、GPS 精确坐标。
3. **实测原始数据大文件**：`validation/**/raw/` 下的 `.csv`/`.s2p`/大图——
   放本地或外部存储，只把结论写进 `report-*.md`。
4. 未获授权公开的第三方资料（厂商受 NDA 约束的原理图、手册）。

若**误提交**了上述内容：

1. 立即在 Issue 中说明（不要只删文件——Git 历史仍保留）；
2. 立刻**轮换**泄露的密钥；
3. 由维护者评估是否需要重写历史（`git filter-repo`）并通知所有协作者重新克隆。

---

## 8. 沟通与求助

- 缺陷、需求、硬件问题分别使用对应的 Issue 模板（见 [.github/OVERVIEW.md](.github/OVERVIEW.md)）。
- 架构级分歧请先提 ADR（提议状态）讨论，不要在 PR 里争论实现细节。
- 涉及射频发射的测试必须由具备业余无线电操作资质的人员在场，并使用假负载或合规天线。

再次感谢你的贡献！
