# system config
STRUCTURE = {
    "prefrontal": {
        "leader_number": 1,
        "leader_ids": [ "Leader_0" ],
        "worker_number": 5,
        "worker_ids": [ "Worker_0", "Worker_1", "Worker_2", "Worker_3", "Worker_4" ],
        "expertise": {
            "Worker_0": {
                "title": "Navigation Agent (Path Planning & Obstacle Avoidance)",
                "detail": "forward _m, backward _m, left_turn _deg, right_turn _deg, stop, adjust_speed _m/s"
            },
            "Worker_1": {
                "title": "Perception Agent (Environment Sensing & Object Recognition)",
                "detail": "detect_objects within _m radius, identify_object at _x _y coordinates, scan_environment for _object_type, measure_distance to _object"
            },
            "Worker_2": {
                "title": "Manipulation Agent (Object Interaction & Handling)",
                "detail": "grab_object at _x _y _z, lift_object _cm height, rotate_object _deg, place_object at _x _y _z"
            },
            "Worker_3": {
                "title": "Task Monitoring Agent (Execution Tracking & Error Handling)",
                "detail": "check_status of _task_name, verify_completion of _subtask, detect_error in _process, report_progress of _task, retry_operation _times"
            },
            "Worker_4": {
                "title": "Motion Planning Agent (Trajectory Optimization & Kinematics Control)",
                "detail": "move_joint _joint_name to _deg, set_velocity _joint_name to _deg/s, follow_trajectory _path_name, maintain_pose for _seconds"
            }
        },
        "inspector_number": 1,
        "inspector_ids": [ "Inspector_0" ]
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

# global parameters
AGENTS = {}

SENSORY_CONFIG = {}
