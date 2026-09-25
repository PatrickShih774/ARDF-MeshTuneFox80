# 06 · 构建与开发环境

> 状态：已建立｜适用版本：V3.7｜权威性：操作性文档

---

## 1. 工具链总览

| 用途 | 工具 | 版本要求 |
|------|------|---------|
| 固件构建 | **ESP-IDF** | **`v6.1`（本项目选用，见 §12.7）**；符号兼容性已实测 |
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
git clone -b v6.1 --recursive https://github.com/espressif/esp-idf.git C:\esp\esp-idf
cd C:\esp\esp-idf

# 2) 安装工具链（仅 esp32c3，节省时间与磁盘）
.\install.ps1 esp32c3

# 3) 每次开发会话先激活环境
. C:\esp\esp-idf\export.ps1
```

### 2.2 Linux / macOS

```bash
git clone -b v6.1 --recursive https://github.com/espressif/esp-idf.git ~/esp/esp-idf
cd ~/esp/esp-idf
./install.sh esp32c3
. ./export.sh
```

### 2.3 验证安装

```bash
idf.py --version
# 期望输出类似：ESP-IDF v6.1
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
> ⚠️ **当前状态**：私有固件仓的 **ESP-IDF 工程骨架已于 2026-09 建成**（`CMakeLists.txt`、
> `sdkconfig.defaults`、`partitions.csv`、`main/`、28 个组件的 `CMakeLists.txt`、`test/`），
> 具备首次构建条件。但：
>
> 1. **尚未实机验证构建** —— 建立骨架的环境**未安装 ESP-IDF**（`IDF_PATH` 为空），
>    配置项名称是对照 ESP-IDF v5.1.4 的 Kconfig 源码逐项核对的，未跑过 `idf.py build`。
>    首次构建时请留意是否有 Kconfig 未知项警告，并核对 `factory` 分区余量。
> 2. **各组件尚无实现** —— 28 个组件目前都注册为"接口组件"（只有 `INCLUDE_DIRS`，无 `SRCS`），
>    `app_main()` 只打印启动日志、不调用任何组件函数。构建产物是一个空壳固件。

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

---

## 11. 本地工作区布局与已知陷阱

- 本地工作区布局与已知陷阱：本文档第 11 节
> 其中**仍然有效**的内容并入本节，临时性内容（迁移步骤、缓存分析）已删除。

### 11.1 本地目录布局

项目根是一个**容器目录**，两个仓库作为子目录——这样 DSH 工作区只设一处即可覆盖两仓，
**`workspace-write` 策略就够用，不需要 `danger-full-access`**：

```
C:\DeepseekProject\ARDF-MeshTuneFox80\          ← 容器（无 .git，DSH 工作区设这里）
├── ARDF-MeshTuneFox80-hardware\                ← 公开仓 → github.com/PatrickShih774/ARDF-MeshTuneFox80
└── ARDF-MeshTuneFox80-firmware\                ← 私有仓 → github.com/PatrickShih774/ARDF-MeshTuneFox80-firmware
```

> ⚠️ **只影响本地路径，GitHub 仓库名不变。** 文档中的跨仓引用一律用 GitHub 绝对 URL，故不受影响。

### 11.2 ⚠️ 相对路径基准是容器目录

| ❌ 不再可用 | ✅ 正确写法 |
|------------|-----------|
| `docs/02-repository-layout.md` | `ARDF-MeshTuneFox80-hardware/docs/02-repository-layout.md` |
| `README.md` | `ARDF-MeshTuneFox80-hardware/README.md` |
| `components/` | `ARDF-MeshTuneFox80-firmware/components/` |

`git` 命令必须指明仓库：

```powershell
git -C ARDF-MeshTuneFox80-hardware status
git -C ARDF-MeshTuneFox80-firmware  status
```

### 11.3 已知陷阱（本项目实际踩过）

