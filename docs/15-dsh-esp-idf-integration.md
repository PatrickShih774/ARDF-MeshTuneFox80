# 15 · 用 DSH 插件机制集成 ESP-IDF 开发与调试

> 状态：调研完成，技能已落地｜适用版本：DSH 0.1.7-rc.2
> 目标：把 ESP-IDF 的构建、烧录、监视、调试能力通过 **DSH 的插件/技能机制**集成进来，而不是每次靠临时拼命令行。

---

## 1. 结论先行

DSH 的扩展点有**四条**，成本从低到高：

| 路径 | 机制 | 成本 | 现状 |
|------|------|------|------|
| **① 技能（Skill）** | 磁盘上的 `SKILL.md`，被自动发现并热重载 | 极低（纯 Markdown） | ✅ **已落地** |
| **② MCP 服务器** | `dsh-mcp-client` 连接 MCP server，把其工具注册到 `ctx.tools` | 中（写一个 MCP server） | ⬜ 待做（**推荐下一步**） |
| **③ 工具插件** | 写一个 cordis 插件包，直接注册工具 | 高（要发 npm 包） | ⬜ 暂不做 |
| **④ 钩子（Hooks）** | `dsh-hooks-claude-code` / `dsh-hooks-codex` 风格的自动化钩子 | 中 | ⬜ 待评估 |

**推荐路线：① 技能（已完成）→ ② MCP 服务器**。理由见第 5 节。

---

## 2. DSH 插件架构（本机实测）

| 项 | 实测值 |
|----|--------|
| 版本 | `0.1.7-rc.2` |
| 插件框架 | **cordis 4.0.4**（`@deepseek-ai/cordis`） |
| 插件包数量 | **284 个** `@deepseek-ai/dsh-*` 包 |
| 包位置 | `<安装目录>/resources/app.asar` → `dsh/node_modules/@deepseek-ai/` |
| Node / pnpm | Node 24.18.1 / pnpm 11.7.0 |

### 2.1 Profile 与补丁层

DSH 用 **profile** 组织插件树。本机 profile 在 `~/.dsh/profiles/desktop/`：

```
profiles/desktop/
├── package.json          # 声明 dsh.profile.bundles: dsh-base, dsh-web-app
├── cordis.yml            # 空数组；树由补丁层组合而成
├── cordis.patch.yml      # ★ 用户补丁层：改这里
└── pnpm-workspace.yaml
```

`cordis.patch.yml` 是**顶层 YAML 数组**，每一项是一个 loader patch：

```yaml
- id: agent-default-model
  name: "@deepseek-ai/dsh-agent-default-model"
  config:
    provider: deepseek-account
    model: deepseek-flash
```

即：**给 `name` 加一行就能挂载一个插件，`config` 传参**。

### 2.2 工具即插件

**DSH 的每个内置工具都是一个独立插件包**：

```
dsh-tool-pwsh   dsh-tool-fs      dsh-tool-fs-search   dsh-tool-web
dsh-tool-todo   dsh-tool-jobs    dsh-tool-present     dsh-tool-skill
dsh-tool-subagent  dsh-tool-workflow  dsh-tool-ask-user  …
```

这意味着"给 agent 加一个 `idf_build` 工具"在架构上是一等公民，不是 hack。

### 2.3 技能发现规则（已实测）

| Rank | 来源 | 路径 |
|------|------|------|
| 100 | `project-dsh` | `<项目根>/.dsh/skills` |
| 200 | `project-agents` | `<项目根>/.agents/skills` |
| 300 | `custom` | 配置 `customSkillDirs` |
| 400 | **`user-dsh`** | **`~/.dsh/skills`** |
| 500 | `user-agents` | `~/.agents/skills` |

- **格式**：`<根>/<名称>/SKILL.md`（目录 bundle）或 `<根>/<名称>.md`（平铺）。**发现深度只有一层**，不支持嵌套。
- **frontmatter**：必填 `name`（kebab-case）+ `description`；可选 `whenToUse`、`metadata`、`disable-model-invocation`、`user-invocable`。
- **项目根** = 最近的含 `.git` 的祖先目录；没有则用当前 cwd。
- **热重载**：根目录被监视，新增/改名/删除/改 frontmatter 在**下一个模型步骤**生效，**无需重启**。（本文件所描述的技能就是这么加进去的，加完立刻出现在技能目录中。）

---

## 3. 已落地：`esp-idf` 技能

安装在**用户级**根 `~/.dsh/skills/esp-idf/SKILL.md`，因此**与工作区无关、切会话不丢**。

