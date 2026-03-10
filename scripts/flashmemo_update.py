#!/usr/bin/env python3
"""
FlashMemo 更新脚本
更新备忘状态（代办 → 完成）
"""

import argparse
import sys
import os
import json
import re
from pathlib import Path
from datetime import datetime


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


def update_memo_status(memo_file: Path, keywords: list, new_status: str) -> dict:
    """
    更新备忘状态
    
    Args:
        memo_file: 备忘文件路径
        keywords: 关键词列表（用于匹配要更新的记录）
        new_status: 新状态（代办/完成）
    
    Returns:
        更新结果字典
    """
    if not memo_file.exists():
        return {"success": False, "message": "备忘文件不存在", "updated": 0}
    
    with open(memo_file, "r", encoding="utf-8") as f:
        lines = f.readlines()
    
    updated_count = 0
    new_lines = []
    updated_records = []
    
    for line in lines:
        line = line.strip()
        if not line:
            new_lines.append("")
            continue
        
        # 检查是否匹配关键词
        matched = False
        for keyword in keywords:
            if keyword in line:
                matched = True
                break
        
        if matched:
            # 更新状态
            if ": 代办-" in line:
                new_line = line.replace(": 代办-", ": 完成-", 1)
                new_lines.append(new_line + "\n")
                updated_count += 1
                updated_records.append(new_line)
            elif ": 完成-" in line and new_status == "代办":
                # 从完成改回代办
                new_line = line.replace(": 完成-", ": 代办-", 1)
                new_lines.append(new_line + "\n")
                updated_count += 1
                updated_records.append(new_line)
            else:
                new_lines.append(line + "\n")
        else:
            new_lines.append(line + "\n")
    
    # 写回文件
    with open(memo_file, "w", encoding="utf-8") as f:
        f.writelines(new_lines)
    
    return {
        "success": True,
        "message": f"已更新 {updated_count} 条记录",
        "updated": updated_count,
        "records": updated_records
    }


def main():
    parser = argparse.ArgumentParser(description='FlashMemo 更新脚本')
    parser.add_argument('--channel', required=True, help='渠道名称')
    parser.add_argument('--user-id', required=True, help='用户 ID')
    parser.add_argument('--base-path', default=None, help='基础路径（可选）')
    parser.add_argument('--keywords', nargs='+', required=True, help='关键词列表（用于匹配要更新的记录）')
    parser.add_argument('--status', choices=['代办', '完成'], default='完成', help='目标状态（默认：完成）')
    
    args = parser.parse_args()
    
    # 获取基础路径
    base_dir = get_base_path(args.base_path)
    user_dir = base_dir / args.channel / args.user_id
    
    memo_file = user_dir / "ImportantMemo.md"
    
    # 更新状态
    result = update_memo_status(memo_file, args.keywords, args.status)
    
    if result["success"]:
        print(f"✅ {result['message']}")
        if result["records"]:
            print("\n更新后的记录:")
            for record in result["records"]:
                print(f"  {record}")
    else:
        print(f"❌ {result['message']}")
        sys.exit(1)


if __name__ == "__main__":
    main()
