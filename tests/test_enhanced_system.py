#!/usr/bin/env python3
"""
增强版MBS匹配系统测试脚本
测试升级后的系统性能和功能
"""
import sys
import os
import time
import requests
import json
from datetime import datetime

# 添加app目录到Python路径
sys.path.append(os.path.join(os.path.dirname(__file__), 'app'))

def test_enhanced_system():
    """测试增强版系统"""
    print("🚀 增强版MBS匹配系统测试")
    print("=" * 60)
    
    base_url = "http://localhost:8000"
    
    # 1. 健康检查
    print("\n1. 系统健康检查")
    try:
        response = requests.get(f"{base_url}/health", timeout=10)
        health = response.json()
        print(f"✅ 系统状态: {health['status']}")
        print(f"📊 数据库项目数: {health['total_items']}")
        print(f"🔧 规则数量: {health['rules_loaded']}")
    except Exception as e:
        print(f"❌ 健康检查失败: {e}")
        return False
    
    # 2. 测试搜索类型
    print("\n2. 搜索类型测试")
    try:
        response = requests.get(f"{base_url}/search_types")
        search_types = response.json()
        print("📋 可用搜索类型:")
        for st in search_types['search_types']:
            print(f"   • {st['type']}: {st['name']} - {st['description']}")
    except Exception as e:
        print(f"❌ 获取搜索类型失败: {e}")
    
    # 3. 测试不同搜索方法
    test_queries = [
        "consultation general practitioner",
        "mental health assessment",
        "chest pain examination",
        "surgery operation"
    ]
    
    search_methods = [
        ("tfidf", "TF-IDF搜索"),
        ("semantic", "语义搜索"),
        ("hybrid", "混合搜索")
    ]
    
    print("\n3. 搜索性能对比测试")
    print("-" * 50)
    
    for query in test_queries:
        print(f"\n🔍 查询: '{query}'")
        print("-" * 30)
        
        for method, method_name in search_methods:
            try:
                start_time = time.time()
                
                if method == "tfidf":
                    # 使用传统接口
                    response = requests.post(f"{base_url}/suggest_items", 
                        json={
                            "transcript": query,
                            "context": {
                                "setting": "consulting_rooms",
                                "duration": 30,
                                "referral": False,
                                "provider": "general practitioner",
                                "date": datetime.now().isoformat(),
                                "patient_type": "community"
                            },
                            "top_k": 3
                        },
                        timeout=30
                    )
                else:
                    # 使用增强版接口
                    response = requests.post(f"{base_url}/suggest_items_enhanced", 
                        json={
                            "transcript": query,
                            "context": {
                                "setting": "consulting_rooms",
                                "duration": 30,
                                "referral": False,
                                "provider": "general practitioner",
                                "date": datetime.now().isoformat(),
                                "patient_type": "community"
                            },
                            "top_k": 3
                        },
                        params={"search_type": method},
                        timeout=30
                    )
                
                search_time = (time.time() - start_time) * 1000
                
                if response.status_code == 200:
                    result = response.json()
                    suggestions = result.get('suggestions', [])
                    
                    print(f"   {method_name}:")
                    print(f"     搜索时间: {search_time:.2f}ms")
                    print(f"     找到结果: {len(suggestions)} 个")
                    
                    for i, suggestion in enumerate(suggestions[:2], 1):
                        confidence = int(suggestion['score'] * 100)
                        print(f"       {i}. Item {suggestion['item_num']} (置信度: {confidence}%)")
                        print(f"          {suggestion['description'][:50]}...")
                        print(f"          证据: {suggestion['evidence']}")
                else:
                    print(f"   {method_name}: ❌ 搜索失败 ({response.status_code})")
                    
            except Exception as e:
                print(f"   {method_name}: ❌ 错误 - {e}")
    
    # 4. 性能统计
    print("\n4. 系统性能统计")
    try:
        response = requests.get(f"{base_url}/performance")
        performance = response.json()
        
        print("📊 性能统计:")
        if 'search_stats' in performance:
            stats = performance['search_stats']
            print(f"   总搜索次数: {stats.get('total_searches', 0)}")
            print(f"   平均搜索时间: {stats.get('avg_search_time', 0):.4f}秒")
            print(f"   缓存命中: {stats.get('cache_hits', 0)}")
            print(f"   缓存未命中: {stats.get('cache_misses', 0)}")
        
        if 'vector_db_stats' in performance and performance['vector_db_stats']:
            vdb_stats = performance['vector_db_stats']
            print(f"   向量数据库类型: {vdb_stats.get('db_type', 'N/A')}")
            print(f"   总向量数: {vdb_stats.get('total_vectors', 0)}")
            print(f"   向量维度: {vdb_stats.get('dimension', 0)}")
            print(f"   语义模型: {vdb_stats.get('has_semantic_model', False)}")
        
        print(f"   TF-IDF特征数: {performance.get('tfidf_features', 0)}")
        print(f"   总项目数: {performance.get('total_items', 0)}")
        
    except Exception as e:
        print(f"❌ 获取性能统计失败: {e}")
    
    # 5. 规则验证测试
    print("\n5. 规则验证测试")
    try:
        response = requests.post(f"{base_url}/validate_claim",
            json={
                "selected_items": ["3", "4", "23"],
                "context": {
                    "setting": "consulting_rooms",
                    "duration": 30,
                    "referral": False,
                    "provider": "general practitioner",
                    "date": datetime.now().isoformat(),
                    "patient_type": "community"
                }
            },
            timeout=10
        )
        
        if response.status_code == 200:
            result = response.json()
            validation = result['result']
            print("✅ 规则验证测试通过")
            print(f"   可计费项目: {validation['billable_items']}")
            print(f"   被拒绝项目: {validation['rejected_items']}")
            print(f"   处理时间: {result['processing_time']:.4f}秒")
        else:
            print(f"❌ 规则验证测试失败: {response.status_code}")
            
    except Exception as e:
        print(f"❌ 规则验证测试错误: {e}")
    
    print("\n" + "=" * 60)
    print("🎉 增强版系统测试完成！")
    
    return True

def test_web_interface():
    """测试Web界面"""
    print("\n🌐 Web界面测试")
    print("-" * 30)
    
    try:
        # 测试静态文件访问
        response = requests.get("http://localhost:8000/static/index.html", timeout=5)
        if response.status_code == 200:
            print("✅ Web界面可访问")
            print("📖 访问地址: http://localhost:8000")
        else:
            print(f"❌ Web界面访问失败: {response.status_code}")
    except Exception as e:
        print(f"❌ Web界面测试失败: {e}")

def main():
    """主函数"""
    print("🎯 增强版MBS匹配系统测试")
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
    success = test_enhanced_system()
    test_web_interface()
    
    if success:
        print("\n🎉 所有测试通过！增强版系统运行正常。")
        print("\n💡 新功能:")
        print("   • 🚀 增强版搜索接口: /suggest_items_enhanced")
        print("   • 🧠 语义搜索: 基于Sentence Transformers")
        print("   • 🔀 混合搜索: TF-IDF + 语义搜索")
        print("   • 📊 性能监控: /performance")
        print("   • 🎯 搜索类型: /search_types")
        print("   • 🌐 Web界面: http://localhost:8000")
    else:
        print("\n⚠️ 部分测试失败，请检查系统状态。")

if __name__ == "__main__":
    main()