它覆盖：

| 章节 | 内容 |
|------|------|
| 环境 | 先查 `IDF_PATH`；未安装时给出安装命令而**不擅自下载**；离线包位置提示 |
| 构建 | `set-target` / `build` / `fullclean` / `size-components`；**本项目工程结构要点**（28 组件、接口组件无 `SRCS`、自定义分区表、独立 `test/` 工程） |
| 已知的坑 | 一张症状→原因→处理表（未激活 export、Kconfig 未知项、换 target 未清理…） |
| 烧录监视 | 串口枚举、`flash monitor`、原生 USB vs USB-UART 桥、烧录失败排查 |
| **调试** | 日志分级约定、**Core Dump**（配置项 + `coredump-info`/`coredump-debug`）、**OpenOCD/GDB**（ESP32-C3 内置 USB-JTAG，与 CDC 共用同一物理口） |
| 工作流 | 两仓分工、发布流程、`validation/` 与 `test/` 的区别 |
| 🔴 安全红线 | 固件源码片段不得进公开仓 |
| 沙箱限制 | `pwsh` 沙箱失败与 `workspace-write` 的越界写入问题 |

**验证方法**：新会话里说"用 esp-idf 技能构建固件"，agent 应当自动加载它。

---

## 4. 为什么把技能放在用户级而不是项目级

| 位置 | 优点 | 缺点 |
|------|------|------|
| `~/.dsh/skills/`（**已采用**） | 与工作区无关；两仓都能用；切会话不丢 | 不进版本控制，换机器要重装 |
| `<项目根>/.dsh/skills/` | 随仓库分发，团队共享 | **项目根取决于工作区**：工作区设为 `C:\DeepseekProject` 时 `.dsh/skills` 会落在两仓**之外**；设为某个仓时才落进那个仓 |
| `~/.agents/skills/` | 兼容其他 agent 工具 | rank 最低 |

> **后续可做**：把技能副本放进固件仓（私有）的 `.dsh/skills/`，这样它随固件源码一起版本化；用户级那份保留为通用兜底。两处同名时按 rank 由项目级优先。

---

## 5. 下一步：MCP 服务器（推荐）

### 5.1 为什么是 MCP 而不是工具插件

| | MCP 服务器 | 工具插件（cordis 包） |
|---|---|---|
| 依赖 | 只需 `dsh-mcp-client` 已在发行版中 | 要写 cordis 插件、发 npm 包 |
| 语言 | 任意（Python / Node / Go / Rust） | 必须是 Node ESM，且遵循 DSH 的 `ctx.tools` API |
| 升级 | 独立进程，改完重启进程即可 | 随 DSH 版本走，要考虑 `peerDependencies` |
| 复用 | **Claude Desktop / Cursor / 其他 MCP 宿主都能用** | 只能用于 DSH |
| 调试 | 独立进程，可直接跑、直接打日志 | 在宿主进程内，调试更绕 |

`dsh-mcp-client` 的自述是：*"MCP client bridge: connects to MCP servers and registers their tools on `ctx.tools`"* —— 也就是 **MCP 工具与原生工具在 agent 眼里没有区别**。

**结论：用 MCP 服务器实现 ESP-IDF 工具集，性价比最高。**

### 5.2 建议暴露的工具集

| 工具 | 作用 | 关键点 |
|------|------|--------|
| `esp_env_status` | 报 `IDF_PATH`、`idf.py --version`、可用串口、OpenOCD 是否存在 | **只读、快速**，让 agent 先自检再决定 |
| `esp_build` | 封装 `idf.py build`，返回**结构化的诊断** | 把 GCC 错误/警告解析成 `{file,line,col,severity,message}`，而不是丢一整坨日志——这是提升调试效率的关键 |
| `esp_size` | `idf.py size` / `size-components` → 分区余量与组件体积 | 结构化输出，便于判断 `factory` 分区是否够用 |
| `esp_flash` | `idf.py -p <port> flash` | 需人工确认（会改硬件状态） |
| `esp_monitor_capture` | 采集串口 N 秒 → 返回日志 | **比让 agent 开交互式 monitor 更合适**：无 TTY、有超时、可返回结构化日志 |
| `esp_coredump` | `idf.py coredump-info` → 解析任务与栈回溯 | 崩溃调试闭环 |
| `esp_serial_ports` | 枚举串口 + 识别芯片型号 | 免去猜 COM 号 |
| `esp_openocd_gdb` | 起 OpenOCD + 执行一批 GDB 命令 | 高危，需确认 |

