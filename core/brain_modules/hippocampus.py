import sys
sys.path.append(r'/Users/hongjunwu/Desktop/Pj/neocortex/memory')
import torch
import networkx as nx
import numpy as np
from typing import List, Tuple
from memory.knowledge_graph import NeuroSemanticMemory

class Hippocampus:
    def __init__(self):
        self.mem_base = NeuroSemanticMemory()
        self.mem_st = []
    
    def retrieve(self, task, query):
        integrated_query = self._integrate(task, query)
        info = self.mem_base.hybrid_retrieval(integrated_query)
        self.mem_st.append(info)
        return info
    
    def _integrate(self, task, query):
        pass