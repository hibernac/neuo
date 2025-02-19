import asyncio
import time
from dataclasses import dataclass
from enum import Enum
from typing import List, Dict
from abc import ABC, abstractmethod
from core.brain_modules.hippocampus import Hippocampus
# from agents.thalamus import thalamus
# from memory.working_memory import WorkingMemory
from utils.legal_checks import check_lead_fmt, check_work_coll_fmt, check_work_refl_fmt, check_work_task_fmt
from utils.neuro_utils import workers_info_list2str, knowledge_info_list2str, filter_subtasks_by_workers, get_clean_json, query_llm
from config.neuro_config import STRUCTURE, AGENTS, INITIAL_EXPERTISE_MAP
from config.prompt_config import LEADER_PROMPT, WORKER_REFL_PROMPT, WORKER_COLL_PROMPT, WORKER_TASK_PROMPT

class BaseAgent(ABC):
    """智能体基类，定义通用消息处理机制"""
    def __init__(self, agent_id: str):
        self.agent_id = agent_id
        self.private_cache = {}     # 独享缓存空间
        self.current_task = None    # 当前处理的任务对象
        self.inbox = []             # 消息接收队列
    
    @abstractmethod
    async def send_message(self, recipient_id: str, content: dict):
        """抽象消息发送方法（由具体类实现路由）"""
        pass
    
    @abstractmethod
    async def receive_message(self, sender_id: str, content: dict):
        """抽象消息接收方法（由具体类实现路由）"""
        pass
    
    @abstractmethod
    def _construct_decision_prompt(self):
        """构建决策提示词,整合当前状态、历史记忆和任务目标"""
        pass

