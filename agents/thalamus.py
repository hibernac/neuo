import numpy as np
from typing import Dict, List, Any

class Thalamus:
    def __init__(self):
        self.hippocampus_memory = {}
        self.current_state = None
        self.pending_inputs = []
    
    def store_to_hippocampus(self, input_data: Dict[str, Any]) -> None:
        """合并输入到海马体记忆"""
        self.hippocampus_memory = self._merge_information(
            input_data, 
            self.hippocampus_memory
        )
    
    def feed_to_prefrontal(self, leader_agent, input_data: Dict[str, Any]) -> bool:
        """传递给前额叶皮质"""
        if not leader_agent.idle:
            self.pending_inputs.append(input_data)
            return False
            
        prefrontal_signal = self._prepare_prefrontal_signal(input_data)
        self.store_to_hippocampus(input_data)

        task_desc = prefrontal_signal.get('merged_data', {}).get('task_description')
        if task_desc:
            leader_agent.assign_task(task_desc)
            return True
            
        return False
    
    def process_pending_inputs(self, leader_agent) -> None:
        """处理当领导者空闲时的待处理输入"""        
        if leader_agent.idle and self.pending_inputs:
            next_input = self.pending_inputs.pop(0)
            self.feed_to_prefrontal(leader_agent, next_input)
    
    def _merge_information(self, new_info: Dict[str, Any], stored_info: Dict[str, Any]) -> Dict[str, Any]:
        """合并新信息与存储的记忆"""
        merged = stored_info.copy()
        for key, value in new_info.items():
            if key in merged:
                if isinstance(value, (list, np.ndarray)):
                    merged[key] = np.concatenate([merged[key], value])
                elif isinstance(value, dict):
                    merged[key].update(value)
                else:
                    merged[key] = [merged[key], value]
            else:
                merged[key] = value
                
        return merged
    
    def _prepare_prefrontal_signal(self, merged_data: Dict[str, Any]) -> Dict[str, Any]:
        """准备发送到前额叶皮质的信号"""
        return {
            'merged_data': merged_data,
            'timestamp': np.datetime64('now'),
            'requires_analysis': True
        }
