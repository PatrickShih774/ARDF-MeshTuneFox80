# 07 · 编码规范

> 状态：已建立｜适用版本：V3.7｜权威性：**★ 唯一权威**（代码风格）
> 语言：C（C11）为主，必要时少量 C++｜基线：ESP-IDF 官方风格 + 嵌入式安全实践

---

## 1. 总则

1. **可读性优先于技巧**。嵌入式代码的调试成本远高于书写成本。
2. **显式优于隐式**。不使用依赖隐式转换、未定义行为、编译器扩展的写法。
3. **不信任外部输入**。ADC 读数、ESP-NOW 收包、NVS 内容都必须校验。
4. **时序关键代码必须可论证**。中断/高优先级任务中的代码要能说明最坏执行时间。
5. **遵循 `.editorconfig`**：UTF-8、**LF 行尾**、4 空格缩进、文件末尾留一个换行。

---

## 2. 文件组织

### 2.1 目录

> 下列结构适用于**私有固件仓**中的固件组件；本公开仓不含固件源码。

```
components/<组件名>/
├── include/<组件名>.h      公共头（对外契约）
├── src/<模块名>.c          实现
├── src/<模块名>_internal.h 私有头（仅本组件内可见）
└── test/                   组件级测试
```

- **公共头只暴露必需内容**：不暴露内部结构体定义、不暴露私有宏。
- 私有头命名必须带 `_internal` 或语义化后缀，且**禁止**被其它组件 `#include`。

### 2.2 文件头注释

每个 `.c` / `.h` 文件顶部：

```c
/*
 * ARDF-MeshTuneFox80 - <模块中文名>
 *
 * 职责：<一句话说明本文件负责什么>
 * 分层：L<n> <层名>
 * 依赖：<本文件依赖的组件>
 *
 * SPDX-License-Identifier: LicenseRef-ARDF-NC-1.0
 * Copyright (c) 2026 ARDF-MeshTuneFox80 Contributors
 */
```

> **每个源文件必须带 SPDX 标识符**。固件源码位于**私有固件仓**，其 SPDX 标识符为 `LicenseRef-ARDF-NC-1.0`（「ARDF 业余无线电非商业许可 1.0」，仅限业余无线电非商业用途，只覆盖编译后的二进制）。中控 PC 软件（`software/master-console/`，规划中，待创建）与共享协议（`software/protocol/`，规划中，待创建）用 `Apache-2.0`。

### 2.3 头文件保护

统一使用 `#pragma once`（ESP-IDF 生态主流做法），不混用 `#ifndef` 守卫。

---

## 3. 命名规范

| 对象 | 规范 | 示例 |
|------|------|------|
| 组件目录 | `snake_case` + 层前缀 | `bsp_board`、`drv_si5351`、`atu_tuner` |
| 源文件 | `snake_case.c` | `atu_tuner.c` |
| 公共头 | `snake_case.h` | `atu_tuner.h` |
| 类型（struct/enum/union） | `snake_case_t`，带组件前缀 | `atu_match_state_t`、`rf_swr_result_t` |
| 枚举常量 | 全大写 + 组件前缀 | `ATU_STATE_IDLE`、`ARDF_MODE_FAST` |
| 函数 | `snake_case()`，带组件前缀 | `atu_tuner_run()`、`rf_swr_read()` |
| 宏 / 常量 | 全大写 + 组件前缀 | `ATU_RELAY_COUNT`、`RF_SWR_LIMIT` |
| 全局变量 | **禁止**。必须用 `static` 或访问函数 | — |
| 静态文件级变量 | `s_` 前缀 | `static atu_match_state_t s_state;` |
| 局部变量 | `snake_case` | `target_swr` |
| 布尔变量 | `is_` / `has_` / `should_` 前缀 | `is_tuning`、`has_memory` |
| FreeRTOS 任务名 | `task_<职责>` | `task_rf_ctrl` |
| 事件常量 | `APP_EVENT_<域>_<动作>` | `APP_EVENT_TX_START` |
| 日志 TAG | 组件名 | `static const char *TAG = "atu_tuner";` |

**单位后缀（强制）**：涉及物理量的变量必须带单位后缀。

| 后缀 | 含义 | 示例 |
|------|------|------|
| `_hz` | 赫兹 | `freq_hz` |
| `_mhz` | 兆赫 | `freq_mhz` |
| `_ms` / `_us` / `_s` | 时间 | `key_down_ms` |
| `_mv` / `_uv` | 电压 | `vbat_mv` |
| `_ma` | 电流 | `pa_current_ma` |
| `_mw` / `_w` | 功率 | `pa_power_mw` |
| `_cdeg` | 摄氏 ×100（定点） | `pa_temp_cdeg` |
| `_uh` / `_pf` | 电感 / 电容 | `ind_uh` |
| `_ohm` | 电阻 | `load_r_ohm` |
| `_x100` | 定点 ×100（SWR） | `swr_x100` |

