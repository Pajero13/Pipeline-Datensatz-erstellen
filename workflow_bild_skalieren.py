from comfy import (
    test_connection,
    load_workflow,
    set_filename,
    submit_workflow,
    wait_until_finished,
    set_image_path,
    set_output_path,
    print_time,
    time,
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

    start_zeit = time.perf_counter()

    print("=== Workflow Bild skalieren ===")

    test_connection()

    i = 0
    n = len(get_images())

    for image in get_images():

        print(f"\nVerarbeite: {image.name} ({i + 1} von {n}) ")

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

        i += 1

end_zeit = time.perf_counter()
print_time(start_zeit,end_zeit,False)