# 03 · 软件架构

> 状态：已建立｜适用版本：V3.7｜权威性：**★ 唯一权威**（软件分层与组件划分）

---

## 1. 技术选型

| 项 | 决策 | 说明 |
|----|------|------|
| 芯片 | **ESP32-C3**（RISC-V 单核，160 MHz，400 KB SRAM，4 MB Flash） | 继承工程基座 |
| 框架 | **ESP-IDF v5.x** | **不使用 Arduino** — 理由见 [ADR-0001](adr/ADR-0001-adopt-esp-idf-over-arduino.md) |
| 目标名 | `esp32c3` | `idf.py set-target esp32c3` |
| 构建 | CMake + `idf.py` | 组件化组织 |
| RTOS | FreeRTOS（`CONFIG_FREERTOS_HZ=1000`） | 1 ms 时基，满足发射时序 <0.1 s 要求 |
| 定时基准 | `esp_timer` + ESP-NOW 每 5 分钟重同步 | 时序精度主保障 |
| 存储 | NVS 分区（配置 / 调谐记忆 / 密钥） | — |
| 无线 | ESP-NOW（原生 CCMP）+ 应用层 HMAC-SHA256 | — |
| 测试 | Unity + pytest-embedded | 纯算法组件必须可宿主机测试 |
| 语言 | C（C11），必要时少量 C++ 封装 | 公共 API 用 Doxygen 风格注释 |

### 1.1 为什么必须迁移到 ESP-IDF

原版工程基于 Arduino/PlatformIO。本项目需要的能力中，有两项 Arduino 框架难以可靠提供：

| 需求 | Arduino 的问题 | ESP-IDF 的优势 |
|------|---------------|---------------|
| **精确发射时序**（5 分钟周期误差 <0.1 s、CW 软起软降 2–5 ms） | `millis()` 轮询 + `delay()`，受 WiFi 协议栈与库函数阻塞影响 | 多任务 + 抢占式优先级 + `esp_timer` 微秒级回调 |
| **ESP-NOW 大规模组网与中继** | 封装层薄，peer 管理、队列、回调上下文不受控 | 原生 API + 事件循环 + 可控任务绑定 |

此外还有 NVS 精细控制、Unity 单元测试、CI 可构建性等收益。代价是 Si5351、12864 LCD、菜单等 Arduino 生态库需自行移植或重写（见 §7 迁移清单）。

---

## 2. 分层架构

```
┌───────────────────────────────────────────────────────────────────────┐
│  L6  应用与集成层                                                      │
│      app_core  ui_menu  comm_console  diag_selftest                   │
├───────────────────────────────────────────────────────────────────────┤
│  L5  网络与同步层                                                      │
│      net_espnow  mesh_router  mesh_security  net_timesync             │
├───────────────────────────────────────────────────────────────────────┤
│  L4  ARDF 业务层                                                       │
│      ardf_mode  ardf_code  ardf_schedule                              │
├───────────────────────────────────────────────────────────────────────┤
│  L3  ATU 自动天调层                                                    │
│      atu_match  atu_tuner  atu_state                                  │
├───────────────────────────────────────────────────────────────────────┤
│  L2  射频层                                                            │
│      rf_swr  rf_keyer  rf_power                                       │
├───────────────────────────────────────────────────────────────────────┤
│  L1  外设驱动层                                                        │
│      drv_si5351  drv_lcd12864  drv_ec11  drv_keys                     │
│      drv_relay   drv_pa        drv_analog                             │
├───────────────────────────────────────────────────────────────────────┤
│  L0  板级与基础层                                                      │
│      bsp_board  bsp_io_expander  bsp_storage  utils_common            │
└───────────────────────────────────────────────────────────────────────┘
                     ▲ 上层依赖下层，禁止反向依赖
```

### 2.1 依赖规则（强制）

1. **只允许向下依赖**：L(n) 可以依赖 L(0)…L(n-1)，**禁止**依赖 L(n+1) 及以上。
2. **禁止同层横向依赖**，除非在组件 README 中显式声明并说明理由。
3. **禁止循环依赖**。若出现循环，说明职责划分有误，必须拆分组件。
4. **跨层调用必须经 `app_core` 事件总线**：例如 `ui_menu` 想触发一次 ATU 调谐，不能直接调用 `atu_tuner`，而应发布 `APP_EVENT_ATU_TUNE_REQ` 事件，由 `app_core` 派发给 `atu_state`。
5. **算法组件禁止直接访问硬件**：`atu_tuner`、`ardf_code`、`rf_swr`、`ardf_schedule` 必须通过注入的抽象接口（函数指针表 / `*_ops_t` 结构）获取测量值，以保证可测试性。
6. **`bsp_board` 是引脚唯一来源**：任何组件不得硬编码 GPIO 号，必须引用 `bsp_board` 暴露的宏或结构体，而 `bsp_board` 的值必须与 [docs/05-hw-sw-interface-contract.md](05-hw-sw-interface-contract.md) 一致。

