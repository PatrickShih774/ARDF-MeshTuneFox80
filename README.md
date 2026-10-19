# ARDF-MeshTuneFox80 —— 硬件设计仓

> **项目全称**：80 米波段（3.5–3.6 MHz）开源 ARDF 猎狐竞赛系统 —— 信号源设备网络 · 赛事管理网关 · PC 中控台
> **原名**：80 米波无线电测向信号源 `ARDF_80M_3.5MHZ`｜**规划版本**：V3.7｜**中文名**：待定
> **许可**：硬件 **CERN-OHL-S v2** · 固件 `LicenseRef-ARDF-NC-1.0` · 中控 **Apache-2.0** · 主控平台 **ESP-IDF v6.1 / ESP32-C3**（详见 [LICENSE](LICENSE) 与 docs/08）
>
> **ARDF-MeshTuneFox80 是一整套面向 ARDF「猎狐」竞赛的端到端系统** —— 不止是一台发射机，
> 而是「**信号源设备网络 + 赛事管理网关 + PC 中控台**」的**三层闭环**：
> 以《无线电测向竞赛规则》【**2024 修订版**】为**合规基线**，
> 面向该基线中**全部 7 个与信号源发射相关的竞赛项目**提供信号源能力。

![Hardware](https://img.shields.io/badge/Hardware-CERN--OHL--S_v2-blue)
![Firmware](https://img.shields.io/badge/Firmware-ARDF--NC--1.0-orange)
![Console](https://img.shields.io/badge/Console-Apache_2.0-green)
![MCU](https://img.shields.io/badge/MCU-ESP32--C3-red)
![Framework](https://img.shields.io/badge/Framework-ESP--IDF_v6.1-orange)

## 简介

本仓是 **80 m 段 ARDF（无线电测向）狐狸发射机 + ATU 自动天调 + mesh 节点** 的硬件设计资料。

- **供电**：2S 锂电 **7.4 V 标称**（6.0–8.4 V），本项目不设升压；
  三级电源 = `VCC`（输入）/ `+5 V`（MP2315 DC-DC）/ `+3V3`（MD7673 LDO）
- **功放**：E 类，直吃 `VCC`，按 **7.4 V 标称定点设计 2.5 W**（满电 8.4 V 由固件降驱动）
- **ATU**：6 只 `HK4100F-DC5V-SHG`（5 V 线圈），单颗 **CA-DV8008N**（I²C `0x28`）低边驱动
- **主控**：ESP32-C3；人机 = ST7567 128×64 液晶（CS 接 GND / RST 走 GPIO12）+ EC11 旋钮与按键
- **场景**：80 m 段 ARDF 训练与比赛（标准距离 / 短距离 / 快速测向等多种模式）

详细技术基线与引脚分配见下方「现行技术基线」链接。

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
