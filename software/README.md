# software/ — 软件入口

> 本目录在公开仓中**只有一个 `README.md`**，不放任何子目录或空占位。
> 原因见下方第 1 节。

---

## 1. 为什么这里这么"空"

公开仓的软件构成是**三块内容、三种状态**，没有一块现在需要子目录：

| 软件部分 | 位置 | 状态 |
|---------|------|------|
| **固件**（ESP32-C3） | **私有仓** `ARDF-MeshTuneFox80-firmware` | 源码不公开；编译产物在 [GitHub Releases](https://github.com/PatrickShih774/ARDF-MeshTuneFox80/releases) |
| **中控 PC 软件** | 尚未开始 | 技术栈待定（[ADR-0005](../docs/adr/ADR-0005-console-tech-stack-tbd.md)） |
| **共享协议**（固件 ↔ 中控） | 尚未开始 | 规范条目已列在 [docs/README.md](../docs/README.md) 的待补清单 |

**不为不存在的代码预建目录。** 本项目曾在公开仓建过 `software/{master-console,protocol,tools,docs}/` 的完整骨架——21 个文件里 15 个是空的 `.gitkeep`。固件源码迁往私有仓后，这套骨架失去了承载对象，因此全部删除，只留本文件。

真正开始写代码时，按 [docs/02-repository-layout.md](../docs/02-repository-layout.md) §3.2 的**文件归属决策表**创建对应目录即可，规范已经写明每个新文件该放哪里。

---

## 2. 固件（私有仓）

**固件基于 ESP-IDF v5.x（目标芯片 `esp32c3`），不使用 Arduino 框架。**

全部源码位于私有仓 `ARDF-MeshTuneFox80-firmware`，**本公开仓不含任何固件源码**。技术选型理由见 [ADR-0001](../docs/adr/ADR-0001-adopt-esp-idf-over-arduino.md)，闭源决策见 [ADR-0007](../docs/adr/ADR-0007-firmware-closed-source-two-repo.md)。

公开可见的固件相关信息：

| 内容 | 位置 |
|------|------|
| 组件划分与依赖规则（28 个 L0–L6 组件） | [docs/03-software-architecture.md](../docs/03-software-architecture.md) |
| 固件对外行为规格（GPIO、协议、功率、时序） | [docs/05-hw-sw-interface-contract.md](../docs/05-hw-sw-interface-contract.md) |
| 构建与调试流程 | [docs/06-build-and-dev-environment.md](../docs/06-build-and-dev-environment.md) |
| 实测验证报告 | [validation/](../validation/README.md) |
| 编译产物 | [GitHub Releases](https://github.com/PatrickShih774/ARDF-MeshTuneFox80/releases) |

> 设计取向：固件**可验证但不可修改**——公开行为规格与实测报告，不公开实现。

---

## 3. 规划中的软件部分

以下内容**尚未开始**，此处只登记规划要点，避免信息散落。

### 3.1 中控 PC 软件

- **职责**：赛事编排、从机实时监控、远程参数下发、赛报导出
- **技术栈**：**待定**（[ADR-0005](../docs/adr/ADR-0005-console-tech-stack-tbd.md)），候选为 Python（pyserial + FastAPI + Web UI）与 .NET/C#（Avalonia）
- **许可**：`Apache-2.0`
- **预期子模块**：`transport`（串口 / USB-CDC / UDP）、`protocol`（帧编解码）、`registry`（从机台账）、`scheduler`（发射窗口编排）、`telemetry`（遥测存储）、`ui`

### 3.2 共享协议

- **定位**：固件与中控之间的**唯一事实来源**，两者都不许各自手写帧结构
- **分层**：Mesh 帧（设备间 ESP-NOW）与 Console 帧（设备 ↔ 中控）分开定义
- **报文清单**：`HELLO`、`TIME_SYNC_REQ/RSP`、`TX_SCHEDULE`、`SET_FREQ`、`SET_POWER`、`SET_MODE`、`ATU_TUNE_START`、`ATU_STATUS`、`TELEMETRY`、`ACK/NACK`、`SELFTEST`
- **遥测字段**：设备 ID、UTC 时间、发射状态、频率、功放温度、电池电压、ATU 调谐状态、SWR
- **安全**：ESP-NOW 原生 CCMP + 应用层 HMAC-SHA256 + MAC 白名单 + 序列号防重放
- **许可**：`Apache-2.0`
- **规范文档**：将写入 [docs/README.md](../docs/README.md) 待补清单中的 `11-mesh-protocol-and-security.md`

### 3.3 跨子工程工具

- `protocol_gen`（协议代码生成）、`package_release`（打包发布）、`bom_cost`（BOM 成本核算）、`docs_check`（文档链接检查）
- **许可**：`Apache-2.0`

---

## 4. 许可

目录级授权映射的唯一权威是仓库根 [`LICENSING.md`](../LICENSING.md)（许可全文在 [`LICENSES/`](../LICENSES/README.md)）。

| 软件资产 | 许可（SPDX） |
|---------|-------------|
| 固件源码（**私有仓**） | `LicenseRef-ARDF-NC-1.0`（不对外授权） |
| 固件二进制（Releases） | `LicenseRef-ARDF-NC-1.0` — **仅限业余无线电非商业用途，不授予源代码** |
| 中控 PC 软件 / 共享协议 / 工具（规划中） | `Apache-2.0` |

---

## 5. 相关文档

- 软件架构详设（组件划分、任务规划、分区表）：[docs/03-software-architecture.md](../docs/03-software-architecture.md)
- 仓库目录规范与文件归属决策表：[docs/02-repository-layout.md](../docs/02-repository-layout.md)
- 软硬件接口契约：[docs/05-hw-sw-interface-contract.md](../docs/05-hw-sw-interface-contract.md)
- 构建与开发环境：[docs/06-build-and-dev-environment.md](../docs/06-build-and-dev-environment.md)
- 编码规范：[docs/07-coding-standards.md](../docs/07-coding-standards.md)
- 许可证与合规：[docs/08-licensing-and-compliance.md](../docs/08-licensing-and-compliance.md)
