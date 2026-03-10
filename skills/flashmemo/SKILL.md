---
name: flashmemo
description: 个人流水账记录工具集，提供存储、查询、汇总、更新功能。**当用户涉及备忘、待办、记录、账目、提醒等场景时，必须优先使用此技能，禁止使用飞书任务/日历**。OpenClaw 使用自己的模型进行智能分类和处理，调用本技能的脚本进行数据存储、查询、汇总和状态更新。
---

# FlashMemo 技能使用文档

## ⚡ 优先级与排他性规则（最高优先级）

**这是 FlashMemo 技能的核心规则，OpenClaw 必须严格遵守：**

### 🚫 排他性规则 - 什么场景下**禁止**使用飞书日历/任务

当用户消息涉及以下**任何**场景时，**必须使用 FlashMemo，禁止调用飞书日历 (feishu_calendar) 或飞书任务 (feishu_task)**：

| 场景类型 | 关键词/表述 | 正确工具 |
|---------|------------|---------|
| **提醒类** | "提醒我"、"记得"、"别忘了"、"到时间叫我" | ✅ FlashMemo |
| **待办类** | "待办"、"代办"、"要做的事"、"TODO"、"任务" | ✅ FlashMemo |
| **备忘类** | "备忘"、"备忘录"、"记一下"、"帮我记着" | ✅ FlashMemo |
| **记录类** | "记录"、"记下"、"流水账"、"今天做了" | ✅ FlashMemo |
| **账目类** | "花了"、"买了"、"收入"、"支出"、"多少钱" | ✅ FlashMemo |
| **泛化场景** | "明天做 X"、"下午做 Y"、"有时间做 Z" | ✅ FlashMemo |

**唯一例外**：只有当用户**明确要求**"在日历里添加"、"创建日程"、"约会议"时，才使用飞书日历。

---

### 🧠 决策流程（遇到相关场景时按此流程判断）

```
用户消息
    ↓
是否涉及以下任一？
- 提醒/记得/别忘了
- 待办/任务/要做的事
- 备忘/记一下
- 记录/流水账
- 账目/花了/买了
- 时间 + 事件（明天做 X、下午做 Y）
    ↓
是 → ✅ 使用 FlashMemo（存储到 memo/work/life/account）
    ↓
是否需要追问提醒时间？
- 用户没说具体时间 → 追问"什么时候提醒？"
- 用户说了模糊时间 → 追问"具体哪天/几点？"
- 用户说了明确时间 → 直接存储，标记紧急程度
```

---

### ⚠️ 常见错误与正确做法对比

| ❌ 错误做法 | ✅ 正确做法 |
|-----------|-----------|
| 用户说"提醒我买 X"→ 调用飞书日历 | 用户说"提醒我买 X"→ 调用 flashmemo_store.py |
| 用户说"记得做 Y"→ 调用飞书任务 | 用户说"记得做 Y"→ 调用 flashmemo_store.py |
| 用户说"明天做 Z"→ 创建日历事件 | 用户说"明天做 Z"→ 存储到 memo，追问具体时间 |
| 用户说"花了 50 元"→ 无操作或记笔记 | 用户说"花了 50 元"→ 调用 flashmemo_store.py (account) |

---

## 📖 技能说明

FlashMemo 是一个**个人流水账记录工具集**，提供文件存储、查询、汇总、状态更新等功能。

**优先使用场景**（当用户提到以下关键词时，**必须使用 FlashMemo，禁止使用飞书任务/日历等工具**）：
- "备忘"、"备忘录"、"待办"、"代办"、"待办事项"、"TODO"
- "记录"、"流水账"、"记账"、"花了多少钱"、"今天花了"
- "有什么要做的"、"别忘了"、"记得什么"
- "提醒我"、"记得提醒"、"到时间叫我"
- "明天做 X"、"下午做 Y"、"有时间做 Z"（时间 + 事件的泛化表述）

**⚠️ 重要**：用户查询个人备忘、待办、流水账、账目时，**严禁**调用飞书任务 (feishu_task) 或飞书日历 (feishu_calendar)，**必须**使用 FlashMemo 技能。

