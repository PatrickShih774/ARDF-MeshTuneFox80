# ARDF-MeshTuneFox80

> **80 米波段（3.5–3.6 MHz）开源 ARDF 无线电测向信号源**
> 原名：80米波无线电测向信号源 ARDF_80M_3.5MHZ｜规划版本：**V3.7**｜中文名：**待定**

[![硬件许可](https://img.shields.io/badge/Hardware-CERN--OHL--S%20v2-blue.svg)](#许可)
[![固件许可](https://img.shields.io/badge/Firmware-ARDF--NC--1.0-orange.svg)](#许可)
[![中控许可](https://img.shields.io/badge/Console-Apache%202.0-green.svg)](#许可)
[![主控](https://img.shields.io/badge/MCU-ESP32--C3-red.svg)](docs/03-software-architecture.md)
[![框架](https://img.shields.io/badge/Framework-ESP--IDF%20v5.x-orange.svg)](docs/06-build-and-dev-environment.md)

---

## 一、这是什么

**ARDF-MeshTuneFox80** 是一款面向业余无线电"猎狐"运动（ARDF）的现代化信号源：

| 基因 | 含义 | 工程体现 |
|------|------|----------|
| **ARDF** | 业余无线电测向 | 覆盖《业余无线电测向竞赛规则》（2019 版）中全部 **6 种**与信号源发射相关的竞赛项目 |
| **Mesh** | ESP-NOW 多机网络 | 主从时钟同步 + 单跳中继容错，多台信号源自动对齐发射窗口 |
| **Tune** | 自动天调 ATU | 6 继电器 L 型匹配网络，64 种组合，算法借鉴 **N7DDC ATU-100** |
| **Fox** | 猎狐运动 | CW 自动拍发（A1A，10–12 WPM）、多台号识别码 |
| **80** | 80 米波段 | 3.5–3.6 MHz，100 Hz 步进，Si5351 可编程本振 |

**核心目标**：解决商业化 ARDF 信号源"体积庞大、技术老旧、缺乏智能化"的痛点。原版复刻成本 57.8 元，本升级版单套 BOM **129.30 元**（不含电池）。

**两大创新点**
1. **多机联动**：ESP-NOW 无线自动同步，从机间 Mesh 中继容错（开阔地 100 m，密林 30–50 m）。
2. **ATU 自动调谐**：解决 80 m 波段短导线天线"高电抗、低辐射电阻"导致的发射效率极低问题（挂树实测 X≈-1050 Ω）。

---

## 二、仓库结构总览

本仓库采用 **软硬件双分区双仓结构**——**公开仓**（本仓）放硬件设计、文档、固件编译产物，以及共享协议与中控 PC 软件（规划中，待创建）；**固件源码在私有固件仓** `ARDF-MeshTuneFox80-firmware`（不对外公开）。硬件与软件各自独立演进，通过 `docs/05-hw-sw-interface-contract.md` 单一契约耦合。双仓决策背景见 [ADR-0007](docs/adr/ADR-0007-firmware-closed-source-two-repo.md)。

```
ARDF-MeshTuneFox80/
│
├── README.md                     ← 你在这里：项目总览与导航
├── LICENSING.md                  ← ★ 目录级授权映射（唯一权威）
├── LICENSES/                     ← 四份许可全文（ARDF-NC-1.0 / CERN-OHL-S / Apache / CC-BY）
├── NOTICE                        ← 第三方组件声明（发布固件二进制时必须随附）
├── CHANGELOG.md                  ← 版本变更记录
├── CONTRIBUTING.md               ← 贡献指南
├── .editorconfig / .gitattributes / .gitignore
│
├── docs/                         【跨专业文档】文件名英文，标题与内容中文
│   ├── 00-project-upgrade-plan.md       ★ 需求与技术指标基线（V3.7 计划书）
│   ├── 01-project-overview.md
│   ├── 02-repository-layout.md          ★ 文件放哪里的唯一权威来源
│   ├── 03-software-architecture.md      ★ ESP-IDF 分层与组件设计
│   ├── 04-hardware-architecture.md      ★ 模块化硬件设计
│   ├── 05-hw-sw-interface-contract.md   ★ GPIO / 连接器 / 协议边界
│   ├── 06-build-and-dev-environment.md
│   ├── 07-coding-standards.md
│   ├── 08-licensing-and-compliance.md
│   └── adr/                             ← 架构决策记录
│
├── hardware/                     【硬件区】CERN-OHL-S v2
│   ├── core-board/               核心底板 130×95 mm 四层板
│   ├── pa-module/                3× BS170 并联 E 类功放 1–2.5 W
│   ├── lpf-module/               三阶椭圆低通，2f₀ 衰减 ≥55 dB
│   ├── atu-module/               6 继电器 L 型自动天调 55×65 mm
│   ├── mcu-ui-module/            ESP32-C3 + 12864 LCD + EC11 + 双按键
│   ├── power-module/             MP2315 + MD7673 + 可调升压
│   ├── antenna/                  5 m 垂直导线 + 5 m 地线
│   ├── enclosure/                外壳 / 3D 打印件
│   ├── interconnect/             模块间连接器与线束定义
│   ├── datasheets/               器件数据手册归档
│   ├── reference/                外部参考设计（ATU-100 等，只读）
│   └── archive/                  历史版本归档
│
├── software/                     【软件区】Apache 2.0；固件二进制 ARDF-NC-1.0
│   ├── README.md                 软件入口与规划要点（软件区总览）
│   ※ 中控 / 协议 / 工具三块内容规划中，待创建；固件源码在私有仓 ARDF-MeshTuneFox80-firmware
│
├── validation/                   【硬件在环验证区】计划书第八章 10 个阶段
│   ├── stage-0-rf-frontend/      … stage-9-competition-modes/
│   └── reports/
│
└── scripts/                      【仓库级脚本】构建/打包/文档检查
```

> **目录命名约定**：目录与文件名一律使用**英文小写**（下划线用于 ESP-IDF 组件名，连字符用于其他目录），**文档内容使用简体中文**。原因见 [ADR-0002](docs/adr/ADR-0002-hardware-software-split-monorepo.md)——中文路径会在 CMake/ESP-IDF/Gerber 工具链中引入编码风险。

---

## 三、技术基线

### 3.1 硬件基线（继承自工程基座 + ATU 扩展）

| 模块 | 原项目 | V3.7 升级后 |
|------|--------|-------------|
| 主控 | ESP32-C3 | ESP32-C3 SuperMini |
| 本振 | Si5351 | Si5351（3.5–3.6 MHz，100 Hz 步进） |
| 功放 | S2SK3476 AB 类 ≈1 W | **3× BS170 并联 E 类，1–2.5 W**（峰值 3.5 W/≤30 s，低功率档 0.02–0.5 W 由 PWM 调压） |
| 滤波 | 三阶椭圆低通 | 同（3.55 MHz 中心，2f₀ 衰减 ≥55 dB） |
| 天调 | **无** | **6 继电器 L 型 ATU**：L=12/33/47 µH，C=22/120/330 pF，64 组合 |
| 电源 | 2S 锂电 + 7805 LDO（效率 ≈68%） | **MP2315 同步降压 + MD7673 LDO + 可调升压** |
| 交互 | 12864 LCD + EC11 + 双按键 | 同（LCD 走 I2C 共享总线） |
| 组网 | 无 | **ESP-NOW Mesh**，HMAC-SHA256 认证 |

### 3.2 软件基线

| 项 | 决策 |
|----|------|
| 框架 | **ESP-IDF v5.x**（`esp32c3`），**不使用 Arduino** — 理由见 [ADR-0001](docs/adr/ADR-0001-adopt-esp-idf-over-arduino.md) |
| 构建 | CMake + `idf.py`，组件化（28 个组件，L0–L6 分层） |
| RTOS | FreeRTOS（`CONFIG_FREERTOS_HZ=1000`） |
| 测试 | Unity + pytest-embedded；纯算法组件必须可脱离硬件测试 |
| 存储 | NVS（配置 / 调谐记忆 / 密钥） |
| 时序基准 | `esp_timer` + 每 5 分钟 ESP-NOW 重同步 |
| 中控 | 技术栈待定，见 [ADR-0005](docs/adr/ADR-0005-console-tech-stack-tbd.md) |

### 3.3 六种竞赛模式

| 模式 | 固件标识 | 频率 | 功率 | 时序 | 识别码 |
|------|---------|------|------|------|--------|
| 标准距离 | `MODE_STANDARD` | 3.550 MHz 统一 | 1–2 W | 5 分钟/1 分钟 | MOE–MO5 |
| 短距离 | `MODE_SHORT_DISTANCE` | 3.500–3.590 MHz（含 3.600） | 0.1–0.5 W | 连续 | MO+单数字 0–9 |
| 快速测向 | `MODE_FAST` | 3.51 / 3.57 MHz | 0.1–0.5 W | 1 分钟/12 秒 | MOE–MO5 |
| 定向猎狐 | `MODE_FOXORING` | 3.5–3.6 MHz | 0.02–0.1 W（信标 1–2 W） | 连续 | MOE–MO5 |
| 阳光测向 | `MODE_SUNSHINE` | 3.5–3.6 MHz | 0.02–0.1 W | 连续 | MO+台号 |
| 短距离定向猎狐 | `MODE_SHORT_FOXORING` | 赛前公布 | 0.02–0.1 W（信标 0.1–0.5 W） | 连续 | 字母编号 AA–OO |

---

## 四、GPIO 分配（✅ 已冻结 2026-09-25）

**开发板**：合宙 LuatOS ESP32C3-CORE（**新款，原生 USB**）· 目标芯片 ESP32-C3 · 4 MB Flash（**必须 DIO 模式**）

> 📖 **完整契约（含理由、风险、回退方案）见 [docs/05 接口契约](docs/05-hw-sw-interface-contract.md) §2
> 与 [ADR-0008](docs/adr/ADR-0008-st7567-spi-and-pa-keying.md)。**
> 固件侧唯一来源是私有仓的 `components/bsp_board/include/board_pins.h`。

### 4.1 可用引脚预算

ESP32-C3 标称 22 个 GPIO，本板实际**可用 12 个**：

| 引脚 | 状态 | 原因 |
|------|------|------|
| GPIO0 – GPIO8、GPIO10 | ✅ 10 个 | GPIO0–4 = ADC1_CH0–4 |
| GPIO12、GPIO13 | ✅ 2 个 | DIO 模式下未接 flash；⚠️ 板载 LED D4/D5 |
| GPIO9 | ❌ | BOOT 按键，上电前不可下拉 |
| GPIO11 | ❌ | VDD_SPI，解锁需烧 eFuse（**已决定不解锁**） |
| GPIO18、GPIO19 | ❌ | **原生 USB**（新款） |
| GPIO20、GPIO21 | ❌ | UART0 |

### 4.2 按模块分配

| 模块 | GPIO | 功能名 | 方向 | 说明 |
|------|------|--------|------|------|
| **电源与 SWR 检测** | 0 | `ADC_FWD` | AI | 前向功率检波（ADC1_CH0），**SWR 必需** |
| | 1 | `ADC_REV` | AI | 反向功率检波（ADC1_CH1），**SWR 必需** |
| | 3 | `ADC_VBAT` | AI | 电池电压分压 `22k/9.1k`（ADC1_CH3） |
| **I²C 总线** | 4 | `I2C_SDA` | IO | 共享：Si5351 + TCA9535，4.7 kΩ 上拉 |
| | 5 | `I2C_SCL` | IO | 同上 |
| **显示（ST7567）** | 6 | `LCD_SCK` | O | SPI2 时钟 |
| | 7 | `LCD_MOSI` | O | SPI2 数据 |
| | 10 | `LCD_DC` | O | 命令/数据选择（每字节翻转，**必须直连**） |
| **人机交互（EC11）** | 2 | `EC11_A` | I | ⚠️ strapping，10 kΩ 上拉，静止为高 |
| | 8 | `EC11_B` | I | ⚠️ strapping，10 kΩ 上拉，静止为高 |
| **射频与功放** | 12 | `PA_PWR_PWM` | O | 功放功率 PWM（LEDC）→ 升压模块 FB；⚠️ 板载 LED D4 随之亮灭 |
| **预留** | 13 | `SPARE` | — | 可作状态灯（LED D5）或扩展器 INT |
| **系统** | 9 | `KEY_USER` | I | 板载 BOOT 按键，启动后可作普通输入 |

**合计：12 个可用引脚用 11 个，余 GPIO13。**

### 4.3 不占用 GPIO 的连接

| 信号 | 接法 | 理由 |
|------|------|------|
| ST7567 `CS` | **接 GND** | LCD 是 SPI2 上唯一从机，片选常有效 → 省 1 脚 |
| ST7567 `RST` | **与板载复位引脚共用** | 上电复位即可 → 省 1 脚与 RC 电路 |
| **CW 键控** | **Si5351 使能命令**（I²C 写 `CLKx_DIS`） | 完全不占 GPIO，且无插入/开关损耗 |

### 4.4 TCA9535 I²C 扩展器（地址 `0x20`，用 8/16 位）

| 位 | 功能名 | 方向 | 说明 |
|----|--------|------|------|
| P0.0 – P0.5 | `IOEXP_RELAY_K1` … `K6` | O | **ATU 6 个继电器**，经 **ULN2003A** 驱动（COM 接 +12 V） |
| P1.0 | `IOEXP_EC11_SW` | I | **EC11 编码器按键（SW）** |
| P1.1 | `IOEXP_LCD_BL` | O | ST7567 背光开关（经晶体管驱动） |
| P1.2 – P1.7、P0.6 – P0.7 | `IOEXP_SPARE` | — | **预留 8 位**（蜂鸣器、散热风扇、天线泄放等） |

### 4.5 ⚠️ 三条必须遵守的硬件约束

| # | 约束 | 不做的后果 |
|---|------|-----------|
| 1 | 🔴 **Flash 必须配 DIO 模式**（`CONFIG_ESPTOOLPY_FLASHMODE_DIO=y`） | 本板 GPIO12/13 未接 flash，QIO 模式下**上电无法启动** |
| 2 | 🔴 **GPIO2 / GPIO8 上电必须为高**（由 EC11 的 10 kΩ 上拉保证） | strapping 判为低 → **启动模式异常**；因此**上电/复位时请勿转动旋钮** |
| 3 | 🔴 **244 输入侧加 10 kΩ 下拉**：Si5351 停振时 CMOS 输入会悬空 | 244 振荡 → **功放自激发射** |

> **为什么 `ADC_VBAT` 在 GPIO3 而不是 GPIO2**：GPIO2 是 strapping 引脚，而分压输出随电池电压变化
> —— 欠电时 6.0 V × 0.29 = **1.74 V**，低于判决阈值（≈0.75×VDD = 2.48 V）→ **电池电量偏低时无法启动**。
> GPIO3 是 ADC1_CH3 且非 strapping，无此约束。
## 五、快速导航

**我是……**

| 角色 | 从这里开始 |
|------|-----------|
| 🆕 第一次了解本项目 | [docs/01-project-overview.md](docs/01-project-overview.md) → [docs/00-project-upgrade-plan.md](docs/00-project-upgrade-plan.md) |
| 💻 要写固件 | [docs/03-software-architecture.md](docs/03-software-architecture.md) → [docs/06-build-and-dev-environment.md](docs/06-build-and-dev-environment.md)（固件源码为**私有仓**，本仓不提供；固件二进制见 GitHub Releases） |
| 🔌 要画板子 | [docs/04-hardware-architecture.md](docs/04-hardware-architecture.md) → [hardware/README.md](hardware/README.md) |
| 🔗 关心软硬件怎么对接 | [docs/05-hw-sw-interface-contract.md](docs/05-hw-sw-interface-contract.md) |
| 🧪 要做实测验证 | [validation/README.md](validation/README.md) |
| 📐 想知道某个文件该放哪 | [docs/02-repository-layout.md](docs/02-repository-layout.md) |
| 📜 关心开源协议与商用 | [LICENSING.md](LICENSING.md) → [docs/08-licensing-and-compliance.md](docs/08-licensing-and-compliance.md) |

**核心概念速查**

- **ATU-100 参考**：本项目 ATU 的硬件拓扑（HK4100F 继电器 + 2N7002 驱动）与调谐算法（粗调 Grundmatch + 细调 Feinabstimmung + 全遍历兜底）借鉴自 N7DDC ATU-100，见 [hardware/reference/atu-100/README.md](hardware/reference/atu-100/README.md)。
- **调谐记忆**：调谐成功后将最佳继电器组合存入 NVS，下次开机能直接加载，微调 <0.5 秒。
- **SWR 联锁**：SWR > 3.0 时禁止发射，防止失谐高压击穿功放管。
- **低功率探测**：ATU 搜索与功放扫点使用低功率探测，避免满功率遍历击穿 BS170。

---

## 六、当前进度

> ⚠️ **本轮交付范围：仓库架构骨架 + 架构说明文档。尚未编写任何实现代码。**

| 区域 | 状态 |
|------|------|
| 仓库软硬件双分区结构 | ✅ 已建立 |
| `docs/` 架构文档体系与 ADR | ✅ 已建立 |
| 需求基线迁入 `docs/00-project-upgrade-plan.md` | ✅ 已完成（唯一副本，根目录 `plan.md` 已删除） |
| 许可结构 `LICENSING.md` + `LICENSES/` | ✅ 已建立（四份许可全文待放入） |
| `hardware/` 模块目录与文档骨架 | ✅ 已建立 |
| 固件源码（私有仓） | ✅ 已迁出本仓 |
| 固件二进制发布（Releases） | ⬜ 待首次构建 |
| ESP-IDF 工程构建文件（`CMakeLists.txt` / `sdkconfig.defaults` / `partitions.csv`） | ⬜ 待创建（在私有固件仓内） |
| 固件各组件实现代码 | ⬜ 待实现（在私有固件仓内） |
| 中控 PC 软件 | ⬜ 待实现（技术栈待定） |
| 原理图 / PCB / Gerber | ⬜ 待设计 |
| 十阶段专项验证 | ⬜ 待执行 |

实施路线图见 [项目升级计划书 第九章](docs/00-project-upgrade-plan.md)。

---

## 七、许可

本项目采用**分层授权**，不同区域适用不同协议，详见 [docs/08-licensing-and-compliance.md](docs/08-licensing-and-compliance.md)：

| 区域 | 许可证 | 商业含义 |
|------|--------|----------|
| `hardware/` | `CERN-OHL-S-2.0` | 强互惠，衍生硬件设计必须开源 |
| 固件二进制（私有仓源码的编译产物） | `LicenseRef-ARDF-NC-1.0` | 仅限业余无线电非商业用途；不授予源代码 |
| `software/master-console/`（规划中，待创建） | `Apache-2.0` | 允许闭源分发 |
| `software/protocol/`（规划中，待创建）、`software/tools/`（规划中，待创建）、`scripts/` | `Apache-2.0` | 工具链不进入固件镜像 |
| `docs/`、`validation/` | `CC-BY-4.0` | 可自由引用，需署名 |
| ATU 调谐算法 / Mesh 路由算法 | **商业授权（闭源）** | 核心技术壁垒 |
| `hardware/reference/` | 各原始项目许可 | 仅作参考，**不纳入本仓库许可范围** |

> **本仓库根目录没有单一 `LICENSE`**，这是有意为之：放一个根许可会让 GitHub 与扫描工具把整仓（含硬件与中控软件）判定为那一种许可。授权映射的唯一权威是 [`LICENSING.md`](LICENSING.md)，各许可全文在 [`LICENSES/`](LICENSES/README.md)。

> **合规提示**：ARDF 信号源属业余电台专用设备，持证火腿使用合法；未组装套件通常不视为整机，但建议明示"组装后使用需持证并办理设台手续"；成品整机对公销售需 **SRRC** 认证。

---

## 八、参考链接

| 类别 | 项目 / 资料 | 链接 |
|------|------------|------|
| 工程基座 | ARDF_80M_3.5MHZ 原项目（立创开源） | https://oshwhub.com/patrickshih/ardf_80m_fox |
| ATU 参考 | N7DDC-ATU-100-mini-and-extended-boards | https://github.com/Dfinitski/N7DDC-ATU-100-mini-and-extended-boards |
| ATU 参考 | ATU-100 by N7DDC | https://github.com/n7ddc/ATU-100 |
| 竞赛规则 | 《业余无线电测向竞赛规则》（2019 版） | https://crsoa.sport.org.cn/download/list_2653_3.html |
| 同类开源 | SignalSlinger（OpenARDF 80 m 发射机） | https://github.com/openardf/signalslinger |
| 理论参考 | The Tandem Match — An Accurate Directional Wattmeter (KI6WX, QST 1987) | https://www.qsl.net/kl7jef/Directional%20Wattmeter.pdf |

---

*本 README 与 [docs/00-project-upgrade-plan.md](docs/00-project-upgrade-plan.md)（V3.7 项目升级计划书）配套使用。技术指标冲突时以计划书为准；目录与接口约定冲突时以 [docs/02-repository-layout.md](docs/02-repository-layout.md)、[docs/05-hw-sw-interface-contract.md](docs/05-hw-sw-interface-contract.md) 为准；授权归属以 [LICENSING.md](LICENSING.md) 为准。*
