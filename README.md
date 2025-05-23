## Structure  

```python
Project directory structure:
brain_embodied_agent/
├── core/
│   ├── brain_modules/
│   │   ├── sensory.py         # Multi-modal perception processing
│   │   ├── prefrontal.py      # Hierarchical decision control
│   │   ├── hippocampus.py     # Memory integration system
│   │   └── basal_ganglia.py   # Behavior selection mechanism
├── agents/
│   ├── coordinator.py         # Central coordination system
│   ├── actuator.py            # Motion execution module
│   └── thalamus.py            # Information routing center
├── memory/
│   ├── knowledge_graph.py     # Semantic memory storage
│   ├── episodic_memory.py     # Episodic memory management
│   └── working_memory.py      # Working memory cache
├── utils/
│   ├── legal_checks.py        # Legality check tools
│   ├── neuro_utils.py         # Neural computation tools
│   └── sim_env.py             # Environment interaction interface
├── evaluation/
│   ├── neural_benchmark.py    # Neural rationality evaluation
│   └── collab_metrics.py      # Collaboration effectiveness metrics
└── config/                    # System configuration
    ├── api_keys.py            # Third-party service keys
    ├── neuro_config.py        # Brain region parameter configuration
    └── prompt_config.py       # Prompt configuration
```

### Requirements

openai==1.69.0
transformer==4.50.3
torch
graphviz
scipy==1.15.2

### How to run

1.  Set the multi-agent architecture and action set in `STRUCTURE` of `neuro_config.py`.
2.  Globally define the `task` field and `context` global object information.
3.  Initialize `leaderAgent`, `pipelineAgent`, `workerAgent`, `InspectorAgent`, and `plannerAgent`.
4.  Insert observation values through `planner.basal.ingest_observation(observation)`.
5.  Select actions through:

```python
selector = ActionSelectorAgent()
selector.initialize_task(task, planner.basal.current_state)
selector.ingest_partial_obsv(observation)
```

6.  Get the currently predicted next action through `planner.get_optm_action()`.