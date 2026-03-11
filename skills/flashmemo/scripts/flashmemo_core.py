#!/usr/bin/env python3
"""
FlashMemo Core - 智能流水账记录核心模块
所有智能处理都使用 AI 模型能力
"""

import os
import sys
import re
from datetime import datetime, timedelta
from pathlib import Path
from typing import Dict, List, Optional

# 导入 AI 处理器
try:
    from flashmemo_ai_processor import (
        classify_content, summarize_records, process_with_ai,
        extract_accounts_with_ai, _call_openclaw_model
    )
    AI_AVAILABLE = True
except ImportError as e:
    AI_AVAILABLE = False
    print(f"警告：AI 处理器未加载：{e}", file=sys.stderr)

# ============================================================================
# 配置
# ============================================================================

BASE_DIR = Path.home() / "Documents" / "FlashMemo"
LOG_FILE = BASE_DIR / ".flashmemo" / "log.txt"
CATEGORIES = ["work", "life", "account"]
MEMO_FILE = "ImportantMemo.md"


# ============================================================================
# 核心功能
# ============================================================================

def ensure_directories(channel: str, user_id: str) -> Dict[str, Path]:
    """确保所需目录存在
    
    渠道名称统一转小写，避免大小写不一致导致目录分散
    """
    # 渠道名称统一转小写（修复 Feishu/feishu 问题）
    channel = str(channel).lower()
    user_dir = BASE_DIR / channel / str(user_id)
    dirs = {}
    
    for category in CATEGORIES:
        dir_path = user_dir / category
        dir_path.mkdir(parents=True, exist_ok=True)
        dirs[category] = dir_path
    
    (BASE_DIR / ".flashmemo").mkdir(parents=True, exist_ok=True)
    return dirs


def get_today_path(dirs: Dict[str, Path], category: str) -> Path:
    """获取今日记录文件路径"""
    now = datetime.now()
    today = now.strftime("%Y-%m-%d")
    year = now.strftime("%Y")
    month = now.strftime("%m")
    return dirs[category] / year / month / f"{today}.md"


def get_timestamp() -> str:
    """获取时间戳"""
    return datetime.now().strftime("%Y-%m-%d.%H:%M:%S")


def append_to_file(file_path: Path, content: str):
    """追加内容到文件"""
    file_path.parent.mkdir(parents=True, exist_ok=True)
    with open(file_path, "a", encoding="utf-8") as f:
        f.write(content + "\n")
    log_operation("APPEND", str(file_path), content)


def append_to_memo(channel: str, user_id: str, content: str, result=None) -> str:
    """追加到重要备忘文件"""
    dirs = ensure_directories(channel, user_id)
    memo_path = BASE_DIR / str(channel) / str(user_id) / MEMO_FILE
    
    # 使用 AI 判断的紧急程度
    urgency = "普通"
    if result and result.urgency:
        urgency = result.urgency.value
    
    # 判断是"完成"还是"代办"
    prefix = "代办"
    if any(kw in content for kw in ["完成", "已", "好了", "搞定"]):
        prefix = "完成"
    
    timestamp = get_timestamp()
    formatted = f"{timestamp}: {prefix}-{urgency}-{content}"
    
    append_to_file(memo_path, formatted)
    return formatted


def read_file_content(file_path: Path) -> str:
    """读取文件内容"""
    if not file_path.exists():
        return ""
    with open(file_path, "r", encoding="utf-8") as f:
        return f.read()


def read_today_records(dirs: Dict[str, Path], category: str) -> List[str]:
    """读取今日记录"""
    file_path = get_today_path(dirs, category)
    content = read_file_content(file_path)
    return [line for line in content.split("\n") if line.strip()]


def calculate_account_summary(records: List[str]) -> Dict:
    """
    计算账目汇总 - 使用 AI 理解
    
    让 AI 理解文本并提取所有金额
    """
    if not records:
        return {"total_income": 0.0, "total_expense": 0.0, "balance": 0.0, "details": []}
    
    try:
        # 使用 AI 提取账目信息
        from flashmemo_ai_processor import extract_accounts_with_ai
        
        # 提取所有文本（去掉时间戳）
        texts = [r.split(": ")[1] if ": " in r else r for r in records]
        
        # 让 AI 提取并汇总
        result = extract_accounts_with_ai(texts)
        
        return {
            "total_income": float(result.get("total_income", 0.0)),
            "total_expense": float(result.get("total_expense", 0.0)),
            "balance": float(result.get("balance", 0.0)),
            "details": result.get("details", [])
        }
    
    except Exception as e:
        print(f"AI 账目汇总失败：{e}，使用简单 fallback", file=sys.stderr)
        
        # Fallback：简单处理
        total_income = 0.0
        total_expense = 0.0
        details = []
        
        for record in records:
            text = record.split(": ")[1] if ": " in record else record
            is_income = any(kw in text for kw in ['收入', '收到', '入账', '工资', '稿费'])
            
            # 简单提取数字
            numbers = re.findall(r'\d+', text)
            if numbers:
                amount = float(numbers[-1])
                if is_income:
                    total_income += amount
                else:
                    total_expense += amount
                details.append(("收入" if is_income else "支出", text, amount))
        
        return {
            "total_income": total_income,
            "total_expense": total_expense,
            "balance": total_income - total_expense,
            "details": sorted(details, key=lambda x: x[2], reverse=True)[:5]
        }


