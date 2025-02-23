# -*- main.py -*-
import asyncio
from core.brain_modules.sensory import MultimodalProcessor
from core.brain_modules.prefrontal import PrefrontalOrchestrator
from agents.coordinator import CorticalCoordinator
from memory.knowledge_graph import NeuroSemanticMemory

class EmbodiedAgentSystem:
    """具身智能系统总控"""
    def __init__(self):
        self.sensory = MultimodalProcessor()
        self.memory = NeuroSemanticMemory()
        self.controller = PrefrontalOrchestrator()
        self.coordinator = CorticalCoordinator()
        
        # 初始化智能体集群
        self._register_core_agents()
    
    def _register_core_agents(self):
        self.coordinator.register_agent(
            agent_id="vision_processor",
            capabilities={"modality": "visual", "processing_rate": 30}
        )
        self.coordinator.register_agent(
            agent_id="motor_actuator",
            capabilities={"joints": 12, "precision": 0.01}
        )
    
    def process_cycle(self, sensory_input):
        # 感知处理
        processed = self.sensory.process(sensory_input)
        
        # 记忆整合
        context = self.memory.hybrid_retrieval(processed)
        
        # 决策生成
        plan = self.controller.execute_decision(context)
        
        # 任务执行
        allocations = self.coordinator.dispatch_task(plan)
        
        # 运动执行
        return self._execute_actions(allocations)

async def test_prefrontal():
    orchestrator = PrefrontalOrchestrator()
    task = '''
    A team of autonomous robots collaborates in a dynamic hospital environment to manage medication delivery, restock supplies, and respond to emergencies (e.g., spills). 
    Using a multi-agent prefrontal reflection framework, they negotiate task priorities (e.g., rerouting deliveries around obstacles), resolve conflicts (e.g., shared corridor access), and adapt strategies in real-time (e.g., redistributing tasks during communication failures). 
    Each robot continuously self-assesses decisions (e.g., "Was prioritizing ICU over Pediatrics optimal?") and shares insights to optimize collective efficiency, safety, and adaptability in unpredictable, human-centric settings.
    '''
    
    metrics = await orchestrator.execute_decision_cycle(task)
    print(f"Task Metrics: {metrics}")
    
if __name__ == "__main__":
    asyncio.run(test_prefrontal())

