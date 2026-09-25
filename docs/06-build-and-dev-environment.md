# 06 · 构建与开发环境

> 状态：已建立｜适用版本：V3.7｜权威性：操作性文档

---

## 1. 工具链总览

| 用途 | 工具 | 版本要求 |
|------|------|---------|
| 固件构建 | **ESP-IDF** | **v5.1 及以上（推荐 v5.3 / v5.5）** |
| 目标芯片 | ESP32-C3（RISC-V） | — |
| 工具链 | `riscv32-esp-elf-gcc` | 随 ESP-IDF 安装（14.2.0 系列） |
| 构建系统 | CMake | ≥3.16 |
| 烧录/调试 | `esptool`、`openocd-esp32`、`riscv32-esp-elf-gdb` | 随 ESP-IDF 安装 |
| Python | 3.9–3.12（ESP-IDF 要求范围） | 由 `install.ps1` 管理虚拟环境 |
| 中控软件 | Python（拟定，**规划中，待创建**）见 [ADR-0005](adr/ADR-0005-console-tech-stack-tbd.md) | 3.11+ |
| 硬件 EDA | KiCad / 立创 EDA（择一，待定） | — |
| 测试框架 | Unity（ESP-IDF 自带）+ `pytest-embedded` | — |

> **重要**：本项目**不使用 Arduino IDE / PlatformIO-Arduino 框架**。理由见 [ADR-0001](adr/ADR-0001-adopt-esp-idf-over-arduino.md)。

> **固件源码在私有仓**：固件源码与构建工程位于私有仓 `ARDF-MeshTuneFox80-firmware`（`https://github.com/PatrickShih774/ARDF-MeshTuneFox80-firmware`），**构建前需先取得访问权**；本公开仓不含固件源码，只发布编译后的固件二进制。以下第 3、4 节中的构建与测试命令均在该私有固件仓根目录下执行。

---

## 2. 安装 ESP-IDF

### 2.1 Windows（推荐）

```powershell
# 1) 获取安装器
git clone -b v5.3 --recursive https://github.com/espressif/esp-idf.git C:\esp\esp-idf
cd C:\esp\esp-idf

# 2) 安装工具链（仅 esp32c3，节省时间与磁盘）
.\install.ps1 esp32c3

# 3) 每次开发会话先激活环境
. C:\esp\esp-idf\export.ps1
```

### 2.2 Linux / macOS

```bash
git clone -b v5.3 --recursive https://github.com/espressif/esp-idf.git ~/esp/esp-idf
cd ~/esp/esp-idf
./install.sh esp32c3
. ./export.sh
```

### 2.3 验证安装

```bash
idf.py --version
# 期望输出类似：ESP-IDF v5.3.x
```

### 2.4 已有离线安装包

若本机 `~/Downloads` 中已有以下文件，可直接使用而不必联网：

| 文件 | 用途 |
|------|------|
| `esp32-3.3.1.zip` | Arduino-ESP32（**本项目不用**，仅供对照原版工程） |
| `esp32-arduino-libs-idf-release_v5.5-129cd0d2-v4.zip` | ESP-IDF 库（Arduino 用，本项目不用） |
| `riscv32-esp-elf-14.2.0_20241119-x86_64-w64-mingw32.zip` | RISC-V 工具链（可手动放置到 `~/.espressif/tools/`） |
| `esptool-v5.1.0-windows-amd64.zip` | 烧录工具 |
| `openocd-esp32-win64-0.12.0-esp32-20250707.zip` | 调试器 |
| `riscv32-esp-elf-gdb-16.2_20250324-x86_64-w64-mingw32.zip` | GDB |

> 推荐仍用 `install.ps1`，它会自动校验版本与哈希，避免手工放置导致的版本错配。

### 2.5 编辑器

| 编辑器 | 配置 |
|--------|------|
| VS Code | 安装 **Espressif IDF** 扩展；打开**私有固件仓**根目录作为工作区（需先取得访问权） |
| CLion / VSCode + clangd | 使用 `idf.py -DCMAKE_EXPORT_COMPILE_COMMANDS=ON build` 生成 `compile_commands.json` |
| 格式化 | 遵循 `.editorconfig`（UTF-8、LF、4 空格、行尾去空白） |

**注意**：`.editorconfig` 要求 **LF 行尾**，Windows 下请勿改为 CRLF（`.gitattributes` 已强制 `eol=lf`）。

---

## 3. 构建固件

