# software/ — 软件入口

> 本目录在公开仓中**只有一个 `README.md`**，不放任何子目录或空占位。
> 原因见下方第 1 节。

---

## 1. 为什么这里这么"空"

公开仓的软件构成是**三块内容、两种状态**，没有一块现在需要子目录：

| 软件部分 | 位置 | 状态 |
|---------|------|------|
| **固件**（ESP32-C3） | **私有仓** `ARDF-MeshTuneFox80-firmware` | 源码不公开；编译产物在 [GitHub Releases](https://github.com/PatrickShih774/ARDF-MeshTuneFox80/releases) |
| **中控 PC 软件** | 🔴 **私有仓**（**不是"尚未开始"**） | ✅ **已实现 6 个界面**（赛前部署 / 赛中监控 / 赛后赛报），**可脱离硬件用假设备演练**；源码在私有仓，**本仓不发布**。授权登记为 `Apache-2.0`（见 [LICENSING.md §一](../LICENSING.md)） |
| **共享协议**（固件 ↔ 中控） | 🔴 **私有仓**（**不是"尚未开始"**） | 已落地（帧编解码 / 调度 / 遥测）；本仓只登记规范要点与待补清单 |

> 🔴 **2026-09-30 口径更正（本表此前写"中控 PC 软件 = 尚未开始"、"共享协议 = 尚未开始"，均不成立）**：
> 中控台与共享协议**都已实现**，源码与固件源码同在**私有仓**；
> 本仓 `software/` 下**只有本文件**，不存在 `software/master-console/` 等目录。
> 准确进度以 [README §六 当前进度](../README.md) 与 [LICENSING.md](../LICENSING.md) 为准。

**不为不存在的代码预建目录。** 本项目曾在公开仓建过 `software/{master-console,protocol,tools,docs}/` 的完整骨架——21 个文件里 15 个是空的 `.gitkeep`。固件源码迁往私有仓后，这套骨架失去了承载对象，因此全部删除，只留本文件。

若将来某一块要落回本仓，按 [docs/02-repository-layout.md](../docs/02-repository-layout.md) §3.2 的**文件归属决策表**创建对应目录即可，规范已经写明每个新文件该放哪里。

---

## 2. 固件（私有仓）

**固件基于 ESP-IDF v6.1（目标芯片 `esp32c3`），不使用 Arduino 框架。**
（🔴 本行此前写 `v5.x`，那是**过时/规划值**；当前实测口径 = `v6.1`，见 [README §3.2](../README.md)。）

全部源码位于私有仓 `ARDF-MeshTuneFox80-firmware`，**本公开仓不含任何固件源码**。技术选型理由见 [ADR-0001](../docs/adr/ADR-0001-adopt-esp-idf-over-arduino.md)，闭源决策见 [ADR-0007](../docs/adr/ADR-0007-firmware-closed-source-two-repo.md)。

公开可见的固件相关信息：

| 内容 | 位置 |
|------|------|
| 组件划分与依赖规则（**2026-09-28 实测 30 个已入库组件**，L0–L6） | [docs/03-software-architecture.md](../docs/03-software-architecture.md) |
| 固件对外行为规格（GPIO、协议、功率、时序） | [docs/05-hw-sw-interface-contract.md](../docs/05-hw-sw-interface-contract.md) |
| 构建与调试流程 | [docs/06-build-and-dev-environment.md](../docs/06-build-and-dev-environment.md) |
| 实测验证报告 | [validation/](../validation/README.md) |
| 编译产物 | [GitHub Releases](https://github.com/PatrickShih774/ARDF-MeshTuneFox80/releases) |

> 设计取向：固件**可验证但不可修改**——公开行为规格与实测报告，不公开实现。

---

## 3. 软件部分：现状与规划

### 3.1 中控 PC 软件（✅ 已实现 —— 源码在**私有仓**）

- ✅ **现状**：**已实现 6 个界面**（赛前部署 / 赛中监控 / 赛后赛报），可脱离硬件、用假设备完整演练。
- **位置**：🔴 **源码在私有仓 `ARDF-MeshTuneFox80-firmware`，本仓不发布**（本仓 `software/` 只有本文件）。
- **职责**：赛事编排、从机实时监控、远程参数下发、赛报导出
- **技术栈**：以私有仓实现为准；历史候选（Python pyserial + FastAPI + Web UI / .NET C# Avalonia）见 [ADR-0005](../docs/adr/ADR-0005-console-tech-stack-tbd.md)
- **许可**：`Apache-2.0`（登记见 [LICENSING.md §三](../LICENSING.md)）

### 3.2 共享协议（✅ 已落地 —— 实现同在**私有仓**）

- **现状**：🔴 **已落地**（此节此前写"尚未开始"，不成立）；本仓仅登记规范要点与待补清单。
- **定位**：固件与中控之间的**唯一事实来源**，两者都不许各自手写帧结构
- **分层**：Mesh 帧（设备间 ESP-NOW）与 Console 帧（设备 ↔ 中控）分开定义
- **报文清单**：`HELLO`、`TIME_SYNC_REQ/RSP`、`TX_SCHEDULE`、`SET_FREQ`、`SET_POWER`、`SET_MODE`、`ATU_TUNE_START`、`ATU_STATUS`、`TELEMETRY`、`ACK/NACK`、`SELFTEST`
- **遥测字段**（共 7 个，负载 16 字节）：设备 ID、UTC 时间、发射状态、频率、电池电压、ATU 调谐状态、SWR
  （原「功放温度」字段已于 2026-09-26 随 NTC 温度功能取消，见 [docs/17 §12.5](../docs/17-gpio-allocation-audit.md)）
- **安全**：ESP-NOW 原生 CCMP + 应用层 HMAC-SHA256 + MAC 白名单 + 序列号防重放
- **许可**：`Apache-2.0`

### 3.3 跨子工程工具（规划中）

- `protocol_gen`（协议代码生成）、`package_release`（打包发布）、`bom_cost`（BOM 成本核算）、`docs_check`（文档链接检查）
- **许可**：`Apache-2.0`

---

## 4. 许可

目录级授权映射的唯一权威是仓库根 [`LICENSING.md`](../LICENSING.md)（许可全文在 [`LICENSES/`](../LICENSES/README.md)）。

| 软件资产 | 许可（SPDX） |
|---------|-------------|
| 固件源码（**私有仓**） | `LicenseRef-ARDF-NC-1.0`（不对外授权） |
| 固件二进制（Releases） | `LicenseRef-ARDF-NC-1.0` — **仅限业余无线电非商业用途，不授予源代码** |
| 中控 PC 软件 / 共享协议（🔴 **已实现，源码均在私有仓、本仓不发布**） | `Apache-2.0`（登记；本仓内无对应文件） |
| 跨子工程工具（规划中） | `Apache-2.0` |

---

## 5. 相关文档

- 软件架构详设（组件划分、任务规划、分区表）：[docs/03-software-architecture.md](../docs/03-software-architecture.md)
- 仓库目录规范与文件归属决策表：[docs/02-repository-layout.md](../docs/02-repository-layout.md)
- 软硬件接口契约：[docs/05-hw-sw-interface-contract.md](../docs/05-hw-sw-interface-contract.md)
- 构建与开发环境：[docs/06-build-and-dev-environment.md](../docs/06-build-and-dev-environment.md)
- 编码规范：[docs/07-coding-standards.md](../docs/07-coding-standards.md)
- 许可证与合规：[docs/08-licensing-and-compliance.md](../docs/08-licensing-and-compliance.md)