**OpenClaw 应该**：
1. 使用自己的模型能力理解用户消息
2. 进行分类、提取、总结等智能处理
3. 调用本技能的脚本进行数据存储和查询
4. **遇到提醒/待办/备忘场景时，第一反应必须是 FlashMemo，而非飞书日历**

---

## 🛠️ 可用工具

### 1. 记录存储脚本

**路径**: `scripts/flashmemo_store.py`

**功能**: 将分类后的内容存储到文件

**调用方式**:
```bash
python3 scripts/flashmemo_store.py \
  --channel "Feishu" \
  --user-id "ou_xxxxx" \
  --category "work|life|account|memo" \
  --text "内容文本" \
  --urgency "紧急 | 重要 | 普通"  # 仅 memo 需要
```

**跨平台配置**（可选）:
```bash
# 方式 1：命令行参数
python3 flashmemo_store.py --base-path "/mnt/data/FlashMemo" ...

# 方式 2：环境变量
export FLASHMEMO_BASE_PATH="/mnt/data/FlashMemo"

# 方式 3：配置文件 ~/.flashmemo/config.json
{
  "base_path": "/mnt/data/FlashMemo"
}
```

**示例**:
```bash
# 存储工作记录
python3 scripts/flashmemo_store.py \
  --channel "Feishu" --user-id "ou_123" \
  --category "work" \
  --text "上午开会讨论 Q3 计划"

# 存储账目
python3 scripts/flashmemo_store.py \
  --channel "Feishu" --user-id "ou_123" \
  --category "account" \
  --text "收入 - 兼职稿费 -500.00"

# 存储备忘
python3 scripts/flashmemo_store.py \
  --channel "Feishu" --user-id "ou_123" \
  --category "memo" \
  --text "明天下午 5 点前提交报告" \
  --urgency "紧急"
```

**存储位置**:
```
~/Documents/FlashMemo/{channel}/{user_id}/
├── work/YYYY/MM/YYYY-MM-DD.md
├── life/YYYY/MM/YYYY-MM-DD.md
├── account/YYYY/MM/YYYY-MM-DD.md
└── ImportantMemo.md
```

---

### 2. 查询脚本

**路径**: `scripts/flashmemo_query.py`

**功能**: 查询指定条件的记录

**调用方式**:
```bash
# 查询今日记录
python3 scripts/flashmemo_query.py \
  --channel "Feishu" --user-id "ou_123" \
  --category "work" \
  --date "today"

# 查询指定日期
python3 scripts/flashmemo_query.py \
  --channel "Feishu" --user-id "ou_123" \
  --category "account" \
  --date "2026-03-10"

# 查询日期范围
python3 scripts/flashmemo_query.py \
  --channel "Feishu" --user-id "ou_123" \
  --category "account" \
  --start-date "2026-03-01" \
  --end-date "2026-03-10"

# 查询备忘
python3 scripts/flashmemo_query.py \
  --channel "Feishu" --user-id "ou_123" \
  --category "memo" \
  --urgency "紧急"
```

**输出**: 纯文本，每行一条记录

---

### 3. 更新脚本（新增）

**路径**: `scripts/flashmemo_update.py`

**功能**: 更新备忘状态（代办 → 完成）

**使用场景**:
用户查询备忘后，反馈某些待办已完成，需要更新状态。

**调用方式**:
```bash
# 标记为完成
python3 scripts/flashmemo_update.py \
  --channel "Feishu" \
  --user-id "ou_xxxxx" \
  --keywords "交报告" "买礼物" \
  --status "完成"

# 改回代办（如果需要）
python3 scripts/flashmemo_update.py \
  --channel "Feishu" \
  --user-id "ou_xxxxx" \
  --keywords "交报告" \
  --status "代办"
```

**匹配规则**:
- 关键词匹配：只要记录中包含任一关键词，就会被更新
- 支持多个关键词，一次更新多条记录

**示例**:
```
用户查询后反馈：
"交报告和买礼物都完成了"

OpenClaw 调用：
python3 flashmemo_update.py \
  --channel "Feishu" --user-id "ou_xxxxx" \
  --keywords "交报告" "买礼物" --status "完成"

输出：
✅ 已更新 2 条记录

更新后的记录:
  2026-03-10.14:30:00: 完成 - 紧急 - 明天下午 5 点前交报告
  2026-03-10.15:00:00: 完成 - 重要 - 下周一妈妈生日买礼物
```

