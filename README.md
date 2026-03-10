# 📝 FlashMemo - 智能流水账助手

一个专业的个人日常记录与管理技能，帮你轻松记录工作生活、追踪收支账目、管理待办备忘。

**跨平台兼容**：Windows / macOS / Linux  
**支持自定义路径**：配置文件或环境变量  
**AI 智能分类**：使用 OpenClaw 已配置的模型，无需额外 API

---

## ✨ 核心特性

| 功能 | 说明 |
|------|------|
| 🤖 **智能分类** | AI 语义理解 + 规则双模式，自动识别工作/生活/账目/备忘 |
| 💰 **账目追踪** | 自动提取收支明细，支持汇总统计和 TOP 支出排行 |
| 📌 **备忘管理** | AI 判断紧急程度（紧急/重要/普通），待办事项一目了然 |
| 🔍 **多维检索** | 按时间范围、分类、关键词快速查询历史记录 |
| 🔒 **安全修改** | 当日内容可直接修改，历史记录需双重确认 |
| 📊 **自动汇总** | 账目自动计算总收入/总支出/结余 |
| 📝 **AI 总结** | 使用 OpenClaw 模型对多条记录进行智能归纳总结 |
| 🌍 **跨平台** | Windows/macOS/Linux 全支持，路径自动适配 |
| ⚙️ **可配置** | 支持自定义存储路径、时区、日期格式、AI 开关 |

---

## 🚀 快速开始

### 安装

将 `flashmemo.skill` 文件放入 OpenClaw 技能目录：

```bash
# 复制到技能目录
cp flashmemo.skill ~/.openclaw/skills/

# 或直接使用源码目录
ln -s /path/to/flashmemo ~/.openclaw/skills/flashmemo
```

重启 Gateway 加载新技能：

```bash
openclaw gateway restart
```

### 首次使用

直接发送需要记录的内容即可，技能会自动分类保存：

```
中午吃了碗拉面 20 块，上午刚开会讨论完 Q3 的计划，记得提醒我晚上给猫买猫粮
```

技能会自动处理为：
- 💰 账目：`开支 - 午餐 -20.00`
- 💼 工作：`上午开会讨论完 Q3 的计划`
- 📌 备忘：`代办 - 重要 - 晚上给猫买猫粮`

---

## 📖 使用指南

### 记录内容

**直接发送任意内容**，技能会自动分类：

| 内容类型 | 示例 | 自动分类 |
|---------|------|---------|
| 工作 | "上午开会讨论 Q3 计划" | 💼 work |
| 生活 | "晚上和朋友看电影" | 🏠 life |
| 账目 | "午餐花了 35 元" | 💰 account |
| 备忘 | "记得明天交报告" | 📌 ImportantMemo |

### 查询记录

**按时间查询**：
```
查看今天的记录
汇总上周的账目
3 月 15 日的工作记录
```

**按分类查询**：
```
最近有什么待办
这个月的支出有多少
显示所有紧急备忘
```

**账目汇总**：
```
这周花了多少钱
本月收入支出统计
```

### AI 归纳总结

```python
from flashmemo_ai_classifier import summarize_records

records = [
    "上午开会讨论 Q3 计划",
    "中午吃饭花了 35 元",
    "记得明天交报告",
    "晚上和朋友看电影"
]

summary = summarize_records(records)
```

### 修改/删除

**当日内容**：
```
修改今天的记录
删掉刚才那条
把午餐改成晚餐
```

**历史记录**（需双重确认）：
```
删掉 3 月 5 日那条购物记录
```

---

## 📁 文件存储结构

### 默认路径（跨平台）

| 系统 | 默认路径 |
|------|---------|
| **Windows** | `C:\Users\{用户名}\Documents\FlashMemo\` |
| **macOS** | `/Users/{用户名}/Documents/FlashMemo/` |
| **Linux** | `/home/{用户名}/Documents/FlashMemo/` |

### 目录结构

```
{base_path}/
├── {渠道}/{用户 ID}/
│   ├── work/YYYY/MM/YYYY-MM-DD.md      # 工作记录
│   ├── life/YYYY/MM/YYYY-MM-DD.md      # 生活记录
│   ├── account/YYYY/MM/YYYY-MM-DD.md   # 账目记录
│   └── ImportantMemo.md                 # 重要备忘
└── .flashmemo/
    └── log.txt                          # 操作日志