### 2.2 数据流示例：一次完整的发射流程

```
 net_timesync                 ardf_schedule              ardf_code
      │                             │                        │
      │ ① 同步 UTC 时间              │                        │
      ├────────────────────────────►│                        │
      │                             │ ② 计算当前时隙与台号     │
      │                             ├───────────────────────►│
      │                             │                        │ ③ 生成 CW 报文
      │                             │                        │   (MOE/MOI/…/AA)
      │                             │◄───────────────────────┤
      │                             │ ④ 到达发射窗口           │
      │                             ▼                        │
      │                        app_core (事件总线)            │
      │                             │                        │
      │                   ⑤ APP_EVENT_TX_START               │
      │                             ▼                        │
      │                        rf_power ──► rf_swr           │
      │                             │      ⑥ 读 SWR          │
      │                             │◄────────┘              │
      │                    ⑦ SWR ≤ 3.0 ?                     │
      │                    ├─ 否 → 禁止发射，上报告警          │
      │                    └─ 是 ↓                           │
      │                        drv_pa (设定功率)              │
      │                        drv_si5351 (设定频率)          │
      │                        rf_keyer (键控发报)            │
      │                             │                        │
      │                             │ ⑧ 报文发完 → TX_STOP    │
      │                             ▼                        │
      │                        ardf_schedule (下一时隙)       │
```

---

## 3. 组件清单（28 个）

> 状态：本轮全部为 **骨架待实现**（仅目录与 README，无实现代码）。
> 组件目录位于**私有固件仓**的 `components/<组件名>/`。

### L0 板级与基础层（4）

| 组件 | 职责 | 依赖 |
|------|------|------|
| `bsp_board` | 板级定义：GPIO 映射、硬件版本识别、上电初始化顺序、板级自描述 | `utils_common` |
| `bsp_io_expander` | TCA9535 16 位 I2C 扩展器驱动（继电器 / 按键 / 编码器 / LCD 背光等慢速 IO 的统一出口） | `bsp_board`、`utils_common` |
| `bsp_storage` | NVS 分区封装：配置区、调谐记忆区、密钥区；版本迁移与默认值 | `utils_common` |
| `utils_common` | 日志、错误码、环形缓冲、时间与单位换算、CRC | — |

### L1 外设驱动层（7）

| 组件 | 职责 | 依赖 |
|------|------|------|
| `drv_si5351` | Si5351 本振驱动（I2C）：3.5–3.6 MHz、100 Hz 步进、频率校准与微调 | `bsp_board`、`utils_common` |
| `drv_lcd12864` | 12864 液晶（ST7567，**I2C 为主 / SPI 为备选**）：字库、绘图、局部刷新 | `bsp_board`、`bsp_io_expander` |
| `drv_ec11` | EC11 旋转编码器：方向识别、加速度、按键（经 TCA9535 或中断） | `bsp_io_expander` |
| `drv_keys` | 双按键消抖与长按识别、有源蜂鸣器提示音 | `bsp_io_expander` |
| `drv_relay` | 6 路继电器组抽象（K1–K6）：组合写入、最小切换间隔、机械寿命计数 | `bsp_io_expander` |
| `drv_pa` | 功放控制：PA_EN 使能 + LEDC 调压（0.02–2.5 W），功率档位映射 | `bsp_board`、`bsp_io_expander` |
| `drv_analog` | ADC 采样与滤波：电池电压、电源电流、NTC 功放温度、前向/反向检波 | `bsp_board` |

### L2 射频层（3）

| 组件 | 职责 | 依赖 |
|------|------|------|
| `rf_swr` | Tandem Match 定向耦合器换算：正/反向功率、SWR、反射系数；检波校准曲线 | `drv_analog` |
| `rf_keyer` | A1A CW 键控：软起软降 2–5 ms、10–12 WPM、长音生成、报文队列 | `bsp_board`、`drv_relay` |
| `rf_power` | 功率设定与闭环、SWR 联锁保护（>3.0 禁发）、低功率探测模式 | `drv_pa`、`rf_swr`、`drv_analog` |

