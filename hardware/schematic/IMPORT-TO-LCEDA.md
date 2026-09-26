# 把本目录的 KiCad 原理图导入立创EDA专业版 —— 操作指引

> 面向：**先盲目生成、再手工细修**的用法。
> 生成器：[`scripts/build-kicad-schematic.py`](../../scripts/build-kicad-schematic.py)
> 自检器：[`scripts/check-kicad-schematic.py`](../../scripts/check-kicad-schematic.py)
> 决策记录：[`KIcad-skeleton-decision.md`](KIcad-skeleton-decision.md)

---

## 1. 文件在哪

8 份**互相独立**的 KiCad 6 原理图（`(version 20211123)`），每份都能单独打开；
**不做层次化**（没有 `sheet` 子页），跨模块网络靠 `global_label` 连起来。

| 文件 | 行数 | 字节 | 器件数 | 图幅 |
|---|---|---|---|---|
| [`atu-module.kicad_sch`](atu-module.kicad_sch) | 1716 | 63325 | 29 | A3 |
| [`pa-module.kicad_sch`](pa-module.kicad_sch) | 953 | 35498 | 14 | A3 |
| [`lpf-module.kicad_sch`](lpf-module.kicad_sch) | 256 | 9035 | 6 | A4 |
| [`mcu-ui.kicad_sch`](mcu-ui.kicad_sch) | 1968 | 76143 | 25 | A3 |
| [`power-module.kicad_sch`](power-module.kicad_sch) | 626 | 22751 | 9 | A4 |
| [`core-board.kicad_sch`](core-board.kicad_sch) | 656 | 24344 | 18 | A4 |
| [`interconnect.kicad_sch`](interconnect.kicad_sch) | 222 | 8022 | 6 | A4 |
| [`antenna.kicad_sch`](antenna.kicad_sch) | 179 | 6346 | 2 | A4 |

配套的机器可读文件（不要手改，重跑脚本会覆盖）：

| 文件 | 用途 |
|---|---|
| [`kicad-net-map.csv`](kicad-net-map.csv) | 212 行 `sheet,ref,pin_number,pin_name,net_label,label_kind` —— 图里**真实存在**的每个「引脚 ↔ 网络」 |
| [`kicad-row-coverage.csv`](kicad-row-coverage.csv) | 181 行 `row,net,net_label,src,dst,status,pins,detail` —— `netlist.csv` 的每一行落在哪、状态是 `DRAWN`/`PARTIAL`/`NOTE`、这一行实际挂到了哪些 `位号.引脚号`（`pins` 列，共 278 处）、以及没能照抄的原因 |
| [`kicad-build-report.md`](kicad-build-report.md) | 人看的报告：文件表、覆盖统计、逐网络落点、符号库、未冻结引脚号、**所有不能照抄的行**、别名表、Value 来源 |
| [`tests/`](tests/) | 自检器的对照组：1 份手写最小合法文件 + 5 份故意写坏的文件 |

**图里有什么**：每个器件一个符号（矩形本体 + 引脚 + 位号 + 值），**所有符号定义都内嵌在文件自己的
`lib_symbols` 段里**（库名统一是 `ARDF:*`），所以打开时**不查任何外部库**。
**图里没有导线**：每个引脚上直接挂一个网络标签（KiCad/立创EDA 都认这种画法）。
`netlist.csv` 的 181 行里：**162 行**两端都按原文落到了图上；**16 行**只落了一端或落到了另一个网络
（每行都写明了原因，见 [`kicad-row-coverage.csv`](kicad-row-coverage.csv) 的 `status`/`detail` 列）；
**3 行**是「没有器件引脚」的板级说明（星形地 2 行 + CW 键控 1 行），以图面文字注释形式保留。
**没有任何一行被悄悄丢掉**——181 行全部有去处，`attached=278` 个「引脚上挂了标签」的位置经自检器
逐个回查过确实存在于文件里。

---

## 2. 立创EDA 导入步骤

### 2.1 先分清两条路（🔴 走错会直接失败）

| 路线 | 吃哪个版本的 KiCad | 依据 |
|---|---|---|
| 立创EDA专业版**应用内**「文件 → 导入 → KiCad」 | **只吃 KiCad 5.1 / 5.9** 的 legacy `.sch` | <https://prodocs.lceda.cn/cn/import-export/import-kicad/index.html> |
| 立创EDA **格式转换助手**（迁移助手，独立工具） | **KiCad 5.x 与 6+**：`.sch` / `.kicad_sch` / `.kicad_pcb` / `.kicad_sym` / `.kicad_mod` / `.kicad_pro` / `.lib` | <https://prodocs.lceda.cn/cn/import-export/easyeda-pro-format-converter/index.html> |