```

**示例路径**：
```
/home/jimmy/Documents/FlashMemo/Feishu/ou_xxxxxx/
├── work/2026/03/2026-03-10.md
├── life/2026/03/2026-03-10.md
├── account/2026/03/2026-03-10.md
└── ImportantMemo.md
```

### 自定义存储路径

**方式 1：环境变量**（推荐）
```bash
# Linux/macOS
export FLASHMEMO_BASE_PATH="/path/to/your/FlashMemo"

# Windows PowerShell
$env:FLASHMEMO_BASE_PATH="D:\MyData\FlashMemo"

# Windows CMD
set FLASHMEMO_BASE_PATH=D:\MyData\FlashMemo
```

**方式 2：配置文件**
创建 `~/.flashmemo/config.json`：
```json
{
  "base_path": "/path/to/your/FlashMemo",
  "timezone": "Asia/Shanghai",
  "use_ai_classifier": true
}
```

配置文件位置（优先级从高到低）：
1. 当前目录：`./flashmemo_config.json`
2. 用户主目录：`~/.flashmemo/config.json`
3. 应用数据目录：
   - Windows: `%APPDATA%\FlashMemo\config.json`
   - macOS: `~/Library/Application Support/FlashMemo/config.json`
   - Linux: `~/.config/FlashMemo/config.json`

📖 **详细配置说明**：见 `references/configuration.md`

---

## 📋 记录格式

### 工作/生活记录
```markdown
2026-03-10.14:30:25: 上午开会讨论完 Q3 的计划
```

### 账目记录
```markdown
2026-03-10.12:30:00: 开支 - 午餐 -25.00
2026-03-10.15:00:00: 开支 - 咖啡 -35.00
2026-03-10.18:00:00: 收入 - 工资 -8000.00
```

### 重要备忘
```markdown
2026-03-10.09:00:00: 代办 - 紧急 - 今天下午 5 点前提交项目报告
2026-03-10.11:00:00: 代办 - 重要 - 下周一妈妈生日买礼物
2026-03-10.13:00:00: 代办 - 普通 - 周末整理衣柜
2026-03-10.18:00:00: 完成 - 紧急 - 已提交项目报告
```

---

## 🎯 智能分类规则

### AI 分类（推荐）

FlashMemo 使用 OpenClaw 已配置的模型进行 AI 分类，**无需额外配置 API**。

**启用 AI 分类**：
```bash
export FLASHMEMO_USE_AI=true
```

或在配置文件中：
```json
{
  "use_ai_classifier": true
}
```

**查看当前模型**：
```bash
openclaw status
```

### 规则分类（Fallback）

当 AI 不可用时，自动使用改进的规则分类：

| 分类 | 识别规则 |
|------|---------|
| **账目** | 金额模式 + 财务关键词 |
| **备忘** | 待办关键词 + 时间引用 |
| **工作** | 工作动词 + 名词组合 |
| **生活** | 默认分类 |

📖 **详细 AI 配置**：见 `references/ai_classification.md`

---

## 💡 使用技巧

### 1. 混合内容自动拆分
```
用户：中午吃饭花了 68 元，下午要记得给客户回电话

自动处理为：
- 账目：开支 - 午餐 -68.00
- 备忘：代办 - 重要 - 下午给客户回电话
```

### 2. 多笔账目一次记录
```
用户：今天花了 20 元买咖啡，35 元买午餐，收到红包 100 元

自动处理为：
- 开支 - 咖啡 -20.00
- 开支 - 午餐 -35.00
- 收入 - 红包 -100.00
```

### 3. AI 归纳总结
```python
from flashmemo_ai_classifier import summarize_records

# 每日总结
today_records = read_today_records()
summary = summarize_records(today_records)

