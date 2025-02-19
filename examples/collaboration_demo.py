from agents.coordinator import TaskCoordinator
from core.brain_modules import MultimodalFusion, HippocampalMemory

class CollaborationDemo:
    def __init__(self):
        # 初始化系统组件
        self.coordinator = TaskCoordinator()
        self.perception = MultimodalFusion()
        self.memory = HippocampalMemory()
        
        # 注册智能体
        self._setup_agents()
    
    def _setup_agents(self):
        self.coordinator.register_agent(
            "vision_agent",
            capabilities={"modality": "vision", "fps": 30}
        )
        self.coordinator.register_agent(
            "planning_agent", 
            capabilities={"reasoning": "multi-step"}
        )
    
    def run_demo(self, input_data):
        # 感知处理
        fused_features = self.perception(input_data)
        
        # 记忆检索
        context = self.memory.retrieve_context(fused_features)
        
        # 创建协作任务
        task = {
            "priority": 1,
            "description": "Navigate to kitchen and find coffee mug",
            "requirements": ["spatial_reasoning", "object_recognition"],
            "context": context
        }
        task_id = self.coordinator.submit_task(task)
        
        # 任务分配执行
        self.coordinator.dispatch_tasks()
        
        # 监控任务状态
        while not self._is_task_complete(task_id):
            self._update_task_status()
        
        return self._collect_results(task_id)