import json
import time
import uuid
import requests
from pathlib import Path

CONFIG = {
    "robot_keys": [],
    "api_url": "http://localhost:1234/v1/chat/completions",
    "model": "qwen:0.5",
    "timeout": 30,
    "output_dir": "output/qwen",
    "max_retries": 3,
    "backoff": 2
}

def load_keys(path="robot_keys.json"):
    try:
        with open(path, "r", encoding="utf-8") as f:
            CONFIG["robot_keys"] = json.load(f)
    except Exception as e:
        print(f"Failed to load keys: {e}")
        CONFIG["robot_keys"] = []

def dispatch_to_qwen(prompt: str, key_idx: int = 0) -> dict:
    if not CONFIG["robot_keys"]:
        load_keys()
    key = CONFIG["robot_keys"][key_idx % len(CONFIG["robot_keys"])]
    headers = {"Authorization": f"Bearer {key}"}
    payload = {
        "model": CONFIG["model"],
        "messages": [{"role": "user", "content": prompt}]
    }
    for attempt in range(1, CONFIG["max_retries"] + 1):
        try:
            resp = requests.post(CONFIG["api_url"], headers=headers, json=payload, timeout=CONFIG["timeout"])
            resp.raise_for_status()
            data = resp.json()
            return data["choices"][0]["message"]
        except Exception as e:
            print(f"[retry {attempt}] {e}")
            time.sleep(CONFIG["backoff"] * attempt)
    raise RuntimeError("Qwen dispatch failed after retries.")

def save_output(prompt: str, response: dict):
    Path(CONFIG["output_dir"]).mkdir(parents=True, exist_ok=True)
    uid = uuid.uuid4().hex
    path = Path(CONFIG["output_dir"]) / f"{uid}.json"
    with open(path, "w", encoding="utf-8") as f:
        json.dump({
            "id": uid,
            "prompt": prompt,
            "response": response
        }, f, ensure_ascii=False, indent=2)
    return path

def run_prompt(prompt: str, key_idx: int = 0):
    response = dispatch_to_qwen(prompt, key_idx)
    path = save_output(prompt, response)
    print(f"✔ Response saved to {path}")
    return response
