# ADR-0001 采用 ESP-IDF 而非 Arduino

- 状态：已接受
- 日期：2026-09
- 决策者：固件组

## 背景

原版参考工程 `ARDF_80M_3.5MHZ` 基于 **Arduino / PlatformIO**，代码量小、上手快，
在单机发射器的场景下足够用。但本项目的定位与之有本质差异：

1. **ESP-NOW 大规模组网**：需要多节点 Mesh 转发、邻居表维护、去重与跳数控制，
   Arduino-ESP32 的 ESP-NOW 封装对底层回调与信道控制暴露不足。
2. **精确时序**：CW 码速误差 <2%、5 分钟周期误差 <0.1 秒、发射窗口误差 <0.1 秒
   （见 `validation/stage-8-cw/`、`validation/stage-9-competition-modes/`），
   需要任务优先级与硬件定时器级别的确定性。
3. **NVS 分区**：调谐结果缓存、密钥存储、参数持久化需要明确的分区规划与 NVS 命名空间。
4. **单元测试**：需要 Unity + pytest-embedded 的宿主机/目标机测试能力。
5. **长期可维护性**：组件化组织、明确的依赖方向、可静态检查的构建系统。

## 决策

固件**全面基于 ESP-IDF v5.x**：

- 目标芯片：`esp32c3`；构建系统：**CMake + `idf.py`**。
- 采用**组件化组织**（私有固件仓的 `components/`，28 个组件），
  每个组件自带 `CMakeLists.txt`、`include/`、`Kconfig`（按需）。
- **不引入 Arduino-ESP32 核心**，不使用 Arduino 库管理器；
  Si5351、U8g2、LCD 驱动等第三方 Arduino 库必须自行移植或重写为 ESP-IDF 组件。
- 应用入口为 `app_main()`，任务编排使用 FreeRTOS 原生 API。

## 后果

**正向**

- 精确的任务优先级与定时控制，可用硬件定时器/高分辨率定时器保证 CW 与窗口时序。
- ESP-NOW 原生 API，回调、信道、速率、peer 管理完全可控。
- NVS、分区表、OTA、加密分区等能力开箱可用。
- Unity 测试框架内建，可配合 pytest-embedded 做目标机自动化测试。
- CI 中可用官方 Docker 镜像稳定构建。

**负向**

- 学习曲线高于 Arduino；团队需熟悉 Kconfig、CMake 组件依赖与 IDF 构建流程。
- **大量 Arduino 库不可直接复用**：Si5351、显示驱动、按键/编码器库均需移植或重写，
  这是本项目最大的前期人力开销。
- 构建环境体积大（ESP-IDF 工具链数 GB），CI 镜像与首次拉取耗时明显。
- 社区示例多以 Arduino 为主，遇到问题时需转向 ESP-IDF 官方文档与论坛。

## 备选方案

| 方案 | 结论 |
| --- | --- |
| 继续使用 Arduino-ESP32 | 拒绝：时序与组网能力不足 |
| PlatformIO + Arduino | 拒绝：仅改善构建体验，未解决运行时能力问题 |
| ESP-IDF + Arduino-as-component | 拒绝：混合依赖难以维护，两套 HAL 并存易出隐性冲突 |

## 关联

- 固件工程细节：私有固件仓
- [ADR-0002 软硬件分区的单仓结构](ADR-0002-hardware-software-split-monorepo.md)
- [ADR-0006 分层授权与 GPL 隔离方案](ADR-0006-layered-licensing-gpl-isolation.md)
- [docs/07-coding-standards.md](../07-coding-standards.md)
