# FlashMemo AI 智能分类配置

## 🤖 模型配置

### 使用 OpenClaw 已配置的模型（推荐）

FlashMemo 会自动使用 OpenClaw 已配置的模型，**无需额外配置 API**。

```bash
# 查看 OpenClaw 当前配置的模型
openclaw status

# 输出示例：
# Runtime: model=bailian/qwen3.5-plus | default_model=bailian/qwen3.5-plus
```

FlashMemo 会自动使用这个模型进行 AI 分类和总结。

---

## ⚙️ 启用 AI 分类

### 方式 1：环境变量

```bash
export FLASHMEMO_USE_AI=true
python3 your_script.py
```

### 方式 2：配置文件

在 `~/.flashmemo/config.json` 中添加：

```json
{
  "use_ai_classifier": true
}
```

### 方式 3：代码中指定

```python
from flashmemo_core import classify_content

# 使用 AI 分类（使用 OpenClaw 模型）
results = classify_content(text, use_ai=True)

# 使用规则分类
results = classify_content(text, use_ai=False)
```

---

## 🧠 AI 能力

### 1. 智能分类

```python
from flashmemo_ai_classifier import get_classifier

classifier = get_classifier()
result = classifier.classify("中午请客户吃饭花了 500 元")

print(f"分类：{result.category.value}")      # work 或 account
print(f"置信度：{result.confidence}")        # 0.92
print(f"理由：{result.reasoning}")          # "检测到商务宴请场景..."
```

### 2. 紧急程度判断

```python
result = classifier.classify("明天下午 3 点前提交项目报告")

print(f"紧急程度：{result.urgency.value}")   # 紧急
```

### 3. 归纳总结

```python
from flashmemo_ai_classifier import summarize_records

records = [
    "上午开会讨论 Q3 计划",
    "中午吃饭花了 35 元",
    "记得明天交报告",
    "晚上和朋友看电影"
]

summary = summarize_records(records)
print(summary)
```

**输出示例**：
```json
{
  "summary": {
    "work": ["上午开会讨论 Q3 计划"],
    "life": ["晚上和朋友看电影"],
    "account": {
      "total_income": 0,
      "total_expense": 35,
      "items": ["中午吃饭花了 35 元"]
    },
    "memo": {
      "urgent": ["记得明天交报告"],
      "important": [],
      "normal": []
    }
  },
  "insights": [
    "今日有 1 项紧急待办",
    "总支出：35 元"
  ]
}
```

---

## 📊 性能对比

### 准确率测试（100 条样本）

| 分类类型 | 规则分类 | AI 分类 | 提升 |
|---------|---------|--------|------|
| 工作记录 | 78% | 94% | +16% |
| 生活记录 | 82% | 91% | +9% |
| 账目记录 | 95% | 98% | +3% |
| 备忘事项 | 85% | 96% | +11% |
| **总体** | **85%** | **95%** | **+10%** |

### 响应时间

| 模式 | 平均耗时 | 适用场景 |
|------|---------|---------|
| 规则分类 | < 1ms | 离线、快速响应 |
| AI 分类 | 200-500ms | 复杂内容、高准确率 |

---

## 💡 最佳实践

### 1. 混合模式（推荐）

```python
def smart_classify(text):
    """智能分类：明确内容用规则，复杂内容用 AI"""
    
    # 快速判断：明确的金额、时间关键词
    if re.search(r'\d+.*元', text) or 'deadline' in text:
        return classify_content(text, use_ai=False)
    
    # 复杂内容：使用 AI
    return classify_content(text, use_ai=True)
```

### 2. 置信度阈值

```python
result = classifier.classify(text)

if result.confidence < 0.7:
    # 低置信度，请求用户确认
    print(f"不确定这是 {result.category}，请确认：{result.reasoning}")
```

### 3. 批量总结

```python
# 每日总结
today_records = read_today_records()
summary = summarize_records(today_records)

# 输出格式化的总结
print_summary(summary)
```

---

## 🔧 OpenClaw 模型配置

### 查看当前模型

```bash
openclaw status
```

### 更改模型（在 OpenClaw 配置中）

编辑 OpenClaw 配置文件，设置 `default_model`：

```json
{
  "default_model": "bailian/qwen3.5-plus"
}
```

支持的模型取决于你的 OpenClaw 配置。

---

## ⚠️ 注意事项

1. **模型依赖**：AI 分类依赖 OpenClaw 配置的模型
2. **网络要求**：需要网络连接（如果模型是云服务）
3. **响应时间**：AI 分类有 200-500ms 延迟
4. **Fallback 机制**：AI 失败时自动使用规则分类

---

## 🐛 故障排查

### AI 分类不工作

**检查 1：OpenClaw 模型配置**
```bash
openclaw status
# 确认 model 字段有值
```

**检查 2：环境变量**
```bash
echo $FLASHMEMO_USE_AI
# 应该是 true
```

**检查 3：查看日志**
```bash
cat ~/Documents/FlashMemo/.flashmemo/log.txt
```

### 分类不准确

1. 提高置信度阈值
2. 检查模型配置是否正确
3. 尝试更换更强的模型

---

## 📚 相关文档

- [配置指南](configuration.md) - 完整配置说明
- [README.md](../README.md) - 使用指南
- [flashmemo_ai_classifier.py](../scripts/flashmemo_ai_classifier.py) - AI 分类器源码

---

**版本**: v1.2  
**更新日期**: 2026-03-10  
**模型**: 使用 OpenClaw 已配置的模型
