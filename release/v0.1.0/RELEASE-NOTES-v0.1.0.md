# ARDF-MeshTuneFox80 固件 v0.1.0

> **本文件 = GitHub Release 描述正文**（连同本目录的 `README.md`、`SHA256SUMS` 一起入库；
> `.bin` / `.elf` 走 **Release 附件**，**不进 git**）。
> 依据：私有固件仓 `docs/RELEASE-PROCESS.md`（发布流程 + 30 条自检清单）· 用户裁定 **R-6**。

---

## 0. 🔴🔴 先读这一条：本发布物的默认角色 = 【网关】（**不会发报**）

| 项 | 值 |
|---|---|
| **默认角色** | **网关 `MASTER`**（`ardf_meshtunefox80-v0.1.0-default.bin`，狐狸板 `hw_rev=1`） |
| **会不会发报** | **❌ 不会发报** —— 网关角色下射频链路被能力掩码整条裁掉、安全联锁永不解除 |
| **怎么变成会发报的狐狸** | 烧 **`…-slave.bin`**（从机 `SLAVE` + `hw_rev=1`）；要自己构建见 §6 |
| **纯网关板（SuperMini）用哪个** | **`…-gw2.bin`**（`MASTER` + `hw_rev=2`）—— 同样**不会发报** |

**本 release 一共三份应用镜像，角色不同、来源同一份源码**：

| 附件 | 角色 | 板型 | 会不会发报 |
|---|---|---|---|
| `ardf_meshtunefox80-v0.1.0-default.bin` | 网关 `MASTER` | `hw_rev=1`（狐狸板全外设） | ❌ **不会** |
| `ardf_meshtunefox80-v0.1.0-slave.bin` | 从机 / 狐狸 `SLAVE` | `hw_rev=1` | ✅ **会**（运行期联锁/SWR 门禁仍然生效） |
| `ardf_meshtunefox80-v0.1.0-gw2.bin` | 网关 `MASTER` | `hw_rev=2`（SuperMini：只有 LCD + EC11） | ❌ **不会** |

> 🔴 **这不是板子坏了，是构建/发布选错了角色。** 把 `default.bin` 或 `gw2.bin` 烧进狐狸板，
> 它**就是不会发报**（这是"默认即安全"的设计，用户裁定 **R-1**）。
> 🔴 **烧录前请先看清 `build*/config/sdkconfig.h` 里的 `ARDF_MESH_ROLE_*`**：
> `sdkconfig` 是**本地生成物**（不入库、可被任何一次本地构建改动）
> ⇒ "默认 = 网关"**对全新克隆成立，对本机工作区不自动成立**。
> 依据：`docs/BUILD-ROLES.md` §1.1 / §2.1 · `docs/DECISIONS-APPROVED.md` §6 **R-1**（用户裁定）。
> 一页版排查表见公开仓 [`QUICKSTART-BEFORE-FLASHING.md`](../../QUICKSTART-BEFORE-FLASHING.md)。

---

## 1. ⚠️ 合规口径（**不得省略** —— 诚实性要求）

本工程已实现 **6 种**竞赛模式；**与《无线电测向竞赛规则》（2024 修订版）存在
9 项已知偏差（D-01~D-11，其中 D-03 命中全部 6 种模式）**，用户已裁定【先不修、后期再修】。
**本版本不声称完全合规。**

- 另有 **1 项基线内缺口**：2024 修订版新增的**中距离无线电测向**（第 7 种）**尚未实现**（登记为优化项 O-12）。
- 逐条差异与修复方案的登记点在私有固件仓 `docs/ARDF-RULES-CONFORMANCE.md` **§R-5**
  （**不随本仓发布**：其中含规则原文摘录，属第三方版权）。

---

## 2. 本版新增 / 修复（首个发布）

> 🔴 **这是本仓的第一个 tag**（此前**没有任何 tag**）⇒ 下面列的是"首发内容 + 本批文档修正"，
> 不是相对上一版的 diff。固件源码的完整历史在**私有仓**（不随本仓发布）。

**新增**

- 公开仓新增 [**`QUICKSTART-BEFORE-FLASHING.md`**](../../QUICKSTART-BEFORE-FLASHING.md)（单页 · 烧录前必读）：
  三档位构建命令 · 烧录前 **5 条硬纪律** · 「我烧了但不发报」**8 条排查表**。
  依据 = 用户裁定 **R-1**「要求手册/标签足够醒目」。
- 公开仓新增 **`release/v0.1.0/`**（本目录）：三档位发布产物 + `SHA256SUMS` + 发布说明。
- README 顶部新增指向快速上手页的**醒目入口**；§五 快速导航新增「🔥 要烧录」一行。

**修复（公开仓文档的事实性错误，本批一并改正）**

