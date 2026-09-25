# 16 · 本地工作区与 DSH 设置（换会话交接）

> **本文档是换工作区/换会话时的唯一交接清单。**
> 状态：已建立｜适用版本：V3.7｜最后更新：2026-09

---

## 1. 目标本地布局

项目根是一个**容器目录**，两个仓库作为它的**子目录**：

```
C:\DeepseekProject\ARDF-MeshTuneFox80\          ← 容器（无 .git）
├── ARDF-MeshTuneFox80-hardware\                ← 公开仓
│   ├── .git\        remote: github.com/PatrickShih774/ARDF-MeshTuneFox80.git
│   ├── hardware\    docs\    validation\    software\    scripts\    .github\
│   ├── LICENSES\    LICENSING.md    NOTICE    README.md    CHANGELOG.md    CONTRIBUTING.md
│   └── .editorconfig  .gitattributes  .gitignore
│
└── ARDF-MeshTuneFox80-firmware\                ← 私有仓
    ├── .git\        remote: github.com/PatrickShih774/ARDF-MeshTuneFox80-firmware.git
    ├── components\  main\  test\  tools\  docs\
    ├── CMakeLists.txt  sdkconfig.defaults  partitions.csv  version.txt
    └── LICENSE  NOTICE  README.md  CHANGELOG.md
```

### 为什么这样放

| 原因 | 说明 |
|------|------|
| **DSH 工作区可以覆盖两个仓** | 工作区设为容器目录即可，**不再依赖会话级的 `danger-full-access`** |
| **物理隔离仍然成立** | 两个 `.git` 各自独立，互不干涉；固件源码不会误入公开仓（跨目录了） |
| **符合 DSH 的"项目根"规则** | 容器无 `.git` → 项目根回退为 cwd → 项目级技能目录是 `<容器>/.dsh/skills`（在两仓之外，干净） |
| **不再有"兄弟目录"问题** | 旧布局里固件仓在工作区外，靠临时策略才能写；新布局彻底消除这个隐患 |

> ⚠️ **公开仓的目录名变了**：从 `ARDF-MeshTuneFox80` 改为 `ARDF-MeshTuneFox80-hardware`。
> 这只影响**本地路径**，**GitHub 仓库名与 URL 不变**（仍是 `PatrickShih774/ARDF-MeshTuneFox80`）。
> 文档里的所有跨仓引用都用 GitHub 绝对 URL，因此**不受影响**。

---

## 2. ✅ 迁移已完成（2026-09-25）

**迁移结果**：

| 仓 | 本地路径 | HEAD | 文件数 | 状态 |
|----|---------|------|--------|------|
| 公开 | `C:\DeepseekProject\ARDF-MeshTuneFox80\ARDF-MeshTuneFox80-hardware` | `83cc2f6` | 101 | clean |
| 私有 | `C:\DeepseekProject\ARDF-MeshTuneFox80\ARDF-MeshTuneFox80-firmware` | `ef8fa54` | 138 | clean |

本节保留迁移步骤作为**历史记录**，并记录一个**必须避免的严重陷阱**。

---

### 2.1 🔴 陷阱：`Move-Item` 失败后**不要**用 `Remove-Item` 回滚

**实际踩到的坑**：第一次迁移时 `Move-Item` 报"没有足够的访问权限"而失败，
当时的回滚逻辑执行了 `Remove-Item -Recurse -Force <临时容器>`。

**后果**：`Move-Item` 在目录上是**递归搬一部分再失败**的——它已经把 `.git/` 的全部内容和
仓库根目录的 8 个文件搬进了临时容器，失败后我的回滚**把那些文件永久删除了**。
结果公开仓的 `.git` 变成空目录，仓库根文件全部消失。

**正确做法**：

