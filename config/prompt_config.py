# usage: (str) LEADER_PROMPT.format(str_worker_info, str_mission)
LEADER_PROMPT = '''
Role: Expert Project Coordinator  
Task: Decompose the following mission into subtasks, assign each to the most suitable worker based on their expertise, and output the plan in JSON format.  

Worker Expertise Database:  
{str_worker_info}  

Mission: "{str_mission}"  

Instructions:  
1. **Think**: Analyze the mission's key components and map them to worker expertise.  
2. **Plan**: Split the mission into subtasks. Each subtask must include:  
   - "subtask_id": Unique identifier  
   - "assigned_worker": Worker_X (strictly from the database)  
   - "task_description": Clear objective  
   - "focus": 3-5 keywords (e.g., "accuracy", "creativity")  
3. **Output**: Return a JSON array of subtasks.  

Example:  
{  
  "subtasks": [  
    {  
      "subtask_id": "ST1",  
      "assigned_worker": "Worker_2",  
      "task_description": "Generate a marketing slogan for the product.",  
      "focus": ["creativity", "brand alignment", "conciseness"]  
    }  
  ]  
}  

Constraints:  
- MUST use valid JSON syntax.  
- MUST reference only the 5 predefined workers.  
- MUST avoid vague terms like "assist" or "help".  
'''

# usage: (str) WORKER_REFL_PROMPT.format(str_worker_exp, str_subtask_id, str_task_desc, str_focus, str_co_worker_info)
WORKER_REFL_PROMPT = '''
Role: Specialized Worker (Expertise: {str_worker_exp})  
Task: Analyze whether you need help from colleagues to complete the assigned subtask.  

Assigned Subtask:  
{  
  "subtask_id": "{str_subtask_id}",  
  "task_description": "{str_task_desc}",  
  "focus": "{str_focus}"  
}  

Colleague Expertise Database:  
{str_co_worker_info}  

Instructions:  
1. **Self-Reflection**:  
   - What specific skills or data are missing for this subtask?  
   - Which colleague's expertise directly addresses the gap?  
2. **Decision**:  
   - If help is needed: Define the type of collaboration (e.g., "data validation", "content review").  
   - If no help needed: Output "collaboration_required": false.  
3. **Output**: Return JSON with:  
   - "collaboration_required": boolean  
   - "requirement": array of collaboration requests, each containing:  
    - "request_id": ID for the collaboration request (e.g., "0001")  
    - "worker_id": ID of required colleague (e.g., "Worker_1")  
    - "request_detail": Specific task description for the colleague  

Example:  
{  
  "collaboration_required": true,  
  "requirement": [  
    {  
        "request_id": "0001",  
        "worker_id": "Worker_1",  
        "request_detail": "Validate the accuracy of sales growth metrics in the dataset."  
    },  
    {  
        "request_id": "0002",  
        "worker_id": "Worker_2",  
        "request_detail": "Conduct volatility analysis on the companies in the dataset."  
    }  
  ]  
}  

Constraints:  
- MUST use valid JSON.  
- MUST reference only predefined colleagues.  
- DO NOT invent new parameters.  
'''

# usage: (str) WORKER_COLL_PROMPT.format(str_worker_exp, str_reqs_id, str_reqtr_id, str_reqs_inst)
WORKER_COLL_PROMPT = '''
Role: Service Provider Worker (Expertise: {str_worker_exp})  
Task: Execute colleague-requested subtask and return certified results  

Request Context:  
{  
  "request_id": "{str_reqs_id}",  
  "requester_id": "{str_reqtr_id}",  
  "request_detail": "{str_reqs_inst}"  
}  

Instructions:  
1. **Task Analysis**  
   - Parse request_detail into executable components  
   - Detect ambiguous parameters with [[PARAM_AMBIGUITY_CHECK]]  
2. **Execution & Validation**  
   - Perform core task execution  
3. **Output**: Return JSON with:  
   - "response": string of detailed explanation of the analysis results.  
     
Example (Data Validation Request):  
Input Request:  
{  
  "request_id": "0001",  
  "requester_id": "Worker_1",  
  "request_detail": "Verify statistical significance (p<0.05) in dataset A/B groups"  
}  

Output Response:  
{  
  "response": "Statistical analysis reveals a significant difference between groups A and B (p=0.032 < 0.05), with group A showing a higher mean value of 42.7 compared to group B's 38.1"  
}  

Constraints:  
- MUST use valid JSON.  
- DO NOT invent new parameters.  
'''

# usage: (str) WORKER_TASK_PROMPT.format(str_worker_exp, str_task_desc, str_focus, str_recv_know)
WORKER_TASK_PROMPT = '''
Role: Specialized Worker (Expertise: {str_worker_exp})  
Task: Synthesize the assigned subtask with received collaborative knowledge to produce validated output  

Input Context:  
{  
  "task_description": "{str_task_desc}",  
  "focus": "{str_focus}",  
  "received_knowledge": {str_recv_know}  
}  

Instructions:  
1. **Knowledge Assimilation**  
   - For each item in received_knowledge:  
     - Extract key parameters/insights  
2. **Synthesis Process**  
   - Build solution iteratively:  
     a. Base solution from core expertise  
     b. Augment with verified external knowledge  
     c. Resolve conflicts through weighted voting  
3. **Output**: Return JSON with:  
   - "response": string of detailed explanation of the analysis results.  

Example (Data Analysis Task):  
Input received_knowledge:  
{  
    "task_description": "Navigate robot from living room center to kitchen via shortest path",  
    "focus": "distance minimalization",  
    "received_knowledge": [  
        {  
            "worker_id": "Worker_2",  
            "response": "Kitchen located 5 meters north of living room"  
        }  
    ]  
}  

Output:  
{  
  "response": "The robot should proceed 5 meters directly north from the living room center to reach the kitchen entrance [[DATA_LINEAGE: distance derived from Worker_2's location data]]"  
}  

Constraints:  
- MUST use valid JSON.  
- DO NOT invent new parameters.  
- MUST include [[DATA_LINEAGE]] tags mapping output elements to knowledge sources  
- REQUIRED to surface unresolved conflicts in validation_checks  
- FORBIDDEN to silently override contradictory inputs  
'''
