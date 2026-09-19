from comfy import (
    test_connection,
    load_workflow,
    set_prompt,
    set_filename,
    submit_workflow,
    wait_until_finished,
    set_output_path,
    set_noise_seed,
    generate_seed_from_filename,
    print_time,
    get_batches,
    get_batch_dateien,
    ausgabe_ordner_fuer_batch,
    time,
)

from config import (
    WORKFLOW_FLUX,
    PROMPTS_DIR,
    OUTPUT_DIR_FLUX1,
)

from pathlib import Path

TEXT_MUSTER = ["*.txt"]


def get_batches_input():
    return get_batches(PROMPTS_DIR, TEXT_MUSTER)


if __name__ == "__main__":

    start_zeit = time.perf_counter()

    print("=== Workflow Bild generieren ===")

    test_connection()

    batches = get_batches_input()

    i = 0
    n = sum(len(get_batch_dateien(ordner, TEXT_MUSTER)) for _, ordner in batches)
    intialisierung_zeit = start_zeit

    for batch_name, batch_ordner in batches:

        if batch_name:
            print(f"\n--- Ordner: {batch_name} ---")

        ausgabe_ordner = ausgabe_ordner_fuer_batch(OUTPUT_DIR_FLUX1, batch_name)

        for prompt in get_batch_dateien(batch_ordner, TEXT_MUSTER):

            bezeichnung = f"{batch_name}/{prompt.name}" if batch_name else prompt.name
            print(f"\nVerarbeite: {bezeichnung} ({i + 1} von {n}) ")

            workflow = load_workflow(
                WORKFLOW_FLUX
            )

            prompt_text = prompt.read_text(
                encoding="utf-8"
            )

            workflow = set_prompt(
                workflow,
                "6",
                prompt_text
            )

            workflow = set_output_path(
                workflow,
                "26",
                str(ausgabe_ordner)
            )

            seed = generate_seed_from_filename(prompt.name)

            workflow = set_noise_seed(
                workflow,
                "25",
                seed
            )

            workflow = set_filename(
                workflow,
                "26",
                prompt.stem
            )

            prompt_id = submit_workflow(
                workflow
            )

            wait_until_finished(
                prompt_id
            )
            if i == 1:
                intialisierung_zeit = time.perf_counter()
            i += 1

    end_zeit = time.perf_counter()
    print_time(start_zeit,end_zeit,False)
    print_time(start_zeit,intialisierung_zeit,True)
