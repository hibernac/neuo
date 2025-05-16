import sys
import os
current_dir = os.path.dirname(os.path.abspath(__file__))
sys.path.append(os.path.abspath(os.path.join(current_dir, '../../')))
import time
from collections import deque
import asyncio
from queue import PriorityQueue
from tqdm import tqdm
from dataclasses import dataclass
from enum import Enum
from config.neuro_config import STRUCTURE, AGENTS
from core.brain_modules.prefrontal import LeaderAgent, WorkerAgent, InspectorAgent, PipelineAgent

@dataclass
class TaskMetrics:
    task_completion: float = 0.0
    collaboration_quality: float = 0.0
    execution_time: float = 0.0
    error_count: int = 0

class TaskStatus(Enum):
    PENDING = "pending"
    RUNNING = "running"
    COMPLETED = "completed"
    FAILED = "failed"
    
class PrefrontalOrchestrator:
    """前额叶皮层协调中枢 (AvaTaR constrastive reasoning mechanism inspired contrastive reflecting)"""
    def __init__(self):
        global AGENTS
        AGENTS.clear()
        
        self.leader = LeaderAgent("Leader_0", STRUCTURE['prefrontal']['worker_ids'], "Inspector_0")
        self.workers = {
            wid: WorkerAgent(wid, "Leader_0", STRUCTURE['prefrontal']['expertise'][wid])
            for wid in STRUCTURE['prefrontal']['worker_ids']
        }
        self.inspector = InspectorAgent("Inspector_0", "Leader_0")
        AGENTS[self.leader.agent_id] = self.leader
        AGENTS.update(self.workers)
        # Register the pipelines agent
        self.pipelines = PipelineAgent(
            STRUCTURE['prefrontal']['pipeline_ids'][0],
            STRUCTURE['prefrontal']['leader_ids'],
        )
        AGENTS[self.pipelines.agent_id] = self.pipelines
        # Register the inspector agent
        AGENTS[self.inspector.agent_id] = self.inspector
        
        self.current_task_status = TaskStatus.PENDING
        self.metrics = TaskMetrics()    

    async def execute_decision_cycle(self, task_description: str, context) -> TaskMetrics:
        """执行完整决策周期"""
        try:
            self.current_task_status = TaskStatus.RUNNING
            self.metrics.execution_time = time.time()

            estimated_total_steps = 3

            with tqdm(total=estimated_total_steps, desc="Initializing", dynamic_ncols=True) as pbar:
                rf_c = await self._execute_assign_phase(task_description, context, pbar)
                pbar.total += rf_c
                pbar.refresh()
                cl_c = await self._execute_reflection_phase(pbar)
                pbar.total += cl_c
                pbar.refresh()
                await self._execute_collaboration_phase(pbar)
                await self._execute_work_phase(pbar)
                # await self._execute_review_phase(pbar)
                self._process_results(pbar)
            self.current_task_status = TaskStatus.COMPLETED
            self.metrics.execution_time = time.time() - self.metrics.execution_time
            return self.metrics

        except Exception as e:
            self.current_task_status = TaskStatus.FAILED
            self.metrics.error_count += 1
            raise
    
    async def _execute_assign_phase(self, task_description: str, context, pbar):
        pbar.set_description("Assign phase")
        await self.leader.assign_task(task_description, context)
        pbar.update(1)
        return len(self.leader.current_task['subtasks'])

    async def _execute_reflection_phase(self, pbar):
        tasks = [w.refl() for w in self.workers.values() if w.current_task]
        pbar.set_description("Reflection phase")
        await self._run_tasks_with_progress(tasks, pbar)
        return sum(len(w.current_task['work_list']) for w in self.workers.values() if w.current_task)
    
    async def _execute_collaboration_phase(self, pbar):
        tasks = [w.coll() for w in self.workers.values() if w.current_task]
        pbar.set_description("Collaboration phase")
        await self._run_tasks_with_progress(tasks, pbar)

    async def _execute_work_phase(self, pbar):
        tasks = [w.work() for w in self.workers.values() if w.current_task]
        pbar.set_description("Work phase")
        await self._run_tasks_with_progress(tasks, pbar)
    
    async def _execute_review_phase(self, pbar):
        pbar.set_description("Review phase")
        await self.inspector.task_review()
        pbar.update(1)
    
    def _process_results(self, pbar):
        pbar.set_description("Results processing")
        self.leader.process_feedback()
        pbar.update(1)   
            
    async def _run_tasks_with_progress(self, tasks, pbar):
        """并发运行任务，并在完成时更新进度条"""
        for task in asyncio.as_completed(tasks):
            await task
            pbar.update(1)