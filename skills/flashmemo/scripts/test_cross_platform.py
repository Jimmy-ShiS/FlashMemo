#!/usr/bin/env python3
"""
FlashMemo 跨平台兼容性测试脚本
"""

import sys
import os
import platform
import tempfile
from pathlib import Path

# 添加脚本路径
sys.path.insert(0, str(Path(__file__).parent))

from flashmemo_core import (
    FlashMemoConfig, ensure_directories, classify_content,
    extract_account_items, determine_urgency, get_config
)

def print_header(text):
    print("\n" + "=" * 60)
    print(f"  {text}")
    print("=" * 60)

def test_platform_info():
    """测试平台信息"""
    print_header("平台信息测试")
    print(f"操作系统：{platform.system()} {platform.release()}")
    print(f"架构：{platform.machine()}")
    print(f"Python 版本：{sys.version}")
    print(f"用户主目录：{Path.home()}")
    print(f"当前工作目录：{Path.cwd()}")

def test_config_loading():
    """测试配置加载"""
    print_header("配置加载测试")
    config = get_config()
    print(f"基础路径：{config.get('base_path')}")
    print(f"时区：{config.get('timezone')}")
    print(f"编码：{config.get('encoding')}")
    print(f"配置来源：{config.get('_config_source', 'default')}")

def test_path_compatibility():
    """测试路径兼容性"""
    print_header("路径兼容性测试")
    
    # 测试路径创建
    test_dir = Path(tempfile.gettempdir()) / "flashmemo_test" / str(os.getpid())
    print(f"测试目录：{test_dir}")
    
    try:
        test_dir.mkdir(parents=True, exist_ok=True)
        print(f"✅ 目录创建成功")
        
        # 测试文件写入
        test_file = test_dir / "test.md"
        with open(test_file, "w", encoding="utf-8") as f:
            f.write("测试内容\n")
        print(f"✅ 文件写入成功")
        
        # 测试文件读取
        with open(test_file, "r", encoding="utf-8") as f:
            content = f.read()
        print(f"✅ 文件读取成功：{content.strip()}")
        
        # 清理
        test_file.unlink()
        test_dir.rmdir()
        print(f"✅ 清理完成")
        
    except Exception as e:
        print(f"❌ 测试失败：{e}")

def test_content_classification():
    """测试内容分类"""
    print_header("内容分类测试")
    
    test_cases = [
        ("中午吃了碗拉面 20 块", "account"),
        ("上午开会讨论项目", "work"),
        ("记得明天交报告", "memo"),
        ("晚上和朋友看电影", "life"),
        ("Spent $50 on lunch", "account"),
        ("Remember to buy gift", "memo"),
    ]
    
    for text, expected in test_cases:
        result = classify_content(text)
        actual = result[0][0] if result else "unknown"
        status = "✅" if actual == expected else "❌"
        print(f"{status} '{text[:20]}...' → {actual} (期望：{expected})")

def test_account_extraction():
    """测试账目提取"""
    print_header("账目提取测试")
    
    test_cases = [
        ("花了 68 元买午餐", 1),
        ("收入 - 工资 -8000 元", 1),
        ("中午吃饭 35 元，买咖啡 20 元", 2),
        ("Spent $20 on coffee", 1),
    ]
    
    for text, expected_count in test_cases:
        items = extract_account_items(text)
        status = "✅" if len(items) == expected_count else "❌"
        print(f"{status} '{text[:25]}...' → {len(items)} 条 (期望：{expected_count})")
        for item in items:
            print(f"    {item['type']}-{item['category']}-{item['amount']:.2f}")

def test_urgency_detection():
    """测试紧急程度检测"""
    print_header("紧急程度检测")
    
    test_cases = [
        ("今天下午 5 点前提交", "紧急"),
        ("记得给妈妈买礼物", "重要"),
        ("周末整理衣柜", "普通"),
        ("Urgent: submit today", "紧急"),
        ("Important meeting", "重要"),
    ]
    
    for text, expected in test_cases:
        result = determine_urgency(text)
        status = "✅" if result == expected else "❌"
        print(f"{status} '{text[:20]}...' → {result} (期望：{expected})")

def test_directory_creation():
    """测试目录创建"""
    print_header("目录创建测试")
    
    try:
        dirs = ensure_directories("test_platform", f"user_{os.getpid()}")
        print(f"✅ 目录创建成功")
        for category, path in dirs.items():
            print(f"   {category}: {path}")
    except Exception as e:
        print(f"❌ 目录创建失败：{e}")

def main():
    """主测试函数"""
    print("\n" + "🧪" * 30)
    print("  FlashMemo 跨平台兼容性测试")
    print("🧪" * 30)
    
    test_platform_info()
    test_config_loading()
    test_path_compatibility()
    test_content_classification()
    test_account_extraction()
    test_urgency_detection()
    test_directory_creation()
    
    print_header("测试完成")
    print("✅ 所有测试完成！")
    print("=" * 60 + "\n")

if __name__ == "__main__":
    main()
