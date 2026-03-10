# FlashMemo AI 架构改进 - 请求式设计

## 🎯 问题反思

### ❌ 之前的错误架构

```
FlashMemo skill → 尝试调用 OpenClaw API → 失败 → Fallback
```

**问题**：
- Skill 自己在尝试调用模型
- 违反了职责分离原则
- 需要处理各种 API 调用细节（端口、认证、会话）
- 耦合度高，难以维护

---

### ✅ 正确的架构

```
用户输入 → OpenClaw → FlashMemo skill → 需要 AI → 提交请求 → OpenClaw 处理 → 返回结果
```

**原则**：
- OpenClaw 是**调用和规划的主导方**
- Skill **不应该直接调用模型**
- Skill 只需要**声明需要 AI 处理什么**
- OpenClaw 负责**捕获请求并使用模型处理**

---

## 🏗️ 新架构设计

### 请求式架构

```python
# FlashMemo skill 代码
def classify_content(text: str):
    # 1. 构建请求（不是调用）
    request = {
        "type": "flashmemo_ai_request",
        "action": "classify",
        "input": {"text": text},
        "prompt": "请分析以下内容并分类..."
    }
    
    # 2. 提交请求（通过 stdout）
    print(f"[FLASHMEMO_AI_REQUEST]\n{json.dumps(request)}\n[/FLASHMEMO_AI_REQUEST]")
    
    # 3. OpenClaw 捕获请求，使用模型处理
    # 4. OpenClaw 将结果返回给 skill
    response = capture_ai_response()
    
    # 5. 解析结果
    return parse_result(response)
```

---

## 📋 OpenClaw 需要实现的功能

### 1. 请求捕获机制

OpenClaw 应该监控 skill 的输出，捕获特殊格式的请求：

```python
# OpenClaw 侧的实现（伪代码）
def run_skill(skill_code, user_input):
    # 捕获 skill 的 stdout
    output = capture_stdout(lambda: skill_code(user_input))
    
    # 检查是否有 AI 请求
    ai_request = extract_ai_request(output)
    
    if ai_request:
        # 使用模型处理
        result = call_model(ai_request["prompt"])
        
        # 将结果返回给 skill
        return result
    
    # 没有 AI 请求，返回普通输出
    return output
```

### 2. 特殊标记格式

Skill 使用特殊标记输出 AI 请求：

```
[FLASHMEMO_AI_REQUEST]
{
  "type": "flashmemo_ai_request",
  "action": "classify",
  "input": {"text": "中午吃饭 25 元"},
  "prompt": "请分析..."
}
[/FLASHMEMO_AI_REQUEST]
```

OpenClaw 正则捕获：
```python
pattern = r'\[FLASHMEMO_AI_REQUEST\](.*?)\[/FLASHMEMO_AI_REQUEST\]'
```

---

## 🎯 优势

### 1. 职责清晰

| 组件 | 职责 |
|------|------|
| **FlashMemo skill** | 构建请求，处理业务逻辑 |
| **OpenClaw** | 捕获请求，调用模型，返回结果 |

### 2. 解耦合

- Skill 不需要知道模型 API 细节
- Skill 不需要处理端口、认证、会话
- OpenClaw 可以切换模型 provider，skill 无感知

### 3. 易于测试

```python
# 测试 skill 时，可以 mock AI 响应
def test_classify():
    mock_response = {"category": "account", "confidence": 0.95}
    result = classify_content("吃饭 25 元", mock_response=mock_response)
    assert result.category == "account"
```

### 4. 统一 AI 能力

所有 skill 使用统一的请求格式，OpenClaw 可以：
- 缓存 AI 结果
- 限流
- 记录日志
- 统一计费

---

## 📝 实现示例

### FlashMemo skill 侧

```python
def classify_content(text: str):
    # 构建请求
    request = {
        "type": "flashmemo_ai_request",
        "action": "classify",
        "input": {"text": text},
        "prompt": """请分析以下内容并分类：
        
分类标准：
- work: 工作任务、会议、项目
- life: 日常生活、娱乐
- account: 金钱、消费
- memo: 待办、提醒

返回 JSON：
{"category": "...", "confidence": 0.0-1.0}"""
    }
    
    # 提交请求
    print(f"[FLASHMEMO_AI_REQUEST]\n{json.dumps(request)}\n[/FLASHMEMO_AI_REQUEST]")
    
    # 等待 OpenClaw 返回结果（通过某种机制）
    response = wait_for_ai_response()
    
    # 解析结果
    return parse_result(response)
```

### OpenClaw 侧（需要实现）

```python
# 在 OpenClaw 的 skill 执行器中
def execute_skill(skill_path, user_input):
    import subprocess
    import re
    
    # 运行 skill
    process = subprocess.run(
        ['python3', skill_path, user_input],
        capture_output=True,
        text=True
    )
    
    output = process.stdout
    
    # 检查 AI 请求
    ai_match = re.search(
        r'\[FLASHMEMO_AI_REQUEST\](.*?)\[/FLASHMEMO_AI_REQUEST\]',
        output,
        re.DOTALL
    )
    
    if ai_match:
        request = json.loads(ai_match.group(1))
        
        # 使用模型处理
        model_response = call_openclaw_model(request["prompt"])
        
        # 解析并返回
        result = json.loads(model_response)
        return result
    
    # 没有 AI 请求，返回普通输出
    return output
```

---

## 🚀 下一步

### OpenClaw 需要实现

1. **请求捕获机制**
   - 监控 skill 输出
   - 正则匹配特殊标记
   - 提取 JSON 请求

2. **模型调用**
   - 使用已配置的模型
   - 处理超时、错误
   - 返回结果给 skill

3. **结果注入**
   - 将 AI 结果返回给 skill
   - 或通过某种 IPC 机制

### FlashMemo 需要修改

1. **移除直接 API 调用**
   - 删除 `_call_openclaw_model`
   - 删除 HTTP 请求代码

2. **使用请求式架构**
   - 构建请求对象
   - 通过 stdout 输出
   - 等待响应

3. **添加 Fallback**
   - AI 不可用时使用规则
   - 保持向后兼容

---

## 📊 对比

| 特性 | 调用式（之前） | 请求式（现在） |
|------|--------------|--------------|
| **职责** | Skill 调用模型 | OpenClaw 主动提供 |
| **耦合度** | 高 | 低 |
| **维护成本** | 高 | 低 |
| **可测试性** | 难 | 易 |
| **扩展性** | 难 | 易 |

---

**版本**: v3.0  
**架构**: 请求式  
**日期**: 2026-03-10  
**状态**: ⏸️ 待 OpenClaw 实现请求捕获
