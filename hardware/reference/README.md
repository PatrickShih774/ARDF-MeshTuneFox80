# reference 外部参考设计（只读）

## 1. 本目录定位

外部开源参考设计的 **只读区**。用于记录本工程所借鉴的外部项目、其技术贡献点与许可状态。

> **重要声明**：本目录内容 **不纳入本仓库的版本管理与许可证范围**。其中的第三方代码、原理图、固件一律按其原始许可证执行；本仓库的 CERN-OHL-S v2（硬件）与分层软件许可 **不覆盖** 这些内容。

## 2. 参考项目表

| 项目 | 用途 | 链接 |
|------|------|------|
| ATU-100 by N7DDC | ATU 匹配拓扑与调谐算法来源 | https://github.com/n7ddc/ATU-100 |
| N7DDC-ATU-100-mini-and-extended-boards (Dfinitski) | ATU-100 硬件与固件源码（PIC16F1938 / PIC18F2520 两套） | https://github.com/Dfinitski/N7DDC-ATU-100-mini-and-extended-boards |
| 本项目工程基座 ARDF_80M_3.5MHZ | 原版 ESP32-C3 + Si5351 信号源 | https://oshwhub.com/patrickshih/ardf_80m_fox |
| SignalSlinger (OpenARDF) | 开源 80m ARDF 发射机 | https://github.com/openardf/signalslinger |

其他相关参考（见项目升级计划书 第十四章）：ATU-10 by N7DDC（QRP 版自动天调，IM41 双稳态继电器）、THE TANDEM MATCH—AN ACCURATE DIRECTIONAL WATTMETER（Grebenkemper, KI6WX, QST 1987 年 1 月，Tandem Match 定向耦合器理论来源）。

## 3. 使用规则

1. **只读**：本目录只存放**本地比对用的摘录**（原理图截图、算法片段注释、参数表），不作为本工程的源码或设计源文件。
2. **不入版本库**：原则上整份第三方源码/工程文件不得提交到本仓库；如需保留，仅提交最小必要的摘录，并在文件头注明来源、版本与许可。
3. **入库前必须确认许可**：任何摘录文件在提交前必须核对其原始许可证与再分发条件；未确认前不得提交。
4. **禁止直接复制未经许可核对的代码**：借鉴算法思想与电路拓扑属于工程参考，但复制代码/图纸必须满足原许可要求（署名、同许可分发等）。

## 4. 子目录说明

| 子目录 | 内容 |
|--------|------|
| `atu-100/` | ATU-100 参考摘录（原理图/源码摘录），仅用于本地比对 |

> `atu-100/` 子目录仅存放本地比对用的原理图/源码摘录；**入库前需确认许可**（ATU-100 为开源项目，但其具体许可证条款需逐项核对后再决定是否可提交摘录）。

## 5. 目录内容

| 路径 | 内容 |
|------|------|
| `README.md` | 本文件 |
| `atu-100/README.md` | ATU-100 摘录目录说明 |
| `atu-100/.gitkeep` | 占位文件（保持空目录入版本库） |

## 6. 验证要点

- 每个摘录文件均标注来源项目、原始版本/commit 与许可。
- 本仓库的授权（见仓库根 [LICENSING.md](../../LICENSING.md)）不覆盖 `reference/` 下的第三方内容；该目录内容版权归各自原作者。
- 提交前复核：不得包含未确认许可的第三方完整源码或工程文件。

## 7. 关联文档

- [项目升级计划书](../../docs/00-project-upgrade-plan.md) 3.2.4 继电器与驱动、3.2.6 调谐算法、14.2 开源项目参考
- [`hardware/README.md`](../README.md)
- [`hardware/reference/atu-100/README.md`](atu-100/README.md)
