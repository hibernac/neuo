import time
import sys
from math import nan
import heapq
import numpy as np
from typing import List, Dict
from abc import ABC, abstractmethod
import os
current_dir = os.path.dirname(os.path.abspath(__file__))
sys.path.append(os.path.abspath(os.path.join(current_dir, '../../')))
from hippocampus import Hippocampus
from basal_ganglia import BasalGanglia
from utils.legal_checks import check_lead_fmt, check_work_coll_fmt, check_work_refl_fmt, check_work_task_fmt, check_insp_review_fmt, check_plan_tree_fmt, check_action_fmt
from utils.neuro_utils import get_action_combinations, workers_info_list2str, knowledge_info_list2str, filter_subtasks_by_workers, get_clean_json, query_llm, decode_difficulty_from_json
from config.neuro_config import STRUCTURE, ACTION_LIST, SURFACE_LIST, OBJECT_LIST, POSSIBLE_BELIEF, AGENTS
from config.prompt_config import LEADER_PROMPT, WORKER_REFL_PROMPT, WORKER_COLL_PROMPT, WORKER_TASK_PROMPT, INSPECTOR_REVIEW_PROMPT, PLANNER_PLAN_PROMPT, ACTION_SELECTOR_PROMPT

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
    """领导者智能体实现分层决策控制"""
    def __init__(self, agent_id: str, workers: List[str], inspector_id: str):
        super().__init__(agent_id)
        self.worker_pool = workers          # 可用员工ID列表
        self.inspector_id = inspector_id    # 审查员ID
        self.idle = True                    # 当前主任务空闲状态
        self.task_counter = 0               # 任务ID计数
        self.feed_back = []                 # 任务审计结果
        
    async def assign_task(self, task_description: str, context):
        """初始化并执行任务分配流程
        工作流程:
        1. 任务初始化与状态检查
        2. 获取任务相关上下文
        3. 智能分配子任务与人员
        4. 任务分发
        """
        if not await self._check_availability():
            return
        task_id = self._initialize_task(task_description)
        self._prepare_task_context(context)
        await self._allocate_subtasks()
  
    def process_feedback(self):
        """处理反馈"""
        if self.current_task['pending_workers']:
            print(f"Workers have not completed their tasks: {self.current_task['pending_workers']}")
            return
        
        print(f"Task: {self.current_task['description']}")
        print(f" └─>Response: {self.inbox}")
        print(f"    └─>Feedback: {self.feed_back}")
        
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
            "subtasks": [],
            "pending_workers": [],
            "iteration": 0
        }
        return task_id
        
    def _prepare_task_context(self, context):
        """准备任务所需的上下文信息"""
        self.current_task['shared_context'] = context
        
    async def _allocate_subtasks(self):
        """分配子任务给合适的工作者"""
        prompt = self._construct_decision_prompt()
        while True:
            llm_response = query_llm(prompt)
            resp_json = get_clean_json(llm_response)
            if check_lead_fmt(resp_json):
                print(resp_json)
                break
        
        difficulty = decode_difficulty_from_json(resp_json)
        if difficulty == 'high':
            self.current_task['subtasks'] = filter_subtasks_by_workers(
                resp_json, self.worker_pool
            )
            await self._broadcast_tasks()
        await self.send_message('Pipeline_0', {
            'type': 'task_difficulty',
            'level': difficulty
        })   
    
    async def _broadcast_tasks(self):
        """向选定的工作者广播任务"""
        for subtask in self.current_task['subtasks']:
            await self.send_message(subtask['assigned_worker'], {
                "type": "task_assign",
                "task_id": self.current_task['id'],
                "subtask_id": subtask['subtask_id'],
                "task": self.current_task['description'],
                "subtask": subtask['task_description'],
                "context": self.current_task['shared_context'],
                "focus": subtask['focus'],
                "collaborators": [(_subtask_['assigned_worker'], STRUCTURE['prefrontal']['expertise'][_subtask_['assigned_worker']]) 
                                  for _subtask_ in self.current_task['subtasks'] 
                                  if _subtask_['assigned_worker'] != subtask['assigned_worker']]
            })
            self.current_task['pending_workers'].append(subtask['assigned_worker'])
        self.idle = False
        
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
    
    async def _request_review(self):
        if not self.current_task['pending_workers']:
            self.send_message(self.inspector_id, {
                "type": "task_review",
                "task_id": self.current_task['id'],
                "task_desc": self.current_task['description'],
                "env_info": self.current_task['shared_context'],
                "worker_resp": [{
                    "sender_id": resp['sender_id'],
                    "content": resp['content']
                } for resp in self.inbox]
            })    
        
    async def receive_message(self, sender_id, content):
        """接收消息"""
        if content['type'] == "task_response" and self.current_task != None and (sender_id in self.current_task['pending_workers']):
            focus = next(_subtask_['focus'] for _subtask_ in self.current_task['subtasks'] 
                            if _subtask_['assigned_worker'])
            self.inbox.append({
                "timestamp": time.time(),
                "sender_id": sender_id,
                "focus": focus,
                "content": content,
            })
            self.current_task['pending_workers'].remove(sender_id)
            await self._request_review()
        elif content['type'] == 'review_response' and self.current_task != None and sender_id == self.inspector_id:
            if content['review_result']['passed']:
                self.feed_back.append("Passed")
            else:
                for issue in content['review_result']['issues']:
                    self.feed_back.append(issue)
          
    def _generate_consensus(self) -> dict: 
        """综合员工反馈生成决策共识"""
        # 从海马体获取历史决策模式
        decision_patterns = Hippocampus.query_decision_patterns(
            self.current_task['description']
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
        worker_exp_pairs = ((worker_id, STRUCTURE['prefrontal']['expertise'][worker_id]) for worker_id in self.worker_pool)
        return LEADER_PROMPT.format(
            str_worker_info=workers_info_list2str(worker_exp_pairs), 
            str_mission=self.current_task['description']
        )
        
class WorkerAgent(BaseAgent):
    """员工智能体实现协作任务处理"""
    class Status:
        IDLE = 0
        PENDING = 1
        BUSY = 2
        
    def __init__(self, agent_id: str, leader_id: str, expertise: str):
        super().__init__(agent_id)
        self.leader_id = leader_id          # 领导ID
        self.expertise = expertise          # 领域专长描述
        self.status = self.Status.IDLE      # 状态码

    def _initialize_task(self, context: dict):
        """初始化新任务的基础结构"""
        self.current_task = {
            "task_id": context['task_id'],              # 任务ID
            "subtask_id": context['subtask_id'],        # 子任务ID
            "task": context['task'],                    # 任务简介
            "subtask": context['subtask'],              # 子任务简介
            "focus": context['focus'],                  # 指示重点
            "collaborators": context['collaborators'],  # 当前协作的智能体列表
            "request_list": [],                         # 需求列表
            "work_list": [],                            # 工作列表
        }
        self.private_cache[context['task_id']] = {
            "subtask": context['subtask'],
            "shared_context": context['context']
        }

    async def refl(self):
        """思考分配的任务并寻助"""
        if self.current_task is None:
            print("Error: No task currently assigned")
            return
        await self._reflect_task()
        
    async def coll(self):
        """执行协作任务"""
        self.status = self.Status.PENDING
        while self.current_task['work_list']:
            for task in self.current_task['work_list'][:]:
                await self._collab_task(task)
                self.current_task['work_list'].remove(task)
        self.status = self.Status.IDLE
        
    async def work(self):
        """执行主任务"""
        if self.status == self.Status.IDLE and not self.current_task['request_list'] and not self.current_task['work_list']:
            self.status = self.Status.BUSY
            await self._work_task()
            self.status = self.Status.IDLE
    
    async def send_message(self, recipient_id: str, content: dict):
        """发送信息"""
        if recipient_id not in AGENTS:
            raise ValueError(f"Recipient {recipient_id} not found in global agents")
        await AGENTS[recipient_id].receive_message(self.agent_id, content)  
    
    async def receive_message(self, sender_id: str, content: dict):
        """接收信息"""
        if sender_id == self.leader_id and content['type'] == "task_assign":
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
            llm_response = query_llm(prompt)
            resp_json = get_clean_json(llm_response)
            if check_work_refl_fmt(resp_json):
                break

        if not resp_json['collaboration_required']:
            return
            
        for req in resp_json['requirement']:
            self.current_task['request_list'].append(req['request_id'])
            await self.send_message(req['worker_id'], {
                "type": "collab_request",
                "request_id": req['request_id'],
                "requester_id": self.agent_id,
                "request_detail": req['request_detail']
            })    
    
    async def _collab_task(self, context: dict):
        """使用LLM进行子任务执行"""
        prompt = self._construct_decision_prompt("collaboration", context)
        while True:
            llm_response = query_llm(prompt)
            resp_json = get_clean_json(llm_response)
            if check_work_coll_fmt(resp_json):
                # print(resp_json)
                break
        
        await self.send_message(context['requester_id'], {
                "type": "collab_response",
                "request_id": context['request_id'],
                "sender_id": self.agent_id,
                "response": resp_json['response']
            })    
    
    async def _work_task(self):
        """使用LLM进行主任务执行"""
        prompt = self._construct_decision_prompt("task")
        while True:
            llm_response = query_llm(prompt)
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
                str_worker_exp=self.expertise,
                str_subtask_id=self.current_task['subtask_id'],
                str_task_desc=self.current_task['subtask'],
                str_focus=self.current_task['focus'], 
                str_co_worker_info=self.current_task['collaborators']
            )
        elif prompt_type == "collaboration":
            return WORKER_COLL_PROMPT.format(
                str_worker_exp=self.expertise,
                str_reqs_id=context['request_id'],
                str_reqtr_id=context['requester_id'],
                str_reqs_inst=context['request_detail']
            )
        elif prompt_type == "task":
            return WORKER_TASK_PROMPT.format(
                str_worker_exp=self.expertise,
                str_task_desc=self.current_task['subtask'],
                str_focus=self.current_task['focus'],
                str_recv_know=knowledge_info_list2str(self.inbox)
            )
        else:
            raise ValueError(f"Unknown prompt type: {prompt_type}")