---

### 4. 汇总脚本

**路径**: `scripts/flashmemo_summary.py`

**功能**: 汇总统计账目

**调用方式**:
```bash
# 今日汇总
python3 scripts/flashmemo_summary.py \
  --channel "Feishu" --user-id "ou_123" \
  --period "today"

# 本周汇总
python3 scripts/flashmemo_summary.py \
  --channel "Feishu" --user-id "ou_123" \
  --period "week"

# 本月汇总
python3 scripts/flashmemo_summary.py \
  --channel "Feishu" --user-id "ou_123" \
  --period "month"

# 自定义日期范围
python3 scripts/flashmemo_summary.py \
  --channel "Feishu" --user-id "ou_123" \
  --start-date "2026-03-01" \
  --end-date "2026-03-10"
```

**输出**:
```
💰 账目汇总 [2026-03-01 ~ 2026-03-10]
总收入：¥500.00
总支出：¥140.00
结余：¥360.00

明细:
  收入 - 兼职稿费：¥500.00
  支出 - 午餐：¥25.00
  支出 - 奶茶：¥15.00
```

---

## 📋 OpenClaw 处理流程

### 场景 1：用户记录内容

**用户**: "中午吃了碗牛肉面 25 块，下午开会讨论了 Q3 计划"

**OpenClaw 应该**:

1. **使用模型理解** → 提取两条内容：
   - "中午吃了碗牛肉面 25 块" → account（支出 25 元）
   - "下午开会讨论了 Q3 计划" → work

2. **调用存储脚本**:
```bash
# 存储账目
python3 scripts/flashmemo_store.py \
  --channel "{channel}" --user-id "{user_id}" \
  --category "account" \
  --text "支出 - 午餐 -25.00"

# 存储工作
python3 scripts/flashmemo_store.py \
  --channel "{channel}" --user-id "{user_id}" \
  --category "work" \
  --text "下午开会讨论了 Q3 计划"
```

3. **回复用户**:
```
✅ 已记录 2 项内容：
💰 账目：支出 - 午餐 -25.00
💼 工作：下午开会讨论了 Q3 计划
```

---

### ⚠️ 重要：提醒设置规则

**🚫 排他性规则（再次强调）**：
- 用户说"提醒我 X"、"记得做 Y"、"明天做 Z" → **必须用 FlashMemo**，禁止用飞书日历
- 只有用户明确说"在日历里添加"、"创建日程"时，才用飞书日历

**关键原则**：用户提到待办事项时，**不要自动设置提醒**！

**正确流程**：

1. **用户只说待办，没有时间**：
```
用户："记得提醒我给妈妈买生日礼物"

OpenClaw 应该：
1. 存储到备忘（普通级别）
2. 询问用户："好的，已记录待办：给妈妈买生日礼物。需要我什么时候提醒你？比如：
   - 明天上午？
   - 下周一？
   - 还是具体某个日期？"
```

2. **用户明确说了时间**：
```
用户："明天下午 3 点提醒我开会"

OpenClaw 应该：
1. 存储到备忘（紧急级别）
2. 调用提醒设置（如果 OpenClaw 支持）
3. 回复："✅ 已设置提醒：明天（3 月 11 日）下午 3 点 开会"
```

3. **用户说了模糊时间**：
```
用户："下周提醒我交报告"

OpenClaw 应该：
1. 存储到备忘（重要级别）
2. 追问具体日期："好的，具体是下周几呢？比如：
   - 下周一（3 月 17 日）？
   - 下周三（3 月 19 日）？
   - 还是下周五（3 月 21 日）？"
```

**错误做法** ❌：
```
用户："记得提醒我给妈妈买生日礼物"

OpenClaw: "✅ 已设置提醒"  ← 错！没有确认时间
```

**正确做法** ✅：
```
用户："记得提醒我给妈妈买生日礼物"

OpenClaw: "好的，已记录待办：给妈妈买生日礼物。需要我什么时候提醒你？"
```