> ⚠️ **前置条件**：固件源码在**私有仓**（`ARDF-MeshTuneFox80-firmware`），需先取得访问权并克隆到本地；**本公开仓不含固件源码**。
>
> ⚠️ **当前状态**：私有固件仓中的构建文件（`CMakeLists.txt`、`sdkconfig.defaults`、`partitions.csv`）**尚未创建**，因此现在还无法构建。以下命令是**规划中的标准流程**。

### 3.1 标准流程

```bash
# 需先取得私有仓访问权
git clone https://github.com/PatrickShih774/ARDF-MeshTuneFox80-firmware.git
cd ARDF-MeshTuneFox80-firmware     # 即 <私有固件仓> 根目录

# 1) 首次：设置目标芯片
idf.py set-target esp32c3

# 2) 配置（可选，调出 menuconfig）
idf.py menuconfig

# 3) 构建
idf.py build

# 4) 烧录 + 监视
idf.py -p COM5 flash monitor
```

### 3.2 关键 `idf.py` 命令速查

| 命令 | 用途 |
|------|------|
| `idf.py set-target esp32c3` | 设置目标芯片（会清空 `sdkconfig`） |
| `idf.py menuconfig` | 图形化配置 |
| `idf.py build` | 编译 |
| `idf.py -p <PORT> flash` | 烧录 |
| `idf.py -p <PORT> monitor` | 串口监视（`Ctrl+]` 退出） |
| `idf.py -p <PORT> flash monitor` | 烧录后立即监视 |
| `idf.py fullclean` | 彻底清理（换目标芯片后必须） |
| `idf.py size` | 查看固件体积构成 |
| `idf.py size-components` | 按组件查看体积 |
| `idf.py erase-flash` | 擦除整片 Flash |
| `idf.py reconfigure` | 重新生成构建系统（改 `CMakeLists.txt` 后） |

### 3.3 构建配置基线

`sdkconfig.defaults` 的规划内容见 [03-软件架构](03-software-architecture.md) §4.4，要点：

```
CONFIG_IDF_TARGET="esp32c3"
CONFIG_FREERTOS_HZ=1000
CONFIG_ESP_DEFAULT_CPU_FREQ_MHZ_160=y
CONFIG_COMPILER_OPTIMIZATION_SIZE=y
CONFIG_BT_ENABLED=n
CONFIG_ESPTOOLPY_FLASHSIZE_4MB=y
CONFIG_PARTITION_TABLE_CUSTOM=y
CONFIG_PARTITION_TABLE_CUSTOM_FILENAME="partitions.csv"
CONFIG_ESP_TASK_WDT_TIMEOUT_S=10
```

### 3.4 分区表

规划见 [03-软件架构](03-software-architecture.md) §4.3。要点：

- `nvs` 24 KB（配置 + 调谐记忆）
- `factory` 1.5 MB（主固件）
- `storage` 512 KB（SPIFFS：字库、Web 页面、OTA 暂存）

### 3.5 注意：目标芯片切换

`idf.py set-target` 会**清空** `sdkconfig`。若需回到 ESP32-C3：

```bash
idf.py fullclean
idf.py set-target esp32c3
idf.py build
```

---

## 4. 单元测试

### 4.1 宿主机可跑（无硬件）

适用于纯算法组件：`atu_tuner`、`atu_match`、`ardf_code`、`ardf_schedule`、`rf_swr`（换算部分）。

这些组件通过**注入的抽象接口**（`*_ops_t` 函数指针表）访问硬件，测试时注入仿真实现。

```bash
cd ARDF-MeshTuneFox80-firmware/test    # 私有固件仓的 test/ 目录
idf.py --preview set-target linux   # 或使用独立的主机侧测试目标
```

> 具体目标名取决于 ESP-IDF 版本的 Linux target 支持情况；若不支持，则用 `pytest` 直接编译纯 C 算法文件（组件需保持无 IDF 依赖或依赖隔离）。

### 4.2 硬件在环（pytest-embedded）

```bash
pip install pytest-embedded pytest-embedded-serial-esp

cd ARDF-MeshTuneFox80-firmware/test    # 私有固件仓的 test/ 目录
pytest --target=esp32c3 --port=COM5
```

### 4.3 测试组织

| 层级 | 位置 |
|------|------|
| 组件级单元测试 | 私有固件仓 `components/<组件>/test/` |
| 跨组件集成测试 | 私有固件仓 `test/main/` |
| 硬件在环实测 | [`validation/`](../validation/README.md)（**需要仪器，不是代码测试**） |

---

## 5. 中控 PC 软件（规划中，待创建）

> 技术栈**待定**，见 [ADR-0005](adr/ADR-0005-console-tech-stack-tbd.md)。以下为 Python 方案的原型流程。
> ⚠️ `software/master-console/`（规划中，待创建）目录**尚不存在**，本节命令要等该目录创建后才可执行。

