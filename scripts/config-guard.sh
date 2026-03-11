#!/bin/bash
# OpenClaw 配置保护管理器
# 用法：
#   ./config-guard.sh start [minutes]  - 启动回滚保护
#   ./config-guard.sh success          - 标记修改成功，取消回滚
#   ./config-guard.sh status           - 查看保护状态

set -e

WORKSPACE="$HOME/.openclaw/workspace"
ROLLBACK_SCRIPT="$WORKSPACE/scripts/config-rollback.sh"
PID_FILE="/tmp/openclaw-config-guard.pid"
STATE_FILE="/tmp/openclaw-config-guard.state"

log() {
    echo "[$(date '+%Y-%m-%d %H:%M:%S')] $1"
}

case "$1" in
    start)
        TIMEOUT=${2:-5}
        log "🛡️ 启动配置保护（${TIMEOUT}分钟倒计时）..."
        
        # 检查是否有正在运行的保护
        if [ -f "$PID_FILE" ]; then
            OLD_PID=$(cat "$PID_FILE")
            if kill -0 "$OLD_PID" 2>/dev/null; then
                log "⚠️ 已有保护进程运行 (PID: $OLD_PID)，先停止它"
                kill "$OLD_PID" 2>/dev/null || true
                sleep 1
            fi
            rm -f "$PID_FILE"
        fi
        
        # 保存当前状态
        echo "protected" > "$STATE_FILE"
        echo "$(date +%s)" >> "$STATE_FILE"
        
        # 后台启动回滚脚本
        nohup "$ROLLBACK_SCRIPT" "$TIMEOUT" > /tmp/openclaw-rollback-console.log 2>&1 &
        ROLLBACK_PID=$!
        echo "$ROLLBACK_PID" > "$PID_FILE"
        
        log "✅ 保护已启动 (PID: $ROLLBACK_PID)"
        log "📝 如需取消回滚，运行：$0 success"
        ;;
        
    success)
        if [ -f "$PID_FILE" ]; then
            GUARD_PID=$(cat "$PID_FILE")
            if kill -0 "$GUARD_PID" 2>/dev/null; then
                log "✅ 修改成功，取消回滚保护..."
                kill "$GUARD_PID" 2>/dev/null || true
                pkill -P "$GUARD_PID" 2>/dev/null || true  # 杀死子进程
                rm -f "$PID_FILE" "$STATE_FILE"
                
                # 提交改动到 git
                cd "$WORKSPACE"
                if [ -n "$(git status --porcelain)" ]; then
                    log "📦 提交配置改动到 git..."
                    git add -A
                    git commit -m "config: $(date '+%Y-%m-%d %H:%M') 配置更新" || true
                    log "✅ 配置已提交"
                else
                    log "ℹ️  无改动需要提交"
                fi
                
                log "✅ 保护已解除"
            else
                log "ℹ️  保护进程已不存在"
                rm -f "$PID_FILE" "$STATE_FILE"
            fi
        else
            log "ℹ️  无活跃的保护进程"
        fi
        ;;
        
    status)
        if [ -f "$PID_FILE" ]; then
            GUARD_PID=$(cat "$PID_FILE")
            if kill -0 "$GUARD_PID" 2>/dev/null; then
                if [ -f "$STATE_FILE" ]; then
                    START_TIME=$(sed -n '2p' "$STATE_FILE")
                    NOW=$(date +%s)
                    ELAPSED=$((NOW - START_TIME))
                    log "🛡️ 保护进行中 (PID: $GUARD_PID)"
                    log "⏱️  已运行：${ELAPSED}秒"
                else
                    log "🛡️ 保护进行中 (PID: $GUARD_PID)"
                fi
                log "📝 如需取消回滚，运行：$0 success"
            else
                log "ℹ️  保护进程已停止（残留 PID 文件）"
                rm -f "$PID_FILE" "$STATE_FILE"
            fi
        else
            log "✅ 无活跃的保护进程"
        fi
        ;;
        
    *)
        echo "用法：$0 {start [minutes]|success|status}"
        echo ""
        echo "命令说明:"
        echo "  start [minutes]  - 启动回滚保护（默认 5 分钟）"
        echo "  success          - 标记修改成功，取消回滚并提交改动"
        echo "  status           - 查看保护状态"
        exit 1
        ;;
esac