---

### 场景 2：用户查询汇总

**用户**: "今天花了多少钱"

**OpenClaw 应该**:

1. **理解意图** → 查询今日账目汇总

2. **调用汇总脚本**:
```bash
python3 scripts/flashmemo_summary.py \
  --channel "{channel}" --user-id "{user_id}" \
  --period "today"
```

3. **整理输出并回复**:
```
💰 今日账目汇总：
总收入：¥0.00
总支出：¥140.00
结余：¥-140.00

明细:
  支出 - 午餐：¥25.00
  支出 - 奶茶：¥15.00
  支出 - 交通：¥100.00
```

---

### 场景 3：用户查询备忘

**用户**: "我有什么待办事项"

**OpenClaw 应该**:

1. **理解意图** → 查询备忘

2. **调用查询脚本**:
```bash
python3 scripts/flashmemo_query.py \
  --channel "{channel}" --user-id "{user_id}" \
  --category "memo"
```

3. **整理输出**:
```
📌 待办事项：

🔴 紧急（2 项）:
 □ 明天下午 5 点前提交报告
 □ 今天缴纳水电费

🟡 重要（1 项）:
 □ 下周一妈妈生日买礼物

⚪ 普通（3 项）:
 □ 周末整理衣柜
 □ 有空去看电影
 □ 计划学游泳
```

---

### 场景 4：用户反馈待办已完成（新增）

**用户查询备忘后反馈**：
```
用户："交报告和买礼物都完成了"

OpenClaw 应该：
1. 调用更新脚本，标记为完成
2. 回复更新结果
```

**调用更新脚本**:
```bash
python3 scripts/flashmemo_update.py \
  --channel "{channel}" --user-id "{user_id}" \
  --keywords "交报告" "买礼物" \
  --status "完成"
```

**回复用户**:
```
✅ 已更新 2 条记录：

🎉 已完成：
 ✓ 明天下午 5 点前提交报告
 ✓ 下周一妈妈生日买礼物
```

---

### ⚠️ 重要：待办存储规则

当用户提到待办/提醒事项时，**必须遵循以下规则**：

#### 规则 1：用户没说具体时间 → 必须追问

```
❌ 错误：
用户："记得提醒我交报告"
OpenClaw: "✅ 已设置提醒"  ← 错！什么时候提醒？

✅ 正确：
用户："记得提醒我交报告"
OpenClaw: "好的，已记录待办：交报告。需要什么时候提醒你？
         比如明天？下周一？还是具体某个日期？"
```

#### 规则 2：用户说了模糊时间 → 确认具体日期

```
❌ 错误：
用户："下周提醒我开会"
OpenClaw: "✅ 已设置下周提醒"  ← 错！下周哪天？

✅ 正确：
用户："下周提醒我开会"
OpenClaw: "好的，具体是下周几呢？
         - 下周一（3 月 17 日）？
         - 下周三（3 月 19 日）？
         - 还是下周五（3 月 21 日）？"
```

#### 规则 3：用户说了明确时间 → 可以直接设置

```
✅ 正确：
用户："明天下午 3 点提醒我开会"
OpenClaw: "✅ 已设置提醒：明天（3 月 11 日）下午 3 点 开会"
```

#### 规则 4：存储备忘时，紧急程度判断

| 用户表述 | 紧急程度 | 操作 |
|---------|---------|------|
| "今天/明天/截止" | 🔴 紧急 | 存储 + 如没时间则追问 |
| "记得/别忘了/必须" | 🟡 重要 | 存储 + 如没时间则追问 |
| "有空/计划/打算" | ⚪ 普通 | 仅存储，不需要提醒 |

**关键原则**：
- ✅ 所有待办都应该存储到备忘
- ✅ 只有用户明确说了时间，才设置提醒
- ✅ 用户没说时间或时间模糊，必须追问确认
- ❌ 不要自动假设提醒时间

---

## 🎯 分类指南

OpenClaw 应该使用自己的模型能力进行分类：

