#!/usr/bin/env python3
"""
FlashMemo 汇总脚本
汇总统计账目

支持跨平台配置（同 flashmemo_store.py）
"""

import argparse
import sys
import os
import json
import re
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
    parser = argparse.ArgumentParser(description='FlashMemo 汇总脚本')
    parser.add_argument('--channel', required=True, help='渠道名称')
    parser.add_argument('--user-id', required=True, help='用户 ID')
    parser.add_argument('--period', choices=['today', 'week', 'month'], default='today', help='统计周期')
    parser.add_argument('--start-date', default=None, help='开始日期')
    parser.add_argument('--end-date', default=None, help='结束日期')
    parser.add_argument('--base-path', default=None, help='基础路径（可选）')
    
    args = parser.parse_args()
    
    # 获取基础路径
    base_dir = get_base_path(args.base_path)
    # 渠道名称统一转小写，避免大小写不一致导致目录分散
    channel = args.channel.lower()
    user_dir = base_dir / channel / args.user_id
    
    account_dir = user_dir / "account"
    if not account_dir.exists():
        print("暂无账目记录")
        return
    
    # 获取日期范围
    dates = get_date_range(args.period, args.start_date, args.end_date)
    
    # 读取所有账目记录
    total_income = 0.0
    total_expense = 0.0
    details = []
    
    for date_str in dates:
        date_obj = datetime.strptime(date_str, "%Y-%m-%d")
        year = date_obj.strftime("%Y")
        month = date_obj.strftime("%m")
        
        file_path = account_dir / year / month / f"{date_str}.md"
        if file_path.exists():
            with open(file_path, "r", encoding="utf-8") as f:
                for line in f:
                    line = line.strip()
                    if not line:
                        continue
                    
                    # 提取金额（支持多种格式）
                    # 匹配最后的数字（金额）
                    amount_match = re.search(r'[-：:](\d+\.\d{2})\s*$', line)
                    if amount_match:
                        amount = float(amount_match.group(1))
                        
                        # 判断收入/支出
                        if any(kw in line for kw in ['收入', '收到', '入账', '工资', '稿费']):
                            total_income += amount
                            details.append(("收入", line.split(": ")[1] if ": " in line else line, amount))
                        else:
                            total_expense += amount
                            details.append(("支出", line.split(": ")[1] if ": " in line else line, amount))
    
    # 输出汇总
    print(f"💰 账目汇总 [{dates[0]} ~ {dates[-1]}]")
    print(f"总收入：¥{total_income:.2f}")
    print(f"总支出：¥{total_expense:.2f}")
    print(f"结余：¥{total_income - total_expense:.2f}")
    
    if details:
        print(f"\n明细 ({len(details)}条):")
        # 按金额排序
        details.sort(key=lambda x: x[2], reverse=True)
        for type_, text, amount in details[:10]:  # 显示前 10 条
            print(f"  {type_}: {text} ¥{amount:.2f}")


def get_date_range(period, start_date_arg, end_date_arg):
    """获取日期范围"""
    today = datetime.now().date()
    
    if start_date_arg and end_date_arg:
        start = datetime.strptime(start_date_arg, "%Y-%m-%d").date()
        end = datetime.strptime(end_date_arg, "%Y-%m-%d").date()
        
        dates = []
        current = start
        while current <= end:
            dates.append(current.strftime("%Y-%m-%d"))
            current += timedelta(days=1)
        
        return dates
    
    elif period == "today":
        return [today.strftime("%Y-%m-%d")]
    
    elif period == "week":
        # 本周一到今天
        monday = today - timedelta(days=today.weekday())
        dates = []
        current = monday
        while current <= today:
            dates.append(current.strftime("%Y-%m-%d"))
            current += timedelta(days=1)
        return dates
    
    elif period == "month":
        # 本月 1 号到今天
        first_day = today.replace(day=1)
        dates = []
        current = first_day
        while current <= today:
            dates.append(current.strftime("%Y-%m-%d"))
            current += timedelta(days=1)
        return dates
    
    else:
        return [today.strftime("%Y-%m-%d")]


if __name__ == "__main__":
    main()
