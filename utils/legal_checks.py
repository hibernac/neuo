import json
import re

def check_lead_fmt(response_json):
    try:
        if isinstance(response_json, str):
            response_json = json.loads(response_json)
        
        # Check if response has 'subtasks' key
        if 'difficulty' not in response_json or 'subtasks' not in response_json:
            return False
                
        # Check if difficulty is valid
        if not isinstance(response_json['difficulty'], str) or response_json['difficulty'] not in ['low', 'medium', 'high']:
            return False
                
        # Check if subtasks is a list
        if not isinstance(response_json['subtasks'], list):
            return False
        
        # Validate each subtask
        for subtask in response_json['subtasks']:
            # Check required keys
            required_keys = ['subtask_id', 'assigned_worker', 'task_description', 'focus']
            if not all(key in subtask for key in required_keys):
                return False
                    
            # Validate types
            if not isinstance(subtask['subtask_id'], str):
                return False
            if not isinstance(subtask['assigned_worker'], str):
                return False
            if not isinstance(subtask['task_description'], str):
                return False
            if not isinstance(subtask['focus'], list):
                return False
                    
            # Validate focus items are strings
            if not all(isinstance(item, str) for item in subtask['focus']):
                return False
                    
        return True
            
    except (json.JSONDecodeError, Exception):
        return False  

def check_work_refl_fmt(response_json):
    try:
        if isinstance(response_json, str):
            response_json = json.loads(response_json)
        
        # Validate required top-level keys
        if not isinstance(response_json.get('collaboration_required'), bool):
            return False
            
        requirements = response_json.get('requirement', [])
        if not isinstance(requirements, list):
            return False
            
        # If collaboration not required, requirements should be empty
        if not response_json['collaboration_required'] and requirements:
            return False
            
        # Validate each requirement object
        for req in requirements:
            # Check required keys exist with correct types
            if not isinstance(req.get('request_id'), str):
                return False
            if not isinstance(req.get('worker_id'), str):
                return False
            if not isinstance(req.get('request_detail'), str):
                return False
                
            # Validate request_id format (assuming 4 digit format)
            if not re.match(r'^\d{4}$', req['request_id']):
                return False
                
            # Validate request_detail is not empty
            if not req['request_detail'].strip():
                return False
                
        return True
        
    except (json.JSONDecodeError, KeyError, TypeError):
        return False
        
def check_work_task_fmt(response_json):
    try:
        if isinstance(response_json, str):
            response_json = json.loads(response_json)
        
        # Check if JSON is valid and has required field
        if not isinstance(response_json, dict) or "response" not in response_json:
            return False
                
        # Check if response is a non-empty string
        response_str = response_json["response"]
        if not isinstance(response_str, str) or not response_str.strip():
            return False
                
        return True
            
    except Exception:
        return False
    
def check_work_coll_fmt(response_json):
    try:
        if isinstance(response_json, str):
            response_json = json.loads(response_json)
        
        # Check if JSON is valid and has required field
        if not isinstance(response_json, dict) or "response" not in response_json:
            return False
                
        # Check if response is a non-empty string
        response_str = response_json["response"]
        if not isinstance(response_str, str) or not response_str.strip():
            return False
                
        return True
            
    except Exception:
        return False
    
def check_insp_review_fmt(response_json):
    try:
        if isinstance(response_json, str):
            response_json = json.loads(response_json)
                
        if "passed" not in response_json or not isinstance(response_json["passed"], bool):
            return False
                
        if "issues" not in response_json or not isinstance(response_json["issues"], list):
            return False
                
        valid_types = ["contradiction", "missing_info", "scope_violation"]
        valid_severities = ["critical", "warning"]
                
        for issue in response_json["issues"]:
            if not isinstance(issue, dict):
                return False
                    
            required_fields = ["issue_id", "type", "description", "severity"]
            if not all(field in issue for field in required_fields):
                return False
                    
            if not isinstance(issue["issue_id"], str):
                return False
            if not isinstance(issue["type"], str) or issue["type"] not in valid_types:
                return False
            if not isinstance(issue["description"], str):
                return False
            if not isinstance(issue["severity"], str) or issue["severity"] not in valid_severities:
                return False
                    
        return True
            
    except Exception:
        return False

def check_plan_tree_fmt(response_json):
    try:
        if isinstance(response_json, str):
            response_json = json.loads(response_json)
            
        if "next_state" not in response_json:
            return False
            
        def validate_state(state_obj):
            if not isinstance(state_obj, dict):
                return False
                
            required_fields = ["state", "score", "is_goal", "transitions"]
            if not all(field in state_obj for field in required_fields):
                return False
                
            if not isinstance(state_obj["state"], str):
                return False
            if not isinstance(state_obj["score"], (int, float)):
                return False
            if not isinstance(state_obj["is_goal"], bool):
                return False
            if not isinstance(state_obj["transitions"], list):
                return False
                
            for transition in state_obj["transitions"]:
                if not isinstance(transition, dict):
                    return False
                    
                required_trans_fields = ["action", "probability", "next_state"]
                if not all(field in transition for field in required_trans_fields):
                    return False
                    
                if not isinstance(transition["action"], str):
                    return False
                if not isinstance(transition["probability"], (int, float)):
                    return False
                if not validate_state(transition["next_state"]):
                    return False
                    
            return True
            
        return validate_state(response_json["next_state"])
            
    except Exception:
        return False
    
def check_action_fmt(response_json):
    try:
        if isinstance(response_json, str):
            response_json = json.loads(response_json)
        required_fields = ["selected_action", "reason"]
        if not all(field in response_json for field in required_fields):
            return False
        if not isinstance(response_json["selected_action"], str):
            return False
        if not isinstance(response_json["reason"], str):
            return False
        return True
    
    except Exception:
        return False