### L3 ATU 自动天调层（3）

| 组件 | 职责 | 依赖 |
|------|------|------|
| `atu_match` | L 型匹配网络模型与继电器编解码：12/33/47 µH × 22/120/330 pF，64 组合；理论 SWR 预估 | `drv_relay`、`utils_common` |
| `atu_tuner` | 调谐算法（移植 N7DDC ATU-100 思路）：粗调 Grundmatch + 细调 Feinabstimmung + 全遍历兜底 | `atu_match`、`rf_swr`（经抽象接口注入） |
| `atu_state` | 调谐状态机、NVS 记忆加载/写入/命中、调谐触发与超时 | `atu_tuner`、`atu_match`、`bsp_storage` |

### L4 ARDF 业务层（3）

| 组件 | 职责 | 依赖 |
|------|------|------|
| `ardf_mode` | 六种竞赛模式时序状态机（`MODE_STANDARD` / `MODE_SHORT_DISTANCE` / `MODE_FAST` / `MODE_FOXORING` / `MODE_SUNSHINE` / `MODE_SHORT_FOXORING`） | `ardf_schedule`、`ardf_code` |
| `ardf_code` | 识别码表与报文编码：MO / MOE / MOI / MOS / MOH / MO5、单数字 0–9、字母 AA–OO；摩尔码字库与 WPM 点划时长换算 | `utils_common` |
| `ardf_schedule` | 发射窗口调度：5 分钟/1 分钟、1 分钟/12 秒、连续发射；频率分配表 | `utils_common` |

### L5 网络与同步层（4）

| 组件 | 职责 | 依赖 |
|------|------|------|
| `net_espnow` | ESP-NOW 链路层：WiFi 初始化、peer 管理、收发队列、信道固定 | `bsp_board`、`mesh_security` |
| `mesh_router` | 单跳中继路由（**仅支持 2 跳**）、转发、去重、跳数限制 | `net_espnow` |
| `mesh_security` | HMAC-SHA256 消息认证、MAC 白名单、序列号防重放（滑动窗口） | `bsp_storage`、`utils_common` |
| `net_timesync` | 主从时钟同步（每 5 分钟重同步）、NTP 校时、RTC（内部 RC + DNP 晶振焊盘） | `net_espnow`、`mesh_router`、`bsp_storage` |

### L6 应用与集成层（4）

| 组件 | 职责 | 依赖 |
|------|------|------|
| `app_core` | 应用主框架、事件总线、任务编排、模式调度、全局状态机（待机/长音/识别码/间隔） | 全部 L0–L5 |
| `ui_menu` | 菜单系统与界面状态机：显示台号/频率/模式/功率/SWR/温度/电池 | `drv_lcd12864`、`drv_ec11`、`drv_keys`、`bsp_storage` |
| `comm_console` | 与中控 PC 的通信：USB-CDC / UART / WiFi；引入 `software/protocol/generated/`（规划中，待创建）的包头 | `net_espnow`、`bsp_storage` |
| `diag_selftest` | 上电自检与产测模式 | 全部 L0–L2、`net_espnow` |

### 3.1 组件依赖图（简版）

```
                        app_core
        ┌───────┬───────────┼───────────┬────────────┐
     ui_menu  comm_console  ardf_mode  atu_state  diag_selftest
        │        │             │           │            │
        │   net_timesync   ardf_schedule  atu_tuner     │
        │        │             │           │            │
        │   mesh_router    ardf_code    atu_match       │
        │        │                         │            │
        │   net_espnow ── mesh_security    │            │
        │                                  │            │
        │              rf_power ─────── rf_swr     drv_relay
        │                 │              │             │
        │             rf_keyer      drv_analog    bsp_io_expander
        │                 │              │             │
        └───────────── bsp_board ────────┴──── bsp_storage ── utils_common
```

---

## 4. ESP-IDF 工程结构

### 4.1 规划目录树

> 下列工程结构位于**私有固件仓**（`ARDF-MeshTuneFox80-firmware`），不在本公开仓。

