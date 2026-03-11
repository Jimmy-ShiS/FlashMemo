#!/bin/bash
# OpenClaw 配置自动回滚脚本
# 用法：./config-rollback.sh [timeout_minutes]

set -e

TIMEOUT_MINUTES=${1:-5}
WORKSPACE="$HOME/.openclaw/workspace"
LOG_FILE="/tmp/openclaw-rollback-$(date +%Y%m%d-%H%M%S).log"

log() {
    echo "[$(date '+%Y-%m-%d %H:%M:%S')] $1" | tee -a "$LOG_FILE"
}

log "=== OpenClaw 配置回滚脚本启动 ==="
log "工作目录：$WORKSPACE"
log "超时时间：$TIMEOUT_MINUTES 分钟"
log "日志文件：$LOG_FILE"

# 等待指定时间（倒计时）
log "开始倒计时 ${TIMEOUT_MINUTES} 分钟..."
SECONDS_TO_WAIT=$((TIMEOUT_MINUTES * 60))
sleep $SECONDS_TO_WAIT

log "倒计时结束，开始检查 Gateway 状态..."

# 检查 Gateway 是否正常运行
if openclaw gateway status 2>&1 | grep -q "RPC probe: ok"; then
    log "✅ Gateway 运行正常，无需回滚，退出"
    exit 0
fi

log "❌ Gateway 异常，开始回滚配置..."

cd "$WORKSPACE"

# 回滚所有未提交的修改
log "执行 git 回滚..."
git checkout -- . 2>&1 | tee -a "$LOG_FILE" || {
    log "⚠️ git checkout 失败，继续尝试其他方式"
}

# 清理未跟踪的文件（可选，谨慎使用）
# git clean -fd 2>&1 | tee -a "$LOG_FILE"

log "配置已回滚到上一个提交版本"

# 重启 Gateway
log "重启 Gateway..."
openclaw gateway restart 2>&1 | tee -a "$LOG_FILE"

# 等待 Gateway 启动
log "等待 Gateway 启动..."
sleep 5

# 验证 Gateway 是否正常
if openclaw gateway status 2>&1 | grep -q "RPC probe: ok"; then
    log "✅ Gateway 重启成功，回滚完成"
else
    log "❌ Gateway 重启后仍异常，请手动检查"
    exit 1
fi

log "=== 回滚脚本执行完毕 ==="
