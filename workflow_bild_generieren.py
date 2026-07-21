from comfy import (
    test_connection,
    load_workflow,
    set_prompt,
    set_filename,
    submit_workflow,
)

from config import WORKFLOW_FLUX


if __name__ == "__main__":

    print("=== Workflow Bild generieren ===")

    test_connection()

    workflow = load_workflow(
        WORKFLOW_FLUX
    )