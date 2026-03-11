#!/bin/bash
# OpenClaw 自动备份脚本
# 每天凌晨 2 点执行，保留最近 7 天的备份

set -e

BACKUP_DIR="$HOME/.openclaw/backups"
TIMESTAMP=$(date +%Y%m%d-%H%M%S)
BACKUP_FILE="$BACKUP_DIR/openclaw-backup-$TIMESTAMP.tar.gz"
LOG_FILE="$BACKUP_DIR/backup.log"

log() {
    echo "[$(date '+%Y-%m-%d %H:%M:%S')] $1" | tee -a "$LOG_FILE"
}

log "=== 开始备份 OpenClaw 配置 ==="

# 创建备份目录
mkdir -p "$BACKUP_DIR"

# 执行备份（仅配置文件，不包含 workspace）
log "创建备份归档..."
openclaw backup create \
    --only-config \
    --output "$BACKUP_FILE" 2>&1 | tee -a "$LOG_FILE"

if [ -f "$BACKUP_FILE" ]; then
    BACKUP_SIZE=$(du -h "$BACKUP_FILE" | cut -f1)
    log "✅ 备份成功：$BACKUP_FILE (大小：$BACKUP_SIZE)"
    
    # 验证备份
    log "验证备份完整性..."
    if openclaw backup verify "$BACKUP_FILE" 2>&1 | tee -a "$LOG_FILE"; then
        log "✅ 备份验证通过"
    else
        log "❌ 备份验证失败，请检查"
        exit 1
    fi
else
    log "❌ 备份文件创建失败"
    exit 1
fi

# 清理旧备份（保留最近 7 天）
log "清理 7 天前的旧备份..."
find "$BACKUP_DIR" -name "openclaw-backup-*.tar.gz" -mtime +7 -delete 2>&1 | tee -a "$LOG_FILE"
DELETED_COUNT=$(find "$BACKUP_DIR" -name "openclaw-backup-*.tar.gz" -mtime +7 | wc -l)
log "已删除 $DELETED_COUNT 个旧备份"

# 保留最近的 10 个备份（即使超过 7 天）
cd "$BACKUP_DIR"
ls -t openclaw-backup-*.tar.gz 2>/dev/null | tail -n +11 | xargs -r rm -f
log "保留最近 10 个备份"

log "=== 备份完成 ==="
log ""