**设计原则**：
1. **先只读后写入** —— `esp_env_status` / `esp_size` / `esp_serial_ports` 无副作用，可自由调用。
2. **输出结构化** —— 编译错误、体积、崩溃栈都要变成结构化数据。agent 消化一坨原始日志的效率远低于消化 JSON。
3. **超时与取消** —— 构建可能几分钟；监控进程要有超时，且能被取消。
4. **不要开交互式 TTY** —— `idf.py monitor` 是交互式的，在非交互沙箱里会出问题（本项目实测过 GCM 因 `/dev/tty` 不存在而失败）。用"采集 N 秒"替代。

### 5.3 建议实现位置

放在**固件仓**（私有）的 `tools/mcp-esp-idf/`，理由：
- 它只对固件开发有意义，涉及固件内部细节（分区、组件、调试）
- 与固件源码一起版本化，改工具与改固件同一个提交
- 不与公开仓的 `Apache-2.0` 工具混在一起

配置则写在**用户或 profile 层**（`cordis.patch.yml`），因为它依赖本机的 ESP-IDF 与串口。

### 5.4 验收标准

1. 新会话里说"构建固件"，agent 调用 `esp_env_status` 先确认环境，再调 `esp_build`。
2. 故意引入一个语法错误，agent 能拿到**结构化**的 `{file,line,message}` 并直接定位修复。
3. 把板子插上，agent 能自己找到串口并采一段日志。
4. 触发一次 panic，agent 能解出崩溃任务与栈回溯。

---

## 6. 切换工作区前必须知道的事

### 6.1 技能不受影响

`esp-idf` 技能装在 `~/.dsh/skills/`（rank 400），**与工作区无关**，换工作区、换会话都还在。

### 6.2 但会话上下文不会跟着走

换工作区 = **新会话** = agent **不记得**本次对话。所有关键结论必须已经落到文件里——本文档、`CHANGELOG.md`、各 README 与 ADR 就是为此。

### 6.3 建议的工作区

| 目标 | 工作区设为 | 说明 |
|------|-----------|------|
| 同时改固件 + 文档 + 硬件 | **`C:\DeepseekProject`** | 两仓都在工作区内，不依赖 `danger-full-access` |
| 只写固件 | `C:\DeepseekProject\ARDF-MeshTuneFox80-firmware` | 最干净，且天然挡住公开仓 |

> ⚠️ 若工作区设为 `C:\DeepseekProject`，注意该目录**没有 `.git`**，因此 DSH 的项目根会回退为 cwd，项目级技能目录是 `C:\DeepseekProject\.dsh\skills`（在两仓之外）。这对"用户级技能"没有影响。

### 6.4 数据不丢

| 内容 | 位置 | 换会话后 |
|------|------|---------|
| 会话记录 | `~/.dsh/sessions/<工作区slug>/` | 保留，可按工作区切回 |
| 会话投影缓存 | `~/.dsh/storages/session_projcache/sessions/<会话id>.json` | 保留，按会话 id 隔离 |
| 技能 | `~/.dsh/skills/` | 保留 |

---

## 7. 缓存与会话续用：换工作区的真实代价

DSH 有**两层**缓存，都与会话绑定，**换工作区必然使两者失效**。

### 7.1 两层缓存

| 层 | 载体 | 键 | 换工作区的影响 |
|----|------|----|--------------|
| **LLM 前缀缓存（KV Cache）** | 模型服务方 | **请求前缀的精确字节**（含系统提示词里的 `cwd`、工具定义） | ❌ `cwd` 变了 → 从变化点起的复用失效 |
| **DSH 投影缓存** | `~/.dsh/storages/session_projcache/sessions/<会话id>.json` | 会话 id + **生命周期身份 `{formatVersion, createdAt, cwd, isSeeded}`** | ❌ `cwd` 是身份的一部分 → 不命中 |

投影缓存的官方说明明确把 **`cwd` 列为生命周期身份字段**，因此这不是猜测：`cwd` 一变，该会话的检查点就与新的身份不匹配。

### 7.2 但"损失"是一次性的

前缀缓存是**位置性**的：变化点之后的全部失效，但**新会话第 1 轮会把新前缀写入缓存，第 2 轮起照常命中**。

所以换工作区的真实代价 ≈ **新会话首轮的一次全量缓存写入**，不是"以后每轮都贵"。

### 7.3 想保住缓存就别换会话

DSH 支持**续用同一会话**：

```powershell
dsh --resume <会话id>
```

