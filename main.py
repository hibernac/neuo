# -*- main.py -*-
import asyncio
from core.brain_modules.sensory import MultimodalProcessor
from agents.coordinator import PrefrontalOrchestrator
from agents.thalamus import Thalamus

class EmbodiedAgentSystem:
    """具身智能系统总控"""
    def __init__(self, str_task):
        self.task = str_task
        # self.sensory = MultimodalProcessor()
        self.info_hub = Thalamus()
        self.controller = PrefrontalOrchestrator()
        
        # 初始化智能体集群
        # self._register_core_agents()
    
    def _register_core_agents(self):
        self.coordinator.register_agent(
            agent_id="vision_processor",
            capabilities={"modality": "visual", "processing_rate": 30}
        )
        self.coordinator.register_agent(
            agent_id="motor_actuator",
            capabilities={"joints": 12, "precision": 0.01}
        )
    
    async def process_cycle(self, processed):
        # 感知处理
        # processed = self.sensory.process(sensory_input)
        
        # 记忆整合
        context = self.info_hub.integrated_retrieval(self.task, processed)
        
        # 决策生成
        plan = await self.controller.execute_decision_cycle(self.task, context)
        print(f"Task Metrics: {plan}") # for testing
        # 任务执行
        # allocations = self.actuator.dispatch_task(plan)
        
        # 运动执行
        # return self._execute_actions(allocations)
        
async def test_embodied_system():
    # Get initial task description
    print("=> Please enter task description (or 'quit' to exit):")
    task = input()
    if task.lower() == 'quit':
        return
    
    # for testing
    task = '''
    A team of autonomous robots collaborates in a dynamic hospital environment to manage medication delivery, restock supplies, and respond to emergencies (e.g., spills). 
    Using a multi-agent prefrontal reflection framework, they negotiate task priorities (e.g., rerouting deliveries around obstacles), resolve conflicts (e.g., shared corridor access), and adapt strategies in real-time (e.g., redistributing tasks during communication failures). 
    Each robot continuously self-assesses decisions (e.g., "Was prioritizing ICU over Pediatrics optimal?") and shares insights to optimize collective efficiency, safety, and adaptability in unpredictable, human-centric settings.
    '''
    
    system = EmbodiedAgentSystem(task)
    
    while True:
        # Get environment observation
        print("==> Please enter environment observation (or 'quit' to exit):")
        observation = input()
        if observation.lower() == 'quit':
            break
            
        # Process cycle
        await system.process_cycle(observation)
        
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
    asyncio.run(test_embodied_system())
    