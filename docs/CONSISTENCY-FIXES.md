# 一致性修正记录 —— 2026-09-28 文档事实性修正批

> **性质**：一次**文档事实性修正**的对照记录。**不引入任何新决策**，不改技术方案与指标。
> **涉及**：公开仓（本仓）`README.md` · `docs/03-software-architecture.md`；
> 私有固件仓 `docs/BUILD-ROLES.md`（原 `docs/BUILD-STRATEGY.md`，本批改名）·
> `docs/GATEWAY-STANDALONE-PLAN.md` §18 · 新增入库文件 `sdkconfig.defaults.slave`。
> **提交状态**：本批改动**未提交**，由项目负责人逐路径复核后暂存提交。

本批共修 **5 处**，其中 **3 处是公开仓的事实性错误**，含 **1 处诚实性问题**（把**未实现**的能力写成**已具备**）。

| # | 位置 | 性质 | 处置 |
|---|---|---|---|
| ① | 本仓 `README.md` §1.3 创新点 3（连带 §1.2 一行） | 🔴 **诚实性**：未实现写成已具备 | ✅ 已改写（明确区分已实现 / 未实现） |
| ② | 本仓 `README.md` §1 徽章 + §3.2；`docs/03` §1 | 版本事实错（写 `v5.x`） | ✅ 改为实测 `v6.1` + 附依据 |
| ③ | 本仓 `docs/03` §4.1 目录树 | 状态全错（已入库标成「⬜ 待创建」） | ✅ 按 `git ls-files` 实测重写 |
| ④ | 从机构建命令 | **新克隆照抄会构建失败** | ✅ 新增入库 `sdkconfig.defaults.slave`，命令补齐，**实测 0 error** |
| ⑤ | `docs/BUILD-STRATEGY.md` 与 `tools/BUILD-STRATEGY.md` 同名不同主题 | 引用歧义 | ✅ 前者改名 `docs/BUILD-ROLES.md`，引用同步 |

---

## ① 诚实性：把「运行期切角色」由「已具备」改为「尚未实现」

**原文（错）**：

> 3. **一份固件、双角色、现场可热切（网关热备）**：……角色保存在**设备本机非易失存储（NVS）**中，
>    在设备的 **LCD + 旋钮菜单**上切换并重启即生效 —— **无需上位机、无需 USB、无需刷写工具**。

问题：这句把**尚未实现**的能力写成了**已具备**。真实情况是——角色**只由编译期配置决定**；
I1 批只落地了「角色 → 外设能力掩码」这**一半**；**运行期切角色**（NVS 存角色 + 菜单入口 +
安全关闭 + 重启生效）属**计划中的批 11**，一行都还没有。

