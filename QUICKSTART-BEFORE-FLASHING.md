# 🔴 快速上手 · 烧录前必读（QUICKSTART — READ THIS BEFORE FLASHING）

> **单页 · 打印出来贴在工位上就够。**
> 🔴 **第一眼要看到的结论**：**默认构建出来的固件是【网关】，它【不会发报】。**
> 把默认构建烧进狐狸板 ⇒ 板子不发报，**这不是板子坏了，是构建选错了角色**。

**口径真源**：本页逐条来自【私有固件仓】`docs/BUILD-ROLES.md`
（§1 结论 · §2.1 真源清单 · §4.1–§4.3 构建命令 · §5/§6 理由与代价 · §9 自检清单）。
**本页与那份真源冲突时，以那份为准**，并请提 issue 修正本页。

关联：[README §3.2 软件基线](README.md#32-软件基线) ·
[发布产物与说明](release/v0.1.0/RELEASE-NOTES-v0.1.0.md) · [CHANGELOG](CHANGELOG.md)

---

## 0. 一句话记住（三行对照表）

| 你敲的命令 | 构建出来是什么 | 会不会发报 |
|---|---|---|
| `idf.py build`（**什么都不加** = 默认档） | **网关** `MASTER`（狐狸板 `hw_rev=1`） | ❌ **不会发报** |
| 加 `-D SDKCONFIG=…\sdkconfig.slave` **和** `-D SDKCONFIG_DEFAULTS=…`（**两个都要给**） | **从机 / 狐狸** `SLAVE` | ✅ 会发报 |
| 加 `-D SDKCONFIG=…\sdkconfig.gw2` **和** `-D SDKCONFIG_DEFAULTS=…` | **网关** `MASTER`（纯网关板 SuperMini `hw_rev=2`） | ❌ 不会发报 |

**为什么默认是"不发报"**：这是**安全设计**（用户裁定 **R-1**「保持现状：默认 = 网关，安全优先」）。
网关角色下射频链路被外设能力掩码整条裁掉（Si5351 / ATU 继电器 / 功放 / 检波 ADC 都不初始化，
整条 I²C 总线不建立）⇒ 安全联锁**永不解除** ⇒ 本机不会发射。
代价是：**照旧烧默认构建的人，会以为"狐狸坏了"** —— 所以才有本页。

> ⚠️ **"默认 = 网关"只对【全新克隆】成立**：`sdkconfig` 是**本地生成物**（不入库、可被任何一次
> `menuconfig` 改动）⇒ **动手烧录前永远看【真正生效的那一份】**
> `build*/config/sdkconfig.h` 里的 `ARDF_MESH_ROLE_*`，**不是**看配置文件名。
> （有一次真实事故就是这样把网关刷成了从机。）

---

## 1. 动手前的 30 秒自检（不构建，秒级）

```powershell
# 在【私有固件仓根目录】执行；$abs = 该仓绝对路径
$abs = (Get-Location).Path

# ① 两条构建期断言（秒级，不构建）：绿 = 默认档确实是网关 + 两角色差异只来自角色
cmake -DARDF_GUARD_PROJECT_DIR=$abs -P main/cmake/ardf_default_role_guard.cmake
cmake -DARDF_GUARD_PROJECT_DIR=$abs -P main/cmake/ardf_config_drift_guard.cmake

# ② 你要烧的那一份，真正生效的角色是哪个（看构建目录，不看文件名）
Select-String -Path build-slave\config\sdkconfig.h -Pattern 'ARDF_MESH_ROLE'
#   期望： #define CONFIG_ARDF_MESH_ROLE_SLAVE 1     （且【没有】MASTER 1）
```

---

## 2. 烧一只会发报的狐狸（从机档）—— 整段照抄

```powershell
$abs = (Get-Location).Path        # ① 私有固件仓根目录（🔴 必须绝对路径）

# ② 构建狐狸档（首次会由【入库的】defaults 生成 sdkconfig.slave，新克隆也能一次成功）
idf.py -B build-slave --ccache `
      -D SDKCONFIG="$abs\sdkconfig.slave" `
      -D SDKCONFIG_DEFAULTS="$abs\sdkconfig.defaults;$abs\sdkconfig.defaults.slave" `
      build

# ③ 🔴 烧录前先自证：这一份真正生效的是【从机】
Select-String -Path build-slave\config\sdkconfig.h -Pattern 'ARDF_MESH_ROLE'

# ④ 烧录 —— `-B` 与 `-D SDKCONFIG=` 都要带（flash 也是）
idf.py -B build-slave -p <COM口> -D SDKCONFIG="$abs\sdkconfig.slave" flash

# ⑤ 看启动日志：同样带上（monitor 也按 SDKCONFIG 缓存挑配置）
idf.py -B build-slave -p <COM口> -D SDKCONFIG="$abs\sdkconfig.slave" monitor
```

**烧完必看的第一行**（上电日志，INFO 级）：

```
I app_main: role      : NODE (capability mask rf=ON atu=ON i2c=ON ...)
```

装的是狐狸 ⇒ `role` **不能**是 `GATEWAY`。若看到 `GATEWAY`，说明这一口烧的是**默认档**，
**先回到第 ③ 步查角色，别去查硬件**。

> 🔴 **为什么是两个 `-D`（缺一不可）**：`-D SDKCONFIG=` 是**产物落点**（本次读写哪份配置，
> 本地生成物）；`-D SDKCONFIG_DEFAULTS=` 是**配置源头**（首次生成它时用哪两份入库 defaults 叠加）。
> 只给前者时，**新克隆的树里没有 `sdkconfig.slave`，构建会直接失败**（不是静默回落）。
> 🔴 **`-B` 必须一路带着**（build / flash / monitor / size 都要）：SDKCONFIG 缓存在各自的
> `build-*/` 里，漏掉 `-B` 就会去默认 `build/` 用**另一套**配置 —— 这正是"把网关刷成从机"的形态之一。

---

## 3. 烧一块纯网关板（SuperMini / `hw_rev=2`）—— 整段照抄

```powershell
$abs = (Get-Location).Path        # 私有固件仓根目录

idf.py -B build-gw2 --ccache `
      -D SDKCONFIG="$abs\sdkconfig.gw2" `
      -D SDKCONFIG_DEFAULTS="$abs\sdkconfig.defaults;$abs\sdkconfig.defaults.gw2" `
      build

Select-String -Path build-gw2\config\sdkconfig.h -Pattern 'ARDF_MESH_ROLE|BSP_BOARD_HW_REV'
#   期望： MASTER 1 + BSP_BOARD_HW_REV 2

idf.py -B build-gw2 -p <COM口> -D SDKCONFIG="$abs\sdkconfig.gw2" flash
```

> 🔴 **`hw_rev` 与角色是两个独立的轴**：`hw_rev=2`（SuperMini）在能力掩码里**只有**
> `(hw_rev=2, GATEWAY)` 这一格成立；`(hw_rev=2, SLAVE)` 是**不成立的组合**
> （SuperMini 没有 GPIO12/13 ⇒ 射频/ATU 全被裁掉，而自检只报"设计跳过"因而**看起来是 pass**）。
> ⇒ 第 2 节与第 3 节的命令**不要交叉使用**。

---

## 4. 烧录前必读（5 条硬纪律）

| # | 纪律 | 为什么（依据） |
|---|---|---|
| 1 | **串口是独占资源**：烧之前先停掉占用该口的程序（含中控实例），或换一个口 | 否则报 `PermissionError(13)`；排查"串口没数据"时**先确认不是别的进程占着**（私有仓 `docs/console/PORT-AND-IO-DISCIPLINE.md` **D-2**） |
| 2 | **只按【进程名 / 精确路径】杀进程**，绝不用会匹配到**自己命令行**的模式 | 用 `CommandLine -match 'ardf-console'` 过滤会**杀掉包裹自己的 PowerShell**；正确写法 `Get-Process 'ardf-console'`（同上 **D-2.1**） |
| 3 | ⚠️ **打开原生 USB-Serial-JTAG 口这个动作本身 = 一次复位脉冲** | 任何"只读一次日志/清单"的动作都会顺手重启设备 ⇒ 重启后对端表为空；需要稳定读数时**连读两次取第二次**（私有仓 `docs/console/10-pitfalls.md` **P-07**） |
| 4 | 🔴 **Flash 模式必须是 `DIO`**（`--flash_mode dio`） | 本板把 `GPIO12/13` 当普通 GPIO 用（功放调压 / EC11 按键），它们仅在 **QIO** 下被 flash 占用 ⇒ 改 QIO 会让这两个脚失效、板上电无法启动。**构建期已硬断言**，esptool 手烧时也要显式给 `dio` |
| 5 | 🔴 **只烧【赛事方授权】的串口** | 授权端口清单**以私有仓为准、本页不复述**（同上 **D-3**） |

---

## 5. 🔴「我烧了，但它不发报」—— 按顺序排查（**第一条就是最常见的那条**）

| # | 现象 / 判据（看哪里） | 结论与处置 |
|---|---|---|
| **1** | 上电日志 `role : GATEWAY`、`rf chain : off by design`；或 `build\config\sdkconfig.h` 是 `CONFIG_ARDF_MESH_ROLE_MASTER 1` | 🔴 **你烧的是默认档（网关）** ⇒ 回 §2 重新构建 + 烧狐狸档。**这不是硬件故障**，别拆板子 |
| **2** | 你以为烧的是狐狸，但上电还是 `GATEWAY` | 检查烧录命令是否**同时**带了 `-B build-slave` 与 `-D SDKCONFIG=…\sdkconfig.slave`：漏任何一个都会去默认 `build/` 拿**另一套**配置 ⇒ 补全后重烧 |
| **3** | `role : NODE` 但后面 `rf=off` | `CONFIG_BSP_BOARD_HW_REV=2`（SuperMini）？⇒ `(hw_rev=2 + SLAVE)` **不成立的组合**（板子没有 GPIO12/13）⇒ 换狐狸板（`hw_rev=1`），不要指望它发报 |
| **4** | `role : NODE`、`rf=ON`，但整机仍不发报 | 看有没有 `rf_power  : interlock released (...)`、`selftest done: fail=N`：自检未过 / 联锁未放行 ⇒ 按日志逐条修。⚠️ 只有 `E`/`W` 才算异常，**INFO 级的"设计跳过"不是故障** |
| **5** | 排程窗口一直不开 | 看 `sched clock: synced=1 basis=timesync`。未出现 ⇒ 世界对齐未就绪；校时链路还受**已知缺陷 S-3**（中继学习把「节点号→MAC」写错 ⇒ 对时握手可能失败）影响 |
| **6** | 模式 / 台号 / 频率没生效 | 看启动日志 `config    : mode=… station=… freq=…`：配置未下发或 NVS 未保存 ⇒ 重下发。⚠️ 从机重启后首次下发可能 `NACK 0x09`（**已知缺陷 S-1**，**重试一次**即可，不必重启设备） |
| **7** | SWR / 联锁不放过，想"先凑合发一次" | 🔴 **不允许任何人工绕过**（用户裁定 **Q-9**：空载 / 高驻波发射会烧功放）⇒ 先接好天线或假负载再试 |
| **8** | 端口完全没数据 | ① 别的进程占着串口？（纪律 1）；② 打开口的动作刚复位过它？（纪律 3）；③ 口选错（授权清单见纪律 5） |

> ⏳ **本页尚未包含的一条**（如实告知）：**固件启动还没有一条"醒目横幅"**明确打出
> "本机角色 + 会不会发报"—— 目前靠上面第 1/3 条的**多条 INFO 日志拼起来**判断。
> 该横幅（R-1 的"标签"三样之一）**已备好待落补丁**，随下一次固件构建进入发布物。

---

## 6. 直接用【发布产物】烧（现场不想装 ESP-IDF）

发布产物在 [`release/v0.1.0/`](release/v0.1.0/)（含 `SHA256SUMS`，可逐文件复核）。
🔴 **这些 `.bin` / `.elf` 不在 git 里**（双仓纪律 + 本仓 CI 门禁 `scripts/check-repo-separation.ps1`
把 `.(bin|elf|map|hex)$` 列为禁止入库）⇒ **请从 [本仓 GitHub Release 页面](https://github.com/PatrickShih774/ARDF-MeshTuneFox80/releases) 的附件下载**，
`release/v0.1.0/` 里入库的只有文本（说明 + `SHA256SUMS`）。
🔴 **先认清你要的是哪一个 `.bin`**（发布物的角色**只由文件名与说明决定**，没有任何"自动识别"）：

| 文件 | 角色 | 会不会发报 |
|---|---|---|
| `…-default.bin` | 网关 `MASTER` + 狐狸板 `hw_rev=1` | ❌ 不会 |
| `…-slave.bin` | 从机 / 狐狸 `SLAVE` + `hw_rev=1` | ✅ **会** |
| `…-gw2.bin` | 网关 `MASTER` + 纯网关板 `hw_rev=2` | ❌ 不会 |

```powershell
# A) 最稳：还装着 ESP-IDF 时，让 idf.py 按构建时的 flasher_args.json 烧（偏移不会写错）
idf.py -B build-slave -p <COM口> -D SDKCONFIG="$abs\sdkconfig.slave" flash

# B) 不装 ESP-IDF：用 esptool 手烧（👇 偏移取自构建产物 build/flasher_args.json，勿凭记忆改）
esptool --chip esp32c3 -p <COM口> -b 460800 write-flash `
        --flash-mode dio --flash-size 4MB --flash-freq 80m `
        0x0     bootloader.bin `
        0x8000  partition-table.bin `
        0xf000  ota_data_initial.bin `
        0x20000 ardf_meshtunefox80-v0.1.0-slave.bin

# C) 只读复核（不改设备）
esptool --chip esp32c3 -p <COM口> verify-flash 0x20000 ardf_meshtunefox80-v0.1.0-slave.bin
```

> ℹ️ 上面用的是 **esptool v5** 的连字符子命令（本机实测 `esptool v5.4.0`）；
> **esptool ≤ 4.x** 写作下划线形式 `write_flash` / `verify_flash`，参数相同。
> ⚠️ `--before default-reset --after hard-reset` 可选；本仓实测命令在
> `build/flasher_args.json` 的 `extra_esptool_args` 里，需要时照抄。

> 🔴 **偏移说明（易错）**：本工程 `factory` 应用分区在 **`0x20000`**，**不是** `0x10000`；
> 另有 `otadata` 在 **`0xf000`**（写 `ota_data_initial.bin`）。
> 权威值来自构建产物 `build/flasher_args.json`（`flash_files` 字段）与私有固件仓的分区表；
> 本页数值为 2026-09-29 实测（ESP-IDF v6.1 / esp32c3 / 4 MB），改分区表后必须重新核对本页。

---

## 7. 合规口径（**不得省略** —— 诚实性要求）

本工程已实现 **6 种**竞赛模式；**与《无线电测向竞赛规则》（2024 修订版）存在 9 项已知偏差
（D-01~D-11，其中 D-03 命中全部 6 种模式）**，用户已裁定【先不修、后期再修】。
**本版本不声称完全合规。** 另：**中距离无线电测向**（2024 基线内新增的第 7 种）**尚未实现**。

> 🔴 本仓**不得**出现"完全符合规则""已通过合规核对"一类无保留说法；
> 逐条差异与修复方案的登记点在**私有固件仓** `docs/ARDF-RULES-CONFORMANCE.md` **§R-5**。
