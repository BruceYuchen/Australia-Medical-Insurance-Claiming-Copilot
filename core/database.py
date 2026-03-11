"""
数据库集成模块：提供SQLite数据库查询功能
"""
import sqlite3
import pandas as pd
from typing import List, Dict, Any, Optional, Tuple
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.metrics.pairwise import linear_kernel
import numpy as np
from .schemas import MBSItem, ItemSuggestion

class DatabaseManager:
    """数据库管理器"""
    
    def __init__(self, db_path: str):
        self.db_path = db_path
        self.vectorizer = None
        self.item_vectors = None
        self.items_df = None
        self._initialize_search_index()
    
    def _initialize_search_index(self):
        """初始化搜索索引"""
        try:
            # 加载所有项目数据
            self.items_df = self.get_all_items()
            
            if not self.items_df.empty:
                # 创建TF-IDF向量化器
                self.vectorizer = TfidfVectorizer(
                    min_df=2,
                    ngram_range=(1, 2),
                    stop_words='english',
                    max_features=5000
                )
                
                # 准备文本数据
                descriptions = self.items_df['description'].fillna('').astype(str).tolist()
                
                # 训练向量化器
                self.item_vectors = self.vectorizer.fit_transform(descriptions)
                
                print(f"搜索索引初始化完成，共 {len(descriptions)} 个项目")
            else:
                print("警告：没有找到项目数据")
                
        except Exception as e:
            print(f"搜索索引初始化失败: {e}")
    
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
            print(f"获取项目数据失败: {e}")
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
            print(f"获取项目 {item_num} 失败: {e}")
        
        return None
    
    def search_items_by_text(self, query_text: str, top_k: int = 10) -> List[ItemSuggestion]:
        """基于文本搜索项目"""
        if self.vectorizer is None or self.item_vectors is None or self.items_df is None:
            return []
        
        try:
            # 向量化查询文本
            query_vector = self.vectorizer.transform([query_text])
            
            # 计算相似度
            similarities = linear_kernel(query_vector, self.item_vectors).ravel()
            
            # 获取最相似的top_k个项目
            top_indices = similarities.argsort()[::-1][:top_k]
            
            suggestions = []
            for i, idx in enumerate(top_indices):
                if similarities[idx] > 0:  # 只返回有相似度的结果
                    row = self.items_df.iloc[idx]
                    
                    # 提取匹配的字段
                    matched_fields = self._extract_matched_fields(query_text, row)
                    
                    suggestion = ItemSuggestion(
                        item_num=str(row['item_num']),
                        description=row['description'] or "",
                        score=float(similarities[idx]),
                        group=row['group'] or "",
                        category=int(row['category']) if pd.notna(row['category']) else 0,
                        provider_type=row['provider_type'],
                        matched_fields=matched_fields,
                        evidence=f"文本相似度: {similarities[idx]:.4f}"
                    )
                    suggestions.append(suggestion)
            
            return suggestions
            
        except Exception as e:
            print(f"文本搜索失败: {e}")
            return []
    
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
            print(f"条件搜索失败: {e}")
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
            print(f"批量获取项目失败: {e}")
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
                
                return {
                    "total_items": total_items,
                    "group_distribution": group_stats,
                    "category_distribution": category_stats,
                    "provider_distribution": provider_stats
                }
                
        except Exception as e:
            print(f"获取统计信息失败: {e}")
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
    
    def rebuild_search_index(self):
        """重建搜索索引"""
        print("重建搜索索引...")
        self._initialize_search_index()
        print("搜索索引重建完成")

# 全局数据库管理器实例
db_manager = None

def get_db_manager(db_path: str = "/Users/yz/Code/mbs-matcher/data/mbs.db") -> DatabaseManager:
    """获取数据库管理器实例"""
    global db_manager
    if db_manager is None:
        db_manager = DatabaseManager(db_path)
    return db_manager
