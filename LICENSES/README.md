# LICENSES/ — 许可全文

本目录存放本项目适用的各许可证**全文**（[REUSE](https://reuse.software/) 风格：文件名 = SPDX 标识符）。
目录级授权映射的**唯一权威**是仓库根 [`LICENSING.md`](../LICENSING.md)。

---

## 🔴 最重要的规则：标准许可全文必须逐字节原样

许可全文是**法律文本**。对**三份标准许可**——`CERN-OHL-S-2.0.txt`、`Apache-2.0.txt`、`CC-BY-4.0.txt`——**禁止**：

- ❌ 改写、精简、"优化"措辞
- ❌ 重新排版、调整换行、转换为其他格式
- ❌ 机翻或"顺手修正"拼写
- ❌ 凭记忆重打（这是最容易出错、后果最严重的方式）

必须从**官方来源**下载，并核对完整性。

> ✅ **适用范围说明**：`LicenseRef-ARDF-NC-1.0.txt` 是本项目的**自定义许可**（REUSE 规范允许 `LicenseRef-` 前缀），由本项目自行撰写，**可以直接编辑**。
> 但任何改动都必须**同步更新** [`../LICENSING.md`](../LICENSING.md) 与 [`../docs/08-licensing-and-compliance.md`](../docs/08-licensing-and-compliance.md)，并重新登记 SHA-256。

---

## 一、应包含的文件（四份）

| 文件 | SPDX 标识符 | 来源 | 状态 |
|------|------------|------|------|
| `CERN-OHL-S-2.0.txt` | `CERN-OHL-S-2.0` | https://gitlab.com/ohwr/project/cernohl/-/raw/master/licence_texts/cern_ohl_s_v2.txt | ✅ 已就位 |
| `Apache-2.0.txt` | `Apache-2.0` | https://www.apache.org/licenses/LICENSE-2.0.txt | ✅ 已就位 |
| `CC-BY-4.0.txt` | `CC-BY-4.0` | https://creativecommons.org/licenses/by/4.0/legalcode.txt | ✅ 已就位 |
| `LicenseRef-ARDF-NC-1.0.txt` | `LicenseRef-ARDF-NC-1.0` | **本项目自撰，无需下载** | ✅ 已就位 |

> ⚠️ **CERN-OHL-S v2 的 URL 容易取错**（实测）：`https://ohwr.org/cern_ohl_s_v2.txt` 与
> `https://gitlab.com/ohwr/project/cernohl/-/raw/master/CERN-OHL-S-2.0.txt` **都会返回 HTML 页面**。
> 正确路径在 `licence_texts/` 子目录下，且拼写是英式的 **`licence`**（非 `license`），
> 文件名为 `cern_ohl_s_v2.txt`。截至登记时该官方版为 **13708 字节**。
>
> SPDX 镜像 `raw.githubusercontent.com/spdx/license-list-data/main/text/CERN-OHL-S-2.0.txt`
> 可用作备用，但实测其内容为 **13419 字节**，与官方版**不一致**（应为重排版），
> 因此**优先使用官方 ohwr 版**。

---

## 二、获取方法（仅三份标准许可）

> ℹ️ `LicenseRef-ARDF-NC-1.0.txt` 是**本项目自撰**的自定义许可，已随仓库提供，**不需要**也不应从外部下载。

在仓库根目录执行（Windows PowerShell）：

```powershell
# 0) 建立目录（若尚未存在）
New-Item -ItemType Directory -Force -Path LICENSES | Out-Null

# 三份标准许可：从官方来源下载
Invoke-WebRequest -Uri "https://ohwr.org/cern_ohl_s_v2.txt"                    -OutFile "LICENSES/CERN-OHL-S-2.0.txt"
Invoke-WebRequest -Uri "https://www.apache.org/licenses/LICENSE-2.0.txt"       -OutFile "LICENSES/Apache-2.0.txt"
Invoke-WebRequest -Uri "https://creativecommons.org/licenses/by/4.0/legalcode.txt" -OutFile "LICENSES/CC-BY-4.0.txt"
```

Linux / macOS 等价命令：

```bash
mkdir -p LICENSES
curl -L -o LICENSES/CERN-OHL-S-2.0.txt   https://ohwr.org/cern_ohl_s_v2.txt
curl -L -o LICENSES/Apache-2.0.txt       https://www.apache.org/licenses/LICENSE-2.0.txt
curl -L -o LICENSES/CC-BY-4.0.txt        https://creativecommons.org/licenses/by/4.0/legalcode.txt
```

---

## 三、获取后校验（必做）

```powershell
# 1) 文件大小与 SHA-256 记录
Get-ChildItem LICENSES\*.txt | ForEach-Object {
    "{0,-28} {1,8} bytes  {2}" -f $_.Name, $_.Length, (Get-FileHash $_.FullName -Algorithm SHA256).Hash
}
```

```bash
sha256sum LICENSES/*.txt   # Linux / macOS
```

**自检要点（三份标准许可）**

| 文件 | 应包含的标识性内容 |
|------|------------------|
| `CERN-OHL-S-2.0.txt` | 首行 `CERN Open Hardware Licence Version 2 - Strongly Reciprocal`；含 `Preamble`；末行含 `8.6 This Licence shall not be enforceable except by a Licensor`（官方版 **289 行 / 13708 字节**） |
| `Apache-2.0.txt` | 含 `Apache License` / `Version 2.0, January 2004` / `END OF TERMS AND CONDITIONS` 与 `APPENDIX: How to apply the Apache License to your work`（**11358 字节**） |
| `CC-BY-4.0.txt` | 含 `Attribution 4.0 International`；含 `Section 2 – Scope`、`Section 3 – License Conditions`（**18657 字节**） |

若任一文件缺失上述标识内容，说明下载被重定向到了 HTML 页面（`.txt` 结尾的 URL 有时会返回网页），必须重新获取。

`LicenseRef-ARDF-NC-1.0.txt` 不适用上述自检规则（自定义许可由本项目自撰）；只需确认其头部保留 `SPDX-License-Identifier: LicenseRef-ARDF-NC-1.0` 声明。

---

## 四、把 SHA-256 登记与归档

校验通过后，把各文件的 SHA-256 记录到本节表格中，作为后续审计依据：

| 文件 | SHA-256 | 字节数 | 登记日期 |
|------|---------|-------|---------|
| `CERN-OHL-S-2.0.txt` | `830BD5A61C579317156E889E98314C0585958854F2FF3C227256697385431C80` | 13708 | 2026-09-25 |
| `Apache-2.0.txt` | `CFC7749B96F63BD31C3C42B5C471BF756814053E847C10F3EB003417BC523D30` | 11358 | 2026-09-25 |
| `CC-BY-4.0.txt` | `9BA9550AD48438D0836DDAB3DA480B3B69FFA0AAC7B7878B5A0039E7AB429411` | 18657 | 2026-09-25 |
| `LicenseRef-ARDF-NC-1.0.txt` | `3AAF0D44929DFEE73B643325098F3AB2F4D71D8DEBAF0C1100CFFFAD75960FC4` | 8084 | 2026-09-25 |

> 重算命令：`Get-ChildItem LICENSES\*.txt | ForEach-Object { "{0}  {1}" -f (Get-FileHash $_.FullName -Algorithm SHA256).Hash, $_.Name }`
> 可同步登记到 [`../LICENSING.md`](../LICENSING.md) 第五节的 `LICENSES/` 目录表，便于集中查阅。

---

## 五、REUSE 规范中的 `LicenseRef-`

[REUSE 规范](https://reuse.software/spec/) 允许项目声明**没有 SPDX 官方标识符**的自定义许可，做法是：

1. **文件位置**：自定义许可全文放在 `LICENSES/LicenseRef-<名称>.txt`。
2. **标识符**：源文件头部、目录映射表与本文档中统一使用 `LicenseRef-<名称>`。
3. **禁止冒用**：不得使用与 SPDX 官方标识符相同的名字（例如自造 `Apache-2.0`），以免被工具误判为标准许可。
4. **正文自撰**：自定义许可的正文由项目自行撰写，可随时修订；每次修订都需同步更新 [`../LICENSING.md`](../LICENSING.md) 与 [`../docs/08-licensing-and-compliance.md`](../docs/08-licensing-and-compliance.md)。

**本项目当前用法**

| 标识符 | 文件 | 适用对象 |
|--------|------|---------|
| `LicenseRef-ARDF-NC-1.0` | `LICENSES/LicenseRef-ARDF-NC-1.0.txt` | **固件二进制**（GitHub Releases 发布的编译产物），以及私有仓中的固件源码（私有仓内另有 `LICENSE`） |

---

## 六、本目录中不再有 GPL 全文

本目录**不再包含**任何 GPL 系列许可全文（原有的 GPLv3 全文文件已随固件许可变更删除）。

> ⚠️ 若本地工作副本中仍残留该文件，属于尚未清理的旧副本：**不要引用它**，也不要把它加入任何新提交；按仓库历史清理流程移除即可。

原因：固件不再使用 GPL，已改用自定义许可 `LicenseRef-ARDF-NC-1.0`——它**只覆盖编译后的二进制**，源码移入私有仓。因此本项目**没有任何目录需要 GPL 全文**；继续保留只会让 GitHub 与扫描工具误判授权范围。

完整的决策背景见 [ADR-0007 固件闭源与双仓结构](../docs/adr/ADR-0007-firmware-closed-source-two-repo.md)。

---

## 七、关联文档

| 文档 | 用途 |
|------|------|
| [`../LICENSING.md`](../LICENSING.md) | 目录级授权映射表（唯一权威） |
| [`../docs/08-licensing-and-compliance.md`](../docs/08-licensing-and-compliance.md) | 分层授权说明、射频合规、落地清单 |
| [ADR-0007 固件闭源与双仓结构](../docs/adr/ADR-0007-firmware-closed-source-two-repo.md) | 固件许可变更与双仓结构的决策背景 |
| [`../docs/07-coding-standards.md`](../docs/07-coding-standards.md) | 源文件 SPDX 头规范 |
| [REUSE 规范](https://reuse.software/spec/) | 本目录组织方式所遵循的规范 |