class LeaderAgent(BaseAgent):
    """领导者智能体实现分层决策控制 (AvaTaR constrastive reasoning mechanism inspired contrastive reflecting)"""
    def __init__(self, agent_id: str, workers: List[str]):
        super().__init__(agent_id)
        self.worker_pool = workers      # 可用员工ID列表
        self.idle = True                # 当前主任务空闲状态
        self.task_counter = 0           # 任务ID计数
        
    async def assign_task(self, task_description: str):
        """初始化并执行任务分配流程
        工作流程:
        1. 任务初始化与状态检查
        2. 获取任务相关上下文
        3. 智能分配子任务与人员
        4. 任务分发与执行
        5. 结果收集与状态重置
        """
        if not await self._check_availability():
            return
        task_id = self._initialize_task(task_description)
        await self._prepare_task_context()
        await self._allocate_subtasks()
        await self._broadcast_tasks()
        await self._monitor_execution()
        self._reset_task_state()
        
    async def _check_availability(self) -> bool:
        """检查leader当前是否可以接收新任务"""
        if not self.idle:
            print("Leader agent is currently busy with another task")
            return False
        return True
        
    def _initialize_task(self, task_description: str) -> str:
        """初始化新任务的基础结构"""
        self.task_counter += 1
        task_id = f"task_{self.task_counter}"
        
        self.current_task = {
            "id": task_id,
            "description": task_description,
            "shared_context": [],
            "selected": [],
            "pending_workers": [],
            "iteration": 0
        }
        return task_id
        
    async def _prepare_task_context(self):
        """准备任务所需的上下文信息"""
        shared_context = Hippocampus.retrieve_shared_context(self.current_task['description'])
        self.current_task['shared_context'] = shared_context
        
    async def _allocate_subtasks(self):
        """分配子任务给合适的工作者"""
        prompt = self._construct_decision_prompt()
        while True:
            llm_response = await query_llm(prompt)
            resp_json = get_clean_json(llm_response)
            if check_lead_fmt(resp_json):
                break
                
        self.current_task['selected'] = await filter_subtasks_by_workers(
            llm_response, self.worker_pool
        )
        
    async def _broadcast_tasks(self):
        """向选定的工作者广播任务"""
        for subtask in self.current_task['selected']:
            await self.send_message(subtask['assigned_worker'], {
                "type": "task_assign",
                "task_id": self.current_task['id'],
                "subtask_id": subtask['subtask_id'],
                "task": self.current_task['description'],
                "subtask": subtask['task_description'],
                "context": self.current_task['shared_context'],
                "focus": subtask['focus'],
                "collaborators": [(_subtask_['assigned_worker'], _subtask_['focus']) 
                                  for _subtask_ in self.current_task['selected'] 
                                  if _subtask_['assigned_worker'] != subtask['assigned_worker']]
            })
            self.current_task['pending_workers'].append(subtask['assigned_worker'])
        self.idle = False
        
    async def _monitor_execution(self):
        """监控任务执行进度"""
        while self.current_task['pending_workers']:
            await asyncio.sleep(10)
            
        print("All workers submitted their reports:")
        print(self.inbox)
        
    def _reset_task_state(self):
        """重置任务状态"""
        self.current_task = None
        self.idle = True
        self.inbox = []  
    
    async def send_message(self, recipient_id, content):
        """发送消息"""
        if recipient_id not in AGENTS:
            raise ValueError(f"Recipient {recipient_id} not found in global agents")
            
        await AGENTS[recipient_id].receive_message(self.agent_id, content)    
    
    async def receive_message(self, sender_id, content):
        """接收消息"""
        if any(tup[0] == sender_id for tup in self.current_task['selected']):
            focus = next(tup[1] for tup in self.current_task['selected'] 
                              if tup[0] == sender_id)
            self.inbox.append({
                "timestamp": time.time(),
                "sender_id": sender_id,
                "focus": focus,
                "content": content,
            })
            self.current_task['pending_workers'].remove(sender_id)
            
    def process_feedback(self, timeout: float = 30.0):
        """处理员工反馈（带超时机制）"""
        print(self.inbox)
        return
        # TODO: implement a more comprehensive prefrontal mechanism
        start_time = time.time()
        while len(self.inbox) < len(self.current_task["selected"]):
            # 处理收到的消息
            for msg in self.inbox:
                if msg["content"]["type"] == "task_feedback":
                    self.inbox[msg["sender"]] = msg["content"]["data"]
            self.inbox = [m for m in self.inbox if m["content"]["type"] != "task_feedback"]
            
            # 超时检查
            if time.time() - start_time > timeout:
                break
            time.sleep(0.5)
        
        # 生成综合决策
        consensus = self._generate_consensus()
        
        if consensus["status"] == "confirmed":
            thalamus.route_decision(consensus["plan"])
        else:
            self._initiate_iteration(consensus["conflicts"])
    
    def _generate_consensus(self) -> dict: 
        """综合员工反馈生成决策共识"""
        # 从海马体获取历史决策模式
        decision_patterns = Hippocampus.query_decision_patterns(
            self.current_task["description"]
        )
        
        # 构建LLM提示词进行综合判断
        feedback_summary = "\n".join(
            [f"{k}: {v}" for k,v in self.inbox.items()]
        )
        prompt = f"""综合以下反馈生成最终方案：
        任务：{self.current_task['description']}
        历史模式：{decision_patterns}
        员工反馈：{feedback_summary}
        请用JSON格式输出："""
        # TODO: implement a more comprehensive prefrontal mechanism
        return query_llm(prompt, response_format="json")
    
    def _construct_decision_prompt(self):
        """构建决策提示词,整合当前状态、历史记忆和任务目标"""
        str_worker_info = workers_info_list2str(self.worker_pool)
        return LEADER_PROMPT.format(str_worker_info, self.current_task['description'])
        