> **本目录给的是 `.kicad_sch`（KiCad 6 s-expression），所以必须走「格式转换助手」，不要用应用内导入。**
>
> ⚠️ 说明：本次会话只能重新取到这两页的标题与导航（正文在返回内容里被截断了），
> 上面两条版本能力是**沿用本仓 [`KIcad-skeleton-decision.md`](KIcad-skeleton-decision.md) 前一轮调研时记录的原文摘录**
> （原文：「嘉立创EDA专业版支持导入 KiCad 5.1 和 KiCad 5.9 版本的格式文件。」
> 以及迁移助手页的 ASCII/非 ASCII 说明）。若你本地界面与上表不符，请以你打开的那个页面为准。

### 2.2 操作顺序

1. 打开立创EDA专业版 → 进入**格式转换助手**（入口在官方文档 §2.1 那一页给出的地址上；菜单名随版本变动，
   以你本地看到的「格式转换助手 / 迁移助手 / Format Converter」为准）。
2. 源格式选 **KiCad**；把上面 8 个 `.kicad_sch` **一个一个**加进去（也可以一次性全加）。
3. 开始转换 → 转换完成后把结果**导入到一个新建工程**里；
   8 份图会变成同一个工程里的 8 个图页，跨页网络是 `global_label`，仍能连上。
4. 打开后**第一件事是点开「网络」面板**（左侧），确认网络数量是 **73** 个（= 有引脚的规范网络数），
   再对照 [`kicad-net-map.csv`](kicad-net-map.csv) 抽查 5~10 个网络。
   > 为什么先看这个：转换器最容易悄悄丢的是**网络标签**，而丢标签在图上「看起来一切正常」。
5. 然后按 §4 的清单细修。

### 2.3 立创EDA 里的一个便利点

本目录的 `.kicad_sch` 是**纯 ASCII**（已用字节扫描验证 `>127` 的字节数 = 0）。
迁移助手页有一条限制：**非 ASCII 的第三方文档需要你本机装对应的 EDA 软件才能转**。
纯 ASCII ⇒ 这一条大概率不会挡你（官方没明文承诺「KiCad 无需装 KiCad」，所以只能算**倾向**，不是保证）。

---

## 3. 🔴 已知可能失败点 —— 报什么错，就改这里

> 用法：先在下面找到**你看到的报错/现象**，按「改这里」做。每一行都给了**可执行的下一步**。

### F1 转换器说版本不接受 / 文件无法识别
- 现象：`unsupported version`、`无法识别文件版本`、直接不让你选文件。
- 原因：文件头是 `(kicad_sch (version 20211123) (generator eeschema)`，这是 **KiCad 6.0** 的格式号。
- 改这里：
  1. 确认走的是**格式转换助手**而不是应用内导入（见 §2.1）。
  2. 转换器里若有「KiCad 版本」下拉，选 **6 / 6.0 / 6+**。
  3. 仍不接受：把 `(version 20211123)` 里的数字改成转换器提示的那个（脚本里是
     `scripts/build-kicad-schematic.py` 的 `FILE_VERSION` 常量，改完重跑即可）——
     **只改数字不要改语法**，6/7/8 的 `.kicad_sch` 语法在本文件用到的子集里是兼容的。

### F2 符号（`ARDF:*`）转换异常 / 满屏问号 / 图形丢失
- 现象：器件只有框、引脚名乱、或提示找不到 `ARDF:Resistor` 之类。
- 原因：这些符号是**文件内自定义**的（`lib_symbols` 里 `ARDF:R`、`ARDF:ULN2003A` …），
  立创EDA 的库里当然没有同名器件——**这是设计如此**，不是文件坏。
- 改这里：
  1. **先看网络面板**。判断标准是**网络对不对**，不是图形漂不漂亮：图形可以重画，网络丢了要重来。
  2. 图形不对的器件，在立创EDA 里用「器件标准化 / 更新工程库」把它替换成 LCSC 的正式器件；
     替换时**按引脚名（不是引脚号）对应**——引脚名就是 [`netlist.csv`](netlist.csv) 里的真实信号名。
  3. 也可以用 [`kicad-symbol-map.csv`](kicad-symbol-map.csv) 第 2 列的建议符号名，在立创EDA 里搜等价器件。