```
私有固件仓 ARDF-MeshTuneFox80-firmware/
├── CMakeLists.txt              ⬜ 待创建  工程根：project(ardf_meshtunefox80)
├── sdkconfig.defaults          ⬜ 待创建  默认配置
├── partitions.csv              ⬜ 待创建  分区表
├── version.txt                 ⬜ 待创建  版本（由 git describe 生成）
├── main/                       ✅ 已建立
│   ├── CMakeLists.txt          ⬜
│   ├── Kconfig.projbuild       ⬜
│   └── app_main.c              ⬜
├── components/                 ✅ 已建立（28 个组件骨架）
├── test/                       ✅ 已建立
├── tools/                      ✅ 已建立
└── docs/                       ✅ 已建立
```

> 本轮**只创建目录与文档**，未创建上述 `⬜` 构建文件。

> ⚠️ 上述目录树与 §4.2 的组件结构均为**私有固件仓**内的工程；本公开仓不含固件源码，只发布编译后的固件二进制。

### 4.2 组件目录约定

```
components/<组件名>/
├── README.md            说明文档（必须先写）
├── CMakeLists.txt       ⬜ idf_component_register(SRCS ... INCLUDE_DIRS "include" REQUIRES ...)
├── Kconfig              ⬜ 组件级配置项（可选）
├── include/             公共头文件 → 自动加入依赖方的 include 路径
│   └── <组件名>.h
├── src/                 私有实现与私有头
│   └── <模块名>.c
└── test/                ⬜ 组件级单元测试（可选）
```

- `include/` 存在时，ESP-IDF 自动将其加入 include 路径；不存在则组件根目录入 include 路径。
- **只把需要对其它组件暴露的内容放 `include/`**；其余一律 `src/`。

### 4.3 分区表规划

| 分区 | 类型 | 大小（规划） | 用途 |
|------|------|-------------|------|
| `nvs` | data/nvs | 24 KB | 配置、调谐记忆 |
| `otadata` | data/ota | 8 KB | OTA 状态 |
| `phy_init` | data/phy | 4 KB | 射频校准 |
| `nvs_keys` | data/nvs_keys | 4 KB | NVS 加密密钥（预留） |
| `factory` | app/factory | 1.5 MB | 主固件 |
| `storage` | data/spiffs | 512 KB | 字库、Web 页面、OTA 暂存 |

### 4.4 默认配置要点（`sdkconfig.defaults`）

| 配置项 | 值 | 理由 |
|--------|----|----|
| `CONFIG_IDF_TARGET` | `esp32c3` | — |
| `CONFIG_FREERTOS_HZ` | `1000` | 1 ms 时基，满足时序精度 |
| `CONFIG_ESP_DEFAULT_CPU_FREQ_MHZ_160` | `y` | 性能优先（choice 形式，非裸 `_MHZ`） |
| `CONFIG_COMPILER_OPTIMIZATION_SIZE` | `y` | `-Os`，Flash 与体积平衡（choice 形式） |
| `CONFIG_BT_ENABLED` | `n` | 不使用蓝牙；配置入口走 USB-CDC |
| `CONFIG_ESP_WIFI_ENABLED` | `y` | **ESP-NOW 依赖 WiFi 协议栈，必须使能**（设 `n` 会导致链路层无法初始化） |
| `CONFIG_ESP_WIFI_SOFTAP_SUPPORT` | `n` | 只用 ESP-NOW，不需要 AP |
| `CONFIG_ESP_WIFI_STATIC_RX_BUFFER_NUM` 等 | 调小 | ESP-NOW 占空比低，省 RAM |
| `CONFIG_ESP_WIFI_ENABLE_WPA3_SAE`、`..._SAE_PK`、`..._ENTERPRISE_SUPPORT` | `n` | 不使用 WPA3 / 企业级（注意符号名，见下） |
| `CONFIG_LWIP_DHCPS` | `n` | 不做 DHCP 服务器 |
| `CONFIG_ESP_MAIN_TASK_STACK_SIZE` | `4096` | — |
| `CONFIG_PARTITION_TABLE_CUSTOM_FILENAME` | `partitions.csv` | 自定义分区 |
| `CONFIG_ESPTOOLPY_FLASHSIZE_4MB` | `y` | 4 MB Flash（choice 形式） |
| `CONFIG_ESP_TASK_WDT_TIMEOUT_S` | `10` | 任务看门狗 |

