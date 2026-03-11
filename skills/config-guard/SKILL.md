# config-guard - 配置自动回滚保护

## 概述

为 OpenClaw 配置文件修改提供自动回滚保护机制，避免配置改崩后无法恢复。

## 核心原理

通过独立的后台回滚进程 + Git 版本控制实现：

1. **修改前**：启动回滚保护，创建 5 分钟倒计时的独立进程
2. **修改后成功**：取消回滚保护，提交改动到 Git
3. **修改后失败**：Gateway 崩溃无法取消保护 → 5 分钟后自动回滚配置并重启

## 工作流程

```
┌─────────────────────────────────────────────────────────────┐
│  1️⃣ 设置保护                                                  │
│     $ ./scripts/config-guard.sh start 5                      │
│     → 启动后台回滚进程（倒计时 5 分钟）                            │
└─────────────────────────────────────────────────────────────┘
                            ↓
┌─────────────────────────────────────────────────────────────┐
│  2️⃣ 执行修改                                                  │
│     - 修改配置文件 (openclaw.json 等)                         │
│     - 重启 Gateway: openclaw gateway restart                 │
└─────────────────────────────────────────────────────────────┘
                            ↓
                    ┌───────┴───────┐
                    ↓               ↓
            ┌───────────┐   ┌───────────┐
            │  成功 ✅   │   │  失败 ❌   │
            └───────────┘   └───────────┘
                    ↓               ↓
    ┌───────────────────────┐  ┌───────────────────────┐
    │ 取消回滚保护           │  │ 等待 5 分钟倒计时结束    │
    │ $ ./config-guard.sh   │  │ → 自动执行 git checkout │
    │   success             │  │ → 自动重启 gateway     │
    │ → 提交改动到 Git       │  │ → 回滚进程自动销毁     │
    └───────────────────────┘  └───────────────────────┘
```

## 使用方法

### 启动保护（修改配置前）

```bash
cd ~/.openclaw/workspace

# 启动保护，默认 5 分钟倒计时
./scripts/config-guard.sh start

# 或指定倒计时时间（分钟）
./scripts/config-guard.sh start 10
```

### 标记成功（确认配置正常后）

```bash
# 取消回滚保护并提交改动
./scripts/config-guard.sh success
```

### 查看状态

```bash
# 查看当前保护状态
./scripts/config-guard.sh status
```

## 集成到 AI 助手工作流

当 AI 助手需要修改配置文件时，应自动执行以下流程：

```bash
# 1. 修改前启动保护
~/.openclaw/workspace/scripts/config-guard.sh start 5

# 2. 执行配置修改
# ... 修改 openclaw.json 等文件 ...

# 3. 重启 Gateway
openclaw gateway restart

# 4. 验证 Gateway 是否正常
openclaw gateway status

# 5. 如果正常，取消保护并提交
~/.openclaw/workspace/scripts/config-guard.sh success
```

## 受保护的核心配置文件

以下文件应纳入 Git 版本管理（在 `.gitignore` 中已排除常变文件）：

- `~/.openclaw/openclaw.json` - 主配置文件
- `~/.openclaw/workspace/*.md` - 核心文档（SOUL.md, AGENTS.md, USER.md 等）
- `~/.openclaw/workspace/scripts/` - 脚本文件
- `~/.openclaw/workspace/skills/` - Skill 定义

## 排除的文件（不纳入版本管理）

- `memory/*.md` - 每日记忆文件
- `MEMORY.md` - 长期记忆（频繁更新）
- `logs/` - 日志文件
- `*.log` - 临时日志
- `credentials/` - 凭证文件（敏感）
- `node_modules/` - 依赖缓存

## 日志查看

回滚脚本的日志保存在：
```bash
# 查看最近的回滚日志
ls -lt /tmp/openclaw-rollback-*.log | head -1

# 查看控制台输出
cat /tmp/openclaw-rollback-console.log
```

## 手动回滚

如需手动回滚到上一个版本：

```bash
cd ~/.openclaw/workspace
git checkout -- .
openclaw gateway restart
```

## 查看 Git 历史

```bash
cd ~/.openclaw/workspace
git log --oneline -10
```

## 注意事项

1. **倒计时时间**：建议设置为 5-10 分钟，给足验证时间
2. **不要同时运行多个保护进程**：脚本会自动检测并停止旧进程
3. **定期清理日志**：`/tmp/openclaw-rollback-*.log` 会累积，定期清理
4. **敏感信息**：凭证文件已加入 `.gitignore`，不会提交到 Git

## 故障排查

### 回滚进程未自动销毁
```bash
# 查看是否有残留进程
ps aux | grep config-rollback

# 手动清理
rm -f /tmp/openclaw-config-guard.pid /tmp/openclaw-config-guard.state
```

### Gateway 重启后仍异常
```bash
# 查看详细日志
tail -100 /tmp/openclaw/openclaw-$(date +%Y-%m-%d).log

# 手动回滚
cd ~/.openclaw/workspace
git log --oneline -5  # 查看历史
git revert HEAD       # 或回退到特定版本
```

## 版本历史

- **v1.0** (2026-03-11): 初始版本，基础回滚功能
