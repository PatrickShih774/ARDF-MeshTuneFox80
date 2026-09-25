# GitHub 协作设施（.github/）

本目录规划仓库在 GitHub 上的协作设施。**本轮仅占位，未配置真实 CI。**

## 1. Issue 模板（规划中）

| 模板 | 用途 | 必填要点 |
| --- | --- | --- |
| 缺陷（Bug） | 软件或硬件功能异常 | 复现步骤、期望/实际行为、固件版本、硬件批次 |
| 需求（Feature） | 新功能或改进 | 使用场景、验收判据、影响范围（固件/中控/硬件） |
| 硬件问题（Hardware） | 原理图/PCB/BOM/结构件问题 | 板本号、原理图页号、实测数据、替代方案 |

## 2. PR 模板（规划中）

必须包含：

- 变更类型（`fw` / `hw` / `docs` / `protocol` / `console` / `ci`）
- 关联 Issue 或 ADR 编号
- **硬件改动**：原理图/PCB 变更说明 + BOM 影响
- **软件改动**：`idf.py build` 与单元测试结果（固件侧在**私有仓**执行；本仓不接收固件源码）
- 文档更新清单、自检清单

## 3. CI（规划中，尚未启用真实配置）

规划中的流水线：

| Job | 触发路径 | 内容 |
| --- | --- | --- |
| 固件构建 | **私有固件仓**（CI 在私有仓运行，产物发布到本仓 Releases） | ESP-IDF（v5.x，`esp32c3`）`idf.py build` |
| 固件单元测试 | **私有固件仓**（CI 在私有仓运行） | 宿主机侧 Unity / pytest-embedded 单元测试 |
| 中控测试 | `software/master-console/**`（规划中，待创建）、`software/protocol/**`（规划中，待创建） | 协议编解码与调度逻辑单元测试（技术栈待定）；**CI 随代码落地后启用** |
| 协议生成一致性 | `software/protocol/**`（规划中，待创建） | 校验 `generated/` 与 `schema/` 一致（禁止手改产物）；**CI 随代码落地后启用** |
| 文档链接检查 | `**/*.md` | 相对链接、锚点、图片路径校验 |
| 硬件输出检查 | `hardware/**` | Gerber/BOM 存在性与命名规范检查 |

> 实现时注意：本仓 CI 只覆盖中控、协议、文档与硬件；**固件构建已移至私有仓**，
> 不再由本仓流水线触发（协议变更后由私有仓 CI 重新构建并发布，见
> [ADR-0002](../docs/adr/ADR-0002-hardware-software-split-monorepo.md)）。

> ⚠️ **中控测试**与**协议生成一致性**两条流水线所依赖的目录——`software/master-console/`（规划中，待创建）
> 与 `software/protocol/`（规划中，待创建）——**目前并不存在**（本仓 `software/` 只有 `README.md`），
> 因此这两条 CI 只是规划：**将随代码落地后启用**。当前实际可跑的是文档链接检查与硬件输出检查。

## 4. Release 产物（规划中）

| 产物 | 内容 |
| --- | --- |
| 固件 bin | `ardf-node.bin`、分区表、OTA 包 + `SHA256SUMS`（由**私有仓**的 CI 构建后发布到本仓 Release） |
| **许可与第三方声明** | 🔴 **必须随附**：[`NOTICE`](../NOTICE)（ESP-IDF 等第三方声明，Apache-2.0/MIT 要求）与 [`LICENSES/LicenseRef-ARDF-NC-1.0.txt`](../LICENSES/LicenseRef-ARDF-NC-1.0.txt)（固件许可全文） |
| Gerber | Gerber + 钻孔文件（zip） |
| BOM | BOM CSV/XLSX + 成本报表 |
| 验证报告 | `validation/**/report-*.md` 汇总 + 关键截图 |
| 发布说明 | 由 `CHANGELOG.md` 对应版本段落生成 |

> ⚠️ **发布前检查**：Release 说明中必须包含或明确指向 `NOTICE` 与固件许可全文。
> 省略第三方声明会违反 ESP-IDF（Apache-2.0）与 FreeRTOS/mbedTLS 的许可条款——
> **闭源不等于可以省略声明**。详见 [docs/08](../docs/08-licensing-and-compliance.md) §4.2。

## 5. 当前状态

> **本轮仅提交 `ISSUE_TEMPLATE/` 占位；`workflows/` 暂不入库。**
>
> 原因：仓库尚无真实 CI 配置，而向 `.github/workflows/**` 推送要求 Personal Access Token
> 具备 `workflow` scope。与其为此申请一个权限更大的令牌，不如等真正要写 CI YAML 时再创建该目录——
> Git 本身不跟踪空目录，届时把 workflow 文件放进去即可（目录缺失不影响 GitHub Actions）。
>
> 相关协作规范见 [CONTRIBUTING.md](../CONTRIBUTING.md)。
