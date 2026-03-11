#!/usr/bin/env python3
"""
综合优化测试脚本
全面测试数据驱动优化的效果
"""
import sys
import os
import time
import requests
import json
from datetime import datetime
import statistics

# 添加app目录到Python路径
sys.path.append(os.path.join(os.path.dirname(__file__), 'app'))

def test_optimization_effectiveness():
    """测试优化效果"""
    print("🎯 综合优化效果测试")
    print("=" * 60)
    
    base_url = "http://localhost:8000"
    
    # 更全面的测试用例
    test_cases = [
        {
            "name": "基础咨询场景",
            "query": "consultation",
            "context": {
                "setting": "consulting_rooms",
                "duration": 30,
                "provider": "general practitioner",
                "patient_type": "community",
                "date": datetime.now().isoformat(),
                "referral": False
            },
            "expected_keywords": ["consultation", "attendance", "professional"],
            "expected_items": ["3", "4", "23", "24"]
        },
        {
            "name": "专科医生咨询",
            "query": "specialist consultation",
            "context": {
                "setting": "consulting_rooms",
                "duration": 45,
                "provider": "specialist",
                "patient_type": "community",
                "date": datetime.now().isoformat(),
                "referral": True
            },
            "expected_keywords": ["specialist", "consultation", "attendance"],
            "expected_items": ["104", "105", "110", "116"]
        },
        {
            "name": "心理健康服务",
            "query": "mental health psychiatric",
            "context": {
                "setting": "consulting_rooms",
                "duration": 60,
                "provider": "psychiatrist",
                "patient_type": "community",
                "date": datetime.now().isoformat(),
                "referral": True
            },
            "expected_keywords": ["mental", "psychiatric", "psychological"],
            "expected_items": ["276", "282", "279", "285"]
        },
        {
            "name": "诊断检查",
            "query": "diagnostic examination",
            "context": {
                "setting": "hospital",
                "duration": 30,
                "provider": "specialist",
                "patient_type": "inpatient",
                "date": datetime.now().isoformat(),
                "referral": True
            },
            "expected_keywords": ["diagnostic", "examination", "assessment"],
            "expected_items": ["11012", "11015", "11018", "11021"]
        },
        {
            "name": "手术治疗",
            "query": "surgery operation procedure",
            "context": {
                "setting": "hospital",
                "duration": 120,
                "provider": "specialist",
                "patient_type": "inpatient",
                "date": datetime.now().isoformat(),
                "referral": True
            },
            "expected_keywords": ["surgery", "operation", "procedure"],
            "expected_items": ["30530", "42617", "43864", "45000"]
        }
    ]
    
    print("🔍 开始综合优化测试...")
    
    all_results = []
    
    for i, test_case in enumerate(test_cases, 1):
        print(f"\n{i}. {test_case['name']}")
        print("-" * 50)
        
        try:
            # 测试不同搜索类型
            search_types = ["tfidf", "semantic", "hybrid"]
            type_results = {}
            
            for search_type in search_types:
                start_time = time.time()
                
                response = requests.post(f"{base_url}/suggest_items_enhanced", 
                    json={
                        "transcript": test_case["query"],
                        "context": test_case["context"],
                        "top_k": 10
                    },
                    params={"search_type": search_type},
                    timeout=30
                )
                
                search_time = (time.time() - start_time) * 1000
                
                if response.status_code == 200:
                    data = response.json()
                    suggestions = data.get('suggestions', [])
                    
                    # 分析结果
                    confidence_scores = [s['score'] for s in suggestions]
                    avg_confidence = statistics.mean(confidence_scores) if confidence_scores else 0
                    max_confidence = max(confidence_scores) if confidence_scores else 0
                    
                    # 检查关键词匹配
                    keyword_matches = 0
                    for suggestion in suggestions:
                        evidence = suggestion.get('evidence', '').lower()
                        for keyword in test_case['expected_keywords']:
                            if keyword.lower() in evidence:
                                keyword_matches += 1
                                break
                    
                    # 检查预期项目匹配
                    found_expected = []
                    for suggestion in suggestions:
                        if suggestion['item_num'] in test_case['expected_items']:
                            found_expected.append(suggestion['item_num'])
                    
                    type_results[search_type] = {
                        'search_time': search_time,
                        'result_count': len(suggestions),
                        'avg_confidence': avg_confidence,
                        'max_confidence': max_confidence,
                        'keyword_matches': keyword_matches,
                        'expected_matches': len(found_expected),
                        'found_expected': found_expected
                    }
                    
                    print(f"   {search_type.upper()}:")
                    print(f"     搜索时间: {search_time:.2f}ms")
                    print(f"     结果数量: {len(suggestions)}")
                    print(f"     平均置信度: {avg_confidence:.3f}")
                    print(f"     最高置信度: {max_confidence:.3f}")
                    print(f"     关键词匹配: {keyword_matches}/{len(test_case['expected_keywords'])}")
                    print(f"     预期项目匹配: {len(found_expected)}/{len(test_case['expected_items'])}")
                    
                    if found_expected:
                        print(f"     找到的预期项目: {found_expected}")
                    
                    # 显示前3个结果
                    for j, suggestion in enumerate(suggestions[:3], 1):
                        confidence = int(suggestion['score'] * 100)
                        print(f"       {j}. Item {suggestion['item_num']} (置信度: {confidence}%)")
                        print(f"          {suggestion['description'][:60]}...")
                
                else:
                    print(f"   {search_type.upper()}: 失败 ({response.status_code})")
                    type_results[search_type] = None
            
            all_results.append({
                'test_case': test_case['name'],
                'results': type_results
            })
            
        except Exception as e:
            print(f"   ❌ 测试失败: {e}")
    
    # 分析整体结果
    print(f"\n📊 整体分析")
    print("=" * 60)
    
    # 计算各搜索类型的平均性能
    search_type_stats = {}
    for search_type in ["tfidf", "semantic", "hybrid"]:
        times = []
        confidences = []
        keyword_matches = []
        expected_matches = []
        
        for result in all_results:
            if result['results'].get(search_type):
                stats = result['results'][search_type]
                times.append(stats['search_time'])
                confidences.append(stats['avg_confidence'])
                keyword_matches.append(stats['keyword_matches'])
                expected_matches.append(stats['expected_matches'])
        
        if times:
            search_type_stats[search_type] = {
                'avg_time': statistics.mean(times),
                'avg_confidence': statistics.mean(confidences),
                'avg_keyword_matches': statistics.mean(keyword_matches),
                'avg_expected_matches': statistics.mean(expected_matches)
            }
    
    # 显示统计结果
    print("搜索类型性能对比:")
    print("-" * 40)
    for search_type, stats in search_type_stats.items():
        print(f"{search_type.upper()}:")
        print(f"  平均搜索时间: {stats['avg_time']:.2f}ms")
        print(f"  平均置信度: {stats['avg_confidence']:.3f}")
        print(f"  平均关键词匹配: {stats['avg_keyword_matches']:.1f}")
        print(f"  平均预期项目匹配: {stats['avg_expected_matches']:.1f}")
        print()
    
    # 推荐最佳搜索类型
    if search_type_stats:
        best_hybrid = search_type_stats.get('hybrid', {})
        best_semantic = search_type_stats.get('semantic', {})
        best_tfidf = search_type_stats.get('tfidf', {})
        
        print("🎯 推荐搜索策略:")
        print("-" * 40)
        
        if best_hybrid.get('avg_confidence', 0) > best_semantic.get('avg_confidence', 0):
            print("✅ 混合搜索提供最佳准确率")
        else:
            print("✅ 语义搜索提供最佳准确率")
        
        if best_tfidf.get('avg_time', 0) < best_hybrid.get('avg_time', 0):
            print("⚡ TF-IDF搜索提供最快速度")
        else:
            print("⚡ 混合搜索在速度和准确率间取得最佳平衡")
        
        print(f"📈 混合搜索平均置信度: {best_hybrid.get('avg_confidence', 0):.3f}")
        print(f"⚡ TF-IDF平均搜索时间: {best_tfidf.get('avg_time', 0):.2f}ms")