| ❌ 错误 | ✅ 正确 |
|---------|--------|
| 失败后 `Remove-Item -Recurse -Force <临时容器>` | **先检查临时容器里有什么**；非空说明发生了部分搬移，应把内容**搬回原位**而不是删除 |
| 假设 `Move-Item` 是原子的 | 目录的 `Move-Item` **可能部分完成**；要么用 `robocopy /MOVE`（可重入），要么每一步都先核验目标 |
| 只靠文件系统操作做大范围搬移 | **先确保远端是最新的**（`git push` + 工作区 clean），这样任何损坏都能 `git clone` 恢复 |

**本次恢复方式**（已验证有效）：

```powershell
# 前提：删除前刚 push 过，GitHub 上有完整副本
Remove-Item -Recurse -Force 'C:\DeepseekProject\ARDF-MeshTuneFox80\ARDF-MeshTuneFox80-hardware'
cd 'C:\DeepseekProject\ARDF-MeshTuneFox80'
git clone https://github.com/PatrickShih774/ARDF-MeshTuneFox80.git ARDF-MeshTuneFox80-hardware
# 校验：git ls-files 计数 == 文件系统计数，git status 为 clean
```

> **教训**：做大范围文件搬移前，**先 push**。"远端是最新的"是唯一的可靠退路。

---

### 2.2 迁移步骤（历史记录，已执行完毕）

旧布局：

```
C:\DeepseekProject\
├── ARDF-MeshTuneFox80\            ← 公开仓（就地）
└── ARDF-MeshTuneFox80-firmware\   ← 私有仓（兄弟目录）
```

**实际可用的步骤**（比原方案更安全——**只用重命名，不做跨目录搬移**）：

```powershell
cd C:\DeepseekProject

# ① 公开仓先纯改名（Rename-Item 比 Move-Item 可靠，实测可行）
Rename-Item 'ARDF-MeshTuneFox80' 'ARDF-MeshTuneFox80-hardware'

# ② 建容器
New-Item -ItemType Directory -Force -Path 'ARDF-MeshTuneFox80' | Out-Null

# ③ 把两个仓移进容器（若失败，把已移入的移回，不要删除）
Move-Item 'ARDF-MeshTuneFox80-hardware' 'ARDF-MeshTuneFox80\ARDF-MeshTuneFox80-hardware'
Move-Item 'ARDF-MeshTuneFox80-firmware' 'ARDF-MeshTuneFox80\ARDF-MeshTuneFox80-firmware'
```

**每一步之后都要核验**：

```powershell
Get-ChildItem C:\DeepseekProject\ARDF-MeshTuneFox80
foreach ($p in @('ARDF-MeshTuneFox80-hardware','ARDF-MeshTuneFox80-firmware')) {
  $full = "C:\DeepseekProject\ARDF-MeshTuneFox80\$p"
  Write-Output "$p : git=$(git -C $full rev-parse --short HEAD 2>&1) files=$(@(git -C $full ls-files).Count)"
}
```

**判据**：两个仓都能 `git rev-parse` 成功，且 `git ls-files` 计数等于文件系统计数。

**若 `Move-Item` 报权限/占用错误**：说明仍有进程以旧路径为工作目录（最常见是 DSH 自身或终端窗口）。
关闭后重试——**注意此时可能已发生部分搬移，务必先检查而不是删除**（见 2.1）。

### 2.3 迁移后自检（已执行通过）

```powershell
$h = 'C:\DeepseekProject\ARDF-MeshTuneFox80\ARDF-MeshTuneFox80-hardware'
$f = 'C:\DeepseekProject\ARDF-MeshTuneFox80\ARDF-MeshTuneFox80-firmware'

foreach ($p in @($h,$f)) {
  Write-Output "--- $p ---"
  Write-Output ("  HEAD   : " + (git -C $p log --oneline -1))
  Write-Output ("  提交数 : " + (git -C $p rev-list --count HEAD))
  Write-Output ("  remote : " + (git -C $p remote get-url origin))
  Write-Output ("  工作区 : " + $(if (git -C $p status --porcelain) { 'dirty' } else { 'clean' }))
  Write-Output ("  ls-files / 文件系统: " + @(git -C $p ls-files).Count + " / " +
                (Get-ChildItem -Recurse -Force -File $p | Where-Object { $_.FullName -notmatch '\\\.git\\' }).Count)
}
```

