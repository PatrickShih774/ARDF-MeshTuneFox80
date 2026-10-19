# ARDF-MeshTuneFox80 —— 硬件设计仓

80 m ARDF 狐狸发射机 + ATU 自动天调 + mesh 节点的**硬件设计资料**（原理图/PCB/Gerber/BOM/结构件）。
软件在并列的固件仓。

> 本 README 只保留「一页速览」；原全文（含完整技术基线/历史基线）已归档到
> [`docs/README-FULL-ARCHIVE-2026-10-19.md`](docs/README-FULL-ARCHIVE-2026-10-19.md)。

## 仓库结构

```
hardware/          硬件设计区（原理图/PCB/Gerber/BOM/结构件索引）
docs/              文档（00–08 / 15 / 17 系列 + DECISIONS + NEXT-PCB-RULES）
```

## 现行技术基线（点开看权威）

| 主题 | 权威文档 |
|---|---|
| **硬件–软件接口契约**（引脚/时序/安全态）| [docs/05-hw-sw-interface-contract.md](docs/05-hw-sw-interface-contract.md) §2.3/§2.4·§7 |
| 硬件架构（电源拓扑/继电器/功放）| [docs/04-hardware-architecture.md](docs/04-hardware-architecture.md) §3 |
| GPIO 分配审计 | [docs/17-gpio-allocation-audit.md](docs/17-gpio-allocation-audit.md) |
| 项目总览 / 仓库布局 | [docs/01](docs/01-project-overview.md) · [docs/02](docs/02-repository-layout.md) |
| **方案变更与决策记录** | [docs/DECISIONS-2026-10-19.md](docs/DECISIONS-2026-10-19.md) |
| **下一版投板强制规则** | [docs/NEXT-PCB-RULES-2026-10-18.md](docs/NEXT-PCB-RULES-2026-10-18.md) |
| 软件架构/构建环境/编码规范/许可 | [docs/03](docs/03-software-architecture.md) · [docs/06](docs/06-build-and-dev-environment.md) · [docs/07](docs/07-coding-standards.md) · [docs/08](docs/08-licensing-and-compliance.md) |

## 许可

硬件：**CERN-OHL-S v2**。软件：分层授权（固件二进制 NC-1.0 / 中控 Apache-2.0、算法商用需授权）。
详见 [docs/08-licensing-and-compliance.md](docs/08-licensing-and-compliance.md)。
