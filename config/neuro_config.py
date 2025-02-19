AGENTS = {}

STRUCTURE = {
    "prefrontal": {
        "leader_number": 1,
        "leader_ids": [ "Leader_0" ],
        "worker_number": 5,
        "worker_ids": [ "Worker_1", "Worker_2", "Worker_3", "Worker_4", "Worker_5" ]
    },
    "hippocampus": {
        "skb": {
            "max_memory": 1000,
        },
        "context": {
            "max_memory": 1000,
        }
    },
    "thalamus": {
        
    },
    "basal_ganglia": {
        
    }
}

INITIAL_EXPERTISE_MAP = {
    "Worker_1": "reasoning",
    "Worker_2": "reasoning",
    "Worker_3": "reasoning",
    "Worker_4": "reasoning",
    "Worker_5": "reasoning"
}

AGENTS = []

NEURO_MODULES = {
    "sensory": {
        "processor": "google/vit-base-patch16-224",
        "model": "facebook/dino-vitb16"
    },
    "memory": {
        "max_episodes": 1000,
        "retrieval_threshold": 0.7
    }
}

COORDINATION_PARAMS = {
    "queue_size": 100,
    "timeout": 5.0,
    "max_retries": 3
}
