# `release/v0.1.0/` —— 首发（v0.1.0）发布产物暂存目录

> **这是什么**：**公开仓**里为 `v0.1.0` 准备的 **GitHub Release 附件暂存区**。
> 依据：私有固件仓 `docs/RELEASE-PROCESS.md`（发布流程与 30 条自检清单）· 用户裁定 **R-6**
> （「要打 tag / 出 release，把固件二进制作为正式发布物」）。
>
> ✅ **本批已发布（既成事实，不是待办）**：**annotated tag `v0.1.0` 已建立**（打在公开仓 `main`），
> **GitHub Release 已发布** ⇒ 线上共有 **12 个上传附件**。逐项清单见 §3。

---

## 1. 🔴 为什么二进制在这里、却**不入库**

```
本仓 .gitignore 原文（第 42 行起）：
  # 二进制不入 Git —— 固件二进制通过 GitHub Releases 分发，不提交到版本库
  *.bin
  *.hex

本仓双仓分离自检脚本 scripts/check-repo-separation.ps1 也把 `\.(bin|elf|map|hex)$`
列为【公开仓禁止入库】的"固件产物"（⚠️ 这是**本地脚本**，本仓**尚未配置** CI workflow，见脚本头部说明与 CHANGELOG）。
```

⇒ **本目录里的 `.bin` / `.elf` 只是"Release 附件"**（附件是独立对象，**不进入 Git 历史**）。
⇒ 本目录里**可以入库**的只有文本：`README.md`（本文件）、`RELEASE-NOTES-v0.1.0.md`、`SHA256SUMS`。

> 🔴 **绝不入库**：`.bin` · `.elf` · 任何固件源码（`.c/.h`）· 规则原文（`docs/rules/*.txt` 一类）。

---

## 2. 目录内容

| 文件 | 是什么 | 入 Git？ | 作为 Release 附件？ |
|---|---|---|---|
| `RELEASE-NOTES-v0.1.0.md` | **发布说明正文**（第 0 节 = 默认角色语义，第 1 节 = 合规口径） | ✅ 可入库 | ✅ 贴进 Release 描述 |
| `SHA256SUMS` | 全部附件的 SHA-256 清单（明文，供用户自行复核） | ✅ 可入库 | ✅ 一并上传 |
| `ardf_meshtunefox80-v0.1.0-default.bin` / `.elf` | 默认档（网关 `MASTER` + 狐狸板 `hw_rev=1`） | ❌ | ✅ |
| `ardf_meshtunefox80-v0.1.0-slave.bin` / `.elf` | 狐狸档（从机 `SLAVE` + `hw_rev=1`）**会发报** | ❌ | ✅ |
| `ardf_meshtunefox80-v0.1.0-gw2.bin` / `.elf` | 纯网关板档（`MASTER` + SuperMini `hw_rev=2`） | ❌ | ✅ |
| `bootloader.bin` | 引导加载器（烧到 `0x0`） | ❌ | ✅ |
| `partition-table.bin` | 分区表（烧到 `0x8000`） | ❌ | ✅ |
| `ota_data_initial.bin` | OTA 数据初始镜像（烧到 `0xf000`） | ❌ | ✅ |

> ⚠️ **`.elf` 不是可选项**：本项目的调试主线是"串口日志 + Core Dump"，
> 现场拿到 Core Dump 后要用 `riscv32-esp-elf-addr2line -e <file>.elf` 反查源码行
> ⇒ **不带符号的发布物等于放弃了现场定位能力**。
>
> ℹ️ **`bootloader.bin` 只放一份**：三档各自构建出的 `bootloader.bin` **仅差构建时间戳与尾部镜像哈希**
> （实测 38 字节：`esp_bootloader_desc` 的 `Sep 29 2026 hh:mm:ss` 串 + 尾部 SHA-256）⇒ 功能等价。
> ⚠️ **三份应用镜像字节数相同（898,720 B）但 SHA-256 互异** —— 角色/板型是**运行期**按能力掩码裁剪，
> 不是编译期删代码。**以 `SHA256SUMS` 为准，不要用体积判断是哪一档。**

---

## 3. ✅ 线上 Release 记录（**已执行完毕** —— 不是待办清单）

| 项 | 既成事实 |
|---|---|
| ① tag | **`v0.1.0`** —— **annotated tag**，打在**【公开仓】**`main`（`d53f2bc`）上 |
| ② Release 标题 | `ARDF-MeshTuneFox80 固件 v0.1.0` |
| ③ Release 描述 | = `RELEASE-NOTES-v0.1.0.md` 全文 |
| ④ 附件 | **线上共 12 个上传附件**（见下表） |
| ⑤ 许可随附件 | `NOTICE`（第三方声明） + `LICENSES/LicenseRef-ARDF-NC-1.0.txt`（固件二进制许可全文）**均已作为附件上传** |

