"""
MBS匹配系统的数据模型和JSON Schema定义
"""
from typing import List, Optional, Dict, Any, Union
from pydantic import BaseModel, Field
from datetime import datetime
from enum import Enum

class RuleType(str, Enum):
    """规则类型枚举"""
    MUTUAL_EXCLUSION = "mutual_exclusion"  # 同日禁并报
    BUNDLED_INCLUDES = "bundled_includes"  # 打包包含
    EXCLUSION_PHRASE = "exclusion_phrase"  # 例外短语
    TIME_ACCOUNTING = "time_accounting"    # 时间计算
    PROVIDER_RESTRICTION = "provider_restriction"  # 提供者限制
    PATIENT_ELIGIBILITY = "patient_eligibility"    # 患者资格

class ItemType(str, Enum):
    """项目类型枚举"""
    CONSULTATION = "consultation"
    PROCEDURE = "procedure"
    DIAGNOSTIC = "diagnostic"
    THERAPEUTIC = "therapeutic"
    ANESTHETIC = "anesthetic"

class MBSItem(BaseModel):
    """MBS项目模型"""
    item_num: str
    description: str
    group: str
    category: int
    subgroup: Optional[float] = None
    subheading: Optional[float] = None
    provider_type: Optional[str] = None
    item_type: str
    benefit_type: str
    fee_type: str
    emsn_cap: str
    emsn_fixed_cap_amount: Optional[float] = None
    exists: Optional[float] = None

class StructuredRule(BaseModel):
    """结构化规则模型"""
    rule_id: str
    rule_type: RuleType
    title: str
    description: str
    conditions: List[Dict[str, Any]]  # 条件列表
    actions: List[Dict[str, Any]]     # 动作列表
    exceptions: List[Dict[str, Any]]  # 例外情况
    priority: int = 1  # 优先级，数字越小优先级越高
    effective_date: Optional[datetime] = None
    source_rule_id: str  # 原始规则ID
    source_text: str     # 原始文本

class RuleCondition(BaseModel):
    """规则条件模型"""
    field: str  # 字段名，如item_num, group, category等
    operator: str  # 操作符，如in, not_in, equals, contains等
    value: Union[str, List[str], int, float]  # 值
    description: str  # 条件描述

class RuleAction(BaseModel):
    """规则动作模型"""
    action_type: str  # 动作类型：reject, allow, modify, warn等
    target_items: List[str]  # 目标项目编号
    reason: str  # 原因
    evidence: str  # 证据片段

class ValidationContext(BaseModel):
    """验证上下文模型"""
    setting: str  # 设置：consulting_rooms, institution, home等
    duration: Optional[int] = None  # 持续时间（分钟）
    referral: bool = False  # 是否转诊
    provider: str  # 提供者类型
    date: datetime  # 日期
    patient_type: str = "community"  # 患者类型：community, hospital_inpatient, aged_care等

class ValidationResult(BaseModel):
    """验证结果模型"""
    billable_items: List[str]  # 可计费项目
    rejected_items: List[str]  # 被拒绝项目
    conflicts: List[Dict[str, Any]]  # 冲突列表
    fixes: List[Dict[str, Any]]  # 修复建议
    why: List[str]  # 原因说明
    evidence: List[Dict[str, str]]  # 证据片段

class ItemSuggestion(BaseModel):
    """项目建议模型"""
    item_num: str
    description: str
    score: float
    group: str
    category: int
    provider_type: Optional[str]
    matched_fields: List[str]  # 匹配的字段
    evidence: str  # 证据片段

class SuggestionRequest(BaseModel):
    """建议请求模型"""
    transcript: str
    context: ValidationContext
    top_k: int = 10

class ValidationRequest(BaseModel):
    """验证请求模型"""
    selected_items: List[str]  # 已选择的项目编号
    context: ValidationContext

class SuggestionResponse(BaseModel):
    """建议响应模型"""
    suggestions: List[ItemSuggestion]
    total_found: int

class ValidationResponse(BaseModel):
    """验证响应模型"""
    result: ValidationResult
    processing_time: float