class InspectorAgent(BaseAgent):
    """审查员智能体实现反馈审查"""
    def __init__(self, agent_id: str, leader_id: str):
        super().__init__(agent_id)
        self.leader_id = leader_id      # 领导ID
        self.idle = True                # 状态码
        self.current_task = {           # 当前任务
            "task_id": "",              # 任务ID
            "task_desc": "",            # 任务描述
            "env_info": [],             # 信息描述列表
            "worker_resp": []           # 员工反馈列表
        }        
        
    async def task_review(self) -> dict:
        """审查任务响应是否合理"""
        prompt = self._construct_decision_prompt()
        while True:
            llm_response = query_llm(prompt)
            resp_json = get_clean_json(llm_response)
            if check_insp_review_fmt(resp_json):
                print(resp_json)
                break
            
        await self.send_message(self.leader_id, {
            'type': 'review_response',
            'task_id': self.current_task['task_id'],
            'review_result': resp_json
        })
        self.idle = True   
        
    def _construct_decision_prompt(self) -> str:
        """构建审查提示词"""
        return INSPECTOR_REVIEW_PROMPT.format(
            str_task_desc=self.current_task['task_desc'], 
            str_env_info=self.current_task['env_info'], 
            str_worker_resp=self.current_task['worker_resp']
        )

    async def send_message(self, recipient, content):
        """发送消息"""
        await AGENTS[recipient].receive_message(self.agent_id, content)
    
    async def receive_message(self, sender_id: str, content: dict):
        """接收消息"""
        if content['type'] == 'task_review' and sender_id == self.leader_id:
            self.idle = False
            self.current_task['task_id'] = content['task_id']
            self.current_task['task_desc'] = content['task_desc']
            self.current_task['env_info'] = content['env_info']
            self.current_task['worker_resp'] = content['worker_resp']