### 3.1 线上 12 个上传附件的构成

> 📌 **该清单由联网核实得到**。来源 = 私有固件仓 `docs/AUDIT-SUMMARY-2026-09-30.md` §5.3
> （「GitHub Release 附件构成」段，✅ 已联网核实 2026-09-30；取数方式 = GitHub 的
> `releases/expanded_assets/v0.1.0` 端点，因 REST API 被限流 403）。
> 🔴 **本仓离线不重复断言线上状态**；引用时请保留这一出处。

| # | 附件 | 类别 | 是否入 Git |
|---|---|---|---|
| 1 | `ardf_meshtunefox80-v0.1.0-default.bin` | 三档应用镜像 · 默认档（网关 `MASTER` + `hw_rev=1`） | ❌ |
| 2 | `ardf_meshtunefox80-v0.1.0-default.elf` | 同上 · 带符号 | ❌ |
| 3 | `ardf_meshtunefox80-v0.1.0-slave.bin` | 三档应用镜像 · 狐狸档（`SLAVE` + `hw_rev=1`）**会发报** | ❌ |
| 4 | `ardf_meshtunefox80-v0.1.0-slave.elf` | 同上 · 带符号 | ❌ |
| 5 | `ardf_meshtunefox80-v0.1.0-gw2.bin` | 三档应用镜像 · 纯网关板档（`MASTER` + `hw_rev=2`） | ❌ |
| 6 | `ardf_meshtunefox80-v0.1.0-gw2.elf` | 同上 · 带符号 | ❌ |
| 7 | `bootloader.bin` | 引导加载器（烧 `0x0`） | ❌ |
| 8 | `partition-table.bin` | 分区表（烧 `0x8000`） | ❌ |
| 9 | `ota_data_initial.bin` | OTA 数据初始镜像（烧 `0xf000`） | ❌ |
| 10 | `SHA256SUMS` | 上表 9 个产物的 SHA-256 明文清单 | ✅ 文本 |
| 11 | `NOTICE` | 第三方组件声明台账（Apache-2.0 合规要求） | ✅ 文本 |
| 12 | `LicenseRef-ARDF-NC-1.0.txt` | 固件二进制许可全文 | ✅ 文本 |

> ℹ️ **与 §2 的 9 个附件的口径关系**：§2 表列的是**本目录里那 9 个产物文件**（= `SHA256SUMS` 的 9 行）；
> **线上 12 个** = 这 9 个 **+** `SHA256SUMS` **+** `NOTICE` **+** `LicenseRef-ARDF-NC-1.0.txt`。
> （GitHub 另会为 tag 自动生成 source 包，那是平台行为，不计入"上传附件"。）
>
> ✅ **另一条已联网证实的结论**：本地 `SHA256SUMS` 里列的 **9 个产物哈希，与 GitHub 上附件的
> sha256 逐字符完全一致** ⇒ "本仓记录的产物 = 线上产物"。出处同 §3.1 引用的那段。
> ⚠️ **边界（如实告知）**：该核实**没有下载附件在本地复算**，只比对了 GitHub 自报的 `sha256`
> 与本地 `SHA256SUMS`。若需抗"平台自报值被篡改"，仍须下载后本地复算。
>
> 🔴 **`.elf` 不是可选项**：本项目的调试主线是"串口日志 + Core Dump"，
> 现场拿到 Core Dump 后要用 `riscv32-esp-elf-addr2line -e <file>.elf` 反查源码行
> ⇒ **不带符号的发布物等于放弃了现场定位能力**。这也是三档 `.bin` 之外**必须**同时上传 `.elf` 的理由。

**为什么这一节此前写的是"待执行"**：`v0.1.0` 的发布动作由 Lead 在**本目录提交之后**执行，
而本文件当时按"提交时点"写的。现已按既成事实改正 —— 后到的读者**不应**再从本仓读出
"v0.1.0 还没发布"，否则会**重复打 tag / 建重复 Release**。

---

## 4. 用这批产物烧录

见公开仓根目录 **[快速上手 · 烧录前必读](../../QUICKSTART-BEFORE-FLASHING.md) §6** ——
三份 `.bin` 分别是什么角色、会不会发报、`esptool` 的**正确偏移**（`0x0` / `0x8000` / `0xf000` / **`0x20000`**）
都在那一页，**不要凭记忆写偏移**。
