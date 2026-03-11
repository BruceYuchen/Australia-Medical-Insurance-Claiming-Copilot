"""
高级向量数据库集成模块
支持FAISS、Chroma、Pinecone等多种向量数据库
"""
import numpy as np
import pandas as pd
from typing import List, Dict, Any, Optional, Tuple
from abc import ABC, abstractmethod
import json
import os

# 尝试导入可选的向量数据库库
try:
    import faiss
    FAISS_AVAILABLE = True
except ImportError:
    FAISS_AVAILABLE = False

try:
    import chromadb
    from chromadb.config import Settings
    CHROMA_AVAILABLE = True
except ImportError:
    CHROMA_AVAILABLE = False

try:
    import pinecone
    PINECONE_AVAILABLE = True
except ImportError:
    PINECONE_AVAILABLE = False

try:
    from sentence_transformers import SentenceTransformer
    SENTENCE_TRANSFORMERS_AVAILABLE = True
except ImportError:
    SENTENCE_TRANSFORMERS_AVAILABLE = False

from core.schemas import ItemSuggestion

class VectorDatabase(ABC):
    """向量数据库抽象基类"""
    
    @abstractmethod
    def add_vectors(self, vectors: np.ndarray, metadata: List[Dict[str, Any]]) -> None:
        """添加向量到数据库"""
        pass
    
    @abstractmethod
    def search(self, query_vector: np.ndarray, top_k: int = 10) -> Tuple[np.ndarray, List[Dict[str, Any]]]:
        """搜索相似向量"""
        pass
    
    @abstractmethod
    def get_stats(self) -> Dict[str, Any]:
        """获取数据库统计信息"""
        pass

class FAISSVectorDB(VectorDatabase):
    """FAISS向量数据库实现"""
    
    def __init__(self, dimension: int = 5000, index_type: str = "flat"):
        if not FAISS_AVAILABLE:
            raise ImportError("FAISS not available. Install with: pip install faiss-cpu")
        
        self.dimension = dimension
        self.metadata = []
        
        # 创建索引
        if index_type == "flat":
            self.index = faiss.IndexFlatIP(dimension)  # 内积索引
        elif index_type == "ivf":
            quantizer = faiss.IndexFlatIP(dimension)
            self.index = faiss.IndexIVFFlat(quantizer, dimension, 100)
        else:
            raise ValueError(f"Unsupported index type: {index_type}")
    
    def add_vectors(self, vectors: np.ndarray, metadata: List[Dict[str, Any]]) -> None:
        """添加向量到FAISS索引"""
        # 归一化向量（内积索引需要归一化）
        faiss.normalize_L2(vectors)
        self.index.add(vectors)
        self.metadata.extend(metadata)
        
        # 如果是IVF索引，需要训练
        if hasattr(self.index, 'is_trained') and not self.index.is_trained:
            self.index.train(vectors)
    
    def search(self, query_vector: np.ndarray, top_k: int = 10) -> Tuple[np.ndarray, List[Dict[str, Any]]]:
        """搜索相似向量"""
        # 归一化查询向量
        faiss.normalize_L2(query_vector)
        
        # 搜索
        scores, indices = self.index.search(query_vector, top_k)
        
        # 获取元数据
        results_metadata = [self.metadata[idx] for idx in indices[0]]
        
        return scores[0], results_metadata
    
    def get_stats(self) -> Dict[str, Any]:
        """获取FAISS索引统计信息"""
        return {
            "total_vectors": self.index.ntotal,
            "dimension": self.dimension,
            "index_type": type(self.index).__name__,
            "is_trained": getattr(self.index, 'is_trained', True)
        }