class PipelineAgent(BaseAgent):
    def __init__(self, agent_id: str, leader_id: str):
        super().__init__(agent_id)
        self.leader_id = leader_id          # 领导ID
        self.ext_alloc = 0
    
    async def send_message(self, recipient_id: str, content: dict):
        return
    
    async def receive_message(self, sender_id: str, content: dict):
        if sender_id == self.leader_id and content['type'] == 'task_difficulty':
            if content['level'] == 'low':
                self.ext_alloc = 1
            else:
                self.ext_alloc = 2
        return
    
    def _construct_decision_prompt(self):
        return


class PlannerAgent:
    def __init__(self):
        self.basal = None
        self.current_task = None

    def initialize_task(self, task_description: str):
        self.current_task = {
            "task": task_description,
            "obsv_buffer": [],
            "new_plan": {},
            "optm_actions": []
        }
        self.basal = BasalGanglia()

    async def plan(self, observations: list):
        self.current_task['obsv_buffer'] = observations
        prompt = self._construct_decision_prompt()
        while True:
            llm_response = query_llm(prompt)
            resp_json = get_clean_json(llm_response)
            if check_plan_tree_fmt(resp_json):
                print(resp_json)
                break
        
        self.current_task['new_plan'] = resp_json
        self._construct_htn(resp_json)
        self.current_task['optm_actions'] = self.generate_actions(resp_json)

    def generate_actions(self, htn_data):
        start_state = htn_data["next_state"]
        pq = []
        heapq.heappush(pq, (-start_state["score"], 1.0, [], start_state))
        best_path = None
        best_score = float("-inf")
        while pq:
            neg_score, probability, actions, node = heapq.heappop(pq)
            current_score = -neg_score
            if node["is_goal"]:
                if current_score > best_score:
                    best_score = current_score
                    best_path = actions
                continue
            for transition in node.get("transitions", []):
                next_node = transition["next_state"]
                action = transition["action"]
                transition_prob = transition["probability"]
                new_score = current_score * transition_prob
                new_actions = actions + [action]
                heapq.heappush(pq, (-new_score, transition_prob, new_actions, next_node))
        return best_path if best_path else []
    
    def get_optm_action(self):
        return self.current_task['optm_actions']
    
    def _construct_htn(self, resp_json, view=True):
        self.basal.merge_htn_from_json(resp_json)
        self.basal.update_state_scores(resp_json, gamma=0.8)
        self.basal.visualize_htn(resp_json)
        
    def _construct_decision_prompt(self):
        return PLANNER_PLAN_PROMPT.format(
            str_task_desc=self.current_task['task'], 
            str_cur_state=self.basal.current_state, 
            str_act_list=get_action_combinations(), 
            str_obsv=self.current_task['obsv_buffer'], 
            str_htn=self.current_task['new_plan']
        )
    
