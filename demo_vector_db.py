#!/usr/bin/env python3
"""
向量数据库演示脚本
展示不同向量数据库和模型的性能对比
"""
import sys
import os
import time
import pandas as pd
import numpy as np
from typing import List, Dict, Any

# 添加app目录到Python路径
sys.path.append(os.path.join(os.path.dirname(__file__), 'app'))

def check_dependencies():
    """检查依赖库"""
    dependencies = {
        'faiss-cpu': 'FAISS',
        'chromadb': 'Chroma',
        'sentence-transformers': 'Sentence Transformers',
        'pinecone-client': 'Pinecone'
    }
    
    available = {}
    for package, name in dependencies.items():
        try:
            if package == 'faiss-cpu':
                import faiss
                available[name] = True
            elif package == 'chromadb':
                import chromadb
                available[name] = True
            elif package == 'sentence-transformers':
                from sentence_transformers import SentenceTransformer
                available[name] = True
            elif package == 'pinecone-client':
                import pinecone
                available[name] = True
        except ImportError:
            available[name] = False
    
    return available

def demo_tfidf_search():
    """演示TF-IDF搜索"""
    print("🔍 TF-IDF搜索演示")
    print("-" * 30)
    
    try:
        from app.database import get_db_manager
        
        # 获取数据库管理器
        db = get_db_manager()
        
        # 测试搜索
        queries = [
            "consultation general practitioner",
            "mental health assessment",
            "chest pain examination",
            "surgery operation"
        ]
        
        for query in queries:
            print(f"\n查询: '{query}'")
            start_time = time.time()
            
            results = db.search_items_by_text(query, top_k=3)
            
            search_time = (time.time() - start_time) * 1000
            
            print(f"  搜索时间: {search_time:.2f}ms")
            print(f"  找到结果: {len(results)} 个")
            
            for i, result in enumerate(results[:3], 1):
                confidence = int(result.score * 100)
                print(f"    {i}. Item {result.item_num} (置信度: {confidence}%)")
                print(f"       {result.description[:60]}...")
        
        # 获取统计信息
        stats = db.get_statistics()
        print(f"\n📊 数据库统计:")
        print(f"  总项目数: {stats.get('total_items', 0)}")
        print(f"  组别数量: {len(stats.get('group_distribution', {}))}")
        
    except Exception as e:
        print(f"❌ TF-IDF搜索失败: {e}")

def demo_faiss_search():
    """演示FAISS搜索"""
    print("\n🚀 FAISS向量数据库演示")
    print("-" * 30)
    
    try:
        from app.vector_db import create_vector_db_manager
        
        # 创建FAISS向量数据库
        manager = create_vector_db_manager(
            db_type="faiss",
            dimension=384,  # MiniLM维度
            use_semantic=True,
            semantic_model="all-MiniLM-L6-v2"
        )
        
        # 加载数据
        from app.database import get_db_manager
        db = get_db_manager()
        items_df = db.get_all_items()
        
        print(f"📥 加载 {len(items_df)} 个项目数据...")
        
        # 构建索引
        start_time = time.time()
        manager.build_index_from_dataframe(items_df.head(100))  # 只使用前100个项目进行演示
        build_time = time.time() - start_time
        
        print(f"✅ 索引构建完成，耗时: {build_time:.2f}秒")
        
        # 测试搜索
        queries = [
            "consultation general practitioner",
            "mental health assessment",
            "chest pain examination"
        ]
        
        for query in queries:
            print(f"\n查询: '{query}'")
            start_time = time.time()
            
            results = manager.search(query, top_k=3)
            
            search_time = (time.time() - start_time) * 1000
            
            print(f"  搜索时间: {search_time:.2f}ms")
            print(f"  找到结果: {len(results)} 个")
            
            for i, result in enumerate(results[:3], 1):
                confidence = int(result.score * 100)
                print(f"    {i}. Item {result.item_num} (置信度: {confidence}%)")
                print(f"       {result.description[:60]}...")
        
        # 获取统计信息
        stats = manager.get_stats()
        print(f"\n📊 FAISS统计:")
        for key, value in stats.items():
            print(f"  {key}: {value}")
        
    except ImportError as e:
        print(f"❌ FAISS不可用: {e}")
        print("💡 安装命令: pip install faiss-cpu")
    except Exception as e:
        print(f"❌ FAISS搜索失败: {e}")

def demo_chroma_search():
    """演示Chroma搜索"""
    print("\n🎨 Chroma向量数据库演示")
    print("-" * 30)
    
    try:
        from app.vector_db import create_vector_db_manager
        
        # 创建Chroma向量数据库
        manager = create_vector_db_manager(
            db_type="chroma",
            collection_name="mbs_demo",
            persist_directory="./chroma_demo",
            use_semantic=True,
            semantic_model="all-MiniLM-L6-v2"
        )
        
        # 加载数据
        from app.database import get_db_manager
        db = get_db_manager()
        items_df = db.get_all_items()
        
        print(f"📥 加载 {len(items_df)} 个项目数据...")
        
        # 构建索引
        start_time = time.time()
        manager.build_index_from_dataframe(items_df.head(50))  # 只使用前50个项目进行演示
        build_time = time.time() - start_time
        
        print(f"✅ 索引构建完成，耗时: {build_time:.2f}秒")
        
        # 测试搜索
        queries = [
            "consultation general practitioner",
            "mental health assessment",
            "chest pain examination"
        ]
        
        for query in queries:
            print(f"\n查询: '{query}'")
            start_time = time.time()
            
            results = manager.search(query, top_k=3)
            
            search_time = (time.time() - start_time) * 1000
            
            print(f"  搜索时间: {search_time:.2f}ms")
            print(f"  找到结果: {len(results)} 个")
            
            for i, result in enumerate(results[:3], 1):
                confidence = int(result.score * 100)
                print(f"    {i}. Item {result.item_num} (置信度: {confidence}%)")
                print(f"       {result.description[:60]}...")
        
        # 获取统计信息
        stats = manager.get_stats()
        print(f"\n📊 Chroma统计:")
        for key, value in stats.items():
            print(f"  {key}: {value}")
        
    except ImportError as e:
        print(f"❌ Chroma不可用: {e}")
        print("💡 安装命令: pip install chromadb")
    except Exception as e:
        print(f"❌ Chroma搜索失败: {e}")