**改后**（完整段落见 [`README.md` §1.3](../README.md#13-名称里的五个基因)），结构为：

- 标题改为「**一份固件、两种角色：信号源（从机）与赛事管理网关**」（去掉"现场可热切"）；
- **✅ 已实现**：同一份源码编译出两种角色（**编译期** `CONFIG_ARDF_MESH_ROLE_*`）·
  角色 → 外设能力掩码（网关角色下射频链路整条不初始化 ⇒ 不会发射）· 仓库默认 = 网关（"默认即安全"）；
- **🔴 尚未实现（计划中 —— 批 11）**：**运行期切换角色**这一整条链路（角色存 NVS + 菜单切换入口 +
  切换前安全关闭 + `esp_restart()` 重启生效）**目前一行都没有**；角色只能由编译期配置决定，
  换角色必须**重新构建 + 重新烧录**；
  ⇒「互联网关坏了，随手拿一台信号源、不接 PC、不用刷写工具就能顶替它」**这一能力现在还不具备**；
- 保留动机（为什么最终要做运行期切换），但**明确标注为尚待批 11 实现的目标**；
- 新增一条**对外口径纪律**：批 11 落地前，不得写成"现场可热切""在菜单里切一下就行"或"已在路上"。

**连带一处（同一根因，同批改）**：`README.md` §1.2 流程表「**网关故障热备**」一行原文写
"任意一台信号源可**现场切换为赛事管理网关**"，与创新点 3 是同一个未实现承诺 ⇒ 已改为
"目标：…… —— 🔴 **运行期切角色尚未实现（计划中，批 11）**"。

---

## ② ESP-IDF 版本：`v5.x` → 实测 `v6.1`

**改动**：`README.md` §1 徽章 `Framework-ESP--IDF v5.x` → `v6.1`；`README.md` §3.2 与 `docs/03` §1 的
「框架 = **ESP-IDF v5.x**」→ **`v6.1`**；并在 README §3.2 下新增**实测依据**与**表述纪律**
（`v5.x` 今后只允许作"引入版本 / 最低支持版本"的历史限定，且必须写明限定语，**不得**表示当前版本）。

**实测依据（本机 `C:\esp\esp-idf`，2026-09-28）**：

| 依据 | 结果 |
|---|---|
| `tools/cmake/version.cmake` | `IDF_VERSION_MAJOR 6` / `MINOR 1` / `PATCH 0` |
| `idf.py --version`（激活 `export.ps1` 后实测） | **`ESP-IDF v6.1`** |
| `tools/idf_py_actions/core_ext.py:549`（旁证·格式名） | `--format` 合法值含 **`json2`**（v6.x 名；老版本为 `json`） |
| 环境路径（旁证） | `%IDF_TOOLS_PATH%\python_env\idf6.1_py3.13_env`（esptool v5.4.0） |

**顺带核对（`docs/03` §4.4 勘误表）**：表中 3 个符号名的存在性已就本机 **v6.1** 源码复核，结论不变 ——
`components/esp_wifi/Kconfig:300` 定义 `ESP_WIFI_ENABLE_WPA3_SAE`、`:767` 定义 `ESP_WIFI_DPP_SUPPORT`；
而 `ESP_WIFI_ENABLE_WPA3_SAFE` / `ESP_WIFI_DPP_ENABLED` / `ESP_WIFI_11B_LONG_PREAMBLE` **零命中**。
该表原先标注的核对版本（`v5.1.4`）已改为按本机 v6.1 口径表述，并把上述出处写进文档。

---

## ③ `docs/03` §4.1 目录树：按 `git ls-files` 实测重写

**原文（错）**：标题为「**规划**目录树」，`CMakeLists.txt` / `sdkconfig.defaults` / `partitions.csv` /
`version.txt` / `main/*` 全部标「⬜ 待创建」，并附注"本轮只创建目录与文档"。

**实测（2026-09-28）**：

```
$ git ls-files | Select-String sdkconfig
sdkconfig.defaults
$ git ls-files -- CMakeLists.txt partitions.csv version.txt main/
CMakeLists.txt · main/CMakeLists.txt · main/Kconfig.projbuild · main/app_main.c · partitions.csv · version.txt
```

⇒ 上述文件**全部已入库**。改后：标题改为「目录树（2026-09-28 以 `git ls-files` 实测校正）」，
各项标 ✅ 已入库，并**明确区分**：

- **入库**：`sdkconfig.defaults`、`sdkconfig.defaults.slave`；
- **不入库**（本地生成物）：`sdkconfig`、`sdkconfig.slave`、`sdkconfig.gw2`。

**顺带改正**：该节原写「28 个组件骨架」；实测 `git ls-files components/*/CMakeLists.txt` =
**30 个已入库组件**（另有 1 个在制品组件目录尚未入库）。同一处旧数字在 `README.md` §3.2 也已按同一实测口径改正。

---

## ④ 从机构建命令：新克隆照抄会失败 —— 已修，且照抄即可成功

**问题**：`.gitignore` 忽略 `sdkconfig`（`:17`）与 `sdkconfig.*`（`:95`），只有 `sdkconfig.defaults`
入库 ⇒ **新克隆的树里没有 `sdkconfig.slave`**；而原 README 的从机构建命令只有
`-D SDKCONFIG=…\sdkconfig.slave` ⇒ **构建直接失败**（不是静默回落）。

**采用方案**（工程做法 = 入库 defaults 叠加，而不是在文档里教人手工复制配置）：

- 新增**入库**文件 `sdkconfig.defaults.slave`（只写与 `sdkconfig.defaults` 的**差异** = 角色那一项）；
- `.gitignore` 增加例外 `!sdkconfig.defaults.slave`。**理由**：`sdkconfig.*` 是**子串匹配**，
  已有的 `!sdkconfig.defaults` **只放行同名文件**，**不会**顺带放行 `.slave`；
- README / `docs/03` §4.4 / 私有仓 `docs/BUILD-ROLES.md` §4.2 / `GATEWAY-STANDALONE-PLAN.md` §18.3
  的从机命令统一补齐**两个 `-D`**（`SDKCONFIG` = **产物落点**，`SDKCONFIG_DEFAULTS` = **配置源头**）。

**实测（本机 ESP-IDF v6.1，2026-09-28）** —— 用**此前不存在**的 SDKCONFIG 路径模拟全新克隆：

```
idf.py -B build-slave-defaults --ccache -D SDKCONFIG="<abs>\sdkconfig.slave-fresh" -D SDKCONFIG_DEFAULTS="<abs>\sdkconfig.defaults;<abs>\sdkconfig.defaults.slave" build
```

| 观测点 | 实测结果 |
|---|---|
| 两个 defaults 都被加载 | 日志含 `Loading defaults file .../sdkconfig.defaults...` 与 `.../sdkconfig.defaults.slave...` |
| 两个变量确实传到了 CMake | 日志中 CMake 实际命令含 `-DSDKCONFIG=...sdkconfig.slave-fresh` **与** `-DSDKCONFIG_DEFAULTS=...sdkconfig.defaults;...sdkconfig.defaults.slave` |
| 配置由「不存在的路径」新建 | `Project sdkconfig file .../sdkconfig.slave-fresh`（构建前已确认该文件不存在） |
| 构建结果 | `[1132/1132]` → `Project build complete.`，**进程退出码 0**，无 `error:` |
| 产物 | `ardf_meshtunefox80.bin` = `0xd8e70`（887,920 B），app 分区余 44% |
| 生成配置里的角色行 | `sdkconfig.slave-fresh:840` = `# CONFIG_ARDF_MESH_ROLE_MASTER is not set`<br>`sdkconfig.slave-fresh:841` = **`CONFIG_ARDF_MESH_ROLE_SLAVE=y`** |

> ℹ️ 为让构建日志干净，`sdkconfig.defaults.slave` 的分隔注释行已改用与既有 `sdkconfig.defaults`
> 相同的 `# ---…` 风格（此前用 `# ===…` 会让 kconfgen 多打两条 `NOTE: ... line was updated to ...`；
> 该 NOTE 只涉及注释行、不影响生成的配置）。改后 `reconfigure` 复测：NOTE 消失、两个 defaults 仍被加载、
> 角色仍为 `CONFIG_ARDF_MESH_ROLE_SLAVE=y`。

⇒ README 的从机构建命令现在是**照抄即可成功**的（**新克隆亦然**）。

**如实登记的未修面**：纯网关板 `hw_rev=2` 用的 `sdkconfig.gw2` **没有**配套的 defaults 叠加文件
⇒ 它在**新克隆**上**仍会构建失败**，仍需先手工生成。此点已在 README、`docs/03`、私有仓
`docs/BUILD-ROLES.md` §4.3 与 `GATEWAY-STANDALONE-PLAN.md` §18.3/§18.4 **如实标注**，未含糊成"已可用"。

---

## ⑤ 同名不同主题的文档改名

`docs/BUILD-STRATEGY.md`（私有固件仓，管**构建产物的角色语义**）与 `tools/BUILD-STRATEGY.md`
（管**机器资源**：并发 ≤2 / 复用 `build/` / `--ccache`）**同名不同主题**，极易引错
⇒ 前者改名为 **`docs/BUILD-ROLES.md`**（用 `git mv`，保留改名历史）。

**已同步的引用点（4 处）**：

| 文件 | 处 |
|---|---|
| 私有仓 `docs/GATEWAY-STANDALONE-PLAN.md` | §18.4「生成办法」的引用 · §18.6 交叉引用块 |
| 私有仓 `docs/BUILD-ROLES.md`（文件自身） | 文件头"不要混淆"→"改名说明 + 两者分工表" |
| 本仓 `README.md` | §3.2 从机构建命令下方的引用 |
| 本仓 `docs/03-software-architecture.md` | §4.4 角色专条内的引用 |

**未同步的引用点**见下方"未做项"第 1、2 条。

---

## 依据与自证

| 项 | 命令 / 出处 | 结果 |
|---|---|---|
| 双仓分离门禁 | `pwsh -File scripts/check-repo-separation.ps1` | ✅ 通过（公开仓 145 · 私有仓 523 已入库文件） |
| 同上，**含未入库文件** | 对 `git ls-files` + `git ls-files --others --exclude-standard` 套门禁同款正则 | ✅ 无越界 |
| 公开仓改动不含规则原文 | 对本批新增行逐一取 20 字窗口，与私有仓 `docs/rules/*.txt`（去空白 56,539 字）比对 | ✅ **零命中** |
| UTF-8 无 BOM + LF | 新增文件首 3 字节实测 | ✅（`sdkconfig.defaults.slave` 首 3 字节 = `23 20 3D`，非 `EF BB BF`） |

> ⚠️ 门禁脚本只扫 `git ls-files`（**已入库**）文件。本批改动**未提交**，故在提交前，
> 上表第二行（**含未入库文件**的同款检查）才是本批真正的自证依据。

---

## 未做项（如实登记）

1. **私有仓 `docs/console/08-progress-log.md`** 第 1479 / 1620 行仍写旧文件名 `docs/BUILD-STRATEGY.md`
   —— 该文件在**本批的禁写范围内**（并发写盘），需另行派工修正。
2. **私有仓 `docs/ARDF-CODE-DASH-REMOVAL.md`** 第 365 / 402 行有同款旧引用 —— 该文件**不在本批可写范围**
   （他人新建的在制品）。
3. **本仓 `docs/06-build-and-dev-environment.md`** 与 **`docs/adr/ADR-0001-*.md`** 内仍有若干 `v5.x`
   （如 `06` 的"`idf.py --version` 输出 v5.1+"、"# 应输出 ESP-IDF v5.3.x"，ADR-0001 的
   "固件全面基于 ESP-IDF v5.x"）—— 本批 ② 的范围**只含 `README.md` 与 `docs/03`**，故**未改**。
   这些是"最低版本 / 引入版本"还是"当前版本"需逐处判断，建议单独一批处理。
4. **私有仓 `sdkconfig.defaults` 第 1 行注释**仍写「ESP-IDF v5.x」—— 该文件不在本批可写范围。
5. **`sdkconfig.gw2`** 无配套 defaults 叠加文件（见 ④），新克隆仍需手工生成。
6. **本仓 `README.md` §1.2「无上位机备用」一行**（网关独立运行）仍按**目标**表述书写，本批**未加**
   "未实现"标注：私有仓计划书把该项记为**批 10 ⬜**，但 `hw_rev=2` 纯网关板与能力掩码**已经落地**，
   其**已落地程度本批未核实** ⇒ 留给项目负责人裁定（若确未实现，应与 ① 同样改写）。
7. **`README.md` §1.1 / §1.2 其余能力表述未逐条与实现状态核对**（超出本批 5 处范围）。