class WorkerAgent(BaseAgent):
    """员工智能体实现协作任务处理"""
    class Status:
        IDLE = 0
        PENDING = 1
        BUSY = 2
        
    def __init__(self, agent_id: str, leader_id: str, expertise: str):
        super().__init__(agent_id)
        self.leader_id = leader_id      # 领导
        self.expertise = expertise      # 领域专长描述
        self.status = self.Status.IDLE  # 状态码

    def _initialize_task(self, context: dict):
        """初始化新任务的基础结构"""
        self.current_task = {
            "focus": context['focus'],                  # 指示重点
            "task_id": context['task_id'],              # 任务ID
            "subtask_id": context['subtask_id'],        # 子任务ID
            "task": context['task'],                    # 任务简介
            "subtask": context['subtask'],              # 子任务简介
            "collaborators": context['collaborators'],  # 当前协作的智能体列表
            "request_list": [],                         # 需求列表
            "work_list": [],                            # 工作列表
        }
        self.private_cache[context['task_id']] = {
            "subtask": context['subtask'],
            "shared_context": context['context']
        }

    async def refl(self, context: dict):
        """思考分配的任务并寻助"""
        self._initialize_task(context)
        await self._reflect_task()
        
    async def coll(self):
        """执行协作任务"""
        self.status = self.Status.PENDING
        while self.current_task["work_list"]:
            for task in self.current_task["work_list"][:]:
                if task["type"] == "collab_request":
                    await self._collab_task(task)
                    self.current_task["work_list"].remove(task)
        self.status = self.Status.IDLE
        
    async def work(self, context: dict):
        """执行主任务"""
        if self.status == self.Status.IDLE and not self.current_task["request_list"] and not self.current_task["work_list"]:
            self.status = self.Status.BUSY
            await self._work_task(context)
            self.status = self.Status.IDLE
    
    async def send_message(self, recipient_id: str, content: dict):
        """发送信息"""
        if recipient_id not in AGENTS:
            raise ValueError(f"Recipient {recipient_id} not found in global agents")
            
        await AGENTS[recipient_id].receive_message(self.agent_id, content)  
    
    async def receive_message(self, sender_id: str, content: dict):
        """接收信息"""
        if sender_id == self.leader_id and content["type"] == "task_assign" and self.current_task == None and self.status == self.Status.IDLE:
            self._initialize_task(content)
        elif any(tup[0] == sender_id for tup in self.current_task['collaborators']):
            if content['type'] == "collab_request":
                self.current_task['work_list'].append({
                    "request_id": content['request_id'],
                    "requester_id": content['requester_id'],
                    "request_detail": content['request_detail']
                })
            elif content['type'] == "collab_response":
                focus = next(tup[1] for tup in self.current_task['collaborators'] 
                                if tup[0] == sender_id)
                self.inbox.append({
                    "timestamp": time.time(),
                    "sender_id": content['sender_id'],
                    "focus": focus,
                    "content": content['response']
                })
                self.current_task['request_list'].remove(content['request_id'])

    async def _reflect_task(self):
        """使用LLM发起与其他员工的协作流程"""
        prompt = self._construct_decision_prompt("reflection")
        while True:
            llm_response = await query_llm(prompt)
            resp_json = get_clean_json(llm_response)
            if check_work_refl_fmt(resp_json):
                break

        if not resp_json["collaboration_required"]:
            return
            
        for req in resp_json["requirement"]:
            self.current_task["request_list"].append(req["request_id"])
            await self.send_message(req["worker_id"], {
                "type": "collab_request",
                "request_id": req["request_id"],
                "requester_id": self.agent_id,
                "request_detail": req["request_detail"]
            })    
    
    async def _collab_task(self, context: dict):
        """使用LLM进行子任务执行"""
        prompt = self._construct_decision_prompt("collaboration", context)
        while True:
            llm_response = await query_llm(prompt)
            resp_json = get_clean_json(llm_response)
            if check_work_coll_fmt(resp_json):
                break
        
        await self.send_message(context['requester_id'], {
                "type": "collab_response",
                "request_id": context['request_id'],
                "sender_id": self.agent_id,
                "response": resp_json['response']
            })    
    
    async def _work_task(self, context: dict):
        """使用LLM进行主任务执行"""
        prompt = self._construct_decision_prompt("task")
        while True:
            llm_response = await query_llm(prompt)
            resp_json = get_clean_json(llm_response)
            if check_work_task_fmt(resp_json):
                break
        
        await self.send_message(self.leader_id, {
                "type": "task_response",
                "worker_id": self.agent_id,
                "task_id": self.current_task['task_id'],
                "subtask_id": self.current_task['subtask_id'],
                "response": resp_json['response']
            })    
            
    def _reset_task_state(self):
        """重置任务状态"""
        self.current_task = None 
        self.status = self.Status.IDLE
        
    def _construct_decision_prompt(self, prompt_type: str, context: dict = None) -> str:
        """构建决策提示词"""
        if prompt_type == "reflection":
            return WORKER_REFL_PROMPT.format(
                self.expertise,
                self.current_task['subtask_id'],
                self.current_task['subtask'],
                self.current_task["focus"],
                self.current_task["collaborators"]
            )
        elif prompt_type == "collaboration":
            return WORKER_COLL_PROMPT.format(
                self.expertise,
                context['request_id'],
                context['requester_id'],
                context['request_detail']
            )
        elif prompt_type == "task":
            return WORKER_TASK_PROMPT.format(
                self.expertise,
                self.current_task['subtask'],
                self.current_task['focus'],
                knowledge_info_list2str(self.inbox)
            )
        else:
            raise ValueError(f"Unknown prompt type: {prompt_type}")

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
        AGENTS = {}
        
        self.leader = LeaderAgent("leader_01", STRUCTURE["prefrontal"]["worker_ids"])
        self.workers = {
            wid: WorkerAgent(wid, "leader_01", INITIAL_EXPERTISE_MAP[wid])
            for wid in STRUCTURE["prefrontal"]["worker_ids"]
        }
        AGENTS["leader_01"] = self.leader
        AGENTS.update(self.workers)
        
        self.current_task_status = TaskStatus.PENDING
        self.metrics = TaskMetrics()
    
    async def execute_decision_cycle(self, task_description: str) -> TaskMetrics:
        """执行完整决策周期"""
        try:
            self.current_task_status = TaskStatus.RUNNING
            self.metrics.execution_time = time.time()
            await self._execute_leader_phase(task_description)
            await self._execute_reflection_phase()
            await self._execute_collaboration_phase()
            await self._execute_work_phase()
            await self._process_results()
            self.current_task_status = TaskStatus.COMPLETED
            self.metrics.execution_time = time.time() - self.metrics.execution_time
            return self.metrics

        except Exception as e:
            self.current_task_status = TaskStatus.FAILED
            self.metrics.error_count += 1
            raise
    
    
    async def _execute_leader_phase(self, task_description: str):
        await self.leader.assign_task(task_description)
        await asyncio.sleep(5)

    async def _execute_reflection_phase(self):
        reflection_tasks = [
            worker.refl(self.leader.current_task["shared_context"])
            for worker in self.workers.values()
        ]
        await asyncio.gather(*reflection_tasks)

    async def _execute_collaboration_phase(self):
        collab_tasks = [
            worker.coll()
            for worker in self.workers.values()
        ]
        await asyncio.gather(*collab_tasks)

    async def _execute_work_phase(self):
        work_tasks = [
            worker.work(self.leader.current_task["shared_context"])
            for worker in self.workers.values()
        ]
        await asyncio.gather(*work_tasks)

    async def _process_results(self):
        await self.leader.process_feedback()
        self._calculate_metrics()

    def _calculate_metrics(self):
        total_messages = len(self.leader.inbox)
        successful_messages = len([msg for msg in self.leader.inbox 
                                 if msg["content"]["type"] == "task_response"])
        
        self.metrics.task_completion = successful_messages / total_messages
        self.metrics.collaboration_quality = len([msg for msg in self.leader.inbox 
                                                if "collaboration" in msg["content"]]) / total_messages


async def test_prefrontal():
    orchestrator = PrefrontalOrchestrator()
    task = "Design a new authentication system"
    
    metrics = await orchestrator.execute_decision_cycle(task)
    print(f"Task Metrics: {metrics}")
    
if __name__ == "__main__":
    asyncio.run(test_prefrontal())