- README §3.2：删去「`sdkconfig.defaults.gw2` 尚未入库」的过时说明（该文件自 2026-09-29 起已入库）。
- README §3.3：合规偏差计数改为与真源一致（**11 条 ❌ 判定 = 9 个独立缺陷**）。
- README §六：许可结构一行去掉「四份许可全文待放入」（四份全文均已入库）。

---

## 3. 已知问题（**如实列，不美化**）

| # | 已知问题 | 影响 | 状态 |
|---|---|---|---|
| 1 | **S-1 源端计数器回退**：从机重启后 `seq` 回到 1，被接收端当"旧帧/重复帧" | 从机重启后首次配置下发可能出现 **5/5 `NACK 0x09`**；**重试一次**即可（不致命） | 🔴 **待用户拍板**（要动协议/安全语义，本版不动协议）。登记：私有仓 `docs/DEDUP-FIX.md` §8.1 |
| 2 | **S-3 中继学习把「节点号→MAC」写错**（中继转发的帧链路层源 MAC 是**中继**的） | 可能使 `peer_mac_by_id()` 查不到 ⇒ 定向配置 `NACK 0x08`；**对时握手可能失败**；同一台设备两次开机结果可能不同 | 🔴 **待用户拍板**（需改邻居表语义）。登记：私有仓 `docs/COM6-WINDOW-RESULTS.md` §1.3 |
| 3 | **中距离模式未实现**（2024 基线内第 7 种） | 该模式下无信号源能力 | 已登记优化项 **O-12**（用户裁定 R-2 = 做，排第 7 优先） |
| 4 | **角色只能编译期决定**（NVS 运行期切角色未实现） | 换角色必须重新构建 + 重新烧录 | 规划中（批 11）；本版**不**支持菜单切角色 |
| 5 | **R-1 的"启动横幅"未进入本版固件** | 上电日志只有分散的 `role : …` / `rf chain : off by design` 等多条 INFO，**没有**一条醒目的"本机角色 + 会不会发报"横幅 | ⏳ 补丁**已备好并验证可干净落地**（R-1 三样之一），将在下一次固件构建进入发布物；见私有仓 `docs/RELEASE-PROCESS.md` 的执行记录 |
| 6 | **本版默认档不含 MAC 白名单 provisioning 命令**（`CONFIG_ARDF_CONSOLE_WL_PROVISIONING` = **n**，= 仓库默认值） | 用 `default.bin`/`gw2.bin` 的网关**不接受** `WL_GET/WL_RSP/WL_SET/WL_PAIR`（0x72–0x75） | ⚠️ **如实告知**：仓库默认就是 `n`（该选项 Kconfig `default n`，`sdkconfig.defaults` 不含它）。维护者本机 `sdkconfig` 把它开成 `y`（BUILD-ROLES §3.2 登记为"本地调试用"的已知漂移）⇒ **本机 `idf.py build` 的镜像与发布物在这一个选项上不同**。需要该命令请按 §6 加 `CONFIG_ARDF_CONSOLE_WL_PROVISIONING=y` 重建 |
| 7 | **本轮未做**：真机实烧验证（`esptool verify-flash` / 实跑三档） | §5 的烧录命令**未经硬件验证**，只是"与构建产物 `flasher_args.json` 逐值一致" | ⏳ 待核（本批纪律：不烧录、不碰串口） |
| 8 | **本版未做**：Core Dump 实机回读验证 | `.elf` 带符号（已用 `addr2line` 抽查证实），但**未在真机上验证**"崩溃 → 回读 → 反查源码行"整链 | ⏳ 待核 |

---

## 4. 产物与校验（SHA-256 明文，请自行复核）

> 🔴 附件在 **GitHub Release**（不随 git 跟踪）。校验（Windows）：
> `Get-FileHash -Algorithm SHA256 .\<文件名>` 与下表逐字符比对（或直接对 `SHA256SUMS` 逐行核对）。

