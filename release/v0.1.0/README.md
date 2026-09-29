# `release/v0.1.0/` —— 首发（v0.1.0）发布产物暂存目录

> **这是什么**：**公开仓**里为 `v0.1.0` 准备的 **GitHub Release 附件暂存区**。
> 依据：私有固件仓 `docs/RELEASE-PROCESS.md`（发布流程与 30 条自检清单）· 用户裁定 **R-6**
> （「要打 tag / 出 release，把固件二进制作为正式发布物」）。

---

## 1. 🔴 为什么二进制在这里、却**不入库**

```
本仓 .gitignore 原文（第 42 行起）：
  # 二进制不入 Git —— 固件二进制通过 GitHub Releases 分发，不提交到版本库
  *.bin
  *.hex

本仓 CI 门禁 scripts/check-repo-separation.ps1 也把 `\.(bin|elf|map|hex)$`
列为【公开仓禁止入库】的"固件产物"。
```

⇒ **本目录里的 `.bin` / `.elf` 只是"待上传的 Release 附件"**，由 Lead 在打 tag 后
作为 **GitHub Release 的附件**上传（附件是独立对象，**不进入 Git 历史**）。
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

## 3. 上传清单（由 **Lead** 执行；本批**没有**打 tag、**没有**建 Release）

```
① tag:  v0.1.0（annotated tag，打在【公开仓】）
② Release 标题:  ARDF-MeshTuneFox80 固件 v0.1.0
③ Release 描述:  = RELEASE-NOTES-v0.1.0.md 全文（🔴 第 0 节必须排在最前）
④ 附件:  上表 9 个文件 + SHA256SUMS
⑤ 🔴 必须随附（Apache-2.0 / 许可条款要求，见 .github/OVERVIEW.md §4）:
     · NOTICE（ESP-IDF 等第三方声明）
     · LICENSES/LicenseRef-ARDF-NC-1.0.txt（固件二进制许可全文）
   ⇒ 二者已在本仓入库；Release 描述里【必须给出指向】，或直接作为附件一并上传。
```

---

## 4. 用这批产物烧录

见公开仓根目录 **[快速上手 · 烧录前必读](../../QUICKSTART-BEFORE-FLASHING.md) §6** ——
三份 `.bin` 分别是什么角色、会不会发报、`esptool` 的**正确偏移**（`0x0` / `0x8000` / `0xf000` / **`0x20000`**）
都在那一页，**不要凭记忆写偏移**。