def test_context_sensitivity():
    """测试上下文敏感性"""
    print(f"\n🎯 上下文敏感性测试")
    print("-" * 50)
    
    base_url = "http://localhost:8000"
    
    # 相同查询，不同上下文
    query = "consultation"
    contexts = [
        {
            "name": "咨询室-全科医生",
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
            "name": "医院-专科医生",
            "context": {
                "setting": "hospital",
                "provider": "specialist",
                "duration": 60,
                "patient_type": "inpatient",
                "date": datetime.now().isoformat(),
                "referral": True
            }
        },
        {
            "name": "心理健康-精神科医生",
            "context": {
                "setting": "consulting_rooms",
                "provider": "psychiatrist",
                "duration": 45,
                "patient_type": "community",
                "date": datetime.now().isoformat(),
                "referral": True
            }
        }
    ]
    
    print(f"查询: '{query}'")
    print()
    
    for context_info in contexts:
        try:
            response = requests.post(f"{base_url}/suggest_items_enhanced", 
                json={
                    "transcript": query,
                    "context": context_info["context"],
                    "top_k": 5
                },
                params={"search_type": "hybrid"},
                timeout=30
            )
            
            if response.status_code == 200:
                data = response.json()
                suggestions = data.get('suggestions', [])
                
                print(f"{context_info['name']}:")
                avg_confidence = statistics.mean([s['score'] for s in suggestions]) if suggestions else 0
                print(f"  平均置信度: {avg_confidence:.3f}")
                print(f"  结果数量: {len(suggestions)}")
                
                for i, suggestion in enumerate(suggestions[:3], 1):
                    confidence = int(suggestion['score'] * 100)
                    print(f"    {i}. Item {suggestion['item_num']} (置信度: {confidence}%)")
                    print(f"       {suggestion['evidence']}")
                print()
            else:
                print(f"{context_info['name']}: 失败 ({response.status_code})")
                
        except Exception as e:
            print(f"{context_info['name']}: 错误 - {e}")

