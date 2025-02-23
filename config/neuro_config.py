# system config
STRUCTURE = {
    "prefrontal": {
        "leader_number": 1,
        "leader_ids": [ "Leader_0" ],
        "worker_number": 5,
        "worker_ids": [ "Worker_1", "Worker_2", "Worker_3", "Worker_4", "Worker_5" ],
        "expertise": {
            "Worker_1": {
                "title": "Environmental Perception Specialist",
                "detail": "Real-time sensor data interpretation (e.g., LiDAR, cameras, tactile sensors), object recognition, spatial mapping, and anomaly detection in dynamic environments."
            },
            "Worker_2": {
                "title": "Dynamic Path Planner",
                "detail": "Multi-objective trajectory optimization, collision avoidance, energy-efficient routing, and real-time adaptation to environmental/operational changes."
            },
            "Worker_3": {
                "title": "Operational Control Expert",
                "detail": "Precise actuator coordination, force/torque optimization, error correction in physical interactions, and safety protocol enforcement."
            },
            "Worker_4": {
                "title": "Human-Robot Interface Coordinator",
                "detail": "Natural language command parsing, user intent recognition, contextual feedback generation, and emotion/gesture interpretation for collaborative tasks."
            },
            "Worker_5": {
                "title": "System Integrity Orchestrator",
                "detail": "Resource allocation monitoring, cross-module dependency management, failure recovery protocols, and energy/performance tradeoff optimization."
            }
        }
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

# global parameters
AGENTS = {}

SENSORY_CONFIG = {}
