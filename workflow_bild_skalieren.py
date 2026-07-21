from comfy import (
    test_connection,
    load_workflow,
    set_filename,
    submit_workflow,
    wait_until_finished,
    set_image_path,
    set_output_path,
)

from config import (
    WORKFLOW_BILD_SKALIEREN,
    INPUT_DIR,
    PREPROCESSED_DIR,
)
from image_utils import normalize_image

from pathlib import Path

def get_images():

    return sorted(
    list(Path(INPUT_DIR).glob("*.jpg")) +
    list(Path(INPUT_DIR).glob("*.jpeg"))
)

if __name__ == "__main__":

    print("=== Workflow Bild skalieren ===")

    test_connection()

    for image in get_images():

        print(f"\nVerarbeite: {image.name}")

        normalized = normalize_image(image)

        workflow = load_workflow(
            WORKFLOW_BILD_SKALIEREN
        )

        workflow = set_image_path(
            workflow,
            "5",
            str(normalized.resolve())
        )
        workflow = set_output_path(
            workflow,
            "11",
            PREPROCESSED_DIR
        )

        workflow = set_filename(
            workflow,
            "11",
            image.stem
        )
        prompt_id = submit_workflow(
            workflow
        )

        wait_until_finished(prompt_id)

        print("✓ Fertig")