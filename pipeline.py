from comfy import (
    test_connection,
    load_workflow,
    set_image,
    submit_workflow
)

from config import WORKFLOW_QWEN


if __name__ == "__main__":

    print("=== AI Pipeline ===")

    test_connection()

    workflow = load_workflow(WORKFLOW_QWEN)

    workflow = set_image(
        workflow,
        "IMG_1455.jpg"
    )

    prompt_id = submit_workflow(workflow)

    print()

    print("Workflow gestartet")

    print(prompt_id)