### F3 网络标签丢了（所有网络都变成各自独立的小网络）
- 现象：网络面板里只有一堆 `NetJ_ANT_1`、`NetU8_3` 这种自动名，看不到 `PA_GATE`、`ATU_L1_LO`。
- 原因：转换器可能只吃 `global_label`，把局部 `label` 丢了（本目录默认**模块内用 `label`，跨模块用 `global_label`**）。
- 改这里（一行命令，已内置）：
  ```powershell
  cd <仓库根>\ARDF-MeshTuneFox80-hardware
  python scripts\build-kicad-schematic.py --all-global
  ```
  这会把**所有**网络都写成 `global_label`，然后重新导入。改完想回到默认模式就再跑一次不带参数的：
  ```powershell
  python scripts\build-kicad-schematic.py
  ```
  两种模式都能过自检（`python scripts\check-kicad-schematic.py`）。

### F4 本来该连的网络没连上（网络数不是 73）
- 现象：网络名对，但数量偏多（说明有标签没落到引脚上）。
- 原因：转换器把标签的坐标做了取整，或者把标签与引脚「贴在一起」判定失败。
- 改这里：
  1. 在图上把明显的飞线用**短线**连一下（本目录刻意没有画任何导线，就是为了让你自己控制）。
  2. 对照 [`kicad-net-map.csv`](kicad-net-map.csv)：它逐行写了「哪个位号的哪个引脚应该在哪条网络上」，
     这是唯一权威的核对表。用立创EDA 的「查找相似对象 / 网络高亮」逐个核。

### F5 引脚号不是数字，报「引脚号非法」/ 封装焊盘对不上
- 现象：`COM`、`NO`、`NC`、`COIL+`、`CENTER`、`GPIO4`、`VDD/VDDIO` 被当成引脚号。
- 原因（**故意的**，且是对的）：这几类器件的**物理脚号在文档里明确没冻结**，见
  [`hardware/atu-module/relay-wiring.md`](../atu-module/relay-wiring.md) §2.5
  （原文要求「**待来料核实（不得凭猜画图）**」）、`mcu-ui-module/README.md`（LCD 排线待确认）、
  `pre-fab-checklist` C-09（J1–J6 排针定义待定）。所以脚本**不发明物理脚号**，
  直接用**功能名/信号名**当引脚号 —— 宁可对不上焊盘，也不编一个错的脚号。
- 改这里：
  1. 来料后按 `relay-wiring.md` §2.5 的**万用表 4 步法**测出 HK4100F 的真实脚号，回填文档，
     下次重跑脚本时在 `SYMBOLS["RELAY_SPDT"]` 的引脚表里换成真实编号。
  2. 其余器件（ESP32-C3 模组、ST7567 模组、Si5351A、MP2315、MD7673、J1–J6）在立创EDA 里
     用「封装管理器」重新绑定焊盘；报告 §5 列了**每一个**「未冻结引脚号」的符号。

### F6 器件没有封装（Footprint 为空）
- 现象：转过去全是无封装器件，无法生成 PCB。
- 原因：**故意的**。KiCad 的 `Footprint` 字段要求形如 `Resistor_SMD:R_0805_2012Metric` 的库 ID，
  而本仓 BOM 的「封装」列是中文描述（`0805`、`DIP 14.5x10.5mm`），塞进去会是非法库 ID。
- 改这里：在立创EDA 里按 [`hardware/bom/bom-summary.csv`](../bom/bom-summary.csv) 的**封装列**逐个选型；
  或者在立创EDA 的 BOM 工具里按位号批量匹配 LCSC 器件。

### F7 一次导入 8 个文件的行为不确定
- 现象：只导入进来 1 页 / 8 个文件变成 8 个互不相干的工程。
- 改这里：**先建一个空工程**，再在该工程内一个一个导入（立创EDA 会把它们当作同一工程的多张图页）。
  即使变成 8 个独立工程，每张图本身仍自带完整信息（网络名、位号、值），不会丢东西。
  跨页网络（17 条，见报告 §3）在**同一工程内**靠 `global_label` 连通；跨工程不连通。