> 🔴 **本表只是设计意图；权威清单是私有固件仓的 `sdkconfig.defaults`。**
> 配置项名称**必须以实际 ESP-IDF 的 Kconfig 为准**——本表早期草稿中曾出现若干**不存在的符号名**，
> 已于 2026-09 逐项对照 ESP-IDF v5.1.4 源码勘误，记录如下以免再被抄错：
>
> | 曾写（错误） | 实际情况 |
> |-------------|---------|
> | `CONFIG_ESP_WIFI_ENABLE_WPA3_SAFE` | ❌ 不存在。正确名为 `CONFIG_ESP_WIFI_ENABLE_WPA3_SAE` |
> | `CONFIG_ESP_WIFI_DPP_ENABLED` | ❌ 不存在。正确名为 `CONFIG_ESP_WIFI_DPP_SUPPORT`（默认已为 `n`） |
> | `CONFIG_ESP_WIFI_11B_LONG_PREAMBLE` | ❌ v5.x 无此符号。长距离模式由**运行期 API** 设置：`esp_wifi_set_protocol(WIFI_PROTOCOL_LR)` + `esp_wifi_config_11b_rate()` |
> | `CONFIG_ESP_ADC_CAL_CURVE_FITTING` | ❌ `esp_adc` 没有选择校准方案的 Kconfig 开关。ESP32-C3 的曲线拟合由**运行期 API** 决定：`adc_cali_create_scheme_curve_fitting()` |
> | `CONFIG_LWIP_IPV4=n` / `CONFIG_LWIP_IPV6=n` | ⚠️ **刻意不采用**。激进裁剪 IP 栈会牵连 `esp_netif` / `esp_wifi` 及后续 `comm_console` 的依赖，收益小、风险大；RAM 节省主要来自 WiFi 收发缓冲调小 |
> | `CONFIG_ESP_DEFAULT_CPU_FREQ_MHZ`、`CONFIG_COMPILER_OPTIMIZATION`、`CONFIG_ESPTOOLPY_FLASHSIZE` | ⚠️ 裸名不生效，实际是 choice：`_160` / `_SIZE` / `_4MB` |

### 4.5 FreeRTOS 任务规划

| 任务名 | 优先级 | 栈（字） | 周期 / 触发 | 职责 |
|--------|--------|---------|------------|------|
| `task_rf_ctrl` | 高（10） | 3072 | `esp_timer` 1 ms 回调 + 事件 | CW 键控时序、软起软降、发射窗口切换 |
| `task_atu` | 中高（8） | 4096 | 事件触发 | 调谐搜索、SWR 采样、NVS 写回 |
| `task_mesh` | 中（6） | 4096 | ESP-NOW 收包回调 + 队列 | 同步帧收发、中继转发、队列处理 |
| `task_telemetry` | 中（5） | 3072 | 1 Hz | ADC 采样、状态打包、上报 |
| `task_ui` | 低中（4） | 4096 | 10–20 Hz | 菜单刷新、编码器/按键处理、LCD 局部刷新 |
| `task_console` | 低（3） | 4096 | 事件触发 | 中控协议解析与应答 |
| `app_main` | — | — | 初始化完成后退出 | 初始化装配 |

**设计约束**

- CW 键控时序必须在**高优先级任务 + `esp_timer`** 中完成，禁止放在 WiFi 任务上下文。
- ESP-NOW 回调上下文（WiFi 任务）**禁止**做重活与阻塞操作，只入队；重活交 `task_mesh`。
- 发射窗口内收到的同步帧入队列，**发射结束后**处理（避免与射频控制竞争）。
- LCD 刷新（I2C，全屏约 25 ms）在 `task_ui` 中完成，不得阻塞 `task_rf_ctrl`。

### 4.6 显示刷新预算

LCD 走 I2C 共享总线（[ADR-0004](adr/ADR-0004-lcd12864-on-shared-i2c.md)）：400 kHz 下全屏 1024 字节约 25 ms。
因此：

- UI 必须采用**局部刷新**（只重绘变化区域）。
- I2C 总线需**互斥**（`xSemaphoreTake`），并给 LCD 传输设置低于继电器写入的优先级或直接串行化在同一任务。
- 若实测刷新不足，备选方案为 SPI 模式 LCD（预留 GPIO9/10），届时重写 `drv_lcd12864` 的传输层即可。

---

## 5. 关键机制设计

### 5.1 事件总线（`app_core`）