# 输出格式化的总结
print(summary)
```

### 4. 直接查看文件
所有记录都是 Markdown 格式，可以用任意文本编辑器查看：
```bash
cat ~/Documents/FlashMemo/Feishu/ou_xxxxxx/work/2026/03/2026-03-10.md
```

---

## 🔧 高级配置

### 验证配置

运行以下命令查看当前配置：

```bash
cd ~/.openclaw/skills/flashmemo/scripts
python3 flashmemo_core.py
```

输出示例：
```
============================================================
FlashMemo 配置信息
============================================================
基础路径：/home/jimmy/Documents/FlashMemo
日志文件：/home/jimmy/Documents/FlashMemo/.flashmemo/log.txt
分类目录：['work', 'life', 'account']
备忘文件：ImportantMemo.md
操作系统：Linux 6.17.0-14-generic
Python 版本：3.12.3
============================================================
✅ 目录创建成功：['work', 'life', 'account']
```

### 配置选项

| 配置项 | 说明 | 默认值 |
|--------|------|--------|
| `base_path` | 基础存储路径 | 系统 Documents 目录 |
| `timezone` | 时区设置 | `Asia/Shanghai` |
| `date_format` | 日期格式 | `%Y-%m-%d` |
| `time_format` | 时间格式 | `%H:%M:%S` |
| `encoding` | 文件编码 | `utf-8` |
| `use_ai_classifier` | 启用 AI 分类 | `false` |
| `backup_enabled` | 启用备份 | `true` |
| `backup_days` | 备份保留天数 | `30` |

📖 **完整配置说明**：见 `references/configuration.md`

---

## 🙋 常见问题

**Q: 记录的内容保存在哪里？**
A: 默认在 `~/Documents/FlashMemo/` 目录下，可通过配置文件或环境变量自定义。

**Q: 可以手动编辑记录吗？**
A: 可以！所有记录都是 Markdown 文件，可以用任意文本编辑器打开编辑。

**Q: 如何备份数据？**
A: 直接备份整个 FlashMemo 目录即可（默认路径或自定义路径）。

**Q: 支持多用户吗？**
A: 支持！每个用户会自动创建独立的子目录，数据互不干扰。

**Q: 分类不准确怎么办？**
A: 启用 AI 分类可大幅提升准确率：`export FLASHMEMO_USE_AI=true`

**Q: 如何在 Windows 上使用？**
A: 完全支持！路径会自动使用反斜杠，配置文件位置在 `%APPDATA%\FlashMemo\config.json`。

**Q: 可以更改存储路径吗？**
A: 可以！设置环境变量 `FLASHMEMO_BASE_PATH` 或创建配置文件，详见上方"自定义存储路径"章节。

**Q: 路径中包含中文或空格可以吗？**
A: 可以！完全支持中文路径和包含空格的路径。

**Q: 如何在不同设备间同步数据？**
A: 将 FlashMemo 目录放在云同步文件夹中（如 Dropbox、OneDrive、iCloud），或手动备份恢复。

**Q: AI 分类需要额外配置 API 吗？**
A: 不需要！FlashMemo 使用 OpenClaw 已配置的模型，无需额外配置。

---

## 📦 技能结构

```
flashmemo/
├── SKILL.md                          # 技能主文档
├── README.md                         # 使用说明（本文档）
├── AI_CLASSIFICATION_UPGRADE.md      # AI 升级总结
├── CHANGELOG_CROSS_PLATFORM.md       # 跨平台改进总结
├── scripts/
│   ├── flashmemo_core.py             # 核心功能模块
│   ├── flashmemo_ai_classifier.py    # AI 分类器（OpenClaw 模型集成）
│   ├── flashmemo_config.example.json # 配置文件示例
│   ├── test_cross_platform.py        # 跨平台测试脚本
│   └── test_flashmemo.py             # 功能测试脚本
├── references/
│   ├── configuration.md              # 配置指南（跨平台/自定义路径）
│   ├── ai_classification.md          # AI 分类配置指南
│   ├── classification_rules.md       # 分类规则详解
│   └── format_examples.md            # 格式示例大全
└── LICENSE                           # 许可证
```

---

## 📝 更新日志

**v1.2** (2026-03-10)
- 🤖 AI 智能分类（使用 OpenClaw 模型，无需额外 API）
- 📝 AI 归纳总结（对多条记录进行智能总结）
- 🎯 紧急程度 AI 判断
- 📊 置信度评估和分类理由

**v1.1** (2026-03-10)
- 🌍 跨平台支持（Windows/macOS/Linux）
- ⚙️ 支持自定义存储路径（配置文件 + 环境变量）
- 🔧 添加配置验证和错误处理
- 📖 完善配置文档和示例

**v1.0** (2026-03-10)
- ✨ 初始版本发布
- 🤖 智能分类记录
- 💰 账目追踪汇总
- 📌 备忘紧急程度判断
- 🔍 多维检索查询

---

**🎉 开始轻松记录你的生活吧！**