### F8 值与 BOM 不一致 / 出现 `TBD`
- 现象：某些器件值是 `TBD`、`TBD-NP0`、`TBD-T106-6`、`TBD-LED-R`。
- 原因：这些器件在 BOM 里**本来就没定值**（LPF 的 L4–L6 / C8–C10、背光限流电阻 R_BLLED、
  C11–C13 电容套件）。
- 改这里：查 [`kicad-build-report.md`](kicad-build-report.md) §8 —— 逐个位号写了
  「用了什么值 + 这个值是从 BOM 的哪一列来的 / 还是脚本兜底的」。
  要改值就改 `scripts/build-kicad-schematic.py` 里的 `VALUE_FIX` / `VALUE_EXTRA` 再重跑。

### F9 电源网络被自动替换成电源符号，且没并成一条
- 现象：出现多个 `+12V`、`GND` 端口符号，各自独立。
- 改这里：立创EDA 里用「网络高亮」确认 `GND`/`+12V`/`+5V`/`+3V3_DIG`/`+3V3_RF`/`VBAT`
  各自只有**一条**网络；不是的话把它们并到同名网络（这 6 条网络在本目录里**全部**是 `global_label`）。

### F10 图面上的中文说明文字丢了
- 现象：每张图底部的 `NOTE` 文字块没转过来。
- 影响：**无**。那些文字只是给人看的（冲突提示、未连接器件清单）。
  同样的内容在 [`kicad-build-report.md`](kicad-build-report.md) 里都有，而且更全。

---

## 4. 手动细修建议清单（按优先级）

1. **先核网络，再核图形**：左侧「网络」面板 → 目标 73 个网络 → 用 [`kicad-net-map.csv`](kicad-net-map.csv) 抽查。
2. **处理 16 条 `PARTIAL` 行**（[`kicad-row-coverage.csv`](kicad-row-coverage.csv) 里 `status != DRAWN`）：
   这 16 行是 `netlist.csv` 自己**互相矛盾**、**用了不存在的引脚**、或**网络名那一列与端点不符**的行，
   脚本**宁可少连也不乱连**。逐条决定怎么办：
   | 行（数据行号） | 网络 | 问题 | 建议 |
   |---|---|---|---|
   | 1、2 | `ADC_FWD` / `ADC_REV` | `T1/T2` 的引脚写法是 `1 (次级)`，与第 105/111 行的 `次级+` 自相矛盾 | 删掉这两行的 T1/T2 端，保留 `U4.GPIO0/GPIO1` 端；检波链路以第 105–118 行为准 |
   | 16、17、18、20、21 | `EC11_A`/`EC11_B`/`EC11_SW`/`I2C_SDA`/`I2C_SCL` | 网络名那一列写的是**信号名**，但端点是 `+3V3_DIG`（这五行都是上拉电阻接电源的那一端） | 脚被钉在 `+3V3_DIG` 上（这是对的）；`net_label` 列在这五行上只是「这个电阻给谁上拉」的备注，不用改 |
   | 180 | `GPIO12_FB_PD` | 网络名列写 `GPIO12_FB_PD`，端点是网络名 `PA_PWR_PWM`（`R12` 是「建议未采纳」的 GPIO12 下拉） | 脚被钉在 `PA_PWR_PWM` 上；`R12` 要不要装配由 `docs/05 §7 #7a` 决定 |
   | 71 | `CW_KEY_SRC` | 两端都不是真实引脚（`U4` 的 `I2C 写 CLKx_DIS`、`U7.CLKx_CONTROL`） | 这是**设计说明**不是连线：CW 键控由 I2C 写 `CLKx_DIS` 实现，图上不用画 |
   | 85、86、90、91、95、96 | `PA_BIAS` / `GND` @ `Q1.G/Q2.G/Q3.G` | 同一个栅极引脚被 4 条网络声明（`PA_GATE`/`PA_GATE_PD`/`PA_BIAS`/`GND`） | 脚本只保留第一条 `PA_GATE`（`PA_GATE_PD` 已按别名并入）；`PA_BIAS` 请经耦合元件接到栅极，`D5` 的**阴极**接栅极、阳极接 GND（现在图上 `D5` 只有阳极在 GND 上） |
   | 103 | `PA_RF_OUT` | `Q1.D` 已被第 87 行占为 `PA_DRAIN` | 类 E 功放的漏极同时是直流馈电点和射频输出点：确认馈电扼流圈位置后，把 `PA_DRAIN` 与 `PA_RF_OUT` 按实际拓扑分开或合并 |
   | 179 | `BUZZER_DRV` | `U1.IOEXP_SPARE` 不是 TCA9535 的引脚（9 个预留位里还没选） | 定了用哪一位之后，把 `LS1.+` 接到那一位（`P0.6/P0.7/P1.0/P1.2…P1.7` 之一） |

   > **行号约定**：本文与所有产物里的「行」都是 `netlist.csv` 的**数据行号**（1 起，等于 CSV 文件行号减 1），
   > 与 [`kicad-row-coverage.csv`](kicad-row-coverage.csv) 的 `row` 列一致。