- 类型：FreeRTOS 队列 + 事件组，或 `esp_event` 默认事件循环。
- 事件命名：`APP_EVENT_<域>_<动作>`，例如 `APP_EVENT_ATU_TUNE_REQ`、`APP_EVENT_TX_START`、`APP_EVENT_TX_STOP`、`APP_EVENT_SWR_ALARM`、`APP_EVENT_TIME_SYNCED`、`APP_EVENT_MESH_RX`。
- 所有跨层交互走事件；组件之间不直接互相 `#include` 对方的私有头。

### 5.2 发射安全联锁（`rf_power`）

```
发射请求
   │
   ├─► 读 SWR (rf_swr)
   │      │
   │      ├─ SWR > 3.0 ──► 拒绝发射，发布 APP_EVENT_SWR_ALARM，蜂鸣器告警
   │      ├─ 2.0 < SWR ≤ 3.0 ──► 降功率发射（或触发重新调谐）
   │      └─ SWR ≤ 2.0 ──► 正常发射
   │
   └─► 温度检查 (drv_analog NTC)
          └─ 超限 ──► 降功率 / 停止发射
```

**低功率探测**：ATU 搜索与功率档位切换时，先以低功率探测扫点，避免满功率失谐遍历击穿 BS170。

### 5.3 ATU 调谐流程（`atu_state` + `atu_tuner`）

```
1. 加载 NVS 记忆组合（若有）
2. 低功率探测当前 SWR
   ├─ SWR ≤ 目标值 ──► 命中，微调 <0.5 秒结束
   └─ 否则 ↓
3. 粗调 Grundmatch：查预定义搜索表，找 SWR 相对较低的起点
4. 细调 Feinabstimmung：坐标下降，每次只改一个继电器，保留改善方向
5. 若细调后 SWR > 2.0 ──► 全遍历 64 组，取全局最优
6. 成功后写回 NVS
```

**性能目标**：粗调+细调 2–4 秒；全遍历约 5 秒；成功率 >95%。

### 5.4 Mesh 通信与安全（`net_espnow` + `mesh_router` + `mesh_security`）

| 层级 | 机制 |
|------|------|
| 链路层 | ESP-NOW 原生 CCMP 加密 |
| 应用层 | HMAC-SHA256 消息认证 |
| 应用层 | MAC 地址白名单 |
| 应用层 | 序列号防重放（滑动窗口） |

- 路由：单跳中继容错，**仅支持 2 跳**，帧携带 TTL 与源 MAC 用于去重。
- 距离：开阔地 100 m，密林 30–50 m。
- 帧排队：发射窗口内收到的同步帧入队列，发射结束后处理。

### 5.5 时钟同步（`net_timesync`）

- 主控为时间源；从机每 **5 分钟**与主控重同步。
- 同步报文带 UTC 时间戳与主控发送时刻，从机用往返延迟（RTT）估算偏差并平滑。
- 依托 5 分钟重同步，内部 RC 振荡器可满足需求；底板**保留 32.768 kHz 晶振 DNP 焊盘**作为升级选项。
- 无主控时支持 NTP 校时（需 WiFi 接入）。

---

## 6. 测试策略

### 6.1 分层测试

| 层级 | 手段 | 运行环境 |
|------|------|---------|
| 纯算法组件 | Unity 单元测试 + 宿主机可跑的抽象接口 | CI（无硬件） |
| 驱动组件 | Unity + pytest-embedded（真实板子） | 本地 / 硬件在环 |
| 集成（模式时序、调谐流程） | pytest-embedded + 逻辑分析仪 / 示波器 | 本地 |
| 端到端（Mesh 容错、竞赛模式） | 多台真机 + 中控软件 | [validation/](../validation/README.md) |

### 6.2 必须可宿主机测试的组件

`atu_tuner`、`atu_match`、`ardf_code`、`ardf_schedule`、`rf_swr`（换算部分）。

实现约束：这些组件的硬件访问必须通过**注入的抽象接口**（`*_ops_t` 函数指针表），使测试可传入仿真阻抗、仿真时钟、仿真继电器状态。

### 6.3 优先测试项

| 测试项 | 断言 |
|--------|------|
| `ardf_code` 识别码表 | MO/MOE/MOI/MOS/MOH/MO5、0–9、AA–OO 全部编码正确；WPM 点划时长符合 10–12 WPM |
| `ardf_schedule` 时序 | 5 分钟周期误差 <0.1 s；1 分钟周期误差 <0.1 s；1 分钟内 5 台各 12 秒 |
| `rf_swr` 换算 | 已知正/反向电压 → SWR 误差 <0.2；SWR 1.2/1.5/2.0 可分辨 |
| `atu_match` 组合编解码 | 64 组继电器状态 ↔ (L, C) 双向映射无歧义 |
| `atu_tuner` 搜索收敛 | 用挂树（120-j1050 Ω）与实验室（50-j1110 Ω、88-j1030 Ω）仿真阻抗，验证收敛到 SWR<2.5 / <1.8 / <2.0 且迭代次数在预算内 |

