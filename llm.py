import os
import requests

def run_llm(prompt):
    url = "https://api.siliconflow.cn/v1/chat/completions"
    
    payload = {
        "model": "deepseek-ai/DeepSeek-V3",
        "messages": [
            {
                "role": "user",
                "content": prompt
            }
        ],
        "stream": True,
        "max_tokens": 512,
        "stop": ["null"],
        "temperature": 0.0,
        "top_p": 0.7,
        "top_k": 50,
        "frequency_penalty": 0.5,
        "n": 1,
        "response_format": {"type": "text"},
        "tools": [
            {
                "type": "function",
                "function": {
                    "description": "<string>",
                    "name": "<string>",
                    "parameters": {},
                    "strict": False
                }
            }
        ]
    }
    token = "Bearer " + os.environ.get("SiliconFlow")
    headers = {
        "Authorization": token,
        "Content-Type": "application/json"
    }
    
    response = requests.request("POST", url, json=payload, headers=headers)
    
    print(response.text)
    return response.json()["choices"][0]["message"]["content"]