| 文件 | 说明 | 字节数 | SHA-256 |
|---|---|---|---|
| `ardf_meshtunefox80-v0.1.0-default.bin` | 默认档＝网关 `MASTER` + `hw_rev=1`（烧 `0x20000`） | 898,720 | `9dd72ce779b89c3a94b5305421909e80d0dc95e2a1d6857f0c9b92b74704e2a4` |
| `ardf_meshtunefox80-v0.1.0-default.elf` | 带符号（Core Dump 反查用） | 10,948,420 | `3ef2d0692a64b310ec8cc343260531549c8d0d18a349eccabb82ce03a67122c1` |
| `ardf_meshtunefox80-v0.1.0-slave.bin` | **狐狸档＝从机 `SLAVE` + `hw_rev=1`（会发报）** | 898,720 | `fb1d83c584a28f3c3fc46d7dae177b3b4399f5602ae0c9ba10b5fbca4ba6f654` |
| `ardf_meshtunefox80-v0.1.0-slave.elf` | 带符号 | 10,948,404 | `456a6df2399bc425fc72c2bb350ccb828d1ee5a6291da32b906f1a69f910cfac` |
| `ardf_meshtunefox80-v0.1.0-gw2.bin` | 纯网关板档＝`MASTER` + SuperMini `hw_rev=2` | 898,720 | `e757f11f2881c0b6275e70a38f1ec24d5b30c6525f4fe3bbc49f2be81a4efb11` |
| `ardf_meshtunefox80-v0.1.0-gw2.elf` | 带符号 | 10,948,424 | `549e9aeabb90f72f9433484efc4c629823bcbad8b185e5e774650fde53a0283d` |
| `bootloader.bin` | 引导加载器（烧 `0x0`） | 21,232 | `294d52469bddf828114e5401e79c2dcefef3a096f62b37d3c0de5e7bfe9866fb` |
| `partition-table.bin` | 分区表（烧 `0x8000`） | 3,072 | `3d574423190fa1ba6be09ea1ecdcb39ddda00a3b8efc1215bf75b09c64811fbc` |
| `ota_data_initial.bin` | OTA 数据初始镜像（烧 `0xf000`） | 8,192 | `7d2c7ac4888bfd75cd5f56e8d61f69595121183afc81556c876732fd3782c62f` |

> ⚠️ **三档应用镜像的字节数相同（都是 898,720 B），但 SHA-256 互不相同。**
> 本工程的角色/板型裁剪发生在**运行期**（各组件按能力掩码跳过初始化），**不是**编译期删代码
> ⇒ 体积不随角色变化。**"体积一样"绝不等于"镜像一样"** —— 请以 `SHA256SUMS` 为准。
>
> ℹ️ **`bootloader.bin` 只随附一份**（默认档那次构建的）。三档各自构建出的 `bootloader.bin`
> **仅差构建时间戳与尾部镜像哈希**（实测 38 字节：`0x55`/`0x57-0x58`/`0x5a-0x5b` 落在
> `esp_bootloader_desc` 的 `Sep 29 2026 hh:mm:ss` 串上，`0x52cf-0x52ef` 是尾部镜像 SHA-256）
> ⇒ **功能上等价**，不需要按档位分别烧。

---

## 5. 烧录（逐条给全）

```
# A) 最稳：装了 ESP-IDF v6.1 时，用 idf.py（偏移由构建产物 flasher_args.json 决定，不会写错）
idf.py -B build-slave -p <COM口> -D SDKCONFIG="$abs\sdkconfig.slave" flash

# B) 不装 ESP-IDF：esptool v5 手烧（🔴 偏移必须来自 flasher_args.json，勿凭记忆）
esptool --chip esp32c3 -p <COM口> -b 460800 write-flash ^
        --flash-mode dio --flash-size 4MB --flash-freq 80m ^
        0x0     bootloader.bin ^
        0x8000  partition-table.bin ^
        0xf000  ota_data_initial.bin ^
        0x20000 ardf_meshtunefox80-v0.1.0-default.bin

# C) 只读复核（不改设备）
esptool --chip esp32c3 -p <COM口> verify-flash 0x20000 ardf_meshtunefox80-v0.1.0-default.bin
```

> 🔴 **为什么偏移是这几个数**（易错点，逐值实测）：三档的 `build*/flasher_args.json`
> 都给出同一组 `flash_files` = `0x0` bootloader · `0x8000` partition-table ·
> **`0xf000` ota_data_initial** · **`0x20000` 应用镜像**（`factory` 分区，**不是 `0x10000`**）。
> ⚠️ 私有仓 `docs/RELEASE-PROCESS.md` §3.3 原版写的是 `0x10000` 且漏了 otadata ——
> 那条**已在 2026-09-29 勘误**（见该文件「勘误 1」）。**照旧文烧会错位。**
> ℹ️ esptool ≤ 4.x 的子命令写作下划线形式（`write_flash` / `verify_flash`），参数相同。

### 烧录前必读（4 条）
1. 先认清**本附件是哪个角色、会不会发报**（§0）。
2. **串口独占**：先停掉占用该口的程序（含中控），否则 `PermissionError(13)`；**只按进程名/精确路径杀**。
3. 打开**原生 USB-Serial-JTAG** 口的动作本身 = 一次复位脉冲（只读探测也会重启设备）。
4. 🔴 **只烧【赛事方授权】的串口**；Flash 模式**必须 `dio`**（QIO 会让 `GPIO12/13` 失效、板子上电无法启动）。

---

## 6. 环境与构建命令（可复现）

