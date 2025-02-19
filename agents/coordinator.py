from collections import deque
from config.neuro_config import COORDINATION_PARAMS
from typing import Dict, List
import uuid
from queue import PriorityQueue

class CorticalCoordinator:
    """皮层协调中枢 (实现CollabLLM协作机制)"""
    def __init__(self):
        self.agent_pool: Dict[str, dict] = {}
        self.task_queue = deque(maxlen=COORDINATION_PARAMS["queue_size"])
        self.communication_protocol = self._init_protocol()
    
    def register_agent(self, agent_id, capabilities):
        """注册智能体"""
        self.agent_pool[agent_id] = {
            'capabilities': capabilities,
            'status': 'idle',
            'current_task': None
        }
        
    def submit_task(self, task: dict):
        """提交任务到队列"""
        task_id = uuid.uuid4().hex
        self.task_queue.put((
            task['priority'],  # 优先级
            {
                'task_id': task_id,
                'description': task['description'],
                'required_capabilities': task['requirements'],
                'context': task.get('context', {})
            }
        ))
        return task_id
    
    def dispatch_task(self, task):
        """任务分配主循环"""
        subtasks = self._decompose_task(task)
        
        for subtask in subtasks:
            suitable_agents = self._match_capabilities(subtask)
            if suitable_agents:
                selected = self._select_agent(suitable_agents)
                self._assign_task(selected, task)
        
        return allocations
    
    def _decompose_task(self, task):
        # 基于HTN的任务分解
        return task.decomposition_tree
    
    def _select_agent(self, candidates: List[str]) -> str:
        """基于负载均衡的选择策略"""
        return min(
            candidates,
            key=lambda x: self.agent_pool[x]['workload']
        )
    def _match_capabilities(self, subtask):
        """能力匹配检测"""
        return [agent_id for agent_id, spec in self.agent_pool.items()
                if subtask.requirements <= spec['capabilities']]
        
    def _assign_task(self, agent_id: str, task: dict):
        """任务分配执行"""
        self.agent_pool[agent_id]['status'] = 'busy'
        self.agent_pool[agent_id]['current_task'] = task
        print(f"Task {task['task_id']} assigned to {agent_id}")
        
        # 记录协作上下文
        self.conversation_stack.append({
            'task_id': task['task_id'],
            'agent': agent_id,
            'state': 'executing'
        })