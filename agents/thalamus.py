import sys
sys.path.append(r'/Users/hongjunwu/Desktop/Pj/neocortex/core/brain_modules')
import numpy as np
from typing import Dict, List, Any
from core.brain_modules.hippocampus import Hippocampus


class Thalamus:
    def __init__(self):
        self.hippocampus = Hippocampus()
        
    def integrated_retrieval(self, task, query):
        self._store_info(task, query)
        info = self.hippocampus.retrieve(task, query)
        return info
    
    def _store_info(self, task, query):
        pass