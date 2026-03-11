"""
规则机：实现确定性的规则验证逻辑
支持禁并报优先、打包包含、例外白名单三大核心逻辑
"""
import sqlite3
from typing import List, Dict, Any, Set, Tuple
from datetime import datetime
from core.schemas import (
    StructuredRule, ValidationContext, ValidationResult, 
    MBSItem, RuleType
)

class RuleEngine:
    """规则机类"""
    
    def __init__(self, db_path: str, structured_rules: List[StructuredRule]):
        self.db_path = db_path
        self.structured_rules = structured_rules
        self.rules_by_type = self._organize_rules_by_type()
    
    def _organize_rules_by_type(self) -> Dict[RuleType, List[StructuredRule]]:
        """按规则类型组织规则"""
        rules_by_type = {}
        for rule in self.structured_rules:
            if rule.rule_type not in rules_by_type:
                rules_by_type[rule.rule_type] = []
            rules_by_type[rule.rule_type].append(rule)
        
        # 按优先级排序
        for rule_type in rules_by_type:
            rules_by_type[rule_type].sort(key=lambda x: x.priority)
        
        return rules_by_type
    
    def validate_claim(self, selected_items: List[str], context: ValidationContext) -> ValidationResult:
        """验证申报项目"""
        # 获取项目详情
        items = self._get_items_details(selected_items)
        
        # 初始化结果
        billable_items = selected_items.copy()
        rejected_items = []
        conflicts = []
        fixes = []
        why = []
        evidence = []
        
        # 按优先级顺序应用规则
        rule_order = [
            RuleType.MUTUAL_EXCLUSION,  # 禁并报优先
            RuleType.BUNDLED_INCLUDES,  # 打包包含
            RuleType.EXCLUSION_PHRASE,  # 例外白名单
            RuleType.TIME_ACCOUNTING,
            RuleType.PROVIDER_RESTRICTION,
            RuleType.PATIENT_ELIGIBILITY
        ]
        
        for rule_type in rule_order:
            if rule_type in self.rules_by_type:
                for rule in self.rules_by_type[rule_type]:
                    result = self._apply_rule(rule, items, context, billable_items, rejected_items)
                    if result:
                        conflicts.extend(result.get('conflicts', []))
                        fixes.extend(result.get('fixes', []))
                        why.extend(result.get('why', []))
                        evidence.extend(result.get('evidence', []))
                        
                        # 更新可计费项目列表
                        if 'rejected' in result:
                            for item in result['rejected']:
                                if item in billable_items:
                                    billable_items.remove(item)
                                    if item not in rejected_items:
                                        rejected_items.append(item)
        
        return ValidationResult(
            billable_items=billable_items,
            rejected_items=rejected_items,
            conflicts=conflicts,
            fixes=fixes,
            why=why,
            evidence=evidence
        )
    
    def _get_items_details(self, item_nums: List[str]) -> Dict[str, MBSItem]:
        """获取项目详情"""
        items = {}
        
        with sqlite3.connect(self.db_path) as conn:
            cursor = conn.cursor()
            
            for item_num in item_nums:
                cursor.execute("""
                    SELECT item_num, description, [group], category, subgroup, subheading,
                           provider_type, item_type, benefit_type, fee_type, emsn_cap,
                           emsn_fixed_cap_amount, [exists]
                    FROM mbs_items WHERE item_num = ?
                """, (item_num,))
                
                row = cursor.fetchone()
                if row:
                    items[item_num] = MBSItem(
                        item_num=str(row[0]),
                        description=row[1] or "",
                        group=row[2] or "",
                        category=row[3] or 0,
                        subgroup=row[4],
                        subheading=row[5],
                        provider_type=row[6],
                        item_type=row[7] or "",
                        benefit_type=row[8] or "",
                        fee_type=row[9] or "",
                        emsn_cap=row[10] or "",
                        emsn_fixed_cap_amount=row[11],
                        exists=row[12]
                    )
        
        return items
    
    def _apply_rule(self, rule: StructuredRule, items: Dict[str, MBSItem], 
                   context: ValidationContext, billable_items: List[str], 
                   rejected_items: List[str]) -> Dict[str, Any]:
        """应用单个规则"""
        if rule.rule_type == RuleType.MUTUAL_EXCLUSION:
            return self._apply_mutual_exclusion_rule(rule, items, context, billable_items)
        elif rule.rule_type == RuleType.BUNDLED_INCLUDES:
            return self._apply_bundled_includes_rule(rule, items, context, billable_items)
        elif rule.rule_type == RuleType.EXCLUSION_PHRASE:
            return self._apply_exclusion_phrase_rule(rule, items, context, billable_items)
        elif rule.rule_type == RuleType.TIME_ACCOUNTING:
            return self._apply_time_accounting_rule(rule, items, context, billable_items)
        elif rule.rule_type == RuleType.PROVIDER_RESTRICTION:
            return self._apply_provider_restriction_rule(rule, items, context, billable_items)
        elif rule.rule_type == RuleType.PATIENT_ELIGIBILITY:
            return self._apply_patient_eligibility_rule(rule, items, context, billable_items)
        
        return {}
    
    def _apply_mutual_exclusion_rule(self, rule: StructuredRule, items: Dict[str, MBSItem],
                                   context: ValidationContext, billable_items: List[str]) -> Dict[str, Any]:
        """应用互斥规则"""
        conflicts = []
        rejected = []
        why = []
        evidence = []
        
        # 查找互斥项目组
        exclusion_groups = self._find_exclusion_groups(rule, items)
        
        for group in exclusion_groups:
            if len(group) > 1:
                # 找到组中在可计费列表中的项目
                conflicting_items = [item for item in group if item in billable_items]
                
                if len(conflicting_items) > 1:
                    # 保留第一个，拒绝其他的
                    keep_item = conflicting_items[0]
                    reject_items = conflicting_items[1:]
                    
                    conflicts.append({
                        "type": "mutual_exclusion",
                        "conflicting_items": conflicting_items,
                        "keep_item": keep_item,
                        "reject_items": reject_items,
                        "rule_id": rule.rule_id
                    })
                    
                    rejected.extend(reject_items)
                    why.append(f"项目 {', '.join(reject_items)} 与 {keep_item} 互斥，同一天不能同时申报")
                    evidence.append({
                        "rule_id": rule.rule_id,
                        "evidence": f"互斥规则: {rule.title}",
                        "source": rule.source_text[:200]
                    })
        
        return {
            "conflicts": conflicts,
            "rejected": rejected,
            "why": why,
            "evidence": evidence
        }
    
    def _apply_bundled_includes_rule(self, rule: StructuredRule, items: Dict[str, MBSItem],
                                   context: ValidationContext, billable_items: List[str]) -> Dict[str, Any]:
        """应用打包包含规则"""
        conflicts = []
        rejected = []
        why = []
        evidence = []
        
        # 查找打包关系
        bundled_relations = self._find_bundled_relations(rule, items)
        
        for main_item, included_items in bundled_relations.items():
            if main_item in billable_items:
                # 主项目在列表中，检查是否包含其他项目
                conflicting_included = [item for item in included_items if item in billable_items]
                
                if conflicting_included:
                    conflicts.append({
                        "type": "bundled_includes",
                        "main_item": main_item,
                        "included_items": conflicting_included,
                        "rule_id": rule.rule_id
                    })
                    
                    rejected.extend(conflicting_included)
                    why.append(f"项目 {main_item} 已包含 {', '.join(conflicting_included)}，无需单独申报")
                    evidence.append({
                        "rule_id": rule.rule_id,
                        "evidence": f"打包规则: {rule.title}",
                        "source": rule.source_text[:200]
                    })
        
        return {
            "conflicts": conflicts,
            "rejected": rejected,
            "why": why,
            "evidence": evidence
        }
    
    def _apply_exclusion_phrase_rule(self, rule: StructuredRule, items: Dict[str, MBSItem],
                                   context: ValidationContext, billable_items: List[str]) -> Dict[str, Any]:
        """应用例外短语规则"""
        conflicts = []
        fixes = []
        why = []
        evidence = []
        
        # 检查项目描述中的例外短语
        exclusion_phrases = [
            "each attendance",
            "attendance at which",
            "including associated attendances",
            "including associated consultations"
        ]
        
        for item_num, item in items.items():
            if item_num in billable_items:
                description_lower = item.description.lower()
                
                for phrase in exclusion_phrases:
                    if phrase in description_lower:
                        conflicts.append({
                            "type": "exclusion_phrase",
                            "item": item_num,
                            "phrase": phrase,
                            "rule_id": rule.rule_id
                        })
                        
                        fixes.append({
                            "type": "warning",
                            "item": item_num,
                            "suggestion": f"项目 {item_num} 包含特殊计费说明: '{phrase}'",
                            "rule_id": rule.rule_id
                        })
                        
                        why.append(f"项目 {item_num} 包含例外短语 '{phrase}'，需要特殊处理")
                        evidence.append({
                            "rule_id": rule.rule_id,
                            "evidence": f"例外短语规则: {rule.title}",
                            "source": f"项目描述: {item.description[:100]}..."
                        })
        
        return {
            "conflicts": conflicts,
            "fixes": fixes,
            "why": why,
            "evidence": evidence
        }
    
    def _apply_time_accounting_rule(self, rule: StructuredRule, items: Dict[str, MBSItem],
                                  context: ValidationContext, billable_items: List[str]) -> Dict[str, Any]:
        """应用时间计算规则"""
        # 这里可以实现时间相关的规则逻辑
        # 例如：咨询时间不能包含操作时间等
        return {}
    
    def _apply_provider_restriction_rule(self, rule: StructuredRule, items: Dict[str, MBSItem],
                                       context: ValidationContext, billable_items: List[str]) -> Dict[str, Any]:
        """应用提供者限制规则"""
        conflicts = []
        rejected = []
        why = []
        evidence = []
        
        # 检查提供者类型限制
        for condition in rule.conditions:
            if condition.get("field") == "provider_type":
                required_provider = condition.get("value", "").lower()
                if context.provider.lower() != required_provider:
                    # 找到需要特定提供者的项目
                    restricted_items = [item for item in billable_items if self._item_requires_provider(item, required_provider)]
                    
                    if restricted_items:
                        conflicts.append({
                            "type": "provider_restriction",
                            "items": restricted_items,
                            "required_provider": required_provider,
                            "actual_provider": context.provider,
                            "rule_id": rule.rule_id
                        })
                        
                        rejected.extend(restricted_items)
                        why.append(f"项目 {', '.join(restricted_items)} 需要 {required_provider} 提供，当前提供者为 {context.provider}")
                        evidence.append({
                            "rule_id": rule.rule_id,
                            "evidence": f"提供者限制规则: {rule.title}",
                            "source": rule.source_text[:200]
                        })
        
        return {
            "conflicts": conflicts,
            "rejected": rejected,
            "why": why,
            "evidence": evidence
        }
    
    def _apply_patient_eligibility_rule(self, rule: StructuredRule, items: Dict[str, MBSItem],
                                      context: ValidationContext, billable_items: List[str]) -> Dict[str, Any]:
        """应用患者资格规则"""
        conflicts = []
        rejected = []
        why = []
        evidence = []
        
        # 检查患者类型限制
        for condition in rule.conditions:
            if condition.get("field") == "patient_type":
                required_patient_type = condition.get("value", "").lower()
                if context.patient_type.lower() != required_patient_type:
                    # 找到需要特定患者类型的项目
                    restricted_items = [item for item in billable_items if self._item_requires_patient_type(item, required_patient_type)]
                    
                    if restricted_items:
                        conflicts.append({
                            "type": "patient_eligibility",
                            "items": restricted_items,
                            "required_patient_type": required_patient_type,
                            "actual_patient_type": context.patient_type,
                            "rule_id": rule.rule_id
                        })
                        
                        rejected.extend(restricted_items)
                        why.append(f"项目 {', '.join(restricted_items)} 需要 {required_patient_type} 患者，当前患者类型为 {context.patient_type}")
                        evidence.append({
                            "rule_id": rule.rule_id,
                            "evidence": f"患者资格规则: {rule.title}",
                            "source": rule.source_text[:200]
                        })
        
        return {
            "conflicts": conflicts,
            "rejected": rejected,
            "why": why,
            "evidence": evidence
        }
    
    def _find_exclusion_groups(self, rule: StructuredRule, items: Dict[str, MBSItem]) -> List[List[str]]:
        """查找互斥项目组"""
        groups = []
        
        for condition in rule.conditions:
            if condition.get("field") == "item_num" and condition.get("operator") == "in":
                item_list = condition.get("value", [])
                if isinstance(item_list, list) and len(item_list) > 1:
                    groups.append(item_list)
        
        return groups
    
    def _find_bundled_relations(self, rule: StructuredRule, items: Dict[str, MBSItem]) -> Dict[str, List[str]]:
        """查找打包关系"""
        relations = {}
        
        for condition in rule.conditions:
            if condition.get("field") == "bundled_items" and condition.get("operator") == "includes":
                value = condition.get("value", [])
                if isinstance(value, list) and len(value) >= 2:
                    main_item = value[0]
                    included_items = value[1:]
                    relations[main_item] = included_items
        
        return relations
    
    def _item_requires_provider(self, item_num: str, provider_type: str) -> bool:
        """检查项目是否需要特定提供者类型"""
        # 这里可以根据项目编号或描述判断
        # 简化实现：检查项目描述中是否包含特定提供者类型
        with sqlite3.connect(self.db_path) as conn:
            cursor = conn.cursor()
            cursor.execute("SELECT description FROM mbs_items WHERE item_num = ?", (item_num,))
            row = cursor.fetchone()
            
            if row and row[0]:
                description = row[0].lower()
                return provider_type.lower() in description
        
        return False
    
    def _item_requires_patient_type(self, item_num: str, patient_type: str) -> bool:
        """检查项目是否需要特定患者类型"""
        # 这里可以根据项目编号或描述判断
        # 简化实现：检查项目描述中是否包含特定患者类型关键词
        with sqlite3.connect(self.db_path) as conn:
            cursor = conn.cursor()
            cursor.execute("SELECT description FROM mbs_items WHERE item_num = ?", (item_num,))
            row = cursor.fetchone()
            
            if row and row[0]:
                description = row[0].lower()
                patient_keywords = {
                    "community": ["community", "outpatient"],
                    "hospital_inpatient": ["inpatient", "hospital"],
                    "aged_care": ["aged care", "residential", "facility"]
                }
                
                keywords = patient_keywords.get(patient_type, [])
                return any(keyword in description for keyword in keywords)
        
        return False
