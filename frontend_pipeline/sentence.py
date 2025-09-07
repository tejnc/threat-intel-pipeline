import os
import requests

from dotenv import load_dotenv

load_dotenv()

HF_TOKEN = os.environ.get("HF_TOKEN")

API_URL = "https://router.huggingface.co/v1/chat/completions"
headers = {
    "Authorization": f"Bearer {HF_TOKEN}",
}

def run_sentence_transformer(messy:  str, query:str):
    def query(payload):
        response = requests.post(API_URL, headers=headers, json=payload)
        return response.json()

    response = query({
        "messages": [
            {
                "role": "user",
                "content": f"analyse this chunk : {messy} for query {query} and give me one line analysis."
            }
        ],
        "model": "meta-llama/Llama-3.2-3B-Instruct:together"
    })
    message = response["choices"][0]["message"]["content"]
    return message