---

## 4. 代码风格

### 4.1 格式

- 缩进：**4 空格**，禁用 Tab。
- 行宽：**≤100 字符**。
- 大括号：**K&R 风格**（左括号不换行），函数定义的左括号换行。
- 指针：`type *name`。
- 每行一个声明。

```c
static esp_err_t atu_tuner_run(atu_tuner_ctx_t *ctx, uint16_t target_swr_x100)
{
    if (ctx == NULL) {
        ESP_LOGE(TAG, "ctx 为空");
        return ESP_ERR_INVALID_ARG;
    }

    for (size_t i = 0; i < ATU_RELAY_COUNT; i++) {
        esp_err_t err = atu_match_set_relay(ctx->match, i, false);
        if (err != ESP_OK) {
            return err;
        }
    }

    return ESP_OK;
}
```

### 4.2 注释

- 注释用**简体中文**（面向国内社区）。
- 公共 API 用 **Doxygen 风格**：

```c
/**
 * @brief 执行一次 ATU 自动调谐。
 *
 * 流程：加载 NVS 记忆 → 低功率探测 → 粗调 Grundmatch → 细调 Feinabstimmung
 *      → 若 SWR 仍 > 2.0 则全遍历 64 组 → 写回 NVS。
 *
 * @param[in]  ctx          调谐上下文（不可为 NULL）
 * @param[in]  target_swr_x100 目标 SWR ×100（如 200 表示 SWR 2.0）
 * @param[out] best_combo   调谐得到的最佳继电器组合
 *
 * @return
 *      - ESP_OK              调谐成功
 *      - ESP_ERR_TIMEOUT     超过调谐时间预算
 *      - ESP_ERR_INVALID_ARG 参数非法
 *      - ESP_FAIL            未找到满足目标的组合
 *
 * @note 必须在非射频控制任务上下文中调用；每次调用约耗时 2–5 秒。
 * @warning 调谐期间禁止发射，须先切到低功率探测模式。
 */
esp_err_t atu_tuner_run(atu_tuner_ctx_t *ctx, uint16_t target_swr_x100, uint8_t *best_combo);
```

- 关键算法（如调谐搜索、SWR 换算）必须注释**算法来源**：

```c
/* 算法借鉴 N7DDC ATU-100 的 Feinabstimmung（坐标下降）：
 * 每次只改变一个继电器状态，保留 SWR 改善方向，直到无法继续改善。
 * 参考 hardware/reference/atu-100/README.md */
```

- 禁止保留被注释掉的代码。用版本控制历史代替。

### 4.3 数值与类型

| 规则 | 说明 |
|------|------|
| 显式宽度 | 用 `uint8_t` / `int16_t` / `uint32_t`，**禁用裸 `int`** 表示有范围含义的量 |
| 禁止浮点用于实时路径 | 时序/中断/高频循环内用**定点**（×100、×1000）；浮点仅用于初始化与离线计算 |
| 物理量定点化 | SWR 用 `_x100`；温度用 `_cdeg`；功率用 `_mw` |
| 禁用 `float` 比较 | 必要时用误差带 |
| 常量加后缀 | `1000U`、`0x1FUL`、`1.5f`（避免隐式提升） |
| 禁止魔术数字 | 用具名宏或 `const` 常量 |
| 禁止有符号/无符号混比 | 编译开 `-Wsign-compare` 并清零警告 |

### 4.4 内存与资源

| 规则 | 说明 |
|------|------|
| 禁止动态内存用于长期对象 | 用静态分配或 `static` 池 |
| 禁止 `malloc` 于中断/高优先级任务 | 可能阻塞 |
| 栈大小必须显式指定 | 每个任务给足并记录在 [03-软件架构](03-software-architecture.md) 任务表 |
| 递归禁止（除非有深度证明） | 栈不可预测 |
| `const` 正确性 | 只读指针参数一律 `const` |
| `static` 一切非导出符号 | 避免符号污染与链接冲突 |

### 4.5 错误处理

- **统一返回 `esp_err_t`**：`ESP_OK` / `ESP_ERR_*` / `ESP_FAIL`。
- **每个返回值都必须检查**。允许显式忽略时写 `(void)func(...)` 并加注释说明。
- 错误路径必须**清理已获取的资源**（用统一的 `goto cleanup` 模式）。
- 禁止 `assert()` 用于可恢复错误；`assert` 只用于**编程错误**（不变量）。
- 日志分级：

| 级别 | 用途 |
|------|------|
| `ESP_LOGE` | 功能失败、需人工介入 |
| `ESP_LOGW` | 异常但可自恢复（如 SWR 偏高触发重新调谐） |
| `ESP_LOGI` | 状态变迁、模式切换（默认关闭或最少输出） |
| `ESP_LOGD` | 调试细节（默认关闭） |
| `ESP_LOGV` | 逐字节级（默认关闭） |

