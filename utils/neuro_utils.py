import numpy as np
# import openai
from openai import OpenAI
import json
import requests
import sys
import os
current_dir = os.path.dirname(os.path.abspath(__file__))
sys.path.append(os.path.abspath(os.path.join(current_dir, '../../')))
from config.api_keys import OPENAI_API_KEY, OPENAI_BASE_URL
from config.neuro_config import ACTION_LIST
from scipy.signal import welch
import urllib3
urllib3.disable_warnings()

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

def get_action_combinations():
    action_combinations = []
    for action, directions in ACTION_LIST.items():
        for direction in directions:
            action_combinations.append(f"{action} {direction}")
    return action_combinations

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
    url = OPENAI_BASE_URL #+ "chat/completions"
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

    client = OpenAI(api_key=api_key, base_url="https://api.deepseek.com/v1")
    response = client.chat.completions.create(
    model="deepseek-chat",
    messages=[
        {"role": "system", "content": "You are a helpful assistant"},
        {"role": "user", "content": "Hello"},
    ],
    stream=False )
    # print(response.choices[0].message.content)
    response = requests.post(url, headers=headers, json=data, verify=False)
    # response.raise_for_status()
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

def decode_difficulty_from_json(json_data):
    """从LLM输出中解析难度"""
    try:
        data = json.loads(json_data) if isinstance(json_data, str) else json_data
        difficulty = data.get("difficulty", "low")
        return difficulty
    except json.JSONDecodeError:
        return "low"