**判据**：两个仓 `git` 可用、工作区 clean、且 **`git ls-files` 计数 == 文件系统计数**。

**本次实测结果**：`-hardware` = 101/101（`83cc2f6`，6 提交）；`-firmware` = 138/138（`ef8fa54`，2 提交）。

---

## 3. ✅ 工作区已经是容器目录（无需改动）

**本会话的工作区路径从未改变**，始终是：

```
C:\DeepseekProject\ARDF-MeshTuneFox80
```

变的只是**它的内容**——从「公开仓本身」变成了「容纳两个仓的容器」。

### 3.1 这是最优解：一次操作同时达成三个目标

| 目标 | 若"换工作区 + 开新会话" | **实际做法：保持路径不变，只重组内容** |
|------|----------------------|-----------------------------------|
| 两仓同处一个工作区 | ✅ | ✅ |
| `workspace-write` 策略即可覆盖（不依赖 `danger-full-access`） | ✅ | ✅ |
| **KV 前缀缓存 / 投影缓存不失效** | ❌ 首轮全量重写 | ✅ **`cwd` 字符串未变 → 缓存身份未失效** |
| **会话上下文与全部对话保留** | ❌ 全新会话 | ✅ **同一会话，`session-0fd161c7-…`** |

**关键洞察**：DSH 的缓存键绑定的是**工作区路径字符串**，不是"这个路径下装了什么"。
所以 **"换工作区"与"重组工作区内的内容"是两回事**——
后者可以在完全不触碰缓存键的前提下把目录结构调整到位。

### 3.2 实测确认

| 项 | 值 |
|----|----|
| 会话 id | `session-0fd161c7-e48a-4c7c-b837-c429c3c9e65b`（未变） |
| 工作区路径 | `C:\DeepseekProject\ARDF-MeshTuneFox80`（未变） |
| 投影缓存记录的 `cwd` | `C:\DeepseekProject\ARDF-MeshTuneFox80` → **与工作区一致，身份未失效** |
| 相对路径基准 | **容器目录**（`docs/…` 不再直接可用，见 3.3） |

### 3.3 ⚠️ 唯一的行为变化：相对路径基准

工作区内容重组后，**相对路径的基准变成了容器目录**：

| ❌ 现在会失败 | ✅ 正确写法 |
|--------------|-----------|
| `docs/02-repository-layout.md` | `ARDF-MeshTuneFox80-hardware/docs/02-repository-layout.md` |
| `README.md` | `ARDF-MeshTuneFox80-hardware/README.md` |
| `components/` | `ARDF-MeshTuneFox80-firmware/components/` |

`git` 命令同样要指明仓库：

```powershell
git -C ARDF-MeshTuneFox80-hardware status
git -C ARDF-MeshTuneFox80-firmware  status
```

### 3.4 仓库映射（已实测确认）

| 本地目录 | GitHub 仓库 | 可见性 | HEAD |
|---------|------------|--------|------|
| `ARDF-MeshTuneFox80-hardware` | https://github.com/PatrickShih774/ARDF-MeshTuneFox80 | public | `1852261` |
| `ARDF-MeshTuneFox80-firmware` | https://github.com/PatrickShih774/ARDF-MeshTuneFox80-firmware | private | `ef8fa54` |

其余设置：

| 项 | 结果 |
|----|------|
| 文件策略 `workspace-write` | ✅ **足够**——两个仓都在工作区内，不再需要 `danger-full-access` |
| DSH 项目根 | 容器无 `.git` → 回退为 cwd → 项目级技能目录 `<容器>/.dsh/skills` |
| 用户级技能 | `~/.dsh/skills/` 照常生效（含 `esp-idf`） |
| 相对路径基准 | 容器目录；`git` 命令要带上 `-C` 或先 `cd` 进子目录 |

