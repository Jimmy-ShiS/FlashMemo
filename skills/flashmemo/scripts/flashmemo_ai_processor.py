#!/usr/bin/env python3
"""
FlashMemo AI 处理器 - 请求式架构

不再主动调用 OpenClaw API，而是：
1. 构建需要 AI 处理的请求
2. 通过标准输出返回请求
3. OpenClaw 捕获请求，使用模型处理
4. 将结果返回给 skill
"""

import json
import re
import sys
from typing import Dict, List, Optional
from dataclasses import dataclass
from enum import Enum


class Category(Enum):
    WORK = "work"
    LIFE = "life"
    ACCOUNT = "account"
    MEMO = "memo"


class UrgencyLevel(Enum):
    URGENT = "紧急"
    IMPORTANT = "重要"
    NORMAL = "普通"


@dataclass
class ClassificationResult:
    category: Category
    confidence: float
    reasoning: str
    urgency: Optional[UrgencyLevel] = None
    account_items: Optional[List[Dict]] = None


# ============================================================================
# AI 请求构建（不是调用）
# ============================================================================

def build_classification_request(text: str) -> dict:
    """
    构建分类请求（返回请求对象，不调用）
    
    OpenClaw 应该捕获这个请求并使用模型处理
    """
    return {
        "type": "flashmemo_ai_request",
        "action": "classify",
        "input": {
            "text": text
        },
        "prompt": """请分析以下内容并分类：

分类标准：
- work (工作): 工作任务、会议、项目、报告等
- life (生活): 日常生活、娱乐、健康、社交等
- account (账目): 涉及金钱、消费、收入、支出等
- memo (备忘): 待办事项、提醒、计划等

如果是账目，请提取所有金额明细。
如果是备忘，请判断紧急程度（紧急/重要/普通）。

返回 JSON：
{
  "category": "work|life|account|memo",
  "confidence": 0.0-1.0,
  "reasoning": "理由",
  "urgency": "紧急 | 重要 | 普通",
  "account_items": [{"type": "收入/支出", "category": "类别", "amount": 数字}]
}"""
    }


def build_account_summary_request(texts: List[str]) -> dict:
    """
    构建账目汇总请求
    """
    return {
        "type": "flashmemo_ai_request",
        "action": "account_summary",
        "input": {
            "texts": texts
        },
        "prompt": f"""请分析以下账目记录，提取所有收入和支出：

{chr(10).join(texts)}

返回 JSON：
{{
  "total_income": 数字，
  "total_expense": 数字，
  "balance": 数字，
  "details": [{{"type": "收入/支出", "text": "原文", "amount": 数字}}]
}}"""
    }


def build_summary_request(records: List[str]) -> dict:
    """
    构建归纳总结请求
    """
    return {
        "type": "flashmemo_ai_request",
        "action": "summarize",
        "input": {
            "records": records
        },
        "prompt": f"""请对以下记录进行归纳总结：

{chr(10).join(records)}

返回 JSON：
{{
  "summary": {{
    "work": ["工作记录"],
    "life": ["生活记录"],
    "account": {{"total_income": 数字，"total_expense": 数字}},
    "memo": {{"urgent": ["紧急"], "important": ["重要"], "normal": ["普通"]}}
  }},
  "insights": ["洞察"]
}}"""
    }


# ============================================================================
# 请求提交（通过 stdout）
# ============================================================================

def submit_ai_request(request: dict) -> Optional[dict]:
    """
    提交 AI 请求到 OpenClaw
    
    通过 stdout 输出特殊格式，OpenClaw 捕获并处理
    这是请求式架构的关键
    """
    # 输出特殊标记的请求
    print(f"\n[FLASHMEMO_AI_REQUEST]\n{json.dumps(request, ensure_ascii=False)}\n[/FLASHMEMO_AI_REQUEST]\n")
    
    # OpenClaw 应该：
    # 1. 捕获这个输出
    # 2. 使用模型处理 request["prompt"]
    # 3. 将结果返回
    
    # 目前返回 None，等待 OpenClaw 实现请求捕获机制
    return None


# ============================================================================
# Fallback 处理（AI 不可用时）
# ============================================================================

