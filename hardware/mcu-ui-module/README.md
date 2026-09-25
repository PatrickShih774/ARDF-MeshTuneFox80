# mcu-ui-module 主控与人机交互模块

## 1. 模块定位

整机的主控与操作界面模块。负责信号源频率合成控制、CW 拍发时序、ATU 调谐流程、电源与功率档位控制、WiFi/NTP 校时与 ESP-NOW Mesh 组网，并提供本地显示与按键交互。

## 2. 关键指标

| 项目 | 指标 |
|------|------|
| 主控 | ESP32-C3 SuperMini |
| 显示 | 12864 LCD（ST7588i 控制器，国产替代） |
| 输入 | EC11 旋转编码器 ×1 + 轻触按键 ×2 |
| 提示 | 有源蜂鸣器 ×1 |
| GPIO 电平 | 3.3V |
| 无线 | WiFi（NTP 校时）+ ESP-NOW（Mesh 同步与状态回传） |
| 频率控制 | Si5351 I²C，3.5–3.6MHz，100Hz 步进 |

## 3. 核心器件

- ESP32-C3 SuperMini 主控模块
- 12864 LCD 液晶屏（ST7588i，国产替代）
- EC11 旋转编码器（带按键）
- 轻触开关 ×2（功能键 / 返回键）
- 有源蜂鸣器
- Si5351 本振模块（I²C 接口，位于射频链路起点）
- 可选：32.768kHz 晶振（底板 DNP 焊盘，Mesh 时钟升级）

## 4. 接口

- 对 `core-board`：2.54mm 排针排母
- I²C：Si5351 配置（频率、输出驱动）
- SPI/并口：12864 LCD 显示
- GPIO 输入：EC11 A/B 相与按键、双按键
- GPIO 输出：蜂鸣器、功放键控（A1A 方波）、升压模块 PWM（功率档位）、6 路 ATU 继电器驱动、LCD 复位/背光
- ADC：SWR 前向/反射检波电压
- 供电：3.3V 数字轨（独立 π 型 RC 滤波）
- 引脚分配以 `docs/05-hw-sw-interface-contract.md` 为唯一权威来源

## 5. 目录内容

| 子目录 | 内容 |
|--------|------|
| `schematic/` | 主控与交互原理图源文件 |
| `pcb/` | 主控模块 PCB 源文件 |
| `gerber/` | 制板 Gerber 包 |
| `bom/` | 物料清单（ESP32-C3、LCD、EC11、按键、蜂鸣器） |

> 本模块不含测试子目录；相关测试记录归入 `atu-module/test/` 与 `pa-module/test/`。

## 6. 验证要点

- **3.3V GPIO 驱动 2N7002 上升沿无振铃**（示波器实测栅极波形）。
- **继电器吸合时间 <6ms、释放时间 <4ms**（含驱动级延时的实测值，与 `atu-module` 联合验证）。
- 2N7002 漏极电压：继电器吸合时 <0.1V，释放时反峰 <20V。
- LCD 显示与 EC11 旋钮手感、去抖可用性检查。
- 键控输出波形：A1A 软起软降 2–5ms 实测。
- WiFi 配置与 NTP 校时功能可用性；ESP-NOW 组网与状态回传成功率（>80%）。

## 7. 关联文档

- [项目升级计划书](../../docs/00-project-upgrade-plan.md) 3.3 多机联动方案、6 CW 自动拍发
- [`hardware/README.md`](../README.md)
- [`hardware/atu-module/README.md`](../atu-module/README.md)
- `docs/05-hw-sw-interface-contract.md`（引脚分配唯一权威来源）