- **禁止在中断与高优先级任务中打日志**（`ESP_LOGI` 会加锁）。

### 4.6 并发

| 规则 | 说明 |
|------|------|
| 共享资源必须加锁 | 用 `SemaphoreHandle_t` / `portMUX_TYPE` |
| 中断与任务共享的变量 | `volatile` + 临界区 |
| 中断中只做最短工作 | 入队，不做计算 |
| ESP-NOW 回调上下文 | **只入队**，禁止阻塞与重活 |
| 禁止在持锁期间调用可能阻塞的 API | 防死锁 |
| 优先级反转防护 | 必要时用互斥量的优先级继承 |

---

## 5. 分层与解耦（强制）

1. **禁止跨层调用**：L(n) 只能依赖 L(0)…L(n-1)（见 [03-软件架构](03-software-architecture.md) §2.1）。
2. **禁止硬编码 GPIO**：必须引用 `bsp_board`。
3. **算法组件禁止直接访问硬件**：通过注入的 `*_ops_t` 函数指针表获取数据，保证可测试。
4. **禁止组件间 `#include` 私有头**。
5. **跨层交互走 `app_core` 事件总线**。

---

## 6. ESP-IDF 特有约定

| 项 | 约定 |
|----|------|
| 日志 TAG | `static const char *TAG = "<组件名>";` 放在文件顶部 |
| 配置项 | 用 Kconfig（`CONFIG_<组件>_<项>`），**禁止**把可配置值硬编码 |
| 组件注册 | `idf_component_register(SRCS ... INCLUDE_DIRS "include" REQUIRES ...)` |
| 初始化顺序 | 集中在 `app_main`，组件提供 `*_init()` 返回 `esp_err_t` |
| 任务创建 | 在 `app_main` 或组件 `*_start()`，栈大小显式写并注释理由 |
| 时间 | 用 `esp_timer_get_time()`（µs）/ `xTaskGetTickCount()`；**禁止裸 `vTaskDelay` 做时序**，用 `vTaskDelayUntil` |
| 中断 | 用 `gpio_isr_handler_add` + `IRAM_ATTR`；ISR 内不做日志与阻塞 |
| NVS | 通过 `bsp_storage` 统一访问，**禁止**组件直接调 `nvs_*` |
| 看门狗 | 长任务（调谐遍历）需定期 `esp_task_wdt_reset()` 或放独立任务并单独配置 |

---

## 7. 安全检查清单（提交前自查）

- [ ] 所有外部输入已校验（ADC 范围、收包长度、NVS 内容、协议字段）
- [ ] 所有数组访问已做边界检查
- [ ] 无 `strcpy` / `sprintf` / `gets`；用 `snprintf` 并检查返回值
- [ ] 收包缓冲区长度**在拷贝前**校验，不信任报文中的长度字段
- [ ] 无动态内存泄漏（每条错误路径都释放）
- [ ] 无密钥、呼号等敏感信息硬编码
- [ ] 中断与高优先级任务中无日志、无阻塞、无动态内存
- [ ] ISR 与任务共享变量有 `volatile` 或临界区保护
- [ ] 发射路径有 SWR 联锁（`SWR > 3.0` 禁发）
- [ ] 调谐/功率切换使用低功率探测（保护 BS170）

---

## 8. 编译警告策略

- 目标：**零警告**构建。
- 基线选项：`-Wall -Wextra -Werror`（`-Werror` 在 CI 中启用）。
- 禁止用 `#pragma GCC diagnostic ignored` 压制警告而不写理由注释。

---

## 9. 中控 PC 软件（规划中，待创建）

中控 PC 软件（`software/master-console/`，规划中，待创建）技术栈待定（[ADR-0005](adr/ADR-0005-console-tech-stack-tbd.md)）。若采用 Python，约定：

| 项 | 约定 |
|----|------|
| 版本 | Python 3.11+ |
| 风格 | PEP 8，`ruff format` + `ruff check` |
| 类型 | 全量类型注解，`mypy --strict` |
| 命名 | 模块/函数 `snake_case`，类 `PascalCase`，常量 `UPPER_SNAKE` |
| 文档字符串 | 简体中文，Google 风格 |
| 测试 | `pytest`，覆盖率目标 ≥80% |
| 协议 | **必须**使用 `software/protocol/generated/`（规划中，待创建）的生成代码，禁止手写帧结构 |

---

## 10. 关联文档

| 文档 | 用途 |
|------|------|
| [03-软件架构](03-software-architecture.md) | 分层与组件划分 |
| [05-软硬件接口契约](05-hw-sw-interface-contract.md) | 引脚与协议契约 |
| [06-构建与开发环境](06-build-and-dev-environment.md) | 工具链与构建 |
| [CONTRIBUTING.md](../CONTRIBUTING.md) | 分支模型与提交流程 |
| [.editorconfig](../.editorconfig) | 编辑器格式基线 |
