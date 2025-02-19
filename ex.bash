# 初始化记忆系统
python -m memory.knowledge_graph --init 

# 启动协调中枢
python -m agents.coordinator --port 50051

# 运行主控制系统
python main.py --config neuro_config.yaml