```bash
cd software/master-console       # 规划中，待创建（该目录尚不存在）
python -m venv .venv
.venv\Scripts\activate          # Windows
pip install -e ".[dev]"
pytest
python -m ardf_console
```

---

## 6. 协议代码生成（规划中，待创建）

`software/protocol/`（规划中，待创建）是协议唯一事实来源，固件与中控的帧代码由脚本生成：

```bash
cd software                       # software/tools/（规划中，待创建）
python tools/protocol_gen.py      # 生成到 software/protocol/generated/（规划中，待创建）
```

> ⚠️ 上述 `software/tools/`（规划中，待创建）与 `software/protocol/generated/`（规划中，待创建）目前均不存在。
> ⚠️ `software/protocol/generated/`（规划中，待创建）**禁止手工修改**，改动会被下次生成覆盖。

---

## 7. 常用开发任务

| 任务 | 命令 / 操作 |
|------|------------|
| 查看串口 | 设备管理器（Windows）→ 端口；`esptool.py chip_id` 验证连通 |
| 擦除 Flash（忘记密码/异常启动） | `idf.py -p COM5 erase-flash` |
| 更换分区表 | 改 `partitions.csv` → `idf.py build flash`（必要时先 `erase-flash`） |
| 查看固件大小 | `idf.py size-components` |
| 生成编译数据库 | `idf.py -DCMAKE_EXPORT_COMPILE_COMMANDS=ON build` |
| 串口监视退出 | `Ctrl+]` |
| 烧录失败（占用） | 关闭串口监视器/其他串口工具 |
| 首烧成功但反复重启 | 检查 strapping 引脚（GPIO2/8/9）外部电平 |

---

## 8. 开发环境检查清单

新成员上手时逐项确认：

- [ ] ESP-IDF 安装成功：`idf.py --version` 输出 v5.1+
- [ ] 工具链已装 RISC-V：`riscv32-esp-elf-gcc --version` 可用（在 IDF 环境中）
- [ ] 目标芯片可设：在私有固件仓根目录执行 `idf.py set-target esp32c3` 成功
- [ ] 串口连通：`esptool.py -p <PORT> chip_id` 返回芯片信息
- [ ] 编辑器遵守 `.editorconfig`（UTF-8 / LF / 4 空格）
- [ ] 已阅读 [02-仓库目录规范](02-repository-layout.md)（知道文件放哪里）
- [ ] 已阅读 [07-编码规范](07-coding-standards.md)
- [ ] 已阅读 [05-软硬件接口契约](05-hw-sw-interface-contract.md)（知道引脚怎么分配）

---

## 9. 故障排查

| 症状 | 可能原因 | 处理 |
|------|---------|------|
| `idf.py` 找不到命令 | 未激活导出脚本 | 执行 `export.ps1` / `export.sh` |
| `CMake Error: Unknown target` | 未 `set-target` | `idf.py set-target esp32c3` |
| 换芯片后编译报错 | 残留旧构建缓存 | `idf.py fullclean` |
| 烧录端口被占用 | 串口监视器未关闭 | 关闭 monitor / 其他串口工具 |
| 上电后反复重启 | strapping 引脚电平错误 | 检查 GPIO2/GPIO8/GPIO9 外部电路 |
| I2C 设备扫描不到 | 上拉缺失 / 地址错误 | 检查 4.7 kΩ 上拉；用 `i2cdetect` 式扫描 |
| ESP-NOW 收不到包 | 信道不一致 | 主从固定同一信道 |
| 时序抖动大 | 逻辑放在 WiFi 任务上下文 | 移到高优先级任务 + `esp_timer` |
| ADC 读数漂移 | 未校准 | 执行多点校准并写入 NVS |

---

## 10. 关联文档

| 文档 | 用途 |
|------|------|
| [03-软件架构](03-software-architecture.md) | 组件划分、任务规划、配置要点 |
| [07-编码规范](07-coding-standards.md) | 代码风格 |
| **私有固件仓**（`ARDF-MeshTuneFox80-firmware`） | 固件工程细节：源码、构建文件、组件文档（需先取得访问权） |
| [CONTRIBUTING.md](../CONTRIBUTING.md) | 分支模型与提交流程 |
| [software/README.md](../software/README.md) | 软件入口与规划要点（中控 PC 软件 / 共享协议 / 工具均规划中，待创建） |
| [ESP-IDF 官方文档](https://docs.espressif.com/projects/esp-idf/zh_CN/latest/esp32c3/) | 上游参考 |
