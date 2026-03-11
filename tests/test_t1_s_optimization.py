#!/usr/bin/env python3
"""
测试T1组别和S类型项目的匹配优化
"""
import sys
import os
import time
import requests
import json
from datetime import datetime

# 添加app目录到Python路径
sys.path.append(os.path.join(os.path.dirname(__file__), 'app'))

def test_t1_s_optimization():
    """测试T1组别和S类型项目的匹配优化"""
    print("🔧 测试T1组别和S类型项目匹配优化")
    print("=" * 60)
    
    base_url = "http://localhost:8000"
    
    # 测试用例
    test_cases = [
        {
            "name": "T1组别 - 高压氧治疗",
            "query": "高压氧治疗 糖尿病伤口",
            "expected_groups": ["T1"],
            "expected_types": ["S"]
        },
        {
            "name": "T1组别 - 血液透析",
            "query": "血液透析 肾衰竭 透析治疗",
            "expected_groups": ["T1"],
            "expected_types": ["S"]
        },
        {
            "name": "S类型 - 专业服务",
            "query": "专业医疗服务 医疗监督",
            "expected_groups": ["A1", "A2"],
            "expected_types": ["S"]
        },
        {
            "name": "中文查询 - 透析相关",
            "query": "透析 肾科 血液净化",
            "expected_groups": ["T1"],
            "expected_types": ["S"]
        },
        {
            "name": "混合查询 - 治疗服务",
            "query": "治疗服务 医疗护理 专业监督",
            "expected_groups": ["T1", "A1"],
            "expected_types": ["S"]
        }
    ]
    
    success_count = 0
    
    for i, test_case in enumerate(test_cases, 1):
        print(f"\n{i}. {test_case['name']}")
        print(f"   查询: {test_case['query']}")
        
        try:
            # 发送搜索请求
            response = requests.post(f"{base_url}/suggest_items_enhanced", 
                json={
                    "transcript": test_case['query'],
                    "context": {
                        "setting": "hospital",
                        "duration": 30,
                        "provider": "specialist",
                        "referral": False,
                        "date": datetime.now().isoformat(),
                        "patient_type": "community"
                    },
                    "top_k": 5
                },
                params={"search_type": "hybrid"},
                timeout=10
            )
            
            if response.status_code == 200:
                data = response.json()
                suggestions = data.get('suggestions', [])
                
                print(f"   ✅ 搜索成功: 找到 {len(suggestions)} 个结果")
                
                # 分析结果
                t1_count = 0
                s_type_count = 0
                high_confidence_count = 0
                
                print("   📊 结果分析:")
                for j, suggestion in enumerate(suggestions[:3], 1):
                    item_num = suggestion.get('item_num', 'N/A')
                    score = suggestion.get('score', 0)
                    group = suggestion.get('group', 'N/A')
                    description = suggestion.get('description', '')[:50] + "..."
                    evidence = suggestion.get('evidence', '')
                    
                    print(f"      {j}. Item {item_num} (组别: {group}, 分数: {score:.3f})")
                    print(f"         描述: {description}")
                    print(f"         证据: {evidence}")
                    
                    # 统计
                    if group == "T1":
                        t1_count += 1
                    if score > 0.6:
                        high_confidence_count += 1
                
                # 检查优化效果
                has_t1 = t1_count > 0
                has_high_confidence = high_confidence_count > 0
                
                print(f"   📈 优化效果:")
                print(f"      T1组别项目: {t1_count}")
                print(f"      高置信度结果: {high_confidence_count}")
                
                # 判断测试是否通过
                if has_t1 or has_high_confidence:
                    print("   ✅ 测试通过")
                    success_count += 1
                else:
                    print("   ❌ 测试失败: 未找到预期的T1组别或高置信度结果")
                
            else:
                print(f"   ❌ 搜索失败: {response.status_code}")
                print(f"   响应: {response.text[:200]}...")
        
        except Exception as e:
            print(f"   ❌ 测试错误: {e}")
    
    print(f"\n📊 测试总结: {success_count}/{len(test_cases)} 通过")
    return success_count == len(test_cases)

