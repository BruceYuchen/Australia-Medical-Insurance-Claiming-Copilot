#!/usr/bin/env python3
"""
MBS匹配系统测试脚本
"""
import sys
import os
import json
from datetime import datetime

# 添加app目录到Python路径
sys.path.append(os.path.join(os.path.dirname(__file__), 'app'))

from app.database import get_db_manager
from app.rule_processor import load_and_process_rules
from app.rule_engine import RuleEngine
from app.schemas import ValidationContext

def test_database():
    """测试数据库连接和查询"""
    print("=== 测试数据库连接 ===")
    
    try:
        db = get_db_manager()
        stats = db.get_statistics()
        
        print(f"✅ 数据库连接成功")
        print(f"📊 总项目数: {stats.get('total_items', 0)}")
        print(f"📊 组分布: {list(stats.get('group_distribution', {}).keys())[:5]}")
        
        # 测试搜索功能
        suggestions = db.search_items_by_text("consultation general practitioner", top_k=3)
        print(f"🔍 搜索测试: 找到 {len(suggestions)} 个建议")
        
        if suggestions:
            print(f"   第一个建议: Item {suggestions[0].item_num} (分数: {suggestions[0].score:.4f})")
        
        return True
        
    except Exception as e:
        print(f"❌ 数据库测试失败: {e}")
        return False

def test_rule_processing():
    """测试规则处理"""
    print("\n=== 测试规则处理 ===")
    
    try:
        rules_file = "/Users/yz/Code/mbs-matcher/data/mbs_rules.json"
        structured_rules = load_and_process_rules(rules_file)
        
        print(f"✅ 规则处理成功")
        print(f"📋 处理了 {len(structured_rules)} 条规则")
        
        # 显示规则类型分布
        rule_types = {}
        for rule in structured_rules:
            rule_type = rule.rule_type
            rule_types[rule_type] = rule_types.get(rule_type, 0) + 1
        
        print(f"📊 规则类型分布: {rule_types}")
        
        # 显示前3条规则
        for i, rule in enumerate(structured_rules[:3]):
            print(f"   规则 {i+1}: {rule.title} ({rule.rule_type})")
        
        return structured_rules
        
    except Exception as e:
        print(f"❌ 规则处理失败: {e}")
        return []

def test_rule_engine(structured_rules):
    """测试规则引擎"""
    print("\n=== 测试规则引擎 ===")
    
    try:
        engine = RuleEngine("/Users/yz/Code/mbs-matcher/data/mbs.db", structured_rules)
        
        print(f"✅ 规则引擎初始化成功")
        print(f"🔧 加载了 {len(engine.structured_rules)} 条规则")
        
        # 测试验证功能
        test_items = ["3", "4", "23"]  # 一些常见的咨询项目
        test_context = ValidationContext(
            setting="consulting_rooms",
            duration=20,
            referral=False,
            provider="general practitioner",
            date=datetime.now(),
            patient_type="community"
        )
        
        print(f"🧪 测试验证: 项目 {test_items}")
        result = engine.validate_claim(test_items, test_context)
        
        print(f"✅ 验证完成")
        print(f"   可计费项目: {result.billable_items}")
        print(f"   被拒绝项目: {result.rejected_items}")
        print(f"   冲突数量: {len(result.conflicts)}")
        print(f"   修复建议: {len(result.fixes)}")
        
        return True
        
    except Exception as e:
        print(f"❌ 规则引擎测试失败: {e}")
        return False

def test_end_to_end():
    """端到端测试"""
    print("\n=== 端到端测试 ===")
    
    try:
        # 初始化组件
        db = get_db_manager()
        rules_file = "/Users/yz/Code/mbs-matcher/data/mbs_rules.json"
        structured_rules = load_and_process_rules(rules_file)
        engine = RuleEngine("/Users/yz/Code/mbs-matcher/data/mbs.db", structured_rules)
        
        # 模拟症状到项目建议
        print("🔍 步骤1: 症状文本搜索")
        transcript = "patient complains of chest pain, shortness of breath, needs consultation"
        suggestions = db.search_items_by_text(transcript, top_k=5)
        
        print(f"   找到 {len(suggestions)} 个建议项目")
        for i, suggestion in enumerate(suggestions[:3]):
            print(f"   {i+1}. Item {suggestion.item_num}: {suggestion.description[:50]}...")
        
        # 模拟项目验证
        print("\n🔍 步骤2: 项目验证")
        selected_items = [s.item_num for s in suggestions[:3]]
        context = ValidationContext(
            setting="consulting_rooms",
            duration=30,
            referral=False,
            provider="general practitioner",
            date=datetime.now(),
            patient_type="community"
        )
        
        validation_result = engine.validate_claim(selected_items, context)
        
        print(f"   验证结果:")
        print(f"   - 可计费: {validation_result.billable_items}")
        print(f"   - 被拒绝: {validation_result.rejected_items}")
        print(f"   - 冲突: {len(validation_result.conflicts)}")
        
        if validation_result.why:
            print(f"   - 原因: {validation_result.why[0]}")
        
        print("✅ 端到端测试完成")
        return True
        
    except Exception as e:
        print(f"❌ 端到端测试失败: {e}")
        return False

def main():
    """主测试函数"""
    print("🚀 开始MBS匹配系统测试\n")
    
    # 测试数据库
    db_ok = test_database()
    
    # 测试规则处理
    structured_rules = test_rule_processing()
    
    # 测试规则引擎
    engine_ok = test_rule_engine(structured_rules) if structured_rules else False
    
    # 端到端测试
    e2e_ok = test_end_to_end()
    
    # 总结
    print("\n" + "="*50)
    print("📋 测试总结:")
    print(f"   数据库: {'✅ 通过' if db_ok else '❌ 失败'}")
    print(f"   规则处理: {'✅ 通过' if structured_rules else '❌ 失败'}")
    print(f"   规则引擎: {'✅ 通过' if engine_ok else '❌ 失败'}")
    print(f"   端到端: {'✅ 通过' if e2e_ok else '❌ 失败'}")
    
    if all([db_ok, structured_rules, engine_ok, e2e_ok]):
        print("\n🎉 所有测试通过！系统可以正常运行。")
        print("\n💡 启动API服务器:")
        print("   cd /Users/yz/Code/mbs-matcher")
        print("   python -m uvicorn app.main:app --reload --host 0.0.0.0 --port 8000")
        print("\n📖 API文档: http://localhost:8000/docs")
    else:
        print("\n⚠️  部分测试失败，请检查错误信息。")
        return 1
    
    return 0

if __name__ == "__main__":
    sys.exit(main())
