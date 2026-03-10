#!/usr/bin/env python3
"""
FlashMemo AI Classifier - 基于 OpenClaw 模型的智能分类器
使用 OpenClaw 已配置的模型进行语义理解，无需额外配置 API
"""

import json
import re
import subprocess
import sys
from typing import Dict, List, Tuple, Optional
from dataclasses import dataclass
from enum import Enum


class Category(Enum):
    """内容分类枚举"""
    WORK = "work"
    LIFE = "life"
    ACCOUNT = "account"
    MEMO = "memo"


class UrgencyLevel(Enum):
    """紧急程度枚举"""
    URGENT = "紧急"
    IMPORTANT = "重要"
    NORMAL = "普通"


@dataclass
class ClassificationResult:
    """分类结果"""
    category: Category
    confidence: float  # 置信度 0-1
    reasoning: str  # 分类理由
    urgency: Optional[UrgencyLevel] = None
    account_items: Optional[List[Dict]] = None


class OpenClawAIClassifier:
    """
    OpenClaw AI 智能分类器
    
    使用 OpenClaw 已配置的模型进行语义理解，支持：
    - 多分类判断（工作/生活/账目/备忘）
    - 紧急程度评估
    - 账目明细提取
    - 置信度评估
    - 内容归纳总结
    """
    
    # 分类系统提示词
    CLASSIFICATION_PROMPT = """你是一个专业的个人助手分类专家。请分析用户输入的内容，并进行智能分类。

## 分类标准

**work (工作)**: 与职业、工作任务、会议、项目、报告、同事协作相关的内容
- 示例："上午开会讨论 Q3 计划"、"完成了产品需求文档"、"和客户确认方案"

**life (生活)**: 日常生活、休闲娱乐、健康、学习、社交、家庭等非工作事项
- 示例："晚上和朋友看电影"、"今天去健身了"、"做了顿好吃的晚餐"

**account (账目)**: 涉及金钱、消费、收入、支出、转账等财务相关信息
- 示例："午餐花了 35 元"、"收到工资 8000 元"、"转账给朋友 200 元"

**memo (备忘)**: 待办事项、提醒、计划、需要记住的事情，通常包含时间敏感性
- 示例："记得明天交报告"、"别忘了给妈妈打电话"、"下周要去体检"

## 输出格式

请严格返回 JSON 格式（不要有其他内容）：
{
  "category": "work|life|account|memo",
  "confidence": 0.0-1.0,
  "reasoning": "分类理由，简要说明为什么这样分类",
  "urgency": "紧急 | 重要 | 普通",
  "account_items": [
    {
      "type": "开支 | 收入",
      "category": "类别名称",
      "amount": 数字，
      "note": "备注"
    }
  ]
}

注意：
1. 如果内容包含多个分类，选择最主要的那个
2. 账目内容如果有明确金额，category 必须是 account
3. 备忘内容如果有明确的时间或任务，category 必须是 memo
4. urgency 仅在 memo 分类时需要，其他分类可以填"普通"
5. account_items 仅在 account 分类时填写具体明细，其他分类填空数组"""

    # 归纳总结提示词
    SUMMARY_PROMPT = """你是一个专业的个人助手。请对用户的多条记录进行归纳总结。

## 要求

1. 按分类分组（工作/生活/账目/备忘）
2. 提取关键信息
3. 账目需要计算总额
4. 备忘需要标注紧急程度
5. 语言简洁清晰

## 输出格式

请返回 JSON 格式：
{
  "summary": {
    "work": ["工作记录 1", "工作记录 2"],
    "life": ["生活记录 1"],
    "account": {
      "total_income": 数字，
      "total_expense": 数字，
      "items": ["开支项 1", "开支项 2"]
    },
    "memo": {
      "urgent": ["紧急待办 1"],
      "important": ["重要待办 1"],
      "normal": ["普通待办 1"]
    }
  },
  "insights": ["洞察 1", "洞察 2"]
}"""

    def __init__(self):
        """初始化分类器"""
        self._model_info = None
    
    def _get_model_info(self) -> dict:
        """获取 OpenClaw 当前配置的模型信息"""
        if self._model_info is None:
            try:
                # 通过 openclaw status 获取模型信息
                result = subprocess.run(
                    ["openclaw", "status"],
                    capture_output=True,
                    text=True,
                    timeout=5
                )
                
                # 解析输出，提取模型信息
                output = result.stdout
                model_line = [line for line in output.split("\n") if "model=" in line]
                
                if model_line:
                    # 提取模型名称
                    model_info = model_line[0].strip()
                    self._model_info = {"raw": model_info}
                else:
                    self._model_info = {"raw": "unknown"}
                    
            except Exception as e:
                print(f"获取模型信息失败：{e}", file=sys.stderr)
                self._model_info = {"raw": "unknown"}
        
        return self._model_info
    
    def _call_llm(self, prompt: str, system_prompt: str = None) -> str:
        """
        调用 OpenClaw LLM
        
        使用 sessions_send 向当前会话发送消息获取 AI 响应
        
        Args:
            prompt: 用户提示词
            system_prompt: 系统提示词
        
        Returns:
            LLM 返回的文本
        """
        try:
            # 构建完整提示
            full_prompt = prompt
            if system_prompt:
                full_prompt = f"{system_prompt}\n\n请分析：{prompt}"
            
            # 使用 sessions_send 调用模型
            # 注意：这需要当前会话支持
            from sessions_send import sessions_send
            
            # 发送到当前会话（非交互式）
            result = sessions_send(
                message=full_prompt,
                timeoutSeconds=30
            )
            
            return result
            
        except ImportError:
            # sessions_send 不可用
            pass
        except Exception as e:
            print(f"sessions_send 调用失败：{e}", file=sys.stderr)
        
        # Fallback：尝试使用 subprocess 调用 openclaw
        try:
            # 尝试不同的 openclaw 命令格式
            for cmd in [
                ["openclaw", "chat", "--non-interactive"],
                ["openclaw", "message", "--non-interactive"],
            ]:
                try:
                    result = subprocess.run(
                        cmd + [prompt],
                        capture_output=True,
                        text=True,
                        timeout=30
                    )
                    if result.returncode == 0 and result.stdout.strip():
                        return result.stdout.strip()
                except (FileNotFoundError, subprocess.TimeoutExpired):
                    continue
        except Exception:
            pass
        
        # 所有方法都失败，抛出异常使用规则 fallback
        raise RuntimeError("OpenClaw LLM 调用不可用，使用规则分类 fallback")
    
    def classify(self, text: str) -> ClassificationResult:
        """
        智能分类单条内容
        
        Args:
            text: 用户输入的文本
        
        Returns:
            ClassificationResult 分类结果
        """
        try:
            # 调用 LLM
            result_text = self._call_llm(
                prompt=f"请分类以下内容：{text}",
                system_prompt=self.CLASSIFICATION_PROMPT
            )
            
            # 解析结果
            return self._parse_llm_result(result_text, text)
            
        except Exception as e:
            print(f"AI 分类失败，使用规则 fallback: {e}", file=sys.stderr)
            return self._classify_with_rules(text)
    
    def _parse_llm_result(self, result_text: str, original_text: str) -> ClassificationResult:
        """解析 LLM 返回的 JSON 结果"""
        try:
            # 提取 JSON 部分（处理可能的 markdown 格式）
            json_match = re.search(r'```(?:json)?\s*(.*?)\s*```', result_text, re.DOTALL)
            if json_match:
                result_json = json.loads(json_match.group(1))
            else:
                # 尝试直接解析
                result_json = json.loads(result_text)
            
            # 构建分类结果
            category_str = result_json.get("category", "life")
            try:
                category = Category(category_str)
            except ValueError:
                category = Category.LIFE
            
            confidence = float(result_json.get("confidence", 0.8))
            reasoning = result_json.get("reasoning", "")
            
            # 紧急程度
            urgency_str = result_json.get("urgency", "普通")
            try:
                urgency = UrgencyLevel(urgency_str)
            except ValueError:
                urgency = UrgencyLevel.NORMAL
            
            # 账目明细
            account_items = result_json.get("account_items", [])
            
            return ClassificationResult(
                category=category,
                confidence=confidence,
                reasoning=reasoning,
                urgency=urgency,
                account_items=account_items if account_items else None
            )
        
        except (json.JSONDecodeError, ValueError) as e:
            print(f"解析 LLM 结果失败：{e}，原始输出：{result_text[:200]}")
            # Fallback 到规则分类
            return self._classify_with_rules(original_text)
    
    def _classify_with_rules(self, text: str) -> ClassificationResult:
        """
        规则分类（LLM 不可用时的 fallback）
        
        使用改进的启发式规则
        """
        text_lower = text.lower()
        
        # 1. 检查是否有明确的金额模式（高优先级）
        has_money = bool(re.search(r'\d+\.?\d*\s*(?:元 | 块 | 圆 | 円)', text))
        has_money_keywords = any(kw in text for kw in [
            "开支", "收入", "支出", "消费", "转账", "工资", "付款", "购买", "花了", "收到"
        ])
        
        if has_money or has_money_keywords:
            account_items = self._extract_account_items(text)
            return ClassificationResult(
                category=Category.ACCOUNT,
                confidence=0.95 if has_money else 0.7,
                reasoning="检测到金额或财务相关词汇",
                account_items=account_items
            )
        
        # 2. 检查是否是备忘（任务 + 时间敏感性）
        memo_indicators = ["记得", "别忘了", "待办", "提醒", "要", "得", "需要"]
        time_references = ["明天", "后天", "下周", "下周", "今天", "截止", "deadline"]
        
        has_memo = any(kw in text for kw in memo_indicators)
        has_time = any(kw in text for kw in time_references)
        
        if has_memo and has_time:
            urgency = self._detect_urgency(text)
            return ClassificationResult(
                category=Category.MEMO,
                confidence=0.9,
                reasoning="检测到待办事项和时间引用",
                urgency=urgency
            )
        elif has_memo:
            return ClassificationResult(
                category=Category.MEMO,
                confidence=0.75,
                reasoning="检测到待办事项关键词"
            )
        
        # 3. 检查工作相关
        work_context = [
            "会议", "开会", "项目", "报告", "客户", "老板", "同事", "公司", "上班",
            "完成", "提交", "需求", "开发", "测试", "设计", "产品", "Q1", "Q2", "Q3", "Q4"
        ]
        
        if any(kw in text for kw in work_context):
            return ClassificationResult(
                category=Category.WORK,
                confidence=0.85,
                reasoning="检测到工作相关上下文"
            )
        
        # 4. 默认归类为生活
        return ClassificationResult(
            category=Category.LIFE,
            confidence=0.6,
            reasoning="未检测到特殊分类特征，归类为生活记录"
        )
    
    def _detect_urgency(self, text: str) -> UrgencyLevel:
        """检测紧急程度"""
        urgent_keywords = ["立即", "马上", "今天", "明天", "截止", "紧急", "快点", "ASAP"]
        important_keywords = ["记得", "别忘了", "必须", "关键", "重要", "一定", "千万"]
        
        if any(kw in text for kw in urgent_keywords):
            return UrgencyLevel.URGENT
        elif any(kw in text for kw in important_keywords):
            return UrgencyLevel.IMPORTANT
        else:
            return UrgencyLevel.NORMAL
    
    def _extract_account_items(self, text: str) -> List[Dict]:
        """
        提取账目明细（改进版）
        
        支持多种格式：
        - "花了 X 元" / "收到 X 元"
        - "开支 - 类别 -X 元"
        - "XX 花了 X 元买 YY"
        """
        items = []
        text_lower = text.lower()
        
        # 模式 1：类型 - 类别 - 金额
        pattern1 = r'(开支 | 收入 | 支出 | 花费 | 收到)-([^-]+)-(\d+\.?\d*)'
        for match in re.finditer(pattern1, text, re.IGNORECASE):
            item_type = "开支" if match.group(1).lower() in ["开支", "支出", "花费"] else "收入"
            items.append({
                "type": item_type,
                "category": match.group(2).strip(),
                "amount": float(match.group(3)),
                "note": ""
            })
        
        # 模式 2：花了/消费 X 元（买 Y）
        pattern2 = r'(?:花了 | 消费 | 付款)(\d+\.?\d*)\s*(?:元 | 块 | ¥|\$)?(?:买 | 用于)?\s*([^\d，,\.]*)'
        for match in re.finditer(pattern2, text, re.IGNORECASE):
            items.append({
                "type": "开支",
                "category": match.group(2).strip() or "消费",
                "amount": float(match.group(1)),
                "note": ""
            })
        
        # 模式 3：收到/收入 X 元（新增）
        pattern3 = r'(?:收到 | 收入 | 入账)(?:了)?\s*(\d+\.?\d*)\s*(?:元 | 块)?\s*(?:的)?([^\d，,\.]*)'
        for match in re.finditer(pattern3, text, re.IGNORECASE):
            items.append({
                "type": "收入",
                "category": match.group(2).strip() or "收入",
                "amount": float(match.group(1)),
                "note": ""
            })
        
        # 模式 4：XX 元买 YY / XX 元的 YY（新增）
        pattern4 = r'(\d+\.?\d*)\s*(?:元 | 块)\s*(?:买 | 的|吃了|喝了)?\s*([^\d，,\.]*)'
        for match in re.finditer(pattern4, text, re.IGNORECASE):
            amount = float(match.group(1))
            category = match.group(2).strip()
            # 避免重复提取
            if category and category not in ['元', '块', '买', '的', '吃了', '喝了']:
                # 检查是否已经提取过
                if not any(abs(item['amount'] - amount) < 0.01 for item in items):
                    items.append({
                        "type": "开支",
                        "category": category,
                        "amount": amount,
                        "note": ""
                    })
        
        # 模式 5：金额 + 元/块（简单模式，作为 fallback）
        if not items:
            money_pattern = r'(\d+\.?\d*)\s*(?:元 | 块)'
            matches = list(re.finditer(money_pattern, text))
            if matches:
                # 判断是收入还是支出
                is_income = any(kw in text for kw in ['收到', '收入', '入账', '工资', '稿费', '红包'])
                item_type = "收入" if is_income else "开支"
                
                for match in matches:
                    amount = float(match.group(1))
                    # 尝试提取类别（金额后面的词）
                    after_match = text[match.end():match.end()+10]
                    category_match = re.match(r'\s*(?:买 | 的 | 吃了)?\s*([^\d，,\.。]{2,8})', after_match)
                    category = category_match.group(1).strip() if category_match else ("收入" if is_income else "消费")
                    
                    items.append({
                        "type": item_type,
                        "category": category,
                        "amount": amount,
                        "note": ""
                    })
        
        return items
    
    def summarize(self, records: List[str]) -> Dict:
        """
        对多条记录进行归纳总结
        
        Args:
            records: 记录列表
        
        Returns:
            总结字典
        """
        try:
            # 构建输入
            records_text = "\n".join([f"{i+1}. {r}" for i, r in enumerate(records)])
            
            result_text = self._call_llm(
                prompt=f"请总结以下记录：\n{records_text}",
                system_prompt=self.SUMMARY_PROMPT
            )
            
            # 解析结果
            json_match = re.search(r'```(?:json)?\s*(.*?)\s*```', result_text, re.DOTALL)
            if json_match:
                return json.loads(json_match.group(1))
            else:
                return json.loads(result_text)
                
        except Exception as e:
            print(f"AI 总结失败：{e}", file=sys.stderr)
            # Fallback：简单汇总
            return self._simple_summarize(records)
    
    def _simple_summarize(self, records: List[str]) -> Dict:
        """简单的规则总结（fallback）"""
        summary = {
            "work": [],
            "life": [],
            "account": {"total_income": 0, "total_expense": 0, "items": []},
            "memo": {"urgent": [], "important": [], "normal": []}
        }
        
        for record in records:
            result = self._classify_with_rules(record)
            
            if result.category == Category.WORK:
                summary["work"].append(record)
            elif result.category == Category.LIFE:
                summary["life"].append(record)
            elif result.category == Category.ACCOUNT:
                if result.account_items:
                    for item in result.account_items:
                        summary["account"]["items"].append(record)
                        if item["type"] == "收入":
                            summary["account"]["total_income"] += item["amount"]
                        else:
                            summary["account"]["total_expense"] += item["amount"]
            elif result.category == Category.MEMO:
                if result.urgency == UrgencyLevel.URGENT:
                    summary["memo"]["urgent"].append(record)
                elif result.urgency == UrgencyLevel.IMPORTANT:
                    summary["memo"]["important"].append(record)
                else:
                    summary["memo"]["normal"].append(record)
        
        summary["insights"] = []
        return summary


