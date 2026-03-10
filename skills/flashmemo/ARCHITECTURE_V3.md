# FlashMemo v3.0 - 工具集架构

## 🎯 架构革新

### v1.0 ❌ 错误架构
```
FlashMemo skill → 尝试调用 AI API → 失败 → Fallback
```
**问题**：Skill 自己调用模型，职责混乱

### v2.0 ❌ 请求式架构
```
FlashMemo → 提交 AI 请求 → OpenClaw 捕获 → 返回结果
```
**问题**：还是需要 OpenClaw 实现捕获机制

### v3.0 ✅ 正确架构
```
OpenClaw → 阅读 FlashMemo 文档 → 使用自己的模型处理 → 调用 FlashMemo 工具
```
**正确**：OpenClaw 主导，FlashMemo 是纯工具集

---

## 📐 新架构设计

### 职责分离

| 组件 | 职责 |
|------|------|
| **OpenClaw** | AI 能力、任务规划、工具调用 |
| **FlashMemo** | 存储、查询、汇总工具集 |

### 工作流程

```
用户："中午吃饭 25 元，下午开会"
    ↓
OpenClaw（使用自己的模型）
    ↓
理解 → 2 条内容：
  1. "吃饭 25 元" → account
  2. "下午开会" → work
    ↓
调用 FlashMemo 工具：
  python3 flashmemo_store.py --category account --text "支出 - 午餐 -25.00"
  python3 flashmemo_store.py --category work --text "下午开会"
    ↓
回复用户："✅ 已记录 2 项内容"
```

---

## 🛠️ 工具集

### 1. flashmemo_store.py

**功能**：存储记录到文件

**用法**：
```bash
python3 flashmemo_store.py \
  --channel "Feishu" \
  --user-id "ou_xxx" \
  --category "work|life|account|memo" \
  --text "内容" \
  --urgency "紧急"  # 仅 memo
```

### 2. flashmemo_query.py

**功能**：查询记录

**用法**：
```bash
# 查询今日
python3 flashmemo_query.py \
  --channel "Feishu" --user-id "ou_xxx" \
  --category "account" --date today

# 查询日期范围
python3 flashmemo_query.py \
  --channel "Feishu" --user-id "ou_xxx" \
  --category "account" \
  --start-date "2026-03-01" --end-date "2026-03-10"
```

### 3. flashmemo_summary.py

**功能**：汇总统计

**用法**：
```bash
# 今日汇总
python3 flashmemo_summary.py \
  --channel "Feishu" --user-id "ou_xxx" \
  --period today

# 本周汇总
python3 flashmemo_summary.py \
  --channel "Feishu" --user-id "ou_xxx" \
  --period week
```

---

## 📊 测试结果

### 存储测试 ✅

```bash
# 存储工作记录
$ python3 flashmemo_store.py --channel test --user-id user1 \
  --category work --text "上午开会讨论 Q3 计划"

✅ 已存储到：/home/jimmy/Documents/FlashMemo/test/user1/work/2026/03/2026-03-10.md
```

### 查询测试 ✅

```bash
$ python3 flashmemo_query.py --channel test --user-id user1 \
  --category account --date today

2026-03-10.14:40:30: 支出 - 午餐 -25.00
2026-03-10.14:40:30: 收入 - 兼职稿费 -500.00
```

### 汇总测试 ✅

```bash
$ python3 flashmemo_summary.py --channel test --user-id user1 --period today

💰 账目汇总 [2026-03-10 ~ 2026-03-10]
总收入：¥500.00
总支出：¥25.00
结余：¥475.00

明细 (2 条):
  收入：收入 - 兼职稿费 -500.00 ¥500.00
  支出：支出 - 午餐 -25.00 ¥25.00
```

### 备忘测试 ✅

```bash
$ python3 flashmemo_query.py --channel test --user-id user1 \
  --category memo

2026-03-10.14:40:31: 代办 - 紧急 - 明天下午 5 点前提交报告
```

---

## 📋 OpenClaw 使用指南

### 场景 1：记录内容

**用户**："中午吃饭 25 元，下午开会"

**OpenClaw 应该**：
1. 使用自己的模型理解 → 2 条内容
2. 分类 → account, work
3. 调用工具：
```bash
flashmemo_store.py --category account --text "支出 - 午餐 -25.00"
flashmemo_store.py --category work --text "下午开会"
```
4. 回复："✅ 已记录 2 项"

### 场景 2：查询汇总

**用户**："今天花了多少钱"

**OpenClaw 应该**：
1. 理解意图 → 查询今日账目
2. 调用工具：
```bash
flashmemo_summary.py --channel {channel} --user-id {user_id} --period today
```
3. 整理输出并回复

### 场景 3：查询备忘

**用户**："我有什么待办"

**OpenClaw 应该**：
1. 理解意图 → 查询备忘
2. 调用工具：
```bash
flashmemo_query.py --channel {channel} --user-id {user_id} --category memo
```
3. 按紧急程度整理并回复

---

## 📁 文件结构

```
flashmemo/
├── SKILL.md                    # 使用文档（OpenClaw 阅读）
├── README.md                   # 使用说明
├── FINAL_TEST_REPORT.md        # 测试报告
├── AI_REQUEST_ARCHITECTURE.md  # 架构说明
├── scripts/
│   ├── flashmemo_store.py      # 存储脚本 ✅
│   ├── flashmemo_query.py      # 查询脚本 ✅
│   ├── flashmemo_summary.py    # 汇总脚本 ✅
│   └── ...
└── references/
    └── ...
```

---

## 🎯 优势

| 特性 | 旧架构 | 新架构 |
|------|--------|--------|
| **职责清晰** | ❌ | ✅ |
| **OpenClaw 主导** | ❌ | ✅ |
| **Skill 简洁** | ❌ | ✅ |
| **易于维护** | ❌ | ✅ |
| **无需 API 调用** | ❌ | ✅ |

---

## 🚀 下一步

OpenClaw 需要：
1. 阅读 `SKILL.md` 了解工具用法
2. 使用自己的模型进行智能分类
3. 调用相应的工具脚本
4. 整理工具输出并回复用户

**FlashMemo 已准备好作为纯工具集！** ✅

---

**版本**: v3.0  
**架构**: 工具集  
**日期**: 2026-03-10  
**状态**: ✅ 完成