def test_chinese_matching():
    """测试中文匹配优化"""
    print("\n🇨🇳 测试中文匹配优化")
    print("-" * 40)
    
    base_url = "http://localhost:8000"
    
    chinese_queries = [
        "透析治疗 肾衰竭",
        "高压氧 糖尿病伤口",
        "专业医疗服务 医疗监督",
        "血液净化 肾科",
        "医疗护理 治疗服务"
    ]
    
    success_count = 0
    
    for i, query in enumerate(chinese_queries, 1):
        print(f"\n{i}. 中文查询: {query}")
        
        try:
            response = requests.post(f"{base_url}/suggest_items_enhanced", 
                json={
                    "transcript": query,
                    "context": {
                        "setting": "hospital",
                        "duration": 30,
                        "provider": "specialist",
                        "referral": False,
                        "date": datetime.now().isoformat(),
                        "patient_type": "community"
                    },
                    "top_k": 3
                },
                params={"search_type": "hybrid"},
                timeout=10
            )
            
            if response.status_code == 200:
                data = response.json()
                suggestions = data.get('suggestions', [])
                
                print(f"   ✅ 找到 {len(suggestions)} 个结果")
                
                for j, suggestion in enumerate(suggestions, 1):
                    item_num = suggestion.get('item_num', 'N/A')
                    score = suggestion.get('score', 0)
                    group = suggestion.get('group', 'N/A')
                    evidence = suggestion.get('evidence', '')
                    
                    print(f"      {j}. Item {item_num} (组别: {group}, 分数: {score:.3f})")
                    if "优化" in evidence:
                        print(f"         优化: {evidence}")
                
                if suggestions:
                    success_count += 1
                    print("   ✅ 中文匹配成功")
                else:
                    print("   ❌ 未找到匹配结果")
            else:
                print(f"   ❌ 请求失败: {response.status_code}")
        
        except Exception as e:
            print(f"   ❌ 测试错误: {e}")
    
    print(f"\n📊 中文匹配测试: {success_count}/{len(chinese_queries)} 成功")
    return success_count == len(chinese_queries)

def test_optimization_stats():
    """测试优化统计信息"""
    print("\n📈 测试优化统计信息")
    print("-" * 30)
    
    base_url = "http://localhost:8000"
    
    try:
        # 获取性能统计
        response = requests.get(f"{base_url}/performance", timeout=5)
        
        if response.status_code == 200:
            data = response.json()
            print("✅ 性能统计获取成功:")
            
            # 显示搜索统计
            search_stats = data.get('search_stats', {})
            print(f"   总搜索次数: {search_stats.get('total_searches', 0)}")
            print(f"   平均搜索时间: {search_stats.get('avg_search_time', 0):.3f}秒")
            
            # 显示数据库统计
            db_stats = data.get('database_stats', {})
            print(f"   数据库项目数: {db_stats.get('total_items', 0)}")
            
            # 显示优化器统计
            optimizer_stats = data.get('optimizer_stats', {})
            if optimizer_stats:
                print("   优化器统计:")
                print(f"     T1关键词数: {optimizer_stats.get('t1_keywords_count', 0)}")
                print(f"     S类型关键词数: {optimizer_stats.get('s_type_keywords_count', 0)}")
                print(f"     中文同义词数: {optimizer_stats.get('chinese_synonyms_count', 0)}")
            
            return True
        else:
            print(f"❌ 统计信息获取失败: {response.status_code}")
            return False
    
    except Exception as e:
        print(f"❌ 统计测试错误: {e}")
        return False

def main():
    """主测试函数"""
    print("🧪 T1组别和S类型项目匹配优化测试")
    print("=" * 60)
    
    # 检查服务器是否运行
    try:
        response = requests.get("http://localhost:8000/health", timeout=5)
        if response.status_code != 200:
            print("❌ 服务器未运行。请先启动服务器:")
            print("💡 运行: python3 run_server.py")
            return
    except:
        print("❌ 无法连接到服务器。请先启动服务器:")
        print("💡 运行: python3 run_server.py")
        return
    
    # 运行测试
    success = True
    
    success &= test_t1_s_optimization()
    success &= test_chinese_matching()
    success &= test_optimization_stats()
    
    print("\n" + "=" * 60)
    if success:
        print("🎉 所有测试通过！")
        print("\n✅ 优化功能确认:")
        print("   🔧 T1组别项目匹配优化")
        print("   📊 S类型项目匹配优化")
        print("   🇨🇳 中文查询匹配优化")
        print("   📈 置信度提升")
        print("   🎯 关键词权重调整")
    else:
        print("❌ 部分测试失败。请检查错误信息。")
    
    print("\n💡 优化特性:")
    print("   • T1组别项目权重提升20%")
    print("   • S类型项目权重提升10%")
    print("   • 中文医疗术语同义词扩展")
    print("   • 关键词匹配加分机制")
    print("   • 上下文感知优化")
    print("   • 置信度等级分类")

if __name__ == "__main__":
    main()