- **ESP-IDF v6.1**（本机 `idf.py --version` = `ESP-IDF v6.1`）· 目标 **esp32c3** ·
  Flash **DIO / 4 MB / 80 MHz** · 工具链 `esp-15.2.0_20251204` · esptool **v5.4.0**
- 🔴 **构建基线 = 私有仓 `7984c1e`**：在 `git archive HEAD` 出来的**干净副本**里构建
  （**不含**任何未提交改动），并只叠加一个"版本号去 `-dev`"补丁
  （`version.txt` 与 `main/app_main.c:73` 两处同批改；补丁 SHA-256 = `514716c904f5bf5ae2fea732d36ddae6707a890515cc2eaf9ea0825336c8a46d`）。
- 🔴 **其后私有仓虽有新提交，但没有任何改动落在固件构建输入上**
  （`components/**` · `main/**` · `CMakeLists.txt` · `sdkconfig.defaults*` · `partitions.csv` · `version.txt` 全部未变，
  新增提交只有 `docs/**` 与 `console/**`）⇒ 本版 `.bin` 的**功能代码**与"当前 HEAD 的固件源码"等价。
- ⚠️ **唯一需要落地的源码差别 = 版本号**：当前私有仓 HEAD 仍是 `0.1.0-dev`（两处）
  ⇒ 本发布物用的是"HEAD + 去 `-dev` 补丁"，该补丁**已备好并验证可干净落地**（见 §3 第 5 条的同一份执行记录）。
  **不打这个补丁就直接构建，固件自报版本会是 `0.1.0-dev`，与 tag 名 `v0.1.0` 不一致**（发布级缺陷）。

```
# 三档（在私有固件仓根目录；$abs = 该仓绝对路径）
# ① 默认档：网关（不发报）—— 什么都不用加
idf.py -B build --ccache build

# ② 狐狸档：从机（会发报）—— 两个 -D 缺一不可
idf.py -B build-slave --ccache -D SDKCONFIG="$abs\sdkconfig.slave" -D SDKCONFIG_DEFAULTS="$abs\sdkconfig.defaults;$abs\sdkconfig.defaults.slave" build

# ③ 纯网关板档：SuperMini hw_rev=2
idf.py -B build-gw2 --ccache -D SDKCONFIG="$abs\sdkconfig.gw2" -D SDKCONFIG_DEFAULTS="$abs\sdkconfig.defaults;$abs\sdkconfig.defaults.gw2" build
```

> 🔴 **三档的 `sdkconfig` 都是"不预置、由入库的 `sdkconfig.defaults`(+叠加档) 现场生成"**
> ⇒ 复现的是**全新克隆按文档命令构建**的语义，**没有**使用任何本机 `sdkconfig`
> （本机 `sdkconfig` 是 gitignored 的本地生成物，可能漂；这正是 §6 第 ⑤/⑥ 条自检要钉的东西）。
> ⚠️ 由此带来一处**已知且已登记**的差异：维护者本机把 `CONFIG_ARDF_CONSOLE_WL_PROVISIONING`
> 开成 `y`（本地调试用），而**仓库默认是 `n`** ⇒ 本版默认档**不含** `WL_*` provisioning 命令（见 §3 第 6 条）。
> ✅ 另一面是**好消息**：现场生成的配置里，`sdkconfig` 与 `sdkconfig.slave` 的生效项差异
> **只有角色那两行**（`sdkconfig.gw2` 与 `sdkconfig.slave` 只多一项 `BSP_BOARD_HW_REV`），
> 两条构建期断言（R-1 角色 + 配置漂移）三档全绿。

---

## 7. 许可与第三方声明（🔴 **必须随附** —— Apache-2.0 / 本仓许可条款要求）

| 文件 | 内容 |
|---|---|
| [`NOTICE`](../../NOTICE) | 第三方组件声明台账（ESP-IDF Apache-2.0 · FreeRTOS MIT · mbedTLS Apache-2.0 · Unity MIT） |
| [`LICENSES/LicenseRef-ARDF-NC-1.0.txt`](../../LICENSES/LicenseRef-ARDF-NC-1.0.txt) | **固件二进制的许可全文**（ARDF 业余无线电非商业许可 1.0） |

> 🔴 **固件二进制适用 `LicenseRef-ARDF-NC-1.0`：仅限业余无线电非商业用途；不授予源代码。**
> 闭源**不等于**可以省略第三方声明 —— ESP-IDF / FreeRTOS / mbedTLS 的版权与许可声明必须随二进制保留。
> 依据：公开仓 [`.github/OVERVIEW.md`](../../.github/OVERVIEW.md) §4 · [`docs/08-licensing-and-compliance.md`](../../docs/08-licensing-and-compliance.md) §4.2。
