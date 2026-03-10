#!/usr/bin/env python3
"""
FlashMemo 查询脚本
查询指定条件的记录

支持跨平台配置（同 flashmemo_store.py）
"""

import argparse
import sys
import os
import json
from pathlib import Path
from datetime import datetime, timedelta


def get_base_path(args_base_path=None) -> Path:
    """获取基础路径（支持跨平台配置）"""
    if args_base_path:
        return Path(args_base_path).expanduser()
    
    env_path = os.environ.get('FLASHMEMO_BASE_PATH')
    if env_path:
        return Path(env_path).expanduser()
    
    config_file = Path.home() / ".flashmemo" / "config.json"
    if config_file.exists():
        try:
            with open(config_file, "r", encoding="utf-8") as f:
                config = json.load(f)
                if "base_path" in config:
                    return Path(config["base_path"]).expanduser()
        except Exception:
            pass
    
    return Path.home() / "Documents" / "FlashMemo"


def main():
    parser = argparse.ArgumentParser(description='FlashMemo 查询脚本')
    parser.add_argument('--channel', required=True, help='渠道名称')
    parser.add_argument('--user-id', required=True, help='用户 ID')
    parser.add_argument('--category', required=True, choices=['work', 'life', 'account', 'memo'], help='分类')
    parser.add_argument('--date', default=None, help='日期（today/yesterday/2026-03-10）')
    parser.add_argument('--start-date', default=None, help='开始日期')
    parser.add_argument('--end-date', default=None, help='结束日期')
    parser.add_argument('--urgency', choices=['紧急', '重要', '普通'], default=None, help='紧急程度（仅 memo）')
    parser.add_argument('--base-path', default=None, help='基础路径（可选）')
    
    args = parser.parse_args()
    
    # 获取基础路径
    base_dir = get_base_path(args.base_path)
    user_dir = base_dir / args.channel / args.user_id
    
    if not user_dir.exists():
        print(f"错误：用户目录不存在：{user_dir}", file=sys.stderr)
        sys.exit(1)
    
    # 处理日期
    if args.category == "memo":
        # 备忘查询
        memo_file = user_dir / "ImportantMemo.md"
        if not memo_file.exists():
            print("暂无备忘记录")
            return
        
        with open(memo_file, "r", encoding="utf-8") as f:
            lines = [l.strip() for l in f.readlines() if l.strip()]
        
        # 按紧急程度过滤
        if args.urgency:
            lines = [l for l in lines if f"-{args.urgency}-" in l]
        
        # 输出
        if not lines:
            print("暂无符合条件的备忘")
            return
        
        for line in lines:
            print(line)
    
    else:
        # 其他分类查询
        dates = get_date_range(args.date, args.start_date, args.end_date)
        
        all_records = []
        for date_str in dates:
            date_obj = datetime.strptime(date_str, "%Y-%m-%d")
            year = date_obj.strftime("%Y")
            month = date_obj.strftime("%m")
            
            file_path = user_dir / args.category / year / month / f"{date_str}.md"
            if file_path.exists():
                with open(file_path, "r", encoding="utf-8") as f:
                    lines = [l.strip() for l in f.readlines() if l.strip()]
                    all_records.extend(lines)
        
        if not all_records:
            print("暂无符合条件的记录")
            return
        
        # 输出
        for record in all_records:
            print(record)


def get_date_range(date_arg, start_date_arg, end_date_arg):
    """获取日期范围"""
    today = datetime.now().date()
    
    if date_arg:
        if date_arg == "today":
            return [today.strftime("%Y-%m-%d")]
        elif date_arg == "yesterday":
            yesterday = today - timedelta(days=1)
            return [yesterday.strftime("%Y-%m-%d")]
        else:
            # 假设是 YYYY-MM-DD 格式
            return [date_arg]
    
    elif start_date_arg and end_date_arg:
        start = datetime.strptime(start_date_arg, "%Y-%m-%d").date()
        end = datetime.strptime(end_date_arg, "%Y-%m-%d").date()
        
        dates = []
        current = start
        while current <= end:
            dates.append(current.strftime("%Y-%m-%d"))
            current += timedelta(days=1)
        
        return dates
    
    else:
        # 默认查询今天
        return [today.strftime("%Y-%m-%d")]


if __name__ == "__main__":
    main()