> ❌ **不要**把工作区设成某个仓库的子目录——那样另一个仓又在工作区外了，问题原样复现。

### 3.5 会话开场白（建议直接用）

> 读 `ARDF-MeshTuneFox80-hardware/README.md`、`docs/02-repository-layout.md`、
> `docs/03-software-architecture.md`、`docs/15-dsh-esp-idf-integration.md`、
> `docs/16-local-workspace-setup.md` 和 `CHANGELOG.md`，然后继续。

---

## 4. 换会话的缓存代价（仅供参考——本次未发生）

> ✅ **本次未更换工作区路径，因此本章描述的代价一条都没有发生。**
> 工作区路径自始至终是 `C:\DeepseekProject\ARDF-MeshTuneFox80`，
> 变的只是它的内容（公开仓 → 容器）。详见第 3.1 节的对比表。
>
> 本章保留，用于说明**万一将来必须更换工作区路径**时的代价。

DSH 有**两层缓存，都与会话绑定，换工作区/换会话必然失效**：

| 层 | 键 | 影响 |
|----|----|------|
| LLM 前缀缓存（KV Cache） | 请求前缀的精确字节（含系统提示词里的 `cwd`） | 从变化点起的复用失效 |
| DSH 投影缓存 `session_projcache` | 会话 id + 生命周期身份 `{formatVersion, createdAt, cwd, isSeeded}`（**`cwd` 是身份字段**） | 不命中 |

**但损失是一次性的**：新会话第 1 轮把新前缀写入缓存，第 2 轮起照常命中。

**要保住缓存就不要换会话**，用：

```powershell
dsh --resume session-0fd161c7-e48a-4c7c-837b-c429c3c9e65b
```

代价是 `--resume` **不改工作区**（仍是旧路径），而旧路径在迁移后已不存在——**所以「迁移目录」与「保住缓存」不可兼得**。本次选择迁移，接受首轮冷启动。

> 完整分析见 [`15-dsh-esp-idf-integration.md`](15-dsh-esp-idf-integration.md) §7。

### 4.1 换会话不会丢的东西

| 内容 | 位置 |
|------|------|
| 旧会话记录 | `~/.dsh/sessions/<旧工作区slug>/`（保留，可按旧工作区切回） |
| 旧会话投影缓存 | `~/.dsh/storages/session_projcache/sessions/<会话id>.json`（保留） |
| 技能 | `~/.dsh/skills/`（与工作区无关） |
| 两个仓库的全部提交 | 本地 + GitHub，与工作区无关 |

**唯一会丢的是"本次对话的上下文"。** 因此关键结论必须已落盘——见第 6 节清单。

---

## 5. 日常操作

```powershell
# ---- 固件 ----
cd C:\DeepseekProject\ARDF-MeshTuneFox80\ARDF-MeshTuneFox80-firmware
idf.py set-target esp32c3      # 仅首次
idf.py build
idf.py -p COM5 flash monitor   # Ctrl+] 退出
git add -A; git commit -m "feat(atu): ..."; git push

# ---- 硬件 / 文档 / 验证 ----
cd C:\DeepseekProject\ARDF-MeshTuneFox80\ARDF-MeshTuneFox80-hardware
git add -A; git commit -m "docs: ..."; git push

# ---- 不动 cwd 的等价写法（agent 更常用）----
git -C <仓路径> status
git -C <仓路径> add -A
git -C <仓路径> commit -m "..."
git -C <仓路径> push
```

### 5.1 两个仓的分工