# 全局分类器实例
_classifier: Optional[OpenClawAIClassifier] = None


def get_classifier() -> OpenClawAIClassifier:
    """获取全局分类器实例"""
    global _classifier
    if _classifier is None:
        _classifier = OpenClawAIClassifier()
    return _classifier


def classify_content(text: str) -> List[Tuple[str, str, ClassificationResult]]:
    """
    智能分类内容（兼容旧接口）
    
    Args:
        text: 用户输入
    
    Returns:
        [(分类，内容，ClassificationResult), ...]
    """
    classifier = get_classifier()
    result = classifier.classify(text)
    
    # 返回兼容格式
    return [(result.category.value, text, result)]


def summarize_records(records: List[str]) -> Dict:
    """
    归纳总结多条记录
    
    Args:
        records: 记录列表
    
    Returns:
        总结字典
    """
    classifier = get_classifier()
    return classifier.summarize(records)


if __name__ == "__main__":
    # 测试代码
    print("🧪 FlashMemo OpenClaw AI Classifier 测试")
    print("=" * 60)
    
    test_cases = [
        "中午吃了碗拉面 20 块",
        "上午刚开会讨论完 Q3 的计划",
        "记得提醒我晚上给猫买猫粮",
        "今天收到工资 8000 元",
        "晚上和朋友去看了电影",
        "明天下午 3 点前提交项目报告给张总",
    ]
    
    classifier = OpenClawAIClassifier()
    
    for text in test_cases:
        print(f"\n输入：{text}")
        result = classifier.classify(text)
        print(f"分类：{result.category.value}")
        print(f"置信度：{result.confidence:.2f}")
        print(f"理由：{result.reasoning}")
        if result.urgency:
            print(f"紧急程度：{result.urgency.value}")
        if result.account_items:
            print(f"账目明细：{result.account_items}")
    
    print("\n" + "=" * 60)
    print("测试完成！")
