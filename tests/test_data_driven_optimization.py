#!/usr/bin/env python3
"""
数据驱动优化测试脚本
测试基于示例数据参考的优化效果
"""
import sys
import os
import time
import requests
import json
from datetime import datetime

# 添加app目录到Python路径
sys.path.append(os.path.join(os.path.dirname(__file__), 'app'))

def test_data_driven_optimization():
    """测试数据驱动优化"""
    print("🧠 数据驱动优化测试")
    print("=" * 60)
    
    base_url = "http://localhost:8000"
    
    # 测试用例
    test_cases = [
        {
            "name": "全科医生咨询场景",
            "query": "consultation general practitioner",
            "context": {
                "setting": "consulting_rooms",
                "duration": 30,
                "provider": "general practitioner",
                "patient_type": "community",
                "date": datetime.now().isoformat(),
                "referral": False
            },
            "expected_items": ["3", "4"],
            "expected_confidence": 0.8
        },
        {
            "name": "心理健康评估场景",
            "query": "mental health assessment",
            "context": {
                "setting": "consulting_rooms",
                "duration": 60,
                "provider": "psychiatrist",
                "patient_type": "community",
                "date": datetime.now().isoformat(),
                "referral": False
            },
            "expected_items": ["276", "282"],
            "expected_confidence": 0.8
        },
        {
            "name": "胸部疼痛检查场景",
            "query": "chest pain examination",
            "context": {
                "setting": "hospital",
                "duration": 45,
                "provider": "specialist",
                "patient_type": "inpatient",
                "date": datetime.now().isoformat(),
                "referral": True
            },
            "expected_items": ["58503", "56307"],
            "expected_confidence": 0.7
        },
        {
            "name": "手术场景",
            "query": "surgery operation",
            "context": {
                "setting": "hospital",
                "duration": 120,
                "provider": "specialist",
                "patient_type": "inpatient",
                "date": datetime.now().isoformat(),
                "referral": True
            },
            "expected_items": ["30530", "42617"],
            "expected_confidence": 0.8
        }
    ]
    
    print("🔍 开始测试数据驱动优化...")
    
    for i, test_case in enumerate(test_cases, 1):
        print(f"\n{i}. {test_case['name']}")
        print("-" * 40)
        
        try:
            # 测试增强版搜索
            start_time = time.time()
            
            response = requests.post(f"{base_url}/suggest_items_enhanced", 
                json={
                    "transcript": test_case["query"],
                    "context": test_case["context"],
                    "top_k": 5
                },
                params={"search_type": "hybrid"},
                timeout=30
            )
            
            search_time = (time.time() - start_time) * 1000
            
            if response.status_code == 200:
                data = response.json()
                suggestions = data.get('suggestions', [])
                
                print(f"   查询: '{test_case['query']}'")
                print(f"   搜索时间: {search_time:.2f}ms")
                print(f"   找到结果: {len(suggestions)} 个")
                
                # 分析结果
                found_expected = []
                confidence_scores = []
                
                for j, suggestion in enumerate(suggestions[:3], 1):
                    item_num = suggestion['item_num']
                    confidence = int(suggestion['score'] * 100)
                    confidence_scores.append(suggestion['score'])
                    
                    # 检查是否匹配预期项目
                    if item_num in test_case['expected_items']:
                        found_expected.append(item_num)
                        print(f"   ✅ {j}. Item {item_num} (置信度: {confidence}%) - 预期匹配")
                    else:
                        print(f"   📋 {j}. Item {item_num} (置信度: {confidence}%)")
                    
                    print(f"       {suggestion['description'][:60]}...")
                    print(f"       证据: {suggestion['evidence']}")
                
                # 计算匹配率
                expected_count = len(test_case['expected_items'])
                found_count = len(found_expected)
                match_rate = (found_count / expected_count) * 100 if expected_count > 0 else 0
                
                # 计算平均置信度
                avg_confidence = sum(confidence_scores) / len(confidence_scores) if confidence_scores else 0
                
                print(f"   📊 预期项目匹配率: {match_rate:.1f}% ({found_count}/{expected_count})")
                print(f"   📊 平均置信度: {avg_confidence:.3f}")
                
                # 评估结果
                if match_rate >= 50 and avg_confidence >= test_case['expected_confidence']:
                    print("   ✅ 测试通过")
                else:
                    print("   ⚠️ 测试部分通过")
                
            else:
                print(f"   ❌ 搜索失败: {response.status_code}")
                
        except Exception as e:
            print(f"   ❌ 测试失败: {e}")
    
    # 测试性能对比
    print(f"\n📊 性能对比测试")
    print("-" * 40)
    
    test_query = "consultation general practitioner"
    test_context = {
        "setting": "consulting_rooms",
        "duration": 30,
        "provider": "general practitioner",
        "patient_type": "community",
        "date": datetime.now().isoformat(),
        "referral": False
    }
    
    search_types = ["tfidf", "semantic", "hybrid"]
    
    for search_type in search_types:
        try:
            start_time = time.time()
            
            response = requests.post(f"{base_url}/suggest_items_enhanced", 
                json={
                    "transcript": test_query,
                    "context": test_context,
                    "top_k": 5
                },
                params={"search_type": search_type},
                timeout=30
            )
            
            search_time = (time.time() - start_time) * 1000
            
            if response.status_code == 200:
                data = response.json()
                suggestions = data.get('suggestions', [])
                
                avg_confidence = sum(s['score'] for s in suggestions) / len(suggestions) if suggestions else 0
                
                print(f"   {search_type.upper()}: {search_time:.2f}ms, 置信度: {avg_confidence:.3f}, 结果: {len(suggestions)}")
            else:
                print(f"   {search_type.upper()}: 失败 ({response.status_code})")
                
        except Exception as e:
            print(f"   {search_type.upper()}: 错误 - {e}")
    
    # 获取优化器统计
    try:
        response = requests.get(f"{base_url}/performance")
        if response.status_code == 200:
            performance = response.json()
            if 'optimizer_stats' in performance:
                stats = performance['optimizer_stats']
                print(f"\n🔧 优化器统计:")
                print(f"   关键词权重: {stats.get('keyword_weights', 0)}")
                print(f"   上下文规则: {stats.get('context_rules', 0)}")
                print(f"   医疗同义词: {stats.get('medical_synonyms', 0)}")
                print(f"   置信度阈值: {stats.get('confidence_thresholds', {})}")
    except Exception as e:
        print(f"❌ 获取优化器统计失败: {e}")