class ActionSelectorAgent:
    def __init__(self):
        self.current_task = {
            'task': "",
            'current_state': "",
            'obsv_buffer': [],
            'action_list': [],
            'selected_action': []
        }
        
    def initialize_task(self, task_description: str, current_state: str):
        self.current_task['task'] = task_description
        self.current_task['current_state'] = current_state
        self.current_task['action_list'] = get_action_combinations() 
        
    def ingest_partial_obsv(self, observation: list):
        self.current_task['obsv_buffer'].append(observation)
        
    async def select_action(self):
        prompt = self._construct_selection_prompt()
        while True:
            llm_response = query_llm(prompt)
            resp_json = get_clean_json(llm_response)
            if check_action_fmt(resp_json):
                print(resp_json)
                break
                
        self.current_task['selected_action'] = resp_json['selected_action']
        return self.current_task['selected_action']
    
    def _construct_selection_prompt(self):
        return ACTION_SELECTOR_PROMPT.format(
            str_task_desc=self.current_task['task'],
            str_cur_state=self.current_task['current_state'],
            str_act_list=self.current_task['action_list'],
            str_obsv=self.current_task['obsv_buffer']
        )    

if __name__ == "__main__":
    import asyncio

    context = {  # Unknown initial position
        'robot': ([0.0, 0.0, 0.0]),
        'bottle': np.array([np.nan, np.nan, np.nan]),
        'book': np.array([np.nan, np.nan, np.nan]),
        'box': np.array([np.nan, np.nan, np.nan]),
        'paper': np.array([np.nan, np.nan, np.nan]),
        'cabinet': np.array([np.nan, np.nan, np.nan]),
        'apple': np.array([np.nan, np.nan, np.nan])
    }
    task = "find and fetch the apple"
    
    leader_id = STRUCTURE['prefrontal']['leader_ids'][0]
    worker_ids = STRUCTURE['prefrontal']['worker_ids']
    expertise_dict = STRUCTURE['prefrontal']['expertise']
    pipe_id = STRUCTURE['prefrontal']['pipeline_ids'][0]
    inspector_id = STRUCTURE['prefrontal']['inspector_ids'][0]
    
    leader = LeaderAgent(agent_id=leader_id, workers=worker_ids, inspector_id=inspector_id)
    workers = [
        WorkerAgent(agent_id=wid, leader_id=leader_id, expertise=expertise_dict[wid]['detail'])
        for wid in worker_ids
    ]
    pipe = PipelineAgent(agent_id=pipe_id, leader_id=leader_id)
    inspector = InspectorAgent(agent_id=inspector_id, leader_id=leader_id)

    AGENTS[leader_id] = leader
    AGENTS[worker_ids] = workers
    AGENTS[pipe_id] = pipe
    AGENTS[inspector_id] = inspector
    
    asyncio.run(leader.assign_task(task, context))  
    
    planner = PlannerAgent()
    planner.initialize_task(task)
    
    # 模拟观测数据
    observation = [
        { "robot":  (0.0, 0.0, 0.0)  },
        { "bottle": (-0.3, 0.7, 0.4) },
        { "book":   (0.0, 0.5, 0.1)  },
        { "box":    (0.0, 0.5, 0.2)  },
        { "paper":  (0.3, 0.6, 0.05) },
        { "cabinet":(0.2, 0.8, 0.5)  },
        { "apple":  (np.nan, np.nan, np.nan) }
    ]
    planner.basal.ingest_observation(observation)
    
    async def run_tasks():
        task1 = await planner.plan(observation)
        task2 = None
        if pipe.ext_alloc == 2:
            selector = ActionSelectorAgent()
            selector.initialize_task(task, planner.basal.current_state)
            selector.ingest_partial_obsv(observation)
            task2 = await selector.select_action()
        
        # await asyncio.gather(task1, task2)
        print("Optimal action sequence:", planner.get_optm_action())
        if task2:
            print("Selected action:", task2)
    
    asyncio.run(run_tasks())        