| 陷阱 | 症状 | 规避 |
|------|------|------|
| **`Move-Item` 失败后回滚删除了数据** | 目录的 `Move-Item` **可能部分完成**；`Remove-Item -Recurse` 回滚会永久删除已搬移的文件（曾导致公开仓 `.git` 被清空） | 先**检查**目标而非删除；可靠退路是**搬移前先 push**，坏了就 `git clone` |
| **重新 `git clone` 后无法提交** | `Author identity unknown` —— clone 不带本地 `user.name`/`user.email`/`core.quotepath`/`i18n.*` | clone 后立即 `git -C <仓> config --local …` 补齐 |
| **`pwsh` 沙箱初始化失败** | `SetNamedSecurityInfoW failed (Win32 5)`，所有 shell 命令不可用 | 需用户提权或调整文件策略；**不要反复重试** |
| **`.NET` API 的相对路径基准是进程 CWD** | `Set-Location` 后 `[System.IO.File]::ReadAllText('a.txt')` 仍读旧目录 | .NET 调用一律用**绝对路径**；PowerShell cmdlet 才受 `Set-Location` 影响 |
| **`WriteAllLines` 写 CRLF** | 违反 `.editorconfig`（要求 LF） | 批量写文件用 `WriteAllText` + 显式 `` `n `` |
| **`.git/config` 被写入令牌** | `git push -u <含令牌URL>` 会把令牌存进 `branch.<name>.remote` | 推送用 `git push <url> main`，**不加 `-u`**；事后查 `git remote -v` |
| **`git ls-files --eol` 报 CRLF** | 工作区文件是 CRLF | 用 `WriteAllText` 转换；`LICENSES/CERN-OHL-S-2.0.txt` 的 CRLF 是**官方原样，不要转** |
| **`git rev-list --count main` 报 ambiguous** | 仓库里有 `main/` 目录，与分支名冲突 | 用 `git rev-list --count HEAD` 或加 `--` |
| **Kconfig 存在不存在的符号** | 首次构建出现 unknown config item 警告 | 权威清单是固件仓的 `sdkconfig.defaults`；已知错误名见 [`03`](03-software-architecture.md) §4.4 勘误表 |
| **ESP-IDF 未安装** | `IDF_PATH` 为空、`idf.py` 不在 PATH | 见技能 `esp-idf` 第 1 节；**不要擅自下载安装** |
| **Python 版本** | ESP-IDF **只设下限无上限**（v5.3≥3.8 / v5.5≥3.9 / v6.1≥3.10）；真正的风险是依赖包缺 wheel | 见 §12.1 |
| **`git push --force` 不能抹除旧提交** | 旧对象仍可通过直接 SHA 访问 | 要彻底清除必须**删除并重建仓库** |
| **推送 `.github/workflows/**` 需要 `workflow` scope** | 令牌无该 scope 时推送被拒 | 故 `.github/workflows/` 暂不入库 |

### 11.4 🔴 安全红线

| 红线 | 原因 |
|------|------|
| **固件源码的任何片段不得进入公开仓** | 包括 Issue 与 PR 描述、贴出的日志里的源码行 |
| 密钥（ESP-NOW / Mesh / 证书）不得入库 | 走 NVS 或本地文件 |
| 不要把私有仓放进公开仓目录内 | 会在某次 `git add -A` 时被一起提交；当前容器布局已从物理上避免 |

公开仓 `.gitignore` 已有防泄漏护栏（`software/firmware/`、`**/components/*/src/*.c`、
`main/app_main.c`、`sdkconfig.defaults`、`partitions.csv` 等），但那只是**兜底**。

---

## 12. ESP-IDF 安装清单（⬜ 待执行）

> 2026-09-25 实测：本机 **`IDF_PATH` 为空、`idf.py` 不在 PATH、无 `esp\esp-idf` 目录**，即**尚未安装 ESP-IDF**。
> 固件工程骨架已就绪，但**从未实机验证过构建**。

### 12.1 Python 版本要求（2026-09-25 经源码实测）

权威来源：ESP-IDF 的 **`tools/python_version_checker.py`**，其中只有一个常量：

```python
OLDEST_PYTHON_SUPPORTED = (3, 10)   # v6.1

def is_supported() -> bool:
    return sys.version_info[:2] >= OLDEST_PYTHON_SUPPORTED[:2]
```

> 🔴 **ESP-IDF 只设下限，没有上限。** 整个检查就是一次 `>=` 比较，
> **不存在"版本太高被拒绝"的逻辑**。

| ESP-IDF 版本 | `OLDEST_PYTHON_SUPPORTED` | 即要求 |
|-------------|--------------------------|--------|
| **`v6.1`（本项目选用）** | **`(3, 10)`** | **Python ≥ 3.10** |
| `v5.5.x` | `(3, 9)` | Python ≥ 3.9 |
| `v5.3.x` | `(3, 8)` | Python ≥ 3.8 |
| `v5.1.x` | `(3, 7)` | Python ≥ 3.7 |

**结论**：本机 **Python 3.13.12 满足 v6.1 的要求（≥3.10）**，可以直接使用。

**真正的风险不在版本检查，而在依赖包**：`install.ps1` 会通过 pip 安装
`tools/requirements/requirements.core.txt` 中的包（`esp-idf-kconfig`、`esp-coredump`、
`esp-idf-monitor`、`cryptography`、`pyyaml` 等）。若其中某个包没有对应 Python 版本的
wheel、需要本地编译而缺少构建工具，**那才是会失败的地方**。

**建议**：**先用 3.13 直接试**（`.\install.ps1 esp32c3`）。只有出现 pip 报"找不到 wheel"
或编译失败时，才退回安装 Python 3.12：

```powershell
winget install Python.Python.3.12
py -3.12 --version
# 然后让 install.ps1 使用 3.12（确保 PATH 中 py -3.12 优先，或用 ESP-IDF 的 --python 参数）
```

> ⚠️ 本文件早期版本曾写"ESP-IDF v5.x 要求 Python 3.9–3.12，3.13 很可能被拒绝"——
> **该说法是错的**（既无上限，下限也是 3.8 而非 3.9）。已按源码实测更正。
### 12.2 安装步骤

```powershell
# ① 准备 Python 3.12（择一）
winget install Python.Python.3.12
#   或从 python.org 下载 3.12 安装包；装完确认：
py -3.12 --version

# ② 克隆 ESP-IDF（推荐 v5.3；分支可换 v5.5）
git clone -b v6.1 --recursive https://github.com/espressif/esp-idf.git C:\esp\esp-idf

# ③ 只装 esp32c3 工具链（省时间与磁盘）
cd C:\esp\esp-idf
.\install.ps1 esp32c3

# ④ 每次新 shell 都要激活
. C:\esp\esp-idf\export.ps1
```

### 12.3 验证清单（逐项打勾）

```powershell
idf.py --version                      # 应输出 ESP-IDF v5.3.x
riscv32-esp-elf-gcc --version         # RISC-V 工具链（在 IDF 环境内）
python --version                      # 3.9–3.12
esptool.py version                    # 烧录工具
[System.IO.Ports.SerialPort]::GetPortNames()   # 串口列表
```

### 12.4 首次构建（在固件仓内）

```powershell
cd C:\DeepseekProject\ARDF-MeshTuneFox80\ARDF-MeshTuneFox80-firmware
idf.py set-target esp32c3
idf.py build
```

**重点检查**：

| 检查项 | 说明 |
|--------|------|
| **Kconfig 未知项警告** | `sdkconfig.defaults` 是对照 v5.1.4 源码核对的；换小版本可能有差异，看到 `unknown config item` 要报告 |
| **`factory` 分区余量** | `idf.py size` 确认 app 未超 1536K |
| **组件注册** | 28 个组件均为"接口组件"（只有 `INCLUDE_DIRS`、无 `SRCS`），这是**合法**的，不是错误 |
| **产物** | 当前是**空壳固件**——组件均无实现，`app_main()` 只打日志 |

### 12.5 离线包线索

`Downloads` 中见过：`riscv32-esp-elf-14.2.0_*.zip`、`esptool-v5.1.0-*.zip`、
`openocd-esp32-win64-*.zip`、`riscv32-esp-elf-gdb-*.zip`。
可手动放入 `~/.espressif/tools/`，但**推荐仍用 `install.ps1`**（会校验版本与哈希）。

> ⚠️ 同目录下的 `esp32-arduino-libs-idf-release_v5.5-*.zip` 是 **Arduino 用的 IDF 库**，
> 本项目**不用**（[ADR-0001](adr/ADR-0001-adopt-esp-idf-over-arduino.md)）。

### 12.6 调试相关

ESP32-C3 用**内置 USB-JTAG**（GPIO18/19），无需额外调试器。
Core Dump 需先在 `sdkconfig.defaults` 开启 `CONFIG_ESP_COREDUMP_ENABLE_TO_FLASH=y` 等项。
完整操作见**用户级技能 `esp-idf`**（`~/.dsh/skills/esp-idf/SKILL.md`）。

### 12.7 版本选择：**v6.1**（2026-09-25 经源码实测修正）

> ⚠️ 本节早期版本推荐 `v5.3.6`，理由是"v5→v6 有破坏性变更，符号可能漂移"。
> **该理由经实测不成立**——实测方法：把本工程 `sdkconfig.defaults` 里的全部
> **27 个** `CONFIG_*` 符号，逐一到 v6.1 与 v5.3.6 的 Kconfig 源码中比对存在性。

**实测结果：27 个符号在 v6.1 中全部存在，无一个被删除。**

初次比对时曾有 5 个"未找到"，逐一追查后确认**都是假警报——符号只是换了定义文件**：

| 符号 | v5.3.6 定义位置 | v6.1 定义位置 |
|------|----------------|--------------|
| `ESP_CONSOLE_UART_DEFAULT` | `components/esp_system/Kconfig` | **`components/esp_stdio/Kconfig`**（v6 新组件） |
| `ESP_CONSOLE_UART_BAUDRATE` | 同上 | 同上 |
| `LOG_DEFAULT_LEVEL_INFO` | `components/log/Kconfig` | **`components/log/Kconfig.level`**（拆分为独立文件） |
| `LOG_MAXIMUM_LEVEL_INFO` | 同上 | 同上 |
| `ESP_DEFAULT_CPU_FREQ_MHZ_160` | `esp_system/port/soc/esp32c3/Kconfig.cpu` | **同一文件**（未抓取而误判） |

> **符号名未变，只是所在文件变了——`sdkconfig.defaults` 只关心符号名，因此无需任何改动。**

| ESP-IDF 版本 | 状态 | ESP32-C3 | Python 下限 |
|-------------|------|----------|------------|
| `v5.1.7` | 维护中 | ✅ | 3.7 |
| `v5.3.6` | 维护中 | ✅ | 3.8 |
| `v5.5.5` | 维护中 | ✅ | 3.9 |
| `v6.0.3` | 已发布 | ✅ | 3.10 |
| **`v6.1`** | **最新稳定（2026-08-27）← 本项目选用** | ✅ | **3.10** |

**为什么选 v6.1**：

1. **符号兼容性已实测通过**（27/27），无需改动配置；
2. **ESP32-C3 完整支持**（`components/soc/esp32c3` 存在）；
3. **Python 3.13.12 满足要求**（≥3.10）；
4. **最新稳定版，支持周期最长**，避免"刚起步就落后一个大版本"；
5. 🔑 **现在迁移成本最低**——本工程**尚无任何组件实现代码**，只有骨架；
   若等 28 个组件写完再跨大版本迁移，代价高得多。

**保留回退方案**：若 v6.1 首次构建暴露了骨架层面的问题（如组件注册行为变化），
可随时切回 `v5.3.6`——因为 `sdkconfig.defaults` 在两版间**通用**。

```powershell
# 选定：v6.1（标签，可复现）
git clone -b v6.1 --recursive https://github.com/espressif/esp-idf.git C:\esp\esp-idf

# 回退用（如需）
git clone -b v6.1 --recursive https://github.com/espressif/esp-idf.git C:\esp\esp-idf
```

**不要选**：`v4.x`（已停止维护，且本项目用 v5+ API）、`master`（开发分支）、`v6.x-rc*` / `*-beta*`（预览版）。### 12.8 ⚠️ 引用名（ref）的坑

ESP-IDF 的版本引用有两种形态，**别混淆**：

| 形态 | 例子 | HTTP 实测 | `git clone -b` 是否可用 |
|------|------|----------|----------------------|
| **标签（tag）** | `v5.3`、`v5.3.6`、`v5.5.5` | ✅ 存在 | ✅ 可（**固定在某次发布，不会动**） |
| **分支（branch）** | `release/v5.3`、`release/v5.5` | ✅ 存在 | ✅ 可（**会移动，始终是最新补丁**） |
| 裸 `v5.3` 当分支查 | `branches/v5.3` | ❌ 404 | — |

**建议用标签**（如 `v5.3.6`）以保证**可复现**；若想始终拿最新补丁，用分支 `release/v5.3`。

> 实测命令：
> `git clone -b v6.1 --recursive https://github.com/espressif/esp-idf.git C:\esp\esp-idf`