---

## 7. Arduino → ESP-IDF 迁移清单

原版工程使用的 Arduino 生态依赖需要替代：

| 原 Arduino 依赖 | 用途 | ESP-IDF 方案 |
|----------------|------|-------------|
| `Etherkit Si5351` (Arduino 库) | Si5351 本振 | **自行实现** `drv_si5351`（I2C 寄存器直写，参考 Si5351A 数据手册） |
| `U8g2` | 12864 显示 | **自行实现** `drv_lcd12864`（ST7567 指令集） |
| `Encoder` / 中断轮询 | EC11 | **自行实现** `drv_ec11`（TCA9535 轮询 + 加速度算法） |
| `WiFi.h` / `esp_now.h` (Arduino 封装) | 联网 | ESP-IDF 原生 `esp_wifi` + `esp_now` |
| `Preferences.h` | 参数存储 | `bsp_storage`（nvs_flash API） |
| `Wire.h` | I2C | ESP-IDF `driver/i2c_master.h`（v5.x 新驱动） |
| `ArduinoOTA` | 固件升级 | ESP-IDF `esp_https_ota` / `esp_ota_ops` |
| `millis()` / `delay()` | 时序 | `esp_timer` + FreeRTOS `vTaskDelayUntil` |

**迁移原则**：不追求 API 一一对应，而是按本项目的分层重新设计接口。原 Arduino 代码仅作**行为参考**（尤其是 Si5351 频率计算与显示字库）。

---

## 8. 许可与固件发布边界

| 项 | 许可 | 说明 |
|------|------|------|
| 固件源码（全部组件） | **不授予** | 源码位于**私有仓** [ARDF-MeshTuneFox80-firmware](https://github.com/PatrickShih774/ARDF-MeshTuneFox80-firmware)，本公开仓不含固件源码 |
| 固件二进制发布物 | `LicenseRef-ARDF-NC-1.0` | 「ARDF 业余无线电非商业许可 1.0」：**仅限业余无线电非商业用途**；只覆盖编译后的二进制，不要求公开源码 |
| `software/master-console/`（规划中，待创建） | **Apache 2.0** | 允许闭源分发 |
| `software/protocol/`（规划中，待创建） | **Apache 2.0** | 共享协议定义的唯一事实来源 |

- 固件工程（`components/`、`main/`、`test/`、`tools/`、组件文档）全部在私有仓维护；本公开仓的 `software/` 当前只放 `README.md`（软件入口与规划要点）。中控 PC 软件（`software/master-console/`，规划中，待创建）、共享协议（`software/protocol/`，规划中，待创建）与跨子工程工具（`software/tools/`，规划中，待创建）**都还没开始写**。
- 固件**编译后的二进制**通过 GitHub Releases 分发，适用 `LicenseRef-ARDF-NC-1.0`（仅限业余无线电非商业用途）。
- 许可全文见 `LICENSES/LicenseRef-ARDF-NC-1.0.txt`，授权映射与合规路径见 [08-许可证与合规](08-licensing-and-compliance.md)。

---

## 9. 关联文档

| 文档 | 用途 |
|------|------|
| [ADR-0001 采用 ESP-IDF 而非 Arduino](adr/ADR-0001-adopt-esp-idf-over-arduino.md) | 选型理由 |
| [ADR-0004 12864 液晶走 I2C 共享总线](adr/ADR-0004-lcd12864-on-shared-i2c.md) | GPIO 分配约束 |
| **私有固件仓**（`ARDF-MeshTuneFox80-firmware`） | 固件工程细节：工程结构、组件清单与依赖规则、构建与测试 |
| [05-软硬件接口契约](05-hw-sw-interface-contract.md) | GPIO / 连接器 / 协议 |
| [06-构建与开发环境](06-build-and-dev-environment.md) | 工具链与构建 |
| [07-编码规范](07-coding-standards.md) | 代码风格 |
| 共享协议（规划中，见 `software/README.md`） | 通信协议唯一事实来源 |