| 内容 | 仓 | 许可 |
|------|----|----|
| 原理图 / PCB / Gerber / BOM / 结构件 | hardware | `CERN-OHL-S-2.0` |
| 文档 / 验证报告 | hardware | `CC-BY-4.0` |
| 中控软件 / 共享协议 / 工具（规划中） | hardware | `Apache-2.0` |
| **固件源码** | **firmware（私有）** | `LicenseRef-ARDF-NC-1.0` |
| **固件二进制** | 发布到 **hardware 仓的 GitHub Releases** | `LicenseRef-ARDF-NC-1.0` |

### 5.2 发布固件（Release）

Release 发布在**公开仓**（`ARDF-MeshTuneFox80-hardware` 对应的 GitHub 仓库
`PatrickShih774/ARDF-MeshTuneFox80`），二进制由**私有仓**构建。

🔴 **发布时必须随附**：
- [`NOTICE`](../NOTICE)（ESP-IDF Apache-2.0、FreeRTOS MIT、mbedTLS Apache-2.0 等第三方声明）
- [`LICENSES/LicenseRef-ARDF-NC-1.0.txt`](../LICENSES/LicenseRef-ARDF-NC-1.0.txt)（固件许可全文）

**闭源 ≠ 可以省略第三方声明。**

---

## 6. 🔴 红线与已知陷阱

### 6.1 安全红线

| 红线 | 原因 |
|------|------|
| **固件源码的任何片段不得进入公开仓** | 包括 Issue 与 PR 描述、贴出的日志里的源码行 |
| 密钥（ESP-NOW / Mesh / 证书）不得入库 | 走 NVS 或本地文件 |
| 不要把私有仓放进公开仓目录内 | 会在某次 `git add -A` 时被一起提交。当前容器布局已从物理上避免 |

公开仓 `.gitignore` 已有防泄漏护栏（`software/firmware/`、`**/components/*/src/*.c`、
`main/app_main.c`、`sdkconfig.defaults`、`partitions.csv` 等），但那只是**兜底**。

### 6.2 已知陷阱

