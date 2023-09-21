import requests
import os
import json

apiUrl = 'https://api.openai.com/v1//chat/completions'

def generate_ai_listing(prompt):
    headers = {'Authorization': 'Bearer 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'}
    body = {
        "model": "gpt-3.5-turbo",
        "messages": [
            {
                "role": "user",
                "content": prompt
            }
        ],
        "temperature": 1,
        "top_p": 1,
        "n": 1,
        "stream": False,
        "max_tokens": 500,
        "presence_penalty": 0,
        "frequency_penalty": 0
    }
    res = requests.post(apiUrl, json=body, headers=headers)
    print(res)
    raw = res.content.decode("utf-8")
    data = json.loads(raw)
    return data['choices'][0]['message']['content']