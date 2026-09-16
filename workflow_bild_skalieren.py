from comfy import (
    test_connection,
    load_workflow,
    set_filename,
    submit_workflow,
    wait_until_finished,
    set_image_path,
    set_output_path,
    print_time,
    get_batches,
    get_batch_dateien,
    ausgabe_ordner_fuer_batch,
    time,
)

from config import (
    WORKFLOW_BILD_SKALIEREN,
    INPUT_DIR,
    PREPROCESSED_DIR,
)
from image_utils import normalize_image

from pathlib import Path

BILD_MUSTER = ["*.jpg", "*.jpeg"]


def get_batches_input():
    return get_batches(INPUT_DIR, BILD_MUSTER)


if __name__ == "__main__":

    start_zeit = time.perf_counter()

    print("=== Workflow Bild skalieren ===")

    test_connection()

    batches = get_batches_input()

    i = 0
    n = sum(len(get_batch_dateien(ordner, BILD_MUSTER)) for _, ordner in batches)

    for batch_name, batch_ordner in batches:

        if batch_name:
            print(f"\n--- Ordner: {batch_name} ---")

        ausgabe_ordner = ausgabe_ordner_fuer_batch(PREPROCESSED_DIR, batch_name)

        for image in get_batch_dateien(batch_ordner, BILD_MUSTER):

            bezeichnung = f"{batch_name}/{image.name}" if batch_name else image.name
            print(f"\nVerarbeite: {bezeichnung} ({i + 1} von {n}) ")

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
                str(ausgabe_ordner)
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
