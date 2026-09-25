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

## 7. 参考

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