3. **处理 3 条 `NOTE` 行**：`GND_DIG ↔ GND_RF`、`GND_PWR ↔ GND_DIG`（底板单点星形地，要在 PCB 上落实）、
   `CW_KEY_SRC`（同上）。这三条**没有器件引脚**，只在图上留了说明，不影响网络。
4. **补 `netlist.csv` 里没有的引脚**：报告 §9 列了「放了但没连线的位号」（LPF 六个、6 个模块侧 SMA、
   J2–J6 排针、TP1–TP8 等）；报告里也能查出「有引脚但没连线的引脚」（如 `U4` 的 `GND`、
   `J_USB` 的 `GND`、`C6`/`C244` 的第 2 脚），这些要么补线，要么确认真的悬空。
5. **确认关键极性/强制项**（这些是文档里的硬要求，图上已经体现，请复核）：
   - ATU 电感旁路用 **COM–NC**（释放=旁路、吸合=接入）；电容支路用 **COM–NO**；未用触点**悬空**。
   - `U2.COM` → `+12V`（内部续流二极管靠它生效）。
   - `R_RLY1–R_RLY6` 六只 10 kΩ 下拉必须存在（否则上电误吸合）。
   - `U8` 输入侧 `R8`/`R9` 10 kΩ 下拉 + `Q1–Q3` 栅极 `R10` 下拉必须存在。
   - `U5.CS` → GND；`U5.RST` 与板复位共用。
6. **替换器件、绑封装**（见 F2/F6），然后跑立创EDA 的 DRC/网络比对。
7. 若你在立创EDA 里改好了，**不要**把改动写回本目录的 `.kicad_sch`——它们每次都是由脚本重新生成的
   （生成是幂等的，手改会丢）。要固化改动，就改 `scripts/build-kicad-schematic.py` 里的表再重跑。

---

## 5. 重新生成 / 自检

```powershell
cd <仓库根>\ARDF-MeshTuneFox80-hardware

# 生成（幂等：重跑结果逐字节相同）
python scripts\build-kicad-schematic.py

# 生成"全部用 global_label"的版本（F3 的应对）
python scripts\build-kicad-schematic.py --all-global

# 自检（不通过会给出具体文件+行列原因；退出码 0 = 通过）
python scripts\check-kicad-schematic.py
python scripts\check-kicad-schematic.py --quiet
```

自检器查什么、以及它自己的对照组，见 [`KIcad-skeleton-decision.md`](KIcad-skeleton-decision.md) §4。

---

## 6. 本次**没有**验证的东西（请你试导入后回报）

- **没有任何 KiCad 打开过这些文件**（本机没有 KiCad，也不允许安装）。语法正确性来自
  自检器的**独立 s-expression 解析器**（括号配平、字符串、token），不是来自 KiCad 本身。
- **立创EDA 转换助手从未运行过**（未安装、未联网调用）。§3 的失败点是从格式差异推断的，
  不是实测得到的错误文案。
- **符号图形是否好看**、引脚名是否与相邻器件文字重叠：只做了**包围盒不重叠**的几何检查
  （109 个实例两两不重叠、全部元素在页面内），**文字宽度没有建模**，长引脚名（如
  `IOEXP_SPARE_P1_0`）可能压到邻近器件上——这只影响观感，不影响网络。
- **电气正确性**：图上的连接完全照抄 [`netlist.csv`](netlist.csv)，
  没有做任何电气规则检查（ERC）、没有算过电流/电压/阻抗。
- **HK4100F / ESP32-C3 模组 / ST7567 模组 / Si5351A / MP2315 / MD7673 / J1–J6 的物理脚号**：
  见报告 §5，全部**待你核实**。
- **`.kicad_sch` 里 `symbol_instances` / `sheet_instances` 段**：这是 KiCad 6 根图的标准写法，
  但转换器是否使用它来恢复位号，未验证。
