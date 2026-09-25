# reference 外部参考设计（只读记录）

## 1. 本目录定位

记录本工程所借鉴的**外部项目、技术贡献点与许可状态**。

> **重要声明**：本目录**只放本工程自己撰写的借鉴说明**，**不放任何上游代码、原理图、图纸或摘录**。
> 上游内容的版权归各自原作者，本仓库的 `CERN-OHL-S-2.0` 与分层软件许可（见
> [LICENSING.md](../../LICENSING.md)）**均不覆盖**它们。

---

## 2. 🔴 许可核查结论（2026-09 经 GitHub API 实测）

| 项目 | GitHub `license` 字段 | 根目录许可文件 | 结论 |
|------|---------------------|--------------|------|
| `Dfinitski/N7DDC-ATU-100-mini-and-extended-boards` | `null` | **无** | 🔴 **无许可 = 保留所有权利**，不可复制任何内容 |
| `n7ddc/ATU-100`（本文档早先引用的"原版仓库"） | — | — | 🔴 **HTTP 404**：作者账号 `n7ddc` 已不存在，链接失效 |
| `openardf/signalslinger` | `MIT` | — | ✅ 可自由参考与再分发（需保留版权声明） |
| 本项目工程基座 `ARDF_80M_3.5MHZ`（立创开源） | — | — | ⚠️ 见该平台页面标注 |

### 2.1 对 ATU-100 的强制处理规则

🔴 **严禁复制、翻译、改写、转录或以任何形式提交 ATU-100（及其任何衍生仓库）的内容**，包括：

- 源代码 —— `main.c` / `main.h` / `oled_control.c` / `pic_init.c` / `pic_init.h` / `font5x8.h` 等全部文件
- 硬件源文件 —— 原理图、PCB 文件、BOM、装配图
- 文档正文 —— 用户手册、技术说明的段落

✅ **允许**：参考其**思想、方法、公开电路拓扑**。

> 法理依据：版权保护的是**表达（expression）**，不是**思想（idea）、方法或电路拓扑**。
> 因此"借鉴调谐搜索思路""采用 HK4100F + 2N7002 低边驱动"这类**方法层面的参考**不构成侵权；
> 而"照着 `main.c` 逐行翻译成 C"则构成侵权。

由此产生的三条硬约束：

1. `atu-100/` 子目录**只放本工程自己撰写的借鉴说明**，**不放任何上游材料**（连截图、片段都不放）；
2. 私有固件仓的 `components/atu_tuner/` 必须是**独立重新实现**——
   不得把上游代码放在旁边逐行对照翻译，也不得沿用其变量名/函数名/注释结构；
3. 文档中可以**事实性引用**项目名称与链接，但**不得大段摘录其正文**。

---

## 3. 参考项目表

| 项目 | 用途 | 链接 | 许可 |
|------|------|------|------|
| N7DDC-ATU-100-mini-and-extended-boards (Dfinitski) | ATU 匹配拓扑与调谐算法的**思想来源**（⚠️ 不得复制内容） | https://github.com/Dfinitski/N7DDC-ATU-100-mini-and-extended-boards | 🔴 无许可 |
| ~~ATU-100 by N7DDC~~ | ~~原版仓库~~ | ~~https://github.com/n7ddc/ATU-100~~ | 🔴 **链接已失效（404）** |
| 本项目工程基座 ARDF_80M_3.5MHZ | 原版 ESP32-C3 + Si5351 信号源 | https://oshwhub.com/patrickshih/ardf_80m_fox | 见平台标注 |
| SignalSlinger (OpenARDF) | 开源 80m ARDF 发射机（可自由参考） | https://github.com/openardf/signalslinger | ✅ MIT |

其他理论参考（见项目升级计划书 第十四章）：

- **ATU-10 by N7DDC**（QRP 版自动天调，IM41 双稳态继电器）—— 与 ATU-100 同源，同样视为**无许可**处理；
- **The Tandem Match — An Accurate Directional Wattmeter**（Grebenkemper, KI6WX, QST 1987 年 1 月）
  —— Tandem Match 定向耦合器的**理论来源**，属公开文献，可引用其原理与公式。

---

## 4. 使用规则

1. **只放自撰说明**：本目录及其子目录**不得包含任何第三方代码、图纸、截图或文档摘录**。
2. **不入版本库**：第三方源码/工程文件**一律不得提交**到本仓库（已由
   [.gitignore](../../.gitignore) 的防泄漏护栏兜底）。
3. **引用可，摘录不可**：可以写"参考了项目 X 的方法 Y"，不得粘贴 X 的正文。
4. **入库前核对许可**：任何新增引用在提交前必须核对上游许可状态并登记到第 2 节表格。

---

## 5. 子目录说明

| 子目录 | 内容 |
|--------|------|
| `atu-100/` | ATU-100 的**借鉴说明**（仅本工程自撰文字，无上游材料） |

---

## 6. 目录内容

| 路径 | 内容 |
|------|------|
| `README.md` | 本文件 |
| `atu-100/README.md` | ATU-100 借鉴说明 |
| `atu-100/.gitkeep` | 占位文件（保持空目录入版本库） |

---

## 7. 验证要点

- 本目录下**不存在**任何第三方文件（可执行 `git ls-files hardware/reference` 核对，应只有 `README.md` 与 `.gitkeep`）。
- 每个引用条目都在第 2 节表格中登记了许可状态。
- [.gitignore](../../.gitignore) 的防泄漏护栏生效：`hardware/reference/**/*.{c,h,ino,asm,zip,pdf}` 不会被提交。

---

## 8. 关联文档

- [项目升级计划书](../../docs/00-project-upgrade-plan.md) 3.2.4 继电器与驱动、3.2.6 调谐算法、14.2 开源项目参考
  （⚠️ 该文件为 V3.7 快照，其中 `n7ddc/ATU-100` 链接已失效，以本文件第 2 节为准）
- [`hardware/README.md`](../README.md)
- [`hardware/reference/atu-100/README.md`](atu-100/README.md)
- [`docs/08-licensing-and-compliance.md`](../../docs/08-licensing-and-compliance.md) §4.1