def log_operation(operation: str, path: str, content: str):
    """记录操作日志"""
    try:
        timestamp = datetime.now().isoformat()
        log_dir = LOG_FILE.parent
        log_dir.mkdir(parents=True, exist_ok=True)
        
        log_entry = f"[{timestamp}] {operation}: {path}\n  Content: {content[:100]}...\n"
        with open(LOG_FILE, "a", encoding="utf-8") as f:
            f.write(log_entry)
    except Exception:
        pass


def process_user_input(text: str, channel: str, user_id: str, dirs: Dict[str, Path]):
    """
    处理用户输入 - 核心函数
    
    所有智能处理都交给 AI
    
    Args:
        text: 用户输入
        channel: 渠道
        user_id: 用户 ID
        dirs: 目录字典
    
    Returns:
        (category, entry_text, result)
    """
    timestamp = get_timestamp()
    
    # 使用 AI 分类和理解
    if AI_AVAILABLE:
        category, content, result = classify_content(text)
    else:
        # Fallback：简单规则
        if any(kw in text for kw in ['元', '块', '收到', '花了']):
            category = "account"
        elif any(kw in text for kw in ['记得', '别忘了', '明天', '待办']):
            category = "memo"
        elif any(kw in text for kw in ['工作', '会议', '项目', '报告']):
            category = "work"
        else:
            category = "life"
        result = None
    
    # 根据分类记录
    if category == "account":
        # 账目：直接使用用户原始文本
        entry = f"{timestamp}: {text}"
        file_path = get_today_path(dirs, "account")
        append_to_file(file_path, entry)
        
    elif category == "memo":
        # 备忘：使用 AI 判断的紧急程度
        entry = append_to_memo(channel, user_id, text, result)
        
    elif category == "work":
        # 工作记录
        entry = f"{timestamp}: {text}"
        file_path = get_today_path(dirs, "work")
        append_to_file(file_path, entry)
        
    else:  # life
        # 生活记录
        entry = f"{timestamp}: {text}"
        file_path = get_today_path(dirs, "life")
        append_to_file(file_path, entry)
    
    return (category, entry, result)


def get_summary_report(dirs: Dict[str, Path], days: int = 1) -> str:
    """
    生成总结报告 - 使用 AI
    
    Args:
        dirs: 目录字典
        days: 天数
    
    Returns:
        格式化的总结报告
    """
    all_records = []
    
    # 读取指定天数的记录
    for i in range(days):
        date = datetime.now() - timedelta(days=i)
        date_str = date.strftime("%Y-%m-%d")
        year = date.strftime("%Y")
        month = date.strftime("%m")
        
        for category in CATEGORIES:
            file_path = dirs[category] / year / month / f"{date_str}.md"
            if file_path.exists():
                content = read_file_content(file_path)
                records = [line for line in content.split("\n") if line.strip()]
                all_records.extend([(category, r) for r in records])
    
    if not all_records:
        return "暂无记录"
    
    # 使用 AI 总结
    try:
        texts = [text for _, text in all_records]
        summary = summarize_records(texts)
        
        # 格式化输出
        report = ["📊 FlashMemo 总结报告\n"]
        
        summ = summary.get("summary", {})
        
        if summ.get("work"):
            report.append(f"💼 工作 ({len(summ['work'])}项):")
            for item in summ["work"]:
                report.append(f"  • {item}")
            report.append("")
        
        if summ.get("life"):
            report.append(f"🏠 生活 ({len(summ['life'])}项):")
            for item in summ["life"]:
                report.append(f"  • {item}")
            report.append("")
        
        account = summ.get("account", {})
        if account:
            report.append(f"💰 账目:")
            report.append(f"  总收入：¥{account.get('total_income', 0):.2f}")
            report.append(f"  总支出：¥{account.get('total_expense', 0):.2f}")
            report.append("")
        
        memo = summ.get("memo", {})
        if memo.get("urgent"):
            report.append(f"🔴 紧急待办 ({len(memo['urgent'])}项):")
            for item in memo["urgent"]:
                report.append(f"  • {item}")
            report.append("")
        
        insights = summary.get("insights", [])
        if insights:
            report.append("💡 洞察:")
            for insight in insights:
                report.append(f"  • {insight}")
        
        return "\n".join(report)
    
    except Exception as e:
        return f"生成总结失败：{e}"