def demo_sentence_transformers():
    """演示Sentence Transformers模型"""
    print("\n🧠 Sentence Transformers模型演示")
    print("-" * 30)
    
    try:
        from app.vector_db import SentenceTransformerModel
        
        # 创建模型
        model = SentenceTransformerModel("all-MiniLM-L6-v2")
        print(f"✅ 模型加载完成，维度: {model.dimension}")
        
        # 测试文本
        texts = [
            "Professional attendance at consulting rooms by general practitioner",
            "Mental health assessment and treatment plan",
            "Chest X-ray examination and interpretation",
            "Surgical procedure for appendectomy"
        ]
        
        # 编码文本
        start_time = time.time()
        embeddings = model.encode_texts(texts)
        encode_time = (time.time() - start_time) * 1000
        
        print(f"📊 编码 {len(texts)} 个文本，耗时: {encode_time:.2f}ms")
        print(f"📊 向量形状: {embeddings.shape}")
        
        # 测试查询
        query = "consultation mental health"
        query_embedding = model.encode_query(query)
        
        # 计算相似度
        similarities = np.dot(embeddings, query_embedding.T).flatten()
        
        print(f"\n查询: '{query}'")
        print("相似度结果:")
        for i, (text, sim) in enumerate(zip(texts, similarities)):
            print(f"  {i+1}. {sim:.4f} - {text[:50]}...")
        
    except ImportError as e:
        print(f"❌ Sentence Transformers不可用: {e}")
        print("💡 安装命令: pip install sentence-transformers")
    except Exception as e:
        print(f"❌ Sentence Transformers演示失败: {e}")

def performance_comparison():
    """性能对比测试"""
    print("\n⚡ 性能对比测试")
    print("=" * 50)
    
    # 测试查询
    test_queries = [
        "consultation general practitioner",
        "mental health assessment",
        "chest pain examination",
        "surgery operation",
        "diagnostic imaging"
    ]
    
    results = {}
    
    # TF-IDF测试
    try:
        from app.database import get_db_manager
        db = get_db_manager()
        
        total_time = 0
        for query in test_queries:
            start_time = time.time()
            db.search_items_by_text(query, top_k=5)
            total_time += time.time() - start_time
        
        results['TF-IDF'] = {
            'avg_time': (total_time / len(test_queries)) * 1000,
            'total_queries': len(test_queries)
        }
        
    except Exception as e:
        print(f"❌ TF-IDF测试失败: {e}")
    
    # FAISS测试
    try:
        from app.vector_db import create_vector_db_manager
        
        manager = create_vector_db_manager(
            db_type="faiss",
            dimension=384,
            use_semantic=True,
            semantic_model="all-MiniLM-L6-v2"
        )
        
        # 构建索引
        from app.database import get_db_manager
        db = get_db_manager()
        items_df = db.get_all_items()
        manager.build_index_from_dataframe(items_df.head(100))
        
        total_time = 0
        for query in test_queries:
            start_time = time.time()
            manager.search(query, top_k=5)
            total_time += time.time() - start_time
        
        results['FAISS + MiniLM'] = {
            'avg_time': (total_time / len(test_queries)) * 1000,
            'total_queries': len(test_queries)
        }
        
    except Exception as e:
        print(f"❌ FAISS测试失败: {e}")
    
    # 显示结果
    print("\n📊 性能对比结果:")
    print("-" * 40)
    print(f"{'方法':<20} {'平均时间(ms)':<15} {'查询数':<10}")
    print("-" * 40)
    
    for method, data in results.items():
        print(f"{method:<20} {data['avg_time']:<15.2f} {data['total_queries']:<10}")
    
    print("-" * 40)

def main():
    """主函数"""
    print("🎯 MBS匹配系统 - 向量数据库演示")
    print("=" * 60)
    
    # 检查依赖
    print("\n🔍 检查依赖库...")
    dependencies = check_dependencies()
    
    for lib, available in dependencies.items():
        status = "✅ 可用" if available else "❌ 不可用"
        print(f"  {lib}: {status}")
    
    print(f"\n📚 可用库: {sum(dependencies.values())}/{len(dependencies)}")
    
    # 演示各种搜索方法
    demo_tfidf_search()
    
    if dependencies.get('FAISS', False):
        demo_faiss_search()
    else:
        print("\n⚠️ FAISS不可用，跳过FAISS演示")
    
    if dependencies.get('Chroma', False):
        demo_chroma_search()
    else:
        print("\n⚠️ Chroma不可用，跳过Chroma演示")
    
    if dependencies.get('Sentence Transformers', False):
        demo_sentence_transformers()
    else:
        print("\n⚠️ Sentence Transformers不可用，跳过模型演示")
    
    # 性能对比
    performance_comparison()
    
    print("\n" + "=" * 60)
    print("🎉 演示完成！")
    print("\n💡 安装建议:")
    print("  • 基础功能: 当前TF-IDF已足够")
    print("  • 高性能: pip install faiss-cpu")
    print("  • 语义搜索: pip install sentence-transformers")
    print("  • 持久化: pip install chromadb")
    print("  • 云端: pip install pinecone-client")

if __name__ == "__main__":
    main()