def test_optimization_effectiveness():
    """测试优化效果"""
    print(f"\n🎯 优化效果测试")
    print("-" * 40)
    
    base_url = "http://localhost:8000"
    
    # 测试相同查询在不同上下文下的结果
    test_queries = [
        {
            "query": "consultation",
            "contexts": [
                {
                    "name": "咨询室",
                    "context": {
                        "setting": "consulting_rooms",
                        "provider": "general practitioner",
                        "duration": 30,
                        "patient_type": "community",
                        "date": datetime.now().isoformat(),
                        "referral": False
                    }
                },
                {
                    "name": "医院",
                    "context": {
                        "setting": "hospital",
                        "provider": "specialist",
                        "duration": 60,
                        "patient_type": "inpatient",
                        "date": datetime.now().isoformat(),
                        "referral": True
                    }
                }
            ]
        }
    ]
    
    for test_query in test_queries:
        print(f"\n查询: '{test_query['query']}'")
        
        for context_info in test_query['contexts']:
            try:
                response = requests.post(f"{base_url}/suggest_items_enhanced", 
                    json={
                        "transcript": test_query['query'],
                        "context": context_info['context'],
                        "top_k": 3
                    },
                    params={"search_type": "hybrid"},
                    timeout=30
                )
                
                if response.status_code == 200:
                    data = response.json()
                    suggestions = data.get('suggestions', [])
                    
                    print(f"   {context_info['name']}:")
                    for suggestion in suggestions[:2]:
                        confidence = int(suggestion['score'] * 100)
                        print(f"     Item {suggestion['item_num']} (置信度: {confidence}%)")
                        print(f"     {suggestion['evidence']}")
                else:
                    print(f"   {context_info['name']}: 失败")
                    
            except Exception as e:
                print(f"   {context_info['name']}: 错误 - {e}")

def main():
    """主函数"""
    print("🎯 数据驱动优化测试")
    print("=" * 60)
    
    # 检查服务器是否运行
    try:
        response = requests.get("http://localhost:8000/health", timeout=5)
        if response.status_code != 200:
            print("❌ 服务器未运行，请先启动服务器")
            print("💡 启动命令: python3 run_server.py")
            return
    except:
        print("❌ 无法连接到服务器，请先启动服务器")
        print("💡 启动命令: python3 run_server.py")
        return
    
    # 运行测试
    test_data_driven_optimization()
    test_optimization_effectiveness()
    
    print("\n" + "=" * 60)
    print("🎉 数据驱动优化测试完成！")
    print("\n💡 优化特性:")
    print("   • 🧠 智能关键词权重")
    print("   • 🎯 上下文感知搜索")
    print("   • 📊 置信度分级")
    print("   • 🔍 医疗术语同义词")
    print("   • ⚡ 性能优化")

if __name__ == "__main__":
    main()
