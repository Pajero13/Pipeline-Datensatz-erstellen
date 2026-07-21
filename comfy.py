# comfy.py
import requests
import json
import time
from config import COMFY_URL
from config import COMFY_URL, PROMPT_FILE

def test_connection():

    try:

        response = requests.get(f"{COMFY_URL}/system_stats")

        if response.status_code == 200:

            print("✅ Verbindung zu ComfyUI erfolgreich.")

        else:

            print("❌ ComfyUI antwortet mit:", response.status_code)

    except Exception as e:

        print("❌ Verbindung fehlgeschlagen")

        print(e)


def load_workflow(path: str) -> dict:
    with open(path, "r", encoding="utf-8") as f:
        return json.load(f)
    

def set_image(workflow: dict, image_name: str) -> dict:

    workflow["13"]["inputs"]["image"] = image_name

    return workflow

def submit_workflow(workflow: dict) -> str:

    payload = {
        "prompt": workflow
    }

    response = requests.post(
        f"{COMFY_URL}/prompt",
        json=payload
    )

    response.raise_for_status()

    data = response.json()

    return data["prompt_id"]

def wait_until_finished(prompt_id: str):

    while True:

        response = requests.get(
            f"{COMFY_URL}/history/{prompt_id}"
        )

        data = response.json()

        if prompt_id in data:
            return data[prompt_id]

        time.sleep(1)

def get_prompt_text(history):

    try:

        return history["outputs"]["15"]["text"][0]

    except Exception:

        return None
    
def read_prompt():

    with open(PROMPT_FILE, "r", encoding="cp1252") as f:
        return f.read()
    
def set_prompt(workflow: dict, prompt: str) -> dict:

    workflow["6"]["inputs"]["text"] = prompt

    return workflow

def set_filename(workflow: dict, filename: str) -> dict:

    workflow["9"]["inputs"]["filename_prefix"] = filename

    return workflow