| 陷阱 | 症状 | 规避 |
|------|------|------|
| **`pwsh` 沙箱初始化失败** | `SetNamedSecurityInfoW failed (Win32 5)`，所有 shell 命令不可用 | 需用户提权或调整文件策略；**不要反复重试** |
| **`.NET` API 的相对路径基准是进程 CWD** | `Set-Location` 后 `[System.IO.File]::ReadAllText('a.txt')` 仍读旧目录 | .NET 调用一律用**绝对路径**；PowerShell cmdlet 才受 `Set-Location` 影响 |
| **`WriteAllLines` 写 CRLF** | 违反 `.editorconfig`（要求 LF） | 批量写文件用 `WriteAllText` + 显式 `` `n `` |
| **`.git/config` 被写入令牌** | `git push -u <含令牌URL>` 会把令牌存进 `branch.<name>.remote` | 推送用 `git push <url> main`，**不要加 `-u`**；事后检查 `git remote -v` |
| **`git ls-files --eol` 报 CRLF** | 工作区文件是 CRLF | 用 `WriteAllText` 转换；`LICENSES/CERN-OHL-S-2.0.txt` 的 CRLF 是**官方原样，不要转** |
| **`git rev-list --count main` 报 ambiguous** | 仓库里有 `main/` 目录，与分支名冲突 | 用 `git rev-list --count HEAD` 或加 `--` |
| **重新 `git clone` 后无法提交** | `Author identity unknown` —— clone 不会带上本地 `user.name`/`user.email`/`core.quotepath`/`i18n.*` | clone 后立即补：`git -C <仓> config --local user.name/user.email/…` |
| **`Move-Item` 失败后回滚删除了数据** | 目录的 `Move-Item` 可能**部分完成**；`Remove-Item -Recurse` 回滚会永久删除已搬移的文件 | 先**检查**目标而非删除；可靠退路是**搬移前先 push**，坏了就 `git clone` |
| **Kconfig 存在不存在的符号** | 首次构建出现 unknown config item 警告 | 权威清单是固件仓的 `sdkconfig.defaults`；已知错误名见 [`03`](03-software-architecture.md) §4.4 勘误表 |
| **ESP-IDF 未安装** | `IDF_PATH` 为空 | 见技能 `esp-idf` 第 1 节；**不要擅自下载安装** |

### 6.3 GitHub 侧的两个坑（已踩过）

| 坑 | 说明 |
|----|------|
| **`git push --force` 不能抹除旧提交** | 旧对象仍可通过直接 SHA 访问。要彻底清除必须**删除并重建仓库**（本项目已做过一次） |
| **推送 `.github/workflows/**` 需要 `workflow` scope** | 故 `.github/workflows/` 暂不入库 |

---

## 7. 当前状态快照（迁移后）

| 项 | 公开仓 | 私有仓 |
|----|--------|--------|
| 本地路径 | `…\ARDF-MeshTuneFox80\ARDF-MeshTuneFox80-hardware` | `…\ARDF-MeshTuneFox80\ARDF-MeshTuneFox80-firmware` |
| GitHub | `PatrickShih774/ARDF-MeshTuneFox80`（public） | `PatrickShih774/ARDF-MeshTuneFox80-firmware`（private） |
| HEAD | `83cc2f6` | `ef8fa54` |
| 提交数 | 6 | 2 |
| 文件数（ls-files / 文件系统） | 101 / 101 | 138 / 138 |
| 工作区 | clean | clean |

**固件仓状态**：ESP-IDF 工程骨架已建成（构建文件 + 28 个组件 `CMakeLists.txt` + 独立 `test/`），
但 **28 个组件均无实现**、`app_main()` 只打日志；**尚未实机验证过 `idf.py build`**（建立环境未装 ESP-IDF）。

---

## 8. 待办（换会话后从这里继续）

| # | 事项 | 优先级 |
|---|------|--------|
| 1 | **执行本地目录迁移**（见第 2 节） | 🔴 立即 |
| 2 | 新会话把工作区设为容器目录 | 🔴 立即 |
| 3 | 装 ESP-IDF v5.x，跑通 `idf.py set-target esp32c3 && idf.py build`，留意 Kconfig 未知项与 `factory` 分区余量 | 高 |
| 4 | 实现第一个组件（建议从 `utils_common` / `bsp_board` 起） | 高 |
| 5 | 做 **ESP-IDF MCP 服务器**（设计见 [`15`](15-dsh-esp-idf-integration.md) §5） | 中 |
| 6 | 首次固件 Release（须附 `NOTICE` + 许可全文） | 中 |
| 7 | `LicenseRef-ARDF-NC-1.0` 律师复核（**商业化前必须**） | 中 |
| 8 | 补齐 `docs/09` ~ `docs/14` | 低 |
| 9 | 🔴 **吊销 GitHub 令牌** `ghp_PTKu8…`（已多次明文出现） | 🔴 立即 |

---

## 9. 关联文档

| 文档 | 用途 |
|------|------|
| [`15-dsh-esp-idf-integration.md`](15-dsh-esp-idf-integration.md) | DSH 插件架构、ESP-IDF 集成方案、缓存与续用分析 |
| [`02-repository-layout.md`](02-repository-layout.md) | 仓库内文件归属（与本地布局是两回事） |
| [`03-software-architecture.md`](03-software-architecture.md) | 固件架构、分区表、任务表 |
| [`06-build-and-dev-environment.md`](06-build-and-dev-environment.md) | 构建与调试流程 |
| [`08-licensing-and-compliance.md`](08-licensing-and-compliance.md) | 分层授权与合规 |
| [`../CHANGELOG.md`](../CHANGELOG.md) | 全部变更与待办 |
| 技能 `esp-idf`（用户级） | `~/.dsh/skills/esp-idf/SKILL.md` —— 构建/烧录/调试的操作手册 |
