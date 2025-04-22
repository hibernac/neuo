## Structure  

```python
项目目录结构：
brain_embodied_agent/
├── core/
│   ├── brain_modules/
│   │   ├── sensory.py         # 多模态感知处理
│   │   ├── prefrontal.py      # 分层决策控制
│   │   ├── hippocampus.py     # 记忆整合系统
│   │   └── basal_ganglia.py   # 行为选择机制
├── agents/
│   ├── coordinator.py         # 中央协调系统
│   ├── actuator.py            # 运动执行模块
│   └── thalamus.py            # 信息路由中心
├── memory/
│   ├── knowledge_graph.py     # 语义记忆存储
│   ├── episodic_memory.py     # 情景记忆管理
│   └── working_memory.py      # 工作记忆缓存
├── utils/
│   ├── legal_checks.py        # 合法性检验工具
│   ├── neuro_utils.py         # 神经计算工具
│   └── sim_env.py             # 环境交互接口
├── evaluation/
│   ├── neural_benchmark.py    # 神经合理性评估
│   └── collab_metrics.py      # 协作效能指标
└── config/                    # 系统配置
    ├── api_keys.py            # 第三方服务密钥
    ├── neuro_config.py        # 脑区参数配置
    └── prompt_config.py       # 提示词配置
```

### Requirements

openai==1.69.0
transformer==4.50.3
torch
graphviz
scipy==1.15.2

### How to run

1. 在`neuro_congig.py`的 `STRUCTURE`中设置多智能体架构、动作集
2. 全局定义`task`字段，`context`全局object信息
3. 初始化`leaderAgent`,`pipelineAgent`,`workerAgent`,`InspectorAgent`,`plannerAgent`
4. 通过`planner.basal.ingest_observation(observation)`插入观测值
5. 通过
```python
selector = ActionSelectorAgent()
selector.initialize_task(task, planner.basal.current_state)
selector.ingest_partial_obsv(observation)
```
选择动作
6. `planner.get_optm_action()`获取当前预测的下一步动作