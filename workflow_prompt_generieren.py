from comfy import (
    test_connection,
    load_workflow,
    submit_workflow,
    wait_until_finished,
    set_image_path,
    set_text_filename,
    set_text_output_path,
    set_custom_prompt,
    print_time,
    get_batches,
    get_batch_dateien,
    ausgabe_ordner_fuer_batch,
    time,
)

from config import (
    WORKFLOW_QWEN,
    PREPROCESSED_DIR,
    PROMPTS_DIR,
    QWEN_CUSTOM_PROMPT,
)

from pathlib import Path

BILD_MUSTER = ["*.png"]


def get_batches_input():
    return get_batches(PREPROCESSED_DIR, BILD_MUSTER)


if __name__ == "__main__":

    start_zeit = time.perf_counter()

    print("=== Workflow Prompt generieren ===")

    test_connection()

    custom_prompt = Path(
        QWEN_CUSTOM_PROMPT
    ).read_text(
        encoding="utf-8"
    )

    batches = get_batches_input()

    i = 0
    n = sum(len(get_batch_dateien(ordner, BILD_MUSTER)) for _, ordner in batches)

    for batch_name, batch_ordner in batches:

        if batch_name:
            print(f"\n--- Ordner: {batch_name} ---")

        ausgabe_ordner = ausgabe_ordner_fuer_batch(PROMPTS_DIR, batch_name)

        for image in get_batch_dateien(batch_ordner, BILD_MUSTER):

            bezeichnung = f"{batch_name}/{image.name}" if batch_name else image.name
            print(f"\nVerarbeite: {bezeichnung} ({i + 1} von {n}) ")

            workflow = load_workflow(
                WORKFLOW_QWEN
            )

            workflow = set_custom_prompt(
            workflow,
            "14",
            custom_prompt
            )
            workflow = set_image_path(
                workflow,
                "17",
                str(image.resolve())
            )

            workflow = set_text_output_path(
                workflow,
                "22",
                str(ausgabe_ordner)
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

            i += 1

    end_zeit = time.perf_counter()
    print_time(start_zeit,end_zeit,False)
