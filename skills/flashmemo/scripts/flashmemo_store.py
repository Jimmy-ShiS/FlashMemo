#!/usr/bin/env python3
"""
FlashMemo 存储脚本
将分类后的内容存储到文件

支持跨平台配置：
1. 环境变量：FLASHMEMO_BASE_PATH
2. 配置文件：~/.flashmemo/config.json
3. 命令行参数：--base-path
"""

import argparse
import sys
import os
import json
from pathlib import Path
from datetime import datetime


def get_base_path(args_base_path=None) -> Path:
    """
    获取基础路径（支持跨平台配置）
    
    优先级：
    1. 命令行参数 --base-path
    2. 环境变量 FLASHMEMO_BASE_PATH
    3. 配置文件 ~/.flashmemo/config.json
    4. 默认路径 ~/Documents/FlashMemo
    """
    # 1. 命令行参数
    if args_base_path:
        return Path(args_base_path).expanduser()
    
    # 2. 环境变量
    env_path = os.environ.get('FLASHMEMO_BASE_PATH')
    if env_path:
        return Path(env_path).expanduser()
    
    # 3. 配置文件
    config_file = Path.home() / ".flashmemo" / "config.json"
    if config_file.exists():
        try:
            with open(config_file, "r", encoding="utf-8") as f:
                config = json.load(f)
                if "base_path" in config:
                    return Path(config["base_path"]).expanduser()
        except Exception:
            pass
    
    # 4. 跨平台默认路径
    return Path.home() / "Documents" / "FlashMemo"


def main():
    parser = argparse.ArgumentParser(description='FlashMemo 存储脚本')
    parser.add_argument('--channel', required=True, help='渠道名称')
    parser.add_argument('--user-id', required=True, help='用户 ID')
    parser.add_argument('--category', required=True, choices=['work', 'life', 'account', 'memo'], help='分类')
    parser.add_argument('--text', required=True, help='内容文本')
    parser.add_argument('--urgency', choices=['紧急', '重要', '普通'], default='普通', help='紧急程度（仅 memo）')
    parser.add_argument('--timestamp', default=None, help='时间戳（可选）')
    parser.add_argument('--base-path', default=None, help='基础路径（可选，覆盖默认路径）')
    
    args = parser.parse_args()
    
    # 获取基础路径（支持跨平台配置）
    base_dir = get_base_path(args.base_path)
    user_dir = base_dir / args.channel / args.user_id
    
    # 确保目录存在
    user_dir.mkdir(parents=True, exist_ok=True)
    
    # 时间戳
    if args.timestamp:
        timestamp = args.timestamp
    else:
        timestamp = datetime.now().strftime("%Y-%m-%d.%H:%M:%S")
    
    # 根据分类存储
    if args.category == "memo":
        # 备忘存储到 ImportantMemo.md
        memo_file = user_dir / "ImportantMemo.md"
        
        # 判断是"完成"还是"代办"，并清理文本中的完成标记
        prefix = "代办"
        text = args.text
        
        # 完成关键词列表（按长度降序排列，先替换长的）
        completion_keywords = ["已完成", "已办", "已做", "已完成", "好了", "搞定", "完成", "✅", "✓", "✔", "已"]
        
        # 检测是否包含完成关键词
        completion_indicators = ["完成", "好了", "搞定", "✅", "✓", "✔"]
        
        if any(kw in args.text for kw in completion_indicators):
            prefix = "完成"
            # 清理文本中的完成标记（按长度降序，避免部分替换）
            for kw in completion_keywords:
                text = text.replace(kw, "")
            # 清理多余的空格和符号
            text = text.strip().rstrip("-").rstrip("—").strip()
            # 清理连续的多个空格
            import re
            text = re.sub(r'\s+', ' ', text).strip()
            # 如果清理后为空，使用原始文本
            if not text:
                text = args.text
        
        entry = f"{timestamp}: {prefix} - {args.urgency} - {text}"
        
        # 检查是否已存在（去重）
        if memo_file.exists():
            with open(memo_file, "r", encoding="utf-8") as f:
                content = f.read()
                if entry in content:
                    print(f"⚠️  记录已存在，跳过：{entry[:50]}...")
                    return
        
        with open(memo_file, "a", encoding="utf-8") as f:
            f.write(entry + "\n")
        
        print(f"✅ 已存储到：{memo_file}")
        
    else:
        # 其他分类存储到日期文件
        date_obj = datetime.now()
        year = date_obj.strftime("%Y")
        month = date_obj.strftime("%m")
        day = date_obj.strftime("%Y-%m-%d")
        
        category_dir = user_dir / args.category / year / month
        category_dir.mkdir(parents=True, exist_ok=True)
        
        file_path = category_dir / f"{day}.md"
        entry = f"{timestamp}: {args.text}"
        
        # 检查是否已存在（去重）
        if file_path.exists():
            with open(file_path, "r", encoding="utf-8") as f:
                content = f.read()
                if entry in content:
                    print(f"⚠️  记录已存在，跳过：{entry[:50]}...")
                    return
        
        with open(file_path, "a", encoding="utf-8") as f:
            f.write(entry + "\n")
        
        print(f"✅ 已存储到：{file_path}")


if __name__ == "__main__":
    main()
