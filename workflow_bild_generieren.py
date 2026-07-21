from comfy import (
    test_connection,
    load_workflow,
    set_prompt,
    set_filename,
    submit_workflow,
    wait_until_finished,
    read_prompt
)

from config import WORKFLOW_FLUX


if __name__ == "__main__":

    print("=== Workflow Bild generieren ===")

    test_connection()

    workflow = load_workflow(
        WORKFLOW_FLUX
    )

prompt = read_prompt()

workflow = set_filename(
    workflow,
    "9",
    "IMG_1455"
)

prompt_id = submit_workflow(
    workflow
)

print()

print("Workflow gestartet")

print(prompt_id)

wait_until_finished(prompt_id)

print()

print("Bild erfolgreich generiert.")