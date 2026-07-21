import json
from comfy import (
    test_connection,
    load_workflow,
    set_image,
    submit_workflow,
    wait_until_finished,
    read_prompt
)


from config import WORKFLOW_QWEN


if __name__ == "__main__":

    print("=== AI Pipeline ===")

    test_connection()

    workflow = load_workflow(WORKFLOW_QWEN)

    workflow = set_image(
    workflow,
    "13",
    "IMG_1455.jpg"
)

    prompt_id = submit_workflow(workflow)

    print()

    print("Workflow gestartet")

    print(prompt_id)

history = wait_until_finished(prompt_id)

prompt = read_prompt()

print()
print("===== Prompt =====")
print(json.dumps(history, indent=2))