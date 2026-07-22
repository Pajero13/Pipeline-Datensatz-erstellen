from comfy import (
    test_connection,
    load_workflow,
    submit_workflow,
    wait_until_finished,
    set_image_path,
    set_text_filename,
    set_text_output_path,
)

from config import (
    WORKFLOW_QWEN,
    PREPROCESSED_DIR,
    PROMPTS_DIR,
)

from pathlib import Path

def get_images():

    return sorted(Path(PREPROCESSED_DIR).glob("*.png"))

if __name__ == "__main__":

    print("=== Workflow Prompt generieren ===")

    test_connection()

    for image in get_images():
        print(f"\nVerarbeite: {image.name}")

        workflow = load_workflow(
            WORKFLOW_QWEN
        )

        workflow = set_image_path(
            workflow,
            "17",
            str(image.resolve())
        )

        workflow = set_text_output_path(
            workflow,
            "22",
            PROMPTS_DIR
        )

        workflow = set_text_filename(
            workflow,
            "22",
            image.stem
        )

        prompt_id = submit_workflow(workflow)

        wait_until_finished(
            prompt_id
        )

        print("✓ Fertig")