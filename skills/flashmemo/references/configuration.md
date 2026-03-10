# FlashMemo 配置指南

## 📋 配置方式（优先级从高到低）

### 1️⃣ 环境变量（最高优先级）

设置环境变量 `FLASHMEMO_BASE_PATH` 可覆盖所有配置：

**Linux/macOS:**
```bash
export FLASHMEMO_BASE_PATH="/path/to/your/FlashMemo"
```

**Windows (PowerShell):**
```powershell
$env:FLASHMEMO_BASE_PATH="C:\path\to\your\FlashMemo"
```

**Windows (CMD):**
```cmd
set FLASHMEMO_BASE_PATH=C:\path\to\your\FlashMemo
```

---

### 2️⃣ 配置文件

FlashMemo 会在以下位置查找配置文件（按优先级排序）：

1. **当前工作目录**: `./flashmemo_config.json`
2. **用户主目录**: `~/.flashmemo/config.json`
3. **应用数据目录**:
   - **Windows**: `%APPDATA%\FlashMemo\config.json`
   - **macOS**: `~/Library/Application Support/FlashMemo/config.json`
   - **Linux**: `~/.config/FlashMemo/config.json`

---

## ⚙️ 配置项说明

### `base_path` (字符串，可选)

自定义数据文件存储路径。

- **默认值**: `null`（使用系统默认路径）
- **默认路径**:
  - Windows: `C:\Users\{用户名}\Documents\FlashMemo`
  - macOS: `/Users/{用户名}/Documents/FlashMemo`
  - Linux: `/home/{用户名}/Documents/FlashMemo`

**示例**：
```json
{
  "base_path": "/mnt/data/FlashMemo"
}
```

或相对路径（相对于用户主目录）：
```json
{
  "base_path": "MyData/FlashMemo"
}
```

---

### `timezone` (字符串，可选)

时区设置，用于时间戳生成。

- **默认值**: `"Asia/Shanghai"`
- **格式**: IANA 时区名称

**常见时区**：
```json
{
  "timezone": "Asia/Shanghai"      // 中国标准时间
}
```
```json
{
  "timezone": "America/New_York"   // 美国东部时间
}
```
```json
{
  "timezone": "Europe/London"      // 英国时间
}
```

---

### `date_format` (字符串，可选)

日期格式（Python strftime 格式）。

- **默认值**: `"%Y-%m-%d"`
- **示例输出**: `2026-03-10`

**其他格式**：
```json
{
  "date_format": "%Y/%m/%d"        // 2026/03/10
}
```
```json
{
  "date_format": "%d-%m-%Y"        // 10-03-2026
}
```

---

### `time_format` (字符串，可选)

时间格式（Python strftime 格式）。

- **默认值**: `"%H:%M:%S"`
- **示例输出**: `14:30:25`

**其他格式**：
```json
{
  "time_format": "%H:%M"           // 14:30
}
```
```json
{
  "time_format": "%I:%M:%S %p"     // 02:30:25 PM
}
```

---

### `encoding` (字符串，可选)

文件编码格式。

- **默认值**: `"utf-8"`（推荐）
- **其他选项**: `"gbk"`, `"big5"`, `"latin-1"` 等

⚠️ **注意**: 修改编码可能导致已有文件读取问题，不建议更改。

---

### `backup_enabled` (布尔值，可选)

是否启用自动备份功能。

- **默认值**: `true`
- **说明**: 启用后，修改/删除操作会创建备份文件

---

### `backup_days` (整数，可选)

备份文件保留天数。

- **默认值**: `30`
- **说明**: 超过此天数的备份文件会被自动清理

---

## 📝 完整配置示例

### 示例 1：自定义路径（Linux）

```json
{
  "base_path": "/home/jimmy/Data/FlashMemo",
  "timezone": "Asia/Shanghai",
  "backup_enabled": true,
  "backup_days": 30
}
```

### 示例 2：自定义路径（Windows）

```json
{
  "base_path": "D:\\MyData\\FlashMemo",
  "timezone": "Asia/Shanghai",
  "date_format": "%Y-%m-%d",
  "time_format": "%H:%M:%S"
}
```

### 示例 3：使用相对路径

```json
{
  "base_path": "Documents/MyMemo",
  "timezone": "America/New_York"
}
```

### 示例 4：最小配置（仅修改路径）

```json
{
  "base_path": "/path/to/FlashMemo"
}
```

---

## 🔧 配置验证

运行以下命令验证配置是否正确加载：

```bash
cd ~/.openclaw/skills/flashmemo/scripts
python3 flashmemo_core.py
```

输出示例：
```
============================================================
FlashMemo 配置信息
============================================================
基础路径：/home/jimmy/Data/FlashMemo
日志文件：/home/jimmy/Data/FlashMemo/.flashmemo/log.txt
分类目录：['work', 'life', 'account']
备忘文件：ImportantMemo.md
操作系统：Linux 6.17.0-14-generic
Python 版本：3.10.12
============================================================
✅ 目录创建成功：['work', 'life', 'account']
```

---

## ⚠️ 常见问题

### Q1: 配置文件不生效？

**检查清单**：
1. 确认 JSON 格式正确（无语法错误）
2. 确认文件名为 `flashmemo_config.json`
3. 确认文件位于正确的目录
4. 检查是否有环境变量覆盖配置

### Q2: 如何查看当前使用的配置？

在 Python 脚本中调用：
```python
from flashmemo_core import get_config, print_config_info
print_config_info()
```

### Q3: 路径中包含中文或空格可以吗？

可以！FlashMemo 使用 Python 的 `pathlib` 处理路径，完全支持：
- 中文字符
- 空格
- 特殊符号（除 `/` 和 `\0` 外）

### Q4: 可以在网络驱动器上使用吗？

可以，但需确保：
1. 网络驱动器已正确挂载
2. 有读写权限
3. 网络连接稳定

---

## 🌍 跨平台兼容性

FlashMemo 已针对以下平台进行测试和优化：

| 平台 | 状态 | 备注 |
|------|------|------|
| Windows 10/11 | ✅ 完全支持 | 路径自动使用反斜杠 |
| macOS 11+ | ✅ 完全支持 | - |
| Ubuntu 20.04+ | ✅ 完全支持 | - |
| CentOS 7+ | ✅ 完全支持 | - |
| WSL2 | ✅ 完全支持 | 建议使用 Linux 路径 |

---

## 📚 相关文档

- [技能使用说明](../README.md)
- [分类规则](./classification_rules.md)
- [格式示例](./format_examples.md)
