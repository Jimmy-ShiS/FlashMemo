#!/bin/bash
# OpenClaw 备份管理命令

BACKUP_DIR="$HOME/.openclaw/backups"

case "$1" in
    list)
        echo "📦 OpenClaw 备份列表："
        echo ""
        ls -lht "$BACKUP_DIR"/openclaw-backup-*.tar.gz 2>/dev/null | head -10 || echo "暂无备份"
        echo ""
        echo "💾 备份目录：$BACKUP_DIR"
        ;;
    run)
        echo "🚀 手动执行备份..."
        ~/.openclaw/workspace/scripts/auto-backup.sh
        ;;
    status)
        echo "⏰ 备份定时任务状态："
        systemctl --user status openclaw-backup.timer 2>&1 | grep -E "(Loaded|Active|Trigger)"
        ;;
    restore)
        if [ -z "$2" ]; then
            echo "用法：$0 restore <备份文件路径>"
            echo ""
            echo "最近的备份："
            ls -lt "$BACKUP_DIR"/openclaw-backup-*.tar.gz 2>/dev/null | head -5
            exit 1
        fi
        echo "🔄 从备份恢复：$2"
        openclaw backup verify "$2" && openclaw backup restore "$2"
        ;;
    *)
        echo "用法：$0 {list|run|status|restore <备份文件>}"
        echo ""
        echo "命令说明:"
        echo "  list    - 查看备份列表"
        echo "  run     - 手动执行备份"
        echo "  status  - 查看定时任务状态"
        echo "  restore - 从备份恢复"
        exit 1
        ;;
esac
