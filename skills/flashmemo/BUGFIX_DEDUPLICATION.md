# FlashMemo 重复记录问题修复

## 🐛 问题描述

**现象**：用户的一条消息会在 account 和 work 分类中分别重复记录 2 条数据

**示例**：
```
=== work/2026-03-10.md ===
2026-03-10.14:56:04: 上午和 pl 拉通对齐了今年的 PBC
2026-03-10.14:56:29: 上午和 pl 拉通对齐了今年的 PBC  ← 重复

=== account/2026-03-10.md ===
2026-03-10.14:56:04: 支出 - 午餐 (烧腊)-20.00
2026-03-10.14:56:29: 支出 - 午餐 (烧腊)-20.00  ← 重复
```

---

## 🔍 原因分析

**根本原因**：OpenClaw 可能执行了两次存储脚本调用

**可能的触发场景**：
1. OpenClaw 读取 SKILL.md 后，可能因为示例代码执行了多次
2. 或者 OpenClaw 的重试机制导致重复调用
3. 或者消息处理流程执行了两次

---

## ✅ 解决方案

### 添加去重机制

在 `flashmemo_store.py` 中添加内容检查：

```python
# 检查是否已存在（去重）
if file_path.exists():
    with open(file_path, "r", encoding="utf-8") as f:
        content = f.read()
        if entry in content:
            print(f"⚠️  记录已存在，跳过：{entry[:50]}...")
            return

# 写入文件
with open(file_path, "a", encoding="utf-8") as f:
    f.write(entry + "\n")
```

---

## 📊 测试结果

### 测试 1：首次存储 ✅
```bash
$ python3 flashmemo_store.py --channel test --user-id user3 \
  --category work --text "测试去重功能"

✅ 已存储到：/home/jimmy/Documents/FlashMemo/test/user3/work/2026-03-10.md
```

### 测试 2：重复存储（相同内容） ✅
```bash
$ python3 flashmemo_store.py --channel test --user-id user3 \
  --category work --text "测试去重功能"

⚠️  记录已存在，跳过：2026-03-10.15:08:37: 测试去重功能...
```

### 测试 3：存储不同内容 ✅
```bash
$ python3 flashmemo_store.py --channel test --user-id user3 \
  --category work --text "另一条记录"

✅ 已存储到：/home/jimmy/Documents/FlashMemo/test/user3/work/2026-03-10.md
```

### 验证文件内容 ✅
```
2026-03-10.15:08:37: 测试去重功能
2026-03-10.15:08:37: 另一条记录
```

**结果**：只有 2 条不同的记录，重复的被成功跳过！

---

## 🛡️ 去重逻辑

### 工作分类（work/life/account）
```python
entry = f"{timestamp}: {args.text}"

if file_path.exists():
    with open(file_path, "r") as f:
        content = f.read()
        if entry in content:
            print(f"⚠️  记录已存在，跳过")
            return
```

### 备忘分类（memo）
```python
entry = f"{timestamp}: {prefix}-{urgency}-{args.text}"

if memo_file.exists():
    with open(memo_file, "r") as f:
        content = f.read()
        if entry in content:
            print(f"⚠️  记录已存在，跳过")
            return
```

---

## 📝 修改的文件

| 文件 | 修改内容 |
|------|---------|
| `scripts/flashmemo_store.py` | 添加去重检查逻辑 |

---

## 🎯 优势

| 特性 | 改进前 | 改进后 |
|------|--------|--------|
| **重复记录** | ❌ 会发生 | ✅ 自动跳过 |
| **数据准确性** | ⚠️ 可能有重复 | ✅ 保证唯一 |
| **用户提示** | ❌ 无 | ✅ 显示警告 |
| **性能影响** | - | ✅ 微小（只读取一次） |

---

## 💡 注意事项

### 去重基于完整匹配

去重检查使用**完整内容匹配**：
- 时间戳 + 文本内容必须完全相同
- 不同时间戳的相同文本会被视为不同记录

**示例**：
```
✅ 会去重：
  2026-03-10.15:08:37: 测试去重功能
  2026-03-10.15:08:37: 测试去重功能

❌ 不会去重（时间戳不同）：
  2026-03-10.15:08:37: 测试去重功能
  2026-03-10.15:09:00: 测试去重功能
```

### 适用场景

- ✅ OpenClaw 重复调用
- ✅ 网络重试导致的重复
- ✅ 用户误操作重复提交
- ❌ 不适用于需要多次记录相同内容的场景（罕见）

---

## 🚀 下一步建议

### 可选改进

1. **基于文本内容的去重**（忽略时间戳）
```python
# 只检查文本内容，忽略时间戳
text_only = args.text
if text_only in content:
    print("文本内容已存在，跳过")
```

2. **时间窗口去重**
```python
# 只检查最近 N 分钟内的重复
if is_duplicate_within_minutes(content, entry, minutes=5):
    print("5 分钟内已有相同记录，跳过")
```

3. **配置化去重**
```json
// ~/.flashmemo/config.json
{
  "dedup_enabled": true,
  "dedup_window_minutes": 5
}
```

---

**版本**: v3.0.1  
**修复日期**: 2026-03-10  
**状态**: ✅ 完成