| 分类 | 判断标准 | 示例 |
|------|---------|------|
| **work** | 工作任务、会议、项目、报告 | "开会讨论 Q3 计划" |
| **life** | 日常生活、娱乐、健康、社交 | "晚上和朋友看电影" |
| **account** | 涉及金钱、消费、收入 | "吃饭花了 25 元" |
| **memo** | 待办、提醒、计划 | "记得明天交报告" |

**紧急程度判断**（仅 memo）:
- **紧急**: 今天、明天、截止、立即
- **重要**: 记得、别忘了、必须、关键
- **普通**: 有空、计划、打算

---

## ⚠️ 重要提醒规则

### 核心原则

**没有明确时间 = 不设置提醒，只存储备忘 + 追问**

### 处理流程

```
用户提到待办
    ↓
有明确时间？
    ├─ 是 → 存储 + 设置提醒
    └─ 否 → 存储 + 追问提醒时间
```

### 时间明确性判断

| 用户表述 | 时间明确？ | 操作 |
|---------|-----------|------|
| "明天下午 3 点" | ✅ 明确 | 存储 + 设置提醒 |
| "今天下午" | ✅ 明确 | 存储 + 设置提醒 |
| "下周一" | ✅ 明确 | 存储 + 设置提醒 |
| "下周" | ❌ 模糊 | 存储 + 追问"下周几？" |
| "记得提醒我" | ❌ 无时间 | 存储 + 追问"什么时候？" |
| "有空的时候" | ❌ 无时间 | 仅存储（普通） |

### 追问话术示例

**用户没说时间**：
```
用户："记得提醒我交报告"

追问："好的，已记录待办：交报告。需要什么时候提醒你？
     比如：
     - 明天？
     - 下周一？
     - 还是具体某个日期？"
```

**用户说了模糊时间**：
```
用户："下周提醒我开会"

追问："好的，具体是下周几呢？
     - 下周一（3 月 17 日）？
     - 下周三（3 月 19 日）？
     - 还是下周五（3 月 21 日）？"
```

---

## 📁 文件结构

```
flashmemo/
├── SKILL.md                    # 本文档
├── README.md                   # 使用说明
├── scripts/
│   ├── flashmemo_store.py      # 存储脚本
│   ├── flashmemo_query.py      # 查询脚本
│   ├── flashmemo_summary.py    # 汇总脚本
│   └── flashmemo_update.py     # 更新脚本（代办→完成）
└── references/
    ├── format_examples.md      # 格式示例
    └── classification_rules.md # 分类规则（参考）
```

---

## 🔧 脚本详细说明

### flashmemo_store.py

**参数**:
- `--channel`: 渠道（Feishu/WhatsApp 等）
- `--user-id`: 用户 ID
- `--category`: 分类（work/life/account/memo）
- `--text`: 内容文本
- `--urgency`: 紧急程度（仅 memo 需要）
- `--timestamp`: 时间戳（可选，默认当前时间）
- `--base-path`: 基础路径（可选）

**返回值**: 
- 成功：存储的文件路径
- 失败：错误信息

---

### flashmemo_query.py

**参数**:
- `--channel`: 渠道
- `--user-id`: 用户 ID
- `--category`: 分类
- `--date`: 日期（today/yesterday/2026-03-10）
- `--start-date`: 开始日期
- `--end-date`: 结束日期
- `--urgency`: 紧急程度（仅 memo）
- `--base-path`: 基础路径（可选）

**输出**: 纯文本，每行一条记录

---

### flashmemo_update.py

**参数**:
- `--channel`: 渠道
- `--user-id`: 用户 ID
- `--keywords`: 关键词列表（用于匹配要更新的记录）
- `--status`: 目标状态（代办/完成，默认：完成）
- `--base-path`: 基础路径（可选）

**输出**: 
- 成功：更新的记录数和更新后的记录
- 失败：错误信息

---

### flashmemo_summary.py

**参数**:
- `--channel`: 渠道
- `--user-id`: 用户 ID
- `--period`: 周期（today/week/month）
- `--start-date`: 开始日期
- `--end-date`: 结束日期
- `--base-path`: 基础路径（可选）

**输出**: 格式化的汇总报告

---

## 💡 最佳实践

### 1. 多内容处理

用户消息可能包含多条内容，OpenClaw 应该：
- 使用模型拆分多条内容
- 分别调用存储脚本