`--resume` 是本会话（`DSH_SESSION_ID`）的公开 CLI 参数；续用会让 `cwd`、工具定义、投影身份**全部保持不变**，因此两层缓存都继续命中。

> ⚠️ **代价**：`--resume` **不会改变工作区**。固件仓若在工作区外，就仍然依赖文件策略（`danger-full-access`）才能写入，而那是**会话级的临时状态**，下次不一定有。

### 7.4 四选一的决策表

| 做法 | KV 前缀缓存 | 投影缓存 | 两仓可写 | 会话记忆 |
|------|-----------|---------|---------|---------|
| **留在本会话**（不换工作区） | ✅ 全程命中 | ✅ 同会话 | ✅ 靠临时策略 | ✅ 保留 |
| **`dsh --resume <本会话id>`** | ✅ 继续命中 | ✅ 同会话 | ✅ 同上 | ✅ 保留 |
| 新会话 + 工作区 `C:\DeepseekProject` | ⚠️ 首轮全量重写，之后命中 | ❌ 新建 | ✅ 不依赖策略 | ❌ 全新 |
| 新会话 + 工作区＝固件仓 | ⚠️ 同上 | ❌ 新建 | ❌ 公开仓在工作区外 | ❌ 全新 |

**结论**：

- **最在意缓存** → 不要换工作区，用 `--resume` 续用本会话；接受"依赖 `danger-full-access`"这一代价。
- **最在意长期稳定** → 换到 `C:\DeepseekProject` 开新会话，接受首轮冷启动；用仓库里的文档（本文、`CHANGELOG.md`、各 README）重建上下文。
- **两者不可兼得** —— 工作区是会话属性，改工作区就等于换了一把缓存钥匙。

### 7.5 换会话时的"上下文交接"清单

为了让新会话第一轮就能自助重建上下文，下面这些**必须已经在文件里**（本轮已完成）：

| 内容 | 位置 |
|------|------|
| DSH 插件架构与 ESP-IDF 集成方案 | 本文档 |
| 双仓结构与固件闭源决策 | `docs/adr/ADR-0007-*.md`、`LICENSING.md` |
| 目录归属与文件放哪里 | `docs/02-repository-layout.md` |
| 软件架构、分区表、任务表 | `docs/03-software-architecture.md` |
| 构建/调试流程与已知的坑 | `docs/06-build-and-dev-environment.md`、用户级技能 `esp-idf` |
| 本轮全部变更与待办 | `CHANGELOG.md` |

> 新会话的开场白建议：
> 「读 `ARDF-MeshTuneFox80/README.md`、`docs/02`、`docs/03`、`docs/15` 和 `CHANGELOG.md`，然后继续。」

---

## 8. 调试策略与能力边界（决策记录）

> 本章是对"能否在 DSH 里复现 VSCode 的 ESP-IDF 扩展"这个问题的**正式结论**。

### 8.1 实测：DSH 没有 IDE 的三块地基

在 DSH 的 284 个插件包中按关键词检索，结果全部为零：

| 关键词 | 命中 | 含义 |
|--------|------|------|
| `lsp` / `language-server` | **0** | 无语言服务客户端 → 无补全、跳转、悬停 |
| `dap` / `debug` / `breakpoint` | **0** | 无调试适配器客户端 → 无断点、单步、变量窗口 |
| `monaco` / `webview` / `chart` | **0** | 无编辑器与可视化渲染宿主 |

DSH 有 **52 个 `dsh-client-ui-*`** 包（GUI 是可插拔的），但**本机没有 DSH 源码 checkout**
（系统提示中的路径不存在；`Documents\deepseek-harness` 只是默认工作区空目录），
客户端插件要靠 `pnpm run dev:web` 构建，**没有源码即无从构建**。

### 8.2 结论：**补全与跳转不需要；断点调试用串口替代**

| VSCode ESP-IDF 扩展的能力 | DSH | 说明 |
|---|---|---|
| 安装向导 / 工具链配置 | ✅ | 技能 + `esp_env_status` |
| 构建 | ✅ | `esp_build`，**输出结构化诊断** |
| 烧录 | ✅ | `esp_flash` |
| 串口监视 | ✅ | `esp_monitor_capture`（**不开交互式 TTY**） |
| Core Dump 解码 | ✅ | `esp_coredump` |
| 体积分析（数值） | ✅ | `esp_size` |
| 单元测试 | ✅ | 包装 `pytest-embedded`，返回结构化结果 |
| 组件管理器 | ✅ | 包装 CLI |
| menuconfig | 🟡 | 无 TUI 宿主；**改为让 agent 直接编辑 `sdkconfig.defaults`**，更高效 |
| 体积/内存图表 | 🟡 | 只能到数值（无 chart/webview） |
| **代码补全、跳转、悬停** | ❌ | **不需要**——AI 直接读文件；编译错误已带 `file:line:col`；找引用 `grep` 足够 |
| **断点、单步、看寄存器/变量** | ❌ | **用串口日志 + Core Dump 替代**（见 8.3） |

