"""
增强版数据库管理器
支持多种向量数据库和混合搜索策略
"""
import sqlite3
import pandas as pd
import numpy as np
from typing import List, Dict, Any, Optional, Tuple, Union
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.metrics.pairwise import linear_kernel
import time
import json
import os

# 导入向量数据库模块
from utils.vector_db import (
    VectorDBManager, create_vector_db_manager,
    SentenceTransformerModel, HybridVectorSearch
)
from models.data_driven_optimizer import get_optimizer
from models.matching_optimizer import MatchingOptimizer

from core.schemas import MBSItem, ItemSuggestion

class EnhancedDatabaseManager:
    """增强版数据库管理器"""
    
    def __init__(self, 
                 db_path: str,
                 vector_db_type: str = "faiss",
                 use_semantic: bool = True,
                 semantic_model: str = "all-MiniLM-L6-v2",
                 hybrid_weights: Tuple[float, float] = (0.3, 0.7)):
        self.db_path = db_path
        self.vector_db_type = vector_db_type
        self.use_semantic = use_semantic
        self.semantic_model = semantic_model
        self.hybrid_weights = hybrid_weights
        
        # 传统TF-IDF组件
        self.tfidf_vectorizer = None
        self.tfidf_vectors = None
        self.items_df = None
        
        # 向量数据库组件
        self.vector_db_manager = None
        self.sentence_model = None
        self.hybrid_search = None
        
        # 搜索统计
        self.search_stats = {
            "total_searches": 0,
            "avg_search_time": 0.0,
            "cache_hits": 0,
            "cache_misses": 0
        }
        
        # 数据驱动优化器
        self.optimizer = get_optimizer()
        
        # 匹配优化器
        self.matching_optimizer = MatchingOptimizer()
        
        # 初始化
        self._initialize_components()
    
    def _initialize_components(self):
        """初始化所有组件"""
        print("🚀 初始化增强版数据库管理器...")
        
        # 1. 加载数据
        self._load_data()
        
        # 2. 初始化TF-IDF
        self._initialize_tfidf()
        
        # 3. 初始化向量数据库
        if self.use_semantic:
            self._initialize_vector_db()
        
        # 4. 初始化混合搜索
        if self.use_semantic and self.vector_db_manager:
            self._initialize_hybrid_search()
        
        print("✅ 增强版数据库管理器初始化完成")
    
    def _load_data(self):
        """加载项目数据"""
        try:
            self.items_df = self.get_all_items()
            print(f"📊 加载了 {len(self.items_df)} 个项目数据")
        except Exception as e:
            print(f"❌ 数据加载失败: {e}")
            self.items_df = pd.DataFrame()
    
    def _initialize_tfidf(self):
        """初始化TF-IDF向量化器"""
        try:
            if not self.items_df.empty:
                # 创建优化的TF-IDF向量化器
                self.tfidf_vectorizer = TfidfVectorizer(
                    min_df=1,                    # 降低最小频率
                    ngram_range=(1, 3),          # 增加3-gram
                    stop_words='english',        # 保持停用词过滤
                    max_features=10000,          # 增加特征数
                    sublinear_tf=True,           # 使用子线性TF
                    use_idf=True,                # 使用IDF
                    smooth_idf=True              # 平滑IDF
                )
                
                # 准备文本数据
                descriptions = self.items_df['description'].fillna('').astype(str).tolist()
                
                # 训练向量化器
                self.tfidf_vectors = self.tfidf_vectorizer.fit_transform(descriptions)
                
                print(f"✅ TF-IDF初始化完成，特征数: {self.tfidf_vectors.shape[1]}")
            else:
                print("⚠️ 没有数据用于TF-IDF初始化")
                
        except Exception as e:
            print(f"❌ TF-IDF初始化失败: {e}")
    
    def _initialize_vector_db(self):
        """初始化向量数据库"""
        try:
            # 创建向量数据库管理器
            self.vector_db_manager = create_vector_db_manager(
                db_type=self.vector_db_type,
                dimension=384,  # MiniLM维度
                use_semantic=True,
                semantic_model=self.semantic_model
            )
            
            # 构建向量索引
            if not self.items_df.empty:
                print("🔨 构建向量索引...")
                start_time = time.time()
                
                # 只使用前1000个项目进行演示，避免内存问题
                sample_df = self.items_df.head(1000)
                self.vector_db_manager.build_index_from_dataframe(sample_df)
                
                build_time = time.time() - start_time
                print(f"✅ 向量索引构建完成，耗时: {build_time:.2f}秒")
            
        except Exception as e:
            print(f"❌ 向量数据库初始化失败: {e}")
            self.vector_db_manager = None
    
    def _initialize_hybrid_search(self):
        """初始化混合搜索"""
        try:
            if self.vector_db_manager and self.tfidf_vectorizer:
                # 创建混合搜索实例
                self.hybrid_search = HybridVectorSearch(
                    vector_db=self.vector_db_manager.vector_db,
                    sentence_model=self.vector_db_manager.sentence_model,
                    tfidf_weights=self.hybrid_weights[0],
                    semantic_weights=self.hybrid_weights[1]
                )
                print("✅ 混合搜索初始化完成")
        except Exception as e:
            print(f"❌ 混合搜索初始化失败: {e}")
    
    def get_all_items(self) -> pd.DataFrame:
        """获取所有MBS项目"""
        try:
            with sqlite3.connect(self.db_path) as conn:
                query = """
                    SELECT item_num, description, [group], category, subgroup, subheading,
                           provider_type, item_type, benefit_type, fee_type, emsn_cap,
                           emsn_fixed_cap_amount, [exists]
                    FROM mbs_items
                    ORDER BY item_num
                """
                return pd.read_sql_query(query, conn)
        except Exception as e:
            print(f"❌ 获取项目数据失败: {e}")
            return pd.DataFrame()
    
    def get_item_by_number(self, item_num: str) -> Optional[MBSItem]:
        """根据项目编号获取项目详情"""
        try:
            with sqlite3.connect(self.db_path) as conn:
                cursor = conn.cursor()
                cursor.execute("""
                    SELECT item_num, description, [group], category, subgroup, subheading,
                           provider_type, item_type, benefit_type, fee_type, emsn_cap,
                           emsn_fixed_cap_amount, [exists]
                    FROM mbs_items WHERE item_num = ?
                """, (item_num,))
                
                row = cursor.fetchone()
                if row:
                    return MBSItem(
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
        except Exception as e:
            print(f"❌ 获取项目 {item_num} 失败: {e}")
        
        return None
    
    def search_items_by_text(self, 
                            query_text: str, 
                            top_k: int = 10,
                            search_type: str = "hybrid",
                            context: Optional[Dict[str, Any]] = None) -> List[ItemSuggestion]:
        """基于文本搜索项目"""
        start_time = time.time()
        
        try:
            if search_type == "tfidf":
                results = self._tfidf_search(query_text, top_k)
            elif search_type == "semantic" and self.vector_db_manager:
                results = self._semantic_search(query_text, top_k)
            elif search_type == "hybrid" and self.hybrid_search:
                results = self._hybrid_search(query_text, top_k)
            else:
                # 回退到TF-IDF搜索
                results = self._tfidf_search(query_text, top_k)
            
            # 应用数据驱动优化
            if context and self.optimizer:
                results = self._apply_data_driven_optimization(results, query_text, context)
            
            # 应用匹配优化（针对T1组别和S类型项目）
            if self.matching_optimizer:
                results = self._apply_matching_optimization(results, query_text, context)
            
            # 更新搜索统计
            search_time = time.time() - start_time
            self._update_search_stats(search_time)
            
            return results
            
        except Exception as e:
            print(f"❌ 文本搜索失败: {e}")
            return []
    
    def _tfidf_search(self, query_text: str, top_k: int) -> List[ItemSuggestion]:
        """TF-IDF搜索"""
        if self.tfidf_vectorizer is None or self.tfidf_vectors is None or self.items_df is None:
            return []
        
        # 向量化查询文本
        query_vector = self.tfidf_vectorizer.transform([query_text])
        
        # 计算相似度
        similarities = linear_kernel(query_vector, self.tfidf_vectors).ravel()
        
        # 获取最相似的top_k个项目
        top_indices = similarities.argsort()[::-1][:top_k]
        
        suggestions = []
        for i, idx in enumerate(top_indices):
            if similarities[idx] > 0:
                row = self.items_df.iloc[idx]
                
                suggestion = ItemSuggestion(
                    item_num=str(row['item_num']),
                    description=row['description'] or "",
                    score=float(similarities[idx]),
                    group=row['group'] or "",
                    category=int(row['category']) if pd.notna(row['category']) else 0,
                    provider_type=row['provider_type'],
                    matched_fields=self._extract_matched_fields(query_text, row),
                    evidence=f"TF-IDF相似度: {similarities[idx]:.4f}"
                )
                suggestions.append(suggestion)
        
        return suggestions
    
    def _semantic_search(self, query_text: str, top_k: int) -> List[ItemSuggestion]:
        """语义搜索"""
        if not self.vector_db_manager:
            return []
        
        return self.vector_db_manager.search(query_text, top_k)
    
    def _hybrid_search(self, query_text: str, top_k: int) -> List[ItemSuggestion]:
        """混合搜索"""
        if not self.hybrid_search:
            return self._tfidf_search(query_text, top_k)
        
        # 获取TF-IDF结果
        tfidf_results = self._tfidf_search(query_text, top_k * 2)
        
        # 获取语义搜索结果
        semantic_results = self._semantic_search(query_text, top_k * 2)
        
        # 合并和重新排序结果
        combined_results = self._combine_search_results(tfidf_results, semantic_results, top_k)
        
        return combined_results
    
    def _combine_search_results(self, 
                               tfidf_results: List[ItemSuggestion], 
                               semantic_results: List[ItemSuggestion], 
                               top_k: int) -> List[ItemSuggestion]:
        """合并搜索结果"""
        # 创建项目编号到结果的映射
        result_map = {}
        
        # 添加TF-IDF结果
        for result in tfidf_results:
            item_num = result.item_num
            if item_num not in result_map:
                result_map[item_num] = {
                    'result': result,
                    'tfidf_score': result.score,
                    'semantic_score': 0.0
                }
            else:
                result_map[item_num]['tfidf_score'] = result.score
        
        # 添加语义搜索结果
        for result in semantic_results:
            item_num = result.item_num
            if item_num not in result_map:
                result_map[item_num] = {
                    'result': result,
                    'tfidf_score': 0.0,
                    'semantic_score': result.score
                }
            else:
                result_map[item_num]['semantic_score'] = result.score
        
        # 计算混合分数
        combined_results = []
        for item_num, data in result_map.items():
            result = data['result']
            tfidf_score = data['tfidf_score']
            semantic_score = data['semantic_score']
            
            # 混合分数计算
            hybrid_score = (self.hybrid_weights[0] * tfidf_score + 
                          self.hybrid_weights[1] * semantic_score)
            
            # 更新结果
            result.score = hybrid_score
            result.evidence = f"混合分数: {hybrid_score:.4f} (TF-IDF: {tfidf_score:.4f}, 语义: {semantic_score:.4f})"
            
            combined_results.append(result)
        
        # 按混合分数排序
        combined_results.sort(key=lambda x: x.score, reverse=True)
        
        return combined_results[:top_k]
    
    def search_items_by_criteria(self, 
                                group: Optional[str] = None,
                                category: Optional[int] = None,
                                provider_type: Optional[str] = None,
                                item_type: Optional[str] = None,
                                limit: int = 100) -> List[MBSItem]:
        """根据条件搜索项目"""
        try:
            with sqlite3.connect(self.db_path) as conn:
                # 构建查询条件
                conditions = []
                params = []
                
                if group:
                    conditions.append('[group] = ?')
                    params.append(group)
                
                if category is not None:
                    conditions.append('category = ?')
                    params.append(category)
                
                if provider_type:
                    conditions.append('provider_type = ?')
                    params.append(provider_type)
                
                if item_type:
                    conditions.append('item_type = ?')
                    params.append(item_type)
                
                where_clause = ' AND '.join(conditions) if conditions else '1=1'
                
                query = f"""
                    SELECT item_num, description, [group], category, subgroup, subheading,
                           provider_type, item_type, benefit_type, fee_type, emsn_cap,
                           emsn_fixed_cap_amount, [exists]
                    FROM mbs_items
                    WHERE {where_clause}
                    ORDER BY item_num
                    LIMIT ?
                """
                params.append(limit)
                
                cursor = conn.cursor()
                cursor.execute(query, params)
                
                items = []
                for row in cursor.fetchall():
                    item = MBSItem(
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
                    items.append(item)
                
                return items
                
        except Exception as e:
            print(f"❌ 条件搜索失败: {e}")
            return []
    
    def get_items_by_numbers(self, item_nums: List[str]) -> List[MBSItem]:
        """根据项目编号列表获取项目"""
        if not item_nums:
            return []
        
        try:
            with sqlite3.connect(self.db_path) as conn:
                # 构建IN查询
                placeholders = ','.join(['?' for _ in item_nums])
                query = f"""
                    SELECT item_num, description, [group], category, subgroup, subheading,
                           provider_type, item_type, benefit_type, fee_type, emsn_cap,
                           emsn_fixed_cap_amount, [exists]
                    FROM mbs_items
                    WHERE item_num IN ({placeholders})
                """
                
                cursor = conn.cursor()
                cursor.execute(query, item_nums)
                
                items = []
                for row in cursor.fetchall():
                    item = MBSItem(
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
                    items.append(item)
                
                return items
                
        except Exception as e:
            print(f"❌ 批量获取项目失败: {e}")
            return []
    
    def get_statistics(self) -> Dict[str, Any]:
        """获取数据库统计信息"""
        try:
            with sqlite3.connect(self.db_path) as conn:
                cursor = conn.cursor()
                
                # 项目总数
                cursor.execute("SELECT COUNT(*) FROM mbs_items")
                total_items = cursor.fetchone()[0]
                
                # 按组统计
                cursor.execute("SELECT [group], COUNT(*) FROM mbs_items GROUP BY [group] ORDER BY COUNT(*) DESC")
                group_stats = dict(cursor.fetchall())
                
                # 按类别统计
                cursor.execute("SELECT category, COUNT(*) FROM mbs_items GROUP BY category ORDER BY category")
                category_stats = dict(cursor.fetchall())
                
                # 按提供者类型统计
                cursor.execute("SELECT provider_type, COUNT(*) FROM mbs_items WHERE provider_type IS NOT NULL GROUP BY provider_type ORDER BY COUNT(*) DESC")
                provider_stats = dict(cursor.fetchall())
                
                # 添加搜索统计
                stats = {
                    "total_items": total_items,
                    "group_distribution": group_stats,
                    "category_distribution": category_stats,
                    "provider_distribution": provider_stats,
                    "search_stats": self.search_stats,
                    "vector_db_type": self.vector_db_type,
                    "use_semantic": self.use_semantic,
                    "semantic_model": self.semantic_model if self.use_semantic else None
                }
                
                return stats
                
        except Exception as e:
            print(f"❌ 获取统计信息失败: {e}")
            return {}
    
    def _extract_matched_fields(self, query_text: str, row: pd.Series) -> List[str]:
        """提取匹配的字段"""
        matched_fields = []
        query_lower = query_text.lower()
        
        # 检查各个字段是否包含查询词
        fields_to_check = ['description', 'group', 'provider_type', 'item_type']
        
        for field in fields_to_check:
            if field in row and pd.notna(row[field]):
                field_value = str(row[field]).lower()
                if any(word in field_value for word in query_lower.split()):
                    matched_fields.append(field)
        
        return matched_fields
    
    def _update_search_stats(self, search_time: float):
        """更新搜索统计"""
        self.search_stats["total_searches"] += 1
        
        # 更新平均搜索时间
        total_searches = self.search_stats["total_searches"]
        current_avg = self.search_stats["avg_search_time"]
        self.search_stats["avg_search_time"] = (
            (current_avg * (total_searches - 1) + search_time) / total_searches
        )
    
    def rebuild_search_index(self):
        """重建搜索索引"""
        print("🔄 重建搜索索引...")
        self._initialize_components()
        print("✅ 搜索索引重建完成")
    
    def _apply_data_driven_optimization(self, 
                                      results: List[ItemSuggestion], 
                                      query: str, 
                                      context: Dict[str, Any]) -> List[ItemSuggestion]:
        """应用数据驱动优化"""
        try:
            # 转换为字典格式
            suggestions_dict = []
            for result in results:
                suggestion_dict = {
                    'item_num': result.item_num,
                    'description': result.description,
                    'score': result.score,
                    'group': result.group,
                    'category': result.category,
                    'provider_type': result.provider_type,
                    'item_type': getattr(result, 'item_type', 'S'),
                    'matched_fields': result.matched_fields,
                    'evidence': result.evidence
                }
                suggestions_dict.append(suggestion_dict)
            
            # 应用优化器
            enhanced_suggestions = self.optimizer.enhance_suggestions(
                suggestions_dict, query, context
            )
            
            # 转换回ItemSuggestion格式
            optimized_results = []
            for suggestion in enhanced_suggestions:
                # 生成增强的解释
                enhanced_evidence = self.optimizer.generate_explanation(suggestion, query)
                
                optimized_result = ItemSuggestion(
                    item_num=suggestion['item_num'],
                    description=suggestion['description'],
                    score=suggestion.get('enhanced_score', suggestion['score']),
                    group=suggestion['group'],
                    category=suggestion['category'],
                    provider_type=suggestion['provider_type'],
                    matched_fields=suggestion['matched_fields'],
                    evidence=enhanced_evidence
                )
                optimized_results.append(optimized_result)
            
            return optimized_results
            
        except Exception as e:
            print(f"❌ 数据驱动优化失败: {e}")
            return results
    
    def _apply_matching_optimization(self, 
                                   results: List[ItemSuggestion], 
                                   query_text: str, 
                                   context: Optional[Dict[str, Any]] = None) -> List[ItemSuggestion]:
        """应用匹配优化"""
        try:
            if not results or not self.matching_optimizer:
                return results
            
            # 转换为字典格式
            suggestions_dict = []
            for result in results:
                suggestion = {
                    'item_num': result.item_num,
                    'description': result.description,
                    'score': result.score,
                    'group': result.group,
                    'category': result.category,
                    'item_type': 'S',  # 假设为S类型，实际应该从数据库获取
                    'provider_type': result.provider_type,
                    'matched_fields': result.matched_fields,
                    'evidence': result.evidence
                }
                suggestions_dict.append(suggestion)
            
            # 应用匹配优化
            optimized_suggestions = self.matching_optimizer.optimize_matching(
                query_text, suggestions_dict, context
            )
            
            # 转换回ItemSuggestion格式
            optimized_results = []
            for suggestion in optimized_suggestions:
                optimized_result = ItemSuggestion(
                    item_num=suggestion['item_num'],
                    description=suggestion['description'],
                    score=suggestion.get('optimized_score', suggestion['score']),
                    group=suggestion['group'],
                    category=suggestion['category'],
                    provider_type=suggestion['provider_type'],
                    matched_fields=suggestion['matched_fields'],
                    evidence=f"{suggestion['evidence']} | Optimization: {suggestion.get('optimization_explanation', '')}"
                )
                optimized_results.append(optimized_result)
            
            return optimized_results
            
        except Exception as e:
            print(f"❌ 匹配优化失败: {e}")
            return results
    
    def get_search_performance(self) -> Dict[str, Any]:
        """获取搜索性能统计"""
        stats = {
            "search_stats": self.search_stats,
            "vector_db_stats": self.vector_db_manager.get_stats() if self.vector_db_manager else None,
            "tfidf_features": self.tfidf_vectors.shape[1] if self.tfidf_vectors is not None else 0,
            "total_items": len(self.items_df) if self.items_df is not None else 0
        }
        
        # 添加优化器统计
        if self.optimizer:
            stats["optimizer_stats"] = self.optimizer.get_optimization_stats()
        
        return stats

# 全局增强数据库管理器实例
enhanced_db_manager = None

def get_enhanced_db_manager(
    db_path: str = "/Users/yz/Code/mbs-matcher/data/mbs.db",
    vector_db_type: str = "faiss",
    use_semantic: bool = True,
    semantic_model: str = "all-MiniLM-L6-v2"
) -> EnhancedDatabaseManager:
    """获取增强版数据库管理器实例"""
    global enhanced_db_manager
    if enhanced_db_manager is None:
        enhanced_db_manager = EnhancedDatabaseManager(
            db_path=db_path,
            vector_db_type=vector_db_type,
            use_semantic=use_semantic,
            semantic_model=semantic_model
        )
    return enhanced_db_manager