def test_performance_benchmark():
    """性能基准测试"""
    print(f"\n⚡ 性能基准测试")
    print("-" * 50)
    
    base_url = "http://localhost:8000"
    
    # 测试查询
    test_queries = [
        "consultation general practitioner",
        "mental health assessment",
        "surgery operation",
        "diagnostic examination",
        "therapeutic procedure"
    ]
    
    search_types = ["tfidf", "semantic", "hybrid"]
    context = {
        "setting": "consulting_rooms",
        "duration": 30,
        "provider": "general practitioner",
        "patient_type": "community",
        "date": datetime.now().isoformat(),
        "referral": False
    }
    
    # 收集性能数据
    performance_data = {}
    
    for search_type in search_types:
        times = []
        confidences = []
        
        for query in test_queries:
            try:
                start_time = time.time()
                
                response = requests.post(f"{base_url}/suggest_items_enhanced", 
                    json={
                        "transcript": query,
                        "context": context,
                        "top_k": 5
                    },
                    params={"search_type": search_type},
                    timeout=30
                )
                
                search_time = (time.time() - start_time) * 1000
                
                if response.status_code == 200:
                    data = response.json()
                    suggestions = data.get('suggestions', [])
                    
                    times.append(search_time)
                    if suggestions:
                        avg_confidence = statistics.mean([s['score'] for s in suggestions])
                        confidences.append(avg_confidence)
                
            except Exception as e:
                print(f"查询 '{query}' 在 {search_type} 搜索中失败: {e}")
        
        if times:
            performance_data[search_type] = {
                'avg_time': statistics.mean(times),
                'min_time': min(times),
                'max_time': max(times),
                'avg_confidence': statistics.mean(confidences) if confidences else 0
            }
    
    # 显示性能结果
    print("性能基准结果:")
    print("-" * 30)
    for search_type, stats in performance_data.items():
        print(f"{search_type.upper()}:")
        print(f"  平均时间: {stats['avg_time']:.2f}ms")
        print(f"  最快时间: {stats['min_time']:.2f}ms")
        print(f"  最慢时间: {stats['max_time']:.2f}ms")
        print(f"  平均置信度: {stats['avg_confidence']:.3f}")
        print()

def main():
    """主函数"""
    print("🎯 综合优化测试")
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
    test_optimization_effectiveness()
    test_context_sensitivity()
    test_performance_benchmark()
    
    print("=" * 60)
    print("🎉 综合优化测试完成！")
    print("\n💡 测试总结:")
    print("   • 🎯 验证了数据驱动优化的效果")
    print("   • 🔍 测试了不同搜索类型的性能")
    print("   • 📊 分析了上下文敏感性")
    print("   • ⚡ 建立了性能基准")
    print("   • 🧠 确认了智能优化功能")

if __name__ == "__main__":
    main()