def _simple_classify(text: str) -> ClassificationResult:
    """简单规则分类（fallback）
    
    分类优先级：account > memo > work > life
    账目关键词优先匹配，确保涉及金额的内容不会误分类为 life
    """
    # 第一优先级：账目（涉及金钱）
    # 关键词：元、块、圆、¥、￥、收入、支出、花了、买了、收到、入账、工资、消费
    account_keywords = ['元', '块', '圆', '¥', '￥', '收入', '支出', '花了', '买了', 
                        '收到', '入账', '工资', '稿费', '消费', '付款', '支付', '花费']
    if any(kw in text for kw in account_keywords):
        # 额外检查：是否有数字（金额）
        import re
        if re.search(r'\d+(?:\.\d+)?', text):
            return ClassificationResult(
                category=Category.ACCOUNT,
                confidence=0.9,
                reasoning="检测到金额数字和财务相关词汇"
            )
        return ClassificationResult(
            category=Category.ACCOUNT,
            confidence=0.7,
            reasoning="检测到财务相关词汇"
        )
    
    # 第二优先级：备忘（待办事项）
    if any(kw in text for kw in ['记得', '别忘了', '明天', '待办', '必须', '提醒']):
        urgency = UrgencyLevel.URGENT if any(kw in text for kw in ['今天', '明天', '必须', '立即']) else UrgencyLevel.IMPORTANT
        return ClassificationResult(
            category=Category.MEMO,
            confidence=0.7,
            reasoning="检测到待办事项",
            urgency=urgency
        )
    
    # 第三优先级：工作
    if any(kw in text for kw in ['工作', '会议', '项目', '报告', '客户', '完成', '上班', '任务']):
        return ClassificationResult(
            category=Category.WORK,
            confidence=0.7,
            reasoning="检测到工作相关词汇"
        )
    
    # 默认：生活
    return ClassificationResult(
        category=Category.LIFE,
        confidence=0.6,
        reasoning="未检测到特殊特征"
    )


def _simple_account_extract(texts: List[str]) -> Dict:
    """简单账目提取（fallback）"""
    total_income = 0.0
    total_expense = 0.0
    details = []
    
    for text in texts:
        is_income = any(kw in text for kw in ['收入', '收到', '入账', '工资', '稿费'])
        numbers = re.findall(r'\d+(?:\.\d+)?', text)
        for num in numbers:
            amount = float(num)
            if amount > 10:
                if is_income:
                    total_income += amount
                else:
                    total_expense += amount
                details.append(("收入" if is_income else "支出", text, amount))
                break
    
    return {
        "total_income": total_income,
        "total_expense": total_expense,
        "balance": total_income - total_expense,
        "details": details
    }


# ============================================================================
# 导出函数
# ============================================================================

def classify_content(text: str, use_ai: bool = True) -> tuple:
    """
    分类内容
    
    Args:
        text: 用户输入
        use_ai: 是否使用 AI（目前只是标记，实际由 OpenClaw 决定）
    
    Returns:
        (category, text, result)
    """
    if use_ai:
        # 构建 AI 请求
        request = build_classification_request(text)
        
        # 提交给 OpenClaw（目前返回 None）
        response = submit_ai_request(request)
        
        if response:
            # AI 响应，解析结果
            # TODO: 实现解析逻辑
            pass
    
    # Fallback：规则分类
    result = _simple_classify(text)
    return (result.category.value, text, result)


def extract_accounts_with_ai(texts: List[str]) -> Dict:
    """
    账目提取和汇总
    """
    # 构建 AI 请求
    request = build_account_summary_request(texts)
    response = submit_ai_request(request)
    
    if response:
        return response
    
    # Fallback
    return _simple_account_extract(texts)


def summarize_records(records: List[str]) -> Dict:
    """
    归纳总结
    """
    request = build_summary_request(records)
    response = submit_ai_request(request)
    
    if response:
        return response
    
    # Fallback
    return {
        "summary": {
            "work": [],
            "life": records,
            "account": {"total_income": 0, "total_expense": 0},
            "memo": {"urgent": [], "important": [], "normal": []}
        },
        "insights": [f"共 {len(records)} 条记录"]
    }
