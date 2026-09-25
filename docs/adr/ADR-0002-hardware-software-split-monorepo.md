# ADR-0002 软硬件分区的单仓结构

- 状态：已接受
- 日期：2026-09
- 决策者：项目组

> 注：本 ADR 的「单仓」范围已于后续变更中调整为「公开仓 + 私有固件仓」双仓结构，详见 ADR-0007。

## 背景

本项目同时包含两类差异很大的资产：

- **硬件**：原理图、PCB、Gerber、BOM、结构件、仿真文件。
- **软件**：ESP-IDF 固件、中控 PC 软件、通信协议定义、跨子工程工具。
- 此外还有**独立验证区**：ATU 专项验证的 10 个阶段与实测报告。

三者的**许可不同**：硬件为 `CERN-OHL-S-2.0`，中控与协议为 `Apache-2.0`，
固件（**源码在私有仓**）二进制为 `LicenseRef-ARDF-NC-1.0`，
ATU/Mesh 算法为商业闭源授权（见 [ADR-0006](ADR-0006-layered-licensing-gpl-isolation.md)）。
三者的**工具链不同**：EDA vs ESP-IDF vs Python、.NET。
三者的**发布节奏不同**：硬件按批次（打样/改板），软件按版本。

同时，软硬件之间存在强耦合：GPIO 分配、接口定义、ATU 的 L/C 档位约束着固件实现，
版本必须能对应发布（"这个固件版本配这块板子"）。

## 决策

采用**单仓库、顶层按专业分区**的结构：

```text
ARDF-MeshTuneFox80/                      （公开仓）
├── hardware/      # 硬件设计：原理图、PCB、Gerber、BOM、结构件（CERN-OHL-S-2.0）
├── software/      # 软件入口（当前仅 README.md）：中控、协议、工具均规划中
├── docs/          # 跨专业文档：目录规范、软件架构、接口契约、编码规范、许可、ADR
├── validation/    # 硬件在环验证：10 个阶段 + 报告
└── scripts/       # 仓库级脚本：构建辅助、发布打包、文档检查、BOM 成本
```

> 固件源码不在公开仓，位于**私有仓** `ARDF-MeshTuneFox80-firmware`（见
> [ADR-0007](ADR-0007-firmware-closed-source-two-repo.md)）。

配套约定：

- **目录名用英文**，**文档内容用中文**（专有名词保留原文）。
- 每个一级目录必须有 `README.md` 说明其职责与边界。
- 许可证文件按目录放置，避免"整仓单一许可"的歧义。
- `.gitignore` 精细区分：硬件输出（Gerber 临时文件）、固件构建目录（`build/`）、验证原始数据（`validation/**/raw/`）分别忽略。

## 后果

**正向**

- 软硬件版本可**联动发布**，一个 tag 对应"某版固件 + 某版板子"的确定组合。
- 接口契约集中管理：`docs/05-hw-sw-interface-contract.md` 成为唯一接口事实来源。
- 许可边界清晰：按目录即可判定适用许可，便于合规审查；验证报告与设计文件同仓，问题可追溯到具体版本。

**负向**

- 仓库体积增大；硬件二进制与截图容易把仓库撑大，必须靠 `.gitignore` 与体积评审控制。
- CI 需要**按路径过滤**，否则一次文档改动也会触发耗时的固件构建。
- `hardware/` 与 `software/` 的评审人往往不是同一批人，PR 模板需强制区分改动类型；单仓权限粒度也偏粗，需靠 CODEOWNERS 缓解。

## 备选方案

| 方案 | 结论 |
| --- | --- |
| 硬件独立仓库 + git submodule | 拒绝：软硬件版本联动困难，submodule 使用体验差、易错 |
| 硬件与软件同一目录混放 | 拒绝：许可与工具链混淆，构建与忽略规则无法清晰隔离 |
| 多仓库 + 私有包管理 | 拒绝：早期阶段协作成本过高，超出团队规模需要 |

## 关联

- [docs/02-repository-layout.md](../02-repository-layout.md)
- [docs/05-hw-sw-interface-contract.md](../05-hw-sw-interface-contract.md)
- [ADR-0001 采用 ESP-IDF 而非 Arduino](ADR-0001-adopt-esp-idf-over-arduino.md)
- [ADR-0006 分层授权与 GPL 隔离方案](ADR-0006-layered-licensing-gpl-isolation.md)