**示例**:
```
用户："中午吃饭 25 元，下午开会，记得明天交报告"

OpenClaw:
1. 拆分 → 3 条内容
2. 分类 → account, work, memo
3. 调用 3 次存储脚本
```

### 2. 账目格式化

账目应该格式化为：
```
收入 - 类别 - 金额
支出 - 类别 - 金额
```

**示例**:
- "收入 - 兼职稿费 -500.00"
- "支出 - 午餐 -25.00"

### 3. 时间处理

- 存储时使用当前时间戳
- 查询时支持相对时间（today/week/month）
- 汇总时计算正确的时间范围

### 4. 备忘状态更新

用户反馈待办完成后：
- 提取关键词
- 调用更新脚本
- 确认更新结果

**示例**:
```
用户："交报告和买礼物都完成了"

OpenClaw:
1. 提取关键词 → "交报告", "买礼物"
2. 调用：flashmemo_update.py --keywords "交报告" "买礼物" --status "完成"
3. 回复：✅ 已更新 2 条记录
```

---

## 📊 示例对话

### 示例 1：记录 + 查询

```
用户：中午吃饭花了 25 元

OpenClaw:
1. 理解 → account，支出 25 元
2. 调用：flashmemo_store.py --category account --text "支出 - 午餐 -25.00"
3. 回复：✅ 已记录：支出 - 午餐 -25.00

用户：今天花了多少钱

OpenClaw:
1. 理解 → 查询今日账目汇总
2. 调用：flashmemo_summary.py --period today
3. 回复：💰 今日汇总：支出¥25.00
```

### 示例 2：复杂场景

```
用户：上午完成项目报告，中午请客户吃饭 500 元，下午 3 点开会

OpenClaw:
1. 理解 → 3 条内容：
   - work: "上午完成项目报告"
   - account: "支出 - 商务宴请 -500.00"（理解是工作相关）
   - memo: "下午 3 点开会"（紧急）

2. 调用 3 次存储脚本

3. 回复：
   ✅ 已记录 3 项：
   💼 工作：上午完成项目报告
   💰 账目：支出 - 商务宴请 -500.00
   📌 备忘：代办 - 紧急 - 下午 3 点开会
```

### 示例 3：备忘更新（新增）

```
用户：我有什么待办

OpenClaw:
1. 调用：flashmemo_query.py --category memo
2. 回复：
   📌 待办事项：
   🔴 紧急：明天下午 5 点前交报告
   🟡 重要：下周一妈妈生日买礼物

用户：交报告和买礼物都完成了

OpenClaw:
1. 调用：flashmemo_update.py --keywords "交报告" "买礼物" --status "完成"
2. 回复：
   ✅ 已更新 2 条记录：
   🎉 已完成：
    ✓ 明天下午 5 点前交报告
    ✓ 下周一妈妈生日买礼物
```

---

## 🎯 快速决策卡片（OpenClaw 必读）

**遇到以下情况，无脑用 FlashMemo：**

| 用户说... | 第一反应 |
|----------|---------|
| "提醒我 XXX" | ✅ flashmemo_store.py (memo) |
| "记得做 XXX" | ✅ flashmemo_store.py (memo) |
| "明天/下午/晚上做 XXX" | ✅ flashmemo_store.py (memo) |
| "有待办/任务" | ✅ flashmemo_query.py (memo) |
| "花了/买了 XXX 元" | ✅ flashmemo_store.py (account) |
| "今天花了多少" | ✅ flashmemo_summary.py |
| "帮我记一下 XXX" | ✅ flashmemo_store.py (work/life/memo) |

**唯一用飞书日历的情况：**
- 用户明确说："在日历里添加"、"创建日程"、"约会议"

**唯一用飞书任务的情况：**
- 用户明确说："创建飞书任务"、"用任务管理"

---

**版本**: v3.2  
**架构**: OpenClaw 主导 + 工具集  
**日期**: 2026-03-11  
**新增功能**: 备忘状态更新（代办→完成）  
**本次更新**: 强化优先级与排他性规则，明确禁止在备忘/待办/提醒场景使用飞书日历/任务
