import numpy as np
import openai
import json
import requests
import sys
sys.path.append(r'/Users/hongjunwu/Desktop/Pj/neocortex/config')
from api_keys import OPENAI_API_KEY, OPENAI_BASE_URL
from scipy.signal import welch

def workers_info_list2str(workers):
    return "\n".join(
        "{}. {}: {}".format(i + 1, worker, dict2str(expertise) if isinstance(expertise, dict) else expertise) for i, (worker, expertise) in enumerate(workers)
    )

def dict2str(a):
    return str(a)

def list2str(a):
    return str(a)

def knowledge_info_list2str(knowledge):
    return json.dumps(knowledge, indent=2, ensure_ascii=False)

# class NeuralDynamicAnalyzer:
#     """神经动力学分析工具 (检测1/f噪声特征)"""
#     def __init__(self, sampling_rate=1000):
#         self.fs = sampling_rate
        
#     def analyze_powerlaw(self, signal):
#         freqs, psd = welch(signal, self.fs)
#         slope, _ = np.polyfit(np.log(freqs[1:]), np.log(psd[1:]), 1)
#         return slope
    
#     def detect_criticality(self, signals):
#         slopes = [self.analyze_powerlaw(s) for s in signals]
#         return np.mean(slopes)
    
def get_clean_json(llm_response):    
    try:
        content = llm_response["choices"][0]["message"]["content"]
        if content.startswith('```json\n'):
            content = content[7:-3]
        return json.loads(content)
    except (KeyError, IndexError, json.JSONDecodeError):
        return {"error": "Unable to parse response."}

def query_llm(prompt, model="gpt-4o"):
    """大语言模型调用"""
    api_key = OPENAI_API_KEY
    url = OPENAI_BASE_URL + "chat/completions"
    headers = {
        "Content-Type": "application/json",
        "Authorization": f"Bearer {api_key}",
    }
    data = {
        "model": model,
        "messages": [
            {"role": "system", "content": "You are a helpful assistant."},
            {"role": "user", "content": prompt},
        ],
    }

    response = requests.post(url, headers=headers, json=data)
    response.raise_for_status()
    return response.json()

def filter_subtasks_by_workers(json_data, allowed_pool):
    """从LLM输出中解析子任务"""
    try:    
        data = json.loads(json_data) if isinstance(json_data, str) else json_data
        filtered_subtasks = [
            subtask for subtask in data["subtasks"]
            if subtask["assigned_worker"] in allowed_pool
        ]
            
        return filtered_subtasks
    except json.JSONDecodeError:
        return []
