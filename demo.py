#!/usr/bin/env python3
"""
MBS匹配系统演示脚本
"""
import requests
import json
from datetime import datetime

def demo_system():
    """演示系统功能"""
    base_url = "http://localhost:8000"
    
    print("🚀 MBS匹配系统演示")
    print("=" * 50)
    
    # 1. 健康检查
    print("\n1. 健康检查")
    try:
        response = requests.get(f"{base_url}/health")
        health = response.json()
        print(f"✅ 系统状态: {health['status']}")
        print(f"📊 数据库项目数: {health['total_items']}")
        print(f"🔧 加载规则数: {health['rules_loaded']}")
    except Exception as e:
        print(f"❌ 健康检查失败: {e}")
        return
    
    # 2. 症状文本搜索演示
    print("\n2. 症状文本搜索演示")
    search_cases = [
        {
            "transcript": "患者主诉胸痛、呼吸困难，需要咨询",
            "description": "胸痛呼吸困难咨询"
        },
        {
            "transcript": "general practitioner consultation 20 minutes",
            "description": "全科医生20分钟咨询"
        },
        {
            "transcript": "mental health assessment and treatment plan",
            "description": "心理健康评估和治疗计划"
        }
    ]
    
    for i, case in enumerate(search_cases, 1):
        print(f"\n案例 {i}: {case['description']}")
        try:
            request_data = {
                "transcript": case["transcript"],
                "context": {
                    "setting": "consulting_rooms",
                    "duration": 30,
                    "referral": False,
                    "provider": "general practitioner",
                    "date": datetime.now().isoformat(),
                    "patient_type": "community"
                },
                "top_k": 3
            }
            
            response = requests.post(f"{base_url}/suggest_items", json=request_data)
            result = response.json()
            
            print(f"   找到 {result['total_found']} 个建议项目:")
            for j, suggestion in enumerate(result['suggestions'], 1):
                print(f"   {j}. Item {suggestion['item_num']} (分数: {suggestion['score']:.4f})")
                print(f"      {suggestion['description'][:80]}...")
                
        except Exception as e:
            print(f"   ❌ 搜索失败: {e}")
    
    # 3. 项目验证演示
    print("\n3. 项目验证演示")
    validation_cases = [
        {
            "items": ["3", "4", "23"],
            "description": "基础咨询项目组合"
        },
        {
            "items": ["721", "723", "732"],
            "description": "慢性病管理项目组合"
        }
    ]
    
    for i, case in enumerate(validation_cases, 1):
        print(f"\n案例 {i}: {case['description']}")
        try:
            request_data = {
                "selected_items": case["items"],
                "context": {
                    "setting": "consulting_rooms",
                    "duration": 30,
                    "referral": False,
                    "provider": "general practitioner",
                    "date": datetime.now().isoformat(),
                    "patient_type": "community"
                }
            }
            
            response = requests.post(f"{base_url}/validate_claim", json=request_data)
            result = response.json()
            
            print(f"   可计费项目: {result['result']['billable_items']}")
            print(f"   被拒绝项目: {result['result']['rejected_items']}")
            print(f"   冲突数量: {len(result['result']['conflicts'])}")
            print(f"   处理时间: {result['processing_time']:.4f}秒")
            
            if result['result']['why']:
                print(f"   原因: {result['result']['why'][0]}")
                
        except Exception as e:
            print(f"   ❌ 验证失败: {e}")
    
    # 4. 统计信息
    print("\n4. 系统统计信息")
    try:
        response = requests.get(f"{base_url}/statistics")
        stats = response.json()
        
        print(f"📊 总项目数: {stats['total_items']}")
        print(f"📊 主要组别分布:")
        for group, count in list(stats['group_distribution'].items())[:5]:
            print(f"   {group}: {count} 个项目")
        
        print(f"📊 类别分布:")
        for category, count in stats['category_distribution'].items():
            print(f"   类别 {category}: {count} 个项目")
            
    except Exception as e:
        print(f"❌ 获取统计信息失败: {e}")
    
    # 5. 规则信息
    print("\n5. 规则信息")
    try:
        response = requests.get(f"{base_url}/rules")
        rules = response.json()
        
        print(f"🔧 总规则数: {rules['total_rules']}")
        print(f"🔧 规则类型分布:")
        
        rule_types = {}
        for rule in rules['rules']:
            rule_type = rule['rule_type']
            rule_types[rule_type] = rule_types.get(rule_type, 0) + 1
        
        for rule_type, count in rule_types.items():
            print(f"   {rule_type}: {count} 条规则")
            
    except Exception as e:
        print(f"❌ 获取规则信息失败: {e}")
    
    print("\n" + "=" * 50)
    print("🎉 演示完成！")
    print("💡 访问 http://localhost:8000/docs 查看完整API文档")

if __name__ == "__main__":
    demo_system()