**核心判断**：本项目**不需要** VSCode 配合。DSH 一侧即可闭环。

### 8.3 为什么串口调试足以替代断点调试

对本项目而言这不是权宜之计，而是**结构性更合适**：

- 编码规范本就规定日志分级，以日志为主要观测手段；
- `validation/` 的十阶段验证是**硬件在环 + 仪器实测**，不是单步调试；
- CW 键控（软起软降 2–5 ms）与发射窗口（误差 <0.1 s）对实时性敏感，
  **断点会直接破坏被测时序**，调试手段本身成为干扰源。

但有三处 printf 顶不住，需提前准备替代手段：

| 边界 | 为什么 printf 不行 | 替代手段 |
|------|------------------|---------|
| **中断上下文（ISR）** | 本项目编码规范**明令禁止**在 ISR 里打日志（`ESP_LOGI` 会加锁） | GPIO 翻转打点 + 逻辑分析仪；或写**无锁环形缓冲**，在主循环里吐出 |
| **µs 级时序** | printf 本身阻塞，会把被测时序改掉 | **GPIO 打点 + 示波器**（`validation/` 方案里已有示波器） |
| **偶发/难复现崩溃** | 复现不了就抓不到 | **Core Dump**：reset 后解出崩溃任务与栈回溯 |

**补充手段**：ESP-IDF 的 **App Tracing（`esp_apptrace`）** 走 **JTAG 非阻塞**输出日志，
不占 UART、对实时性影响远小于 printf——适合"既要看日志又不能扰动时序"的场景，**且不需要 GUI**。

### 8.4 由此对 MCP 工具集的加强要求

既然调试全靠这条线，工具集必须往这个方向收紧（已下发实现要求）：

| 工具 | 加强点 |
|------|--------|
| `esp_monitor_capture` | **触发式捕获**（等关键字出现再计时；带触发超时与行数上限）；返回 `{triggered, trigger_line, elapsed_s, lines, entries, truncated}` |
| （日志解析） | **结构化日志纯函数解析器**：`I (1234) app_main: msg` → `{level, tick_ms, tag, message, raw}`；支持 `min_level` 过滤。agent 应按 `level`/`tag` 过滤，而非读裸文本 |
| `esp_coredump` | 栈回溯地址用 **`riscv32-esp-elf-addr2line` 反查 `file:line`**；工具链不可用时优雅降级 |
| `esp_env_status` | 扩充探测：`openocd`、`addr2line`、App Tracing 可用性 |

### 8.5 明确不做

- ❌ 不为 DAP / 断点 / 单步 / 变量窗口 / 代码补全做任何设计（无宿主能力，且本项目不需要）
- ❌ 不引入 GUI、图表、webview 相关依赖
- ❌ 不设计"交互式调试会话"

---
## 9. 参考

| 资料 | 说明 |
|------|------|
| `@deepseek-ai/dsh-skill-filesystem` README（中文） | 技能发现根目录、格式、监视与热重载 |
| `@deepseek-ai/dsh-mcp-client` README（中文） | MCP 客户端桥接与 `ctx.tools` 注册 |
| `@deepseek-ai/dsh-plugin-manager`、`dsh-client-ui-settings-plugins` | 插件管理与 UI |
| `@deepseek-ai/dsh-tool-todo` README（中文） | 一个完整工具插件的参考实现 |
| 相关文档 | [`06-build-and-dev-environment.md`](06-build-and-dev-environment.md)、[`07-coding-standards.md`](07-coding-standards.md) |
| 关联 ADR | [ADR-0001](adr/ADR-0001-adopt-esp-idf-over-arduino.md)（选 ESP-IDF 而非 Arduino）、[ADR-0007](adr/ADR-0007-firmware-closed-source-two-repo.md)（双仓结构） |

> DSH 自带文档可从 `<安装目录>/resources/app.asar` 中提取：asar 头为
> `[u32=4][u32][u32=jsonLen][u32][JSON 索引]`，文件数据紧随其后；按索引里的 `offset`/`size`
> 加上 `16 + jsonLen` 即可取出任意文件。各插件包均带 `README.zh.md`。