class ChromaVectorDB(VectorDatabase):
    """Chroma向量数据库实现"""
    
    def __init__(self, collection_name: str = "mbs_items", persist_directory: str = "./chroma_db"):
        if not CHROMA_AVAILABLE:
            raise ImportError("Chroma not available. Install with: pip install chromadb")
        
        self.client = chromadb.Client(Settings(
            persist_directory=persist_directory
        ))
        
        try:
            self.collection = self.client.get_collection(collection_name)
        except:
            self.collection = self.client.create_collection(
                name=collection_name,
                metadata={"hnsw:space": "cosine"}
            )
    
    def add_vectors(self, vectors: np.ndarray, metadata: List[Dict[str, Any]]) -> None:
        """添加向量到Chroma集合"""
        # 准备数据
        embeddings = vectors.tolist()
        documents = [meta.get('description', '') for meta in metadata]
        metadatas = [{k: v for k, v in meta.items() if k != 'description'} for meta in metadata]
        ids = [str(meta.get('item_num', i)) for i, meta in enumerate(metadata)]
        
        # 添加到集合
        self.collection.add(
            embeddings=embeddings,
            documents=documents,
            metadatas=metadatas,
            ids=ids
        )
    
    def search(self, query_vector: np.ndarray, top_k: int = 10) -> Tuple[np.ndarray, List[Dict[str, Any]]]:
        """搜索相似向量"""
        # 搜索
        results = self.collection.query(
            query_embeddings=query_vector.tolist(),
            n_results=top_k
        )
        
        # 提取分数和元数据
        scores = np.array(results['distances'][0])
        metadata = results['metadatas'][0]
        
        return scores, metadata
    
    def get_stats(self) -> Dict[str, Any]:
        """获取Chroma集合统计信息"""
        count = self.collection.count()
        return {
            "total_vectors": count,
            "collection_name": self.collection.name
        }

class SentenceTransformerModel:
    """Sentence Transformers模型"""
    
    def __init__(self, model_name: str = "all-MiniLM-L6-v2"):
        if not SENTENCE_TRANSFORMERS_AVAILABLE:
            raise ImportError("Sentence Transformers not available. Install with: pip install sentence-transformers")
        
        self.model = SentenceTransformer(model_name)
        self.dimension = self.model.get_sentence_embedding_dimension()
    
    def encode_texts(self, texts: List[str]) -> np.ndarray:
        """编码文本为向量"""
        return self.model.encode(texts, convert_to_numpy=True)
    
    def encode_query(self, query: str) -> np.ndarray:
        """编码查询文本"""
        return self.model.encode([query], convert_to_numpy=True)

class HybridVectorSearch:
    """混合向量搜索系统"""
    
    def __init__(self, 
                 vector_db: VectorDatabase,
                 sentence_model: Optional[SentenceTransformerModel] = None,
                 tfidf_weights: float = 0.3,
                 semantic_weights: float = 0.7):
        self.vector_db = vector_db
        self.sentence_model = sentence_model
        self.tfidf_weights = tfidf_weights
        self.semantic_weights = semantic_weights
        
        # 如果提供了语义模型，调整权重
        if self.sentence_model:
            total_weight = self.tfidf_weights + self.semantic_weights
            self.tfidf_weights /= total_weight
            self.semantic_weights /= total_weight
    
    def search(self, query: str, top_k: int = 10) -> List[ItemSuggestion]:
        """混合搜索"""
        results = []
        
        if self.sentence_model:
            # 语义搜索
            query_vector = self.sentence_model.encode_query(query)
            scores, metadata = self.vector_db.search(query_vector, top_k)
            
            # 创建建议结果
            for i, (score, meta) in enumerate(zip(scores, metadata)):
                suggestion = ItemSuggestion(
                    item_num=str(meta.get('item_num', '')),
                    description=meta.get('description', ''),
                    score=float(score),
                    group=meta.get('group', ''),
                    category=int(meta.get('category', 0)),
                    provider_type=meta.get('provider_type'),
                    matched_fields=['description'],
                    evidence=f"语义相似度: {score:.4f}"
                )
                results.append(suggestion)
        
        return results

class VectorDBManager:
    """向量数据库管理器"""
    
    def __init__(self, db_type: str = "faiss", **kwargs):
        self.db_type = db_type
        self.vector_db = self._create_vector_db(db_type, **kwargs)
        self.sentence_model = None
        
        # 如果指定了语义模型
        if kwargs.get('use_semantic', False):
            model_name = kwargs.get('semantic_model', 'all-MiniLM-L6-v2')
            self.sentence_model = SentenceTransformerModel(model_name)
    
    def _create_vector_db(self, db_type: str, **kwargs) -> VectorDatabase:
        """创建向量数据库实例"""
        if db_type == "faiss":
            dimension = kwargs.get('dimension', 5000)
            index_type = kwargs.get('index_type', 'flat')
            return FAISSVectorDB(dimension=dimension, index_type=index_type)
        
        elif db_type == "chroma":
            collection_name = kwargs.get('collection_name', 'mbs_items')
            persist_directory = kwargs.get('persist_directory', './chroma_db')
            return ChromaVectorDB(collection_name=collection_name, persist_directory=persist_directory)
        
        else:
            raise ValueError(f"Unsupported vector database type: {db_type}")
    
    def build_index_from_dataframe(self, df: pd.DataFrame, text_column: str = 'description') -> None:
        """从DataFrame构建向量索引"""
        texts = df[text_column].fillna('').astype(str).tolist()
        
        if self.sentence_model:
            # 使用语义模型编码
            vectors = self.sentence_model.encode_texts(texts)
        else:
            # 使用TF-IDF编码（需要先训练）
            from sklearn.feature_extraction.text import TfidfVectorizer
            vectorizer = TfidfVectorizer(
                min_df=2,
                ngram_range=(1, 2),
                stop_words='english',
                max_features=5000
            )
            vectors = vectorizer.fit_transform(texts).toarray()
        
        # 准备元数据
        metadata = []
        for _, row in df.iterrows():
            meta = {
                'item_num': str(row.get('item_num', '')),
                'description': str(row.get('description', '')),
                'group': str(row.get('group', '')),
                'category': int(row.get('category', 0)),
                'provider_type': row.get('provider_type')
            }
            metadata.append(meta)
        
        # 添加到向量数据库
        self.vector_db.add_vectors(vectors, metadata)
    
    def search(self, query: str, top_k: int = 10) -> List[ItemSuggestion]:
        """搜索相似项目"""
        if self.sentence_model:
            # 语义搜索
            query_vector = self.sentence_model.encode_query(query)
            scores, metadata = self.vector_db.search(query_vector, top_k)
            
            results = []
            for score, meta in zip(scores, metadata):
                suggestion = ItemSuggestion(
                    item_num=str(meta.get('item_num', '')),
                    description=meta.get('description', ''),
                    score=float(score),
                    group=meta.get('group', ''),
                    category=int(meta.get('category', 0)),
                    provider_type=meta.get('provider_type'),
                    matched_fields=['description'],
                    evidence=f"语义相似度: {score:.4f}"
                )
                results.append(suggestion)
            
            return results
        else:
            # 如果没有语义模型，返回空结果
            return []
    
    def get_stats(self) -> Dict[str, Any]:
        """获取统计信息"""
        stats = self.vector_db.get_stats()
        stats['db_type'] = self.db_type
        stats['has_semantic_model'] = self.sentence_model is not None
        
        if self.sentence_model:
            stats['semantic_model_dimension'] = self.sentence_model.dimension
        
        return stats

# 工厂函数
def create_vector_db_manager(db_type: str = "faiss", **kwargs) -> VectorDBManager:
    """创建向量数据库管理器"""
    return VectorDBManager(db_type=db_type, **kwargs)

# 使用示例
if __name__ == "__main__":
    # 创建FAISS向量数据库
    manager = create_vector_db_manager(
        db_type="faiss",
        dimension=384,  # MiniLM维度
        use_semantic=True,
        semantic_model="all-MiniLM-L6-v2"
    )
    
    # 模拟数据
    import pandas as pd
    df = pd.DataFrame({
        'item_num': ['1', '2', '3'],
        'description': [
            'Professional attendance at consulting rooms',
            'Mental health assessment and treatment',
            'Chest X-ray examination'
        ],
        'group': ['A1', 'A40', 'D1'],
        'category': [1, 1, 2]
    })
    
    # 构建索引
    manager.build_index_from_dataframe(df)
    
    # 搜索
    results = manager.search("consultation mental health", top_k=3)
    for result in results:
        print(f"Item {result.item_num}: {result.score:.4f} - {result.description}")
    
    # 统计信息
    stats = manager.get_stats()
    print(f"Database stats: {stats}")
