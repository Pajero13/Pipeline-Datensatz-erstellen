from comfy import (
    test_connection,
    load_workflow,
    set_image,
    set_filename,
    submit_workflow,
    wait_until_finished,
)

from config import WORKFLOW_BILD_SKALIEREN


if __name__ == "__main__":

    print("=== Workflow Bild skalieren ===")

    test_connection()

    workflow = load_workflow(
        WORKFLOW_BILD_SKALIEREN
    )

    workflow = set_image(
        workflow,
        "1",
        "IMG_1455.jpg"
    )

    workflow = set_filename(
        workflow,
        "3",
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

    print("Bild erfolgreich skaliert.")