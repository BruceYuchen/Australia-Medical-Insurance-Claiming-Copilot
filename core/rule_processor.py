"""
规则处理器：将原始规则文本转换为结构化规则
"""
import json
import re
from typing import List, Dict, Any, Optional
from datetime import datetime
from core.schemas import StructuredRule, RuleType, RuleCondition, RuleAction

class RuleProcessor:
    """规则处理器类"""
    
    def __init__(self):
        self.rule_patterns = {
            RuleType.MUTUAL_EXCLUSION: [
                r"not.*claim.*same.*day",
                r"same.*day.*not.*permitted",
                r"co-claiming.*not.*permitted",
                r"cannot.*claim.*together"
            ],
            RuleType.BUNDLED_INCLUDES: [
                r"including.*associated",
                r"each attendance.*including",
                r"covers.*former",
                r"benefit.*covers"
            ],
            RuleType.EXCLUSION_PHRASE: [
                r"each attendance",
                r"attendance at which",
                r"including associated attendances",
                r"including associated consultations"
            ],
            RuleType.TIME_ACCOUNTING: [
                r"time.*not.*included",
                r"consultation time",
                r"time spent.*procedure"
            ],
            RuleType.PROVIDER_RESTRICTION: [
                r"specialist.*specialty",
                r"general practitioner",
                r"consultant physician",
                r"medical practitioner"
            ],
            RuleType.PATIENT_ELIGIBILITY: [
                r"not available to",
                r"available to",
                r"patient.*eligibility",
                r"residential aged care"
            ]
        }
    
    def process_rules(self, raw_rules: List[Dict[str, Any]]) -> List[StructuredRule]:
        """处理原始规则列表，返回结构化规则"""
        structured_rules = []
        
        for rule in raw_rules:
            try:
                structured_rule = self._process_single_rule(rule)
                if structured_rule:
                    structured_rules.append(structured_rule)
            except Exception as e:
                print(f"处理规则 {rule.get('rule_id', 'unknown')} 时出错: {e}")
                continue
        
        return structured_rules
    
    def _process_single_rule(self, rule: Dict[str, Any]) -> Optional[StructuredRule]:
        """处理单个规则"""
        rule_id = rule.get('rule_id', '')
        raw_text = rule.get('raw_text', '')
        
        if not raw_text:
            return None
        
        # 识别规则类型
        rule_type = self._identify_rule_type(raw_text)
        
        # 提取条件
        conditions = self._extract_conditions(raw_text, rule_type)
        
        # 提取动作
        actions = self._extract_actions(raw_text, rule_type)
        
        # 提取例外
        exceptions = self._extract_exceptions(raw_text)
        
        # 生成标题和描述
        title = self._generate_title(raw_text, rule_type)
        description = self._generate_description(raw_text, rule_type)
        
        return StructuredRule(
            rule_id=f"structured_{rule_id}",
            rule_type=rule_type,
            title=title,
            description=description,
            conditions=conditions,
            actions=actions,
            exceptions=exceptions,
            priority=self._calculate_priority(rule_type),
            source_rule_id=rule_id,
            source_text=raw_text
        )
    
    def _identify_rule_type(self, text: str) -> RuleType:
        """识别规则类型"""
        text_lower = text.lower()
        
        for rule_type, patterns in self.rule_patterns.items():
            for pattern in patterns:
                if re.search(pattern, text_lower):
                    return rule_type
        
        # 默认返回互斥规则
        return RuleType.MUTUAL_EXCLUSION
    
    def _extract_conditions(self, text: str, rule_type: RuleType) -> List[Dict[str, Any]]:
        """提取规则条件"""
        conditions = []
        
        if rule_type == RuleType.MUTUAL_EXCLUSION:
            # 提取互斥项目
            item_patterns = [
                r"items?\s+(\d+(?:[-\s]\d+)?(?:,\s*\d+(?:[-\s]\d+)?)*)",
                r"item\s+(\d+)",
                r"(\d{3,5})"
            ]
            
            for pattern in item_patterns:
                matches = re.findall(pattern, text, re.IGNORECASE)
                for match in matches:
                    if isinstance(match, tuple):
                        match = match[0]
                    
                    # 解析项目编号
                    items = self._parse_item_numbers(match)
                    if items:
                        conditions.append({
                            "field": "item_num",
                            "operator": "in",
                            "value": items,
                            "description": f"项目编号: {match}"
                        })
        
        elif rule_type == RuleType.BUNDLED_INCLUDES:
            # 提取包含关系
            include_patterns = [
                r"item\s+(\d+).*includes?\s+item\s+(\d+)",
                r"(\d+).*covers?\s+(\d+)"
            ]
            
            for pattern in include_patterns:
                matches = re.findall(pattern, text, re.IGNORECASE)
                for match in matches:
                    if len(match) == 2:
                        conditions.append({
                            "field": "bundled_items",
                            "operator": "includes",
                            "value": [match[0], match[1]],
                            "description": f"项目 {match[0]} 包含 {match[1]}"
                        })
        
        elif rule_type == RuleType.PROVIDER_RESTRICTION:
            # 提取提供者限制
            provider_patterns = [
                r"(general practitioner|specialist|consultant physician)",
                r"(\w+)\s+in\s+the\s+practice\s+of"
            ]
            
            for pattern in provider_patterns:
                matches = re.findall(pattern, text, re.IGNORECASE)
                for match in matches:
                    conditions.append({
                        "field": "provider_type",
                        "operator": "equals",
                        "value": match.lower(),
                        "description": f"提供者类型: {match}"
                    })
        
        return conditions
    
    def _extract_actions(self, text: str, rule_type: RuleType) -> List[Dict[str, Any]]:
        """提取规则动作"""
        actions = []
        
        if rule_type == RuleType.MUTUAL_EXCLUSION:
            actions.append({
                "action_type": "reject",
                "target_items": [],
                "reason": "同日互斥项目不能同时申报",
                "evidence": "规则要求同一天不能申报互斥的项目"
            })
        
        elif rule_type == RuleType.BUNDLED_INCLUDES:
            actions.append({
                "action_type": "modify",
                "target_items": [],
                "reason": "打包项目已包含其他服务",
                "evidence": "规则要求打包项目包含其他服务时不再单独计费"
            })
        
        elif rule_type == RuleType.EXCLUSION_PHRASE:
            actions.append({
                "action_type": "warn",
                "target_items": [],
                "reason": "包含例外短语的项目有特殊计费规则",
                "evidence": "项目描述包含特殊计费说明"
            })
        
        return actions
    
    def _extract_exceptions(self, text: str) -> List[Dict[str, Any]]:
        """提取例外情况"""
        exceptions = []
        
        # 查找例外关键词
        exception_patterns = [
            r"except\s+where\s+(.+?)(?:\.|$)",
            r"unless\s+(.+?)(?:\.|$)",
            r"provided\s+that\s+(.+?)(?:\.|$)"
        ]
        
        for pattern in exception_patterns:
            matches = re.findall(pattern, text, re.IGNORECASE | re.DOTALL)
            for match in matches:
                exceptions.append({
                    "condition": match.strip(),
                    "description": f"例外情况: {match.strip()}"
                })
        
        return exceptions
    
    def _parse_item_numbers(self, text: str) -> List[str]:
        """解析项目编号文本"""
        items = []
        
        # 处理范围，如 "3-5" 或 "3 to 5"
        range_pattern = r"(\d+)\s*[-–]\s*(\d+)"
        range_matches = re.findall(range_pattern, text)
        for start, end in range_matches:
            start_num, end_num = int(start), int(end)
            for i in range(start_num, end_num + 1):
                items.append(str(i))
        
        # 处理单个编号
        single_pattern = r"\b(\d{3,5})\b"
        single_matches = re.findall(single_pattern, text)
        for match in single_matches:
            if match not in items:
                items.append(match)
        
        return items
    
    def _generate_title(self, text: str, rule_type: RuleType) -> str:
        """生成规则标题"""
        titles = {
            RuleType.MUTUAL_EXCLUSION: "同日互斥规则",
            RuleType.BUNDLED_INCLUDES: "打包包含规则",
            RuleType.EXCLUSION_PHRASE: "例外短语规则",
            RuleType.TIME_ACCOUNTING: "时间计算规则",
            RuleType.PROVIDER_RESTRICTION: "提供者限制规则",
            RuleType.PATIENT_ELIGIBILITY: "患者资格规则"
        }
        
        return titles.get(rule_type, "通用规则")
    
    def _generate_description(self, text: str, rule_type: RuleType) -> str:
        """生成规则描述"""
        # 提取前100个字符作为描述
        description = text[:100].strip()
        if len(text) > 100:
            description += "..."
        
        return description
    
    def _calculate_priority(self, rule_type: RuleType) -> int:
        """计算规则优先级"""
        priorities = {
            RuleType.MUTUAL_EXCLUSION: 1,  # 最高优先级
            RuleType.BUNDLED_INCLUDES: 2,
            RuleType.EXCLUSION_PHRASE: 3,
            RuleType.TIME_ACCOUNTING: 4,
            RuleType.PROVIDER_RESTRICTION: 5,
            RuleType.PATIENT_ELIGIBILITY: 6
        }
        
        return priorities.get(rule_type, 10)

def load_and_process_rules(rules_file: str) -> List[StructuredRule]:
    """加载并处理规则文件"""
    with open(rules_file, 'r', encoding='utf-8') as f:
        raw_rules = json.load(f)
    
    processor = RuleProcessor()
    return processor.process_rules(raw_rules)

if __name__ == "__main__":
    # 测试规则处理
    rules_file = "/Users/yz/Code/mbs-matcher/data/mbs_rules.json"
    structured_rules = load_and_process_rules(rules_file)
    
    print(f"处理了 {len(structured_rules)} 条结构化规则")
    for rule in structured_rules[:3]:  # 显示前3条
        print(f"\n规则ID: {rule.rule_id}")
        print(f"类型: {rule.rule_type}")
        print(f"标题: {rule.title}")
        print(f"条件数: {len(rule.conditions)}")
        print(f"动作数: {len(rule.actions)}")
