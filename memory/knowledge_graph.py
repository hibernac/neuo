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
        # 关系型查询
        return [p for p in nx.all_simple_paths(self.graph, query[0], query[2]) if any(e[2] == query[1] for e in p)]
    
    def semantic_search(self, text_query):
        # 向量语义检索
        emb = self.embedder.encode(text_query)
        return self._nearest_neighbors(emb)
    
    def hybrid_retrieval(self, query):
        # 混合检索策略
        struct_results = self.structured_query(query)
        semantic_results = self.semantic_search(query)
        return self._fusion(struct_results, semantic_results)