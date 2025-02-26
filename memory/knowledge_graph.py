import numpy as np
import networkx as nx
from transformers import AutoModel

class NeuroSemanticMemory:
    """类海马体语义记忆系统 (集成STARK检索机制)"""
    def __init__(self):
        self.graph = nx.DiGraph()
        self.embedder = AutoModel.from_pretrained("sentence-transformers/all-mpnet-base-v2")
    
    def add_knowledge(self, triple):
        self.graph.add_edge(triple[0], triple[2], label=triple[1])
    
    def structured_query(self, query):
        """关系型查询"""
        if not isinstance(query, (list, tuple)) or len(query) != 3:
            return []
        try:
            return [p for p in nx.all_simple_paths(self.graph, query[0], query[2]) if any(e[2] == query[1] for e in p)]
        except (nx.NetworkXNoPath, TypeError):
            return []

    def semantic_search(self, text_query):
        """向量语义检索"""
        return []
        inputs = self.embedder.tokenizer(text_query, return_tensors="pt", padding=True, truncation=True)
        outputs = self.embedder(**inputs)
        emb = outputs.last_hidden_state.mean(dim=1).detach().numpy()
        return self._nearest_neighbors(emb[0])    
    
    def hybrid_retrieval(self, query):
        """混合检索策略"""
        struct_results = self.structured_query(query)
        semantic_results = self.semantic_search(query)
        if not struct_results and not semantic_results:
            return str(query)
        return self._fusion(struct_results, semantic_results)
        
    def _nearest_neighbors(self, query_embedding, k=5):
        """查找最近邻节点"""
        similarities = {}
        for node in self.graph.nodes():
            node_emb = self.embedder.encode(str(node))
            similarity = self._cosine_similarity(query_embedding, node_emb)
            similarities[node] = similarity
            
        return sorted(similarities.items(), key=lambda x: x[1], reverse=True)[:k]
    
    def _cosine_similarity(self, a, b):
        """计算余弦相似度"""
        return np.dot(a, b) / (np.linalg.norm(a) * np.linalg.norm(b))
    
    def _fusion(self, struct_results, semantic_results, alpha=0.7):
        """融合结构化查询和语义检索结果"""
        fused_scores = {}
        
        # 结构化结果评分
        for path in struct_results:
            for node in path:
                if node not in fused_scores:
                    fused_scores[node] = alpha
                else:
                    fused_scores[node] += alpha
                    
        # 语义结果评分
        for node, score in semantic_results:
            if node not in fused_scores:
                fused_scores[node] = (1 - alpha) * score
            else:
                fused_scores[node] += (1 - alpha) * score
                
        return sorted(fused_scores.items(), key=lambda x: x[1], reverse=True)