---

## 10. MCP 接入实录：三个把集成卡住的坑（2026-09-26 已解决）

`tools/mcp-esp-idf/` 的工具**已成功接入 DSH**（`mcp__espidf__*` 共 8 个）。
过程中踩到三个坑，全部记录如下以免重犯。

### 10.1 🔴 新增插件行**必须**包在 `- insert:` 里

**症状**：`cordis.patch.yml` 里按文档写了一条 `- id: mcp-espidf / name: ... / config: ...`，
harness 重启后**工具完全不出现，且没有任何报错**（连 `failOnStartupError: true` 都不触发）。

**根因**：`cordis.patch.yml` 的顶层「行形状」条目（`- id` / `name` / `config`）语义是
**按 id 覆盖已有行**。`dsh-base` 的插件树（91 行，见
`<安装目录>/resources/app.asar` → `dsh/node_modules/@deepseek-ai/dsh-base/cordis.patch.yml`）
里**没有 mcp-client 这一行**，所以裸写会被当作"找不到目标的覆盖"而**静默丢弃**。
失败发生在**补丁应用阶段**，根本到不了连接阶段，因此 `failOnStartupError` 无从触发。

**正确写法**（与 `dsh-base/cordis.patch.yml` 的样板一致）：

```yaml
- insert:                       # ← 新增行必须在 insert 列表里
    - id: mcp-espidf
      name: '@deepseek-ai/dsh-mcp-client'
      config: { ... }
```

**判别方法**：若你的条目在 dsh-base 的行 id 列表里 → 顶层覆盖写法正确；
若是**新 id** → 必须用 `insert`。

### 10.2 🔴 MCP 进程**不继承**你 export 过的 shell

**症状**：工具出现了，但 `esp_env_status` 返回 `environment="missing"`、
`missing: ["IDF_PATH","idf.py"]`。

**根因**：DSH 拉起的 MCP 服务器是**独立进程**，环境是"清洗过的"，
不会继承你手动执行 `export.ps1` 的那个 shell。

**处置**：用**包装脚本**启动 —— 先在本进程内激活 ESP-IDF，再把同一进程交给 `server.py`：
私有仓 `tools/mcp-esp-idf/launch-with-idf.ps1`。

```yaml
command: 'powershell.exe'
args: ['-NoProfile','-ExecutionPolicy','Bypass','-File','<...>/launch-with-idf.ps1']
```

**包装脚本的两个必须点**：

| 点 | 原因 |
|---|------|
| **`export.ps1` 的输出全部丢弃**（`*> $null`） | MCP 的 stdio 传输把 **stdout 当 JSON-RPC 通道**，任何多余输出都会破坏握手 |
| **`$ErrorActionPreference` 不能是 `Stop`** | `export.ps1` 内部调用 python，其 stderr 被包成 ErrorRecord；在 `Stop` 下会变成**终止性错误**，激活中断、`IDF_PATH` 根本没设上 |

### 10.3 ⚠️ Windows 下 PowerShell 脚本必须存为 **UTF-8 带 BOM**

含中文注释的 `.ps1` 若存为**无 BOM 的 UTF-8**，Windows PowerShell 5.1 会按 ANSI 解码，
中文变乱码并**导致语法错误**（实测：字符串被吃掉 → `Missing '=' operator in hash literal`）。

本项目受影响的脚本：`scripts/check-repo-separation.ps1`、
`tools/mcp-esp-idf/launch-with-idf.ps1`。

### 10.4 排查方法论

这次没有靠猜，每一步排除一个假设：

| 假设 | 验证方式 | 结论 |
|------|---------|------|
| 配置语法错 | 比对官方文档示例 | ❌ 逐字段一致 |
| 服务器有问题 | 手工拉起，看 `initialize` 响应 | ❌ 8 工具正常 |
| 环境被清洗 | 用最小环境变量集复现 | ❌ 也正常 |
| 包未安装 | GUI「添加插件」 | ❌ 提示**已安装** |
| 进程未创建 | 查进程列表 | ✅ 排除连接阶段 |
| **补丁语义错** | **读 dsh-base 样板 + 比对 id 列表** | ✅ **根因** |

**教训**：当"照文档做却不生效且毫无报错"时，去读**发行版内部的实际样板文件**
（`app.asar` 里的 `cordis.patch.yml`），比反复猜文档措辞有效得多。
