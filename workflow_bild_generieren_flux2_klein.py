# workflow_bild_generieren_flux2_klein.py
#
# Wie workflow_bild_generieren_flux1.py, aber mit dem flux2-klein-
# Modell. Node "9" (Save-Node) im ComfyUI-Workflow ist der "Image
# Save"-Custom-Node (mit output_path-Feld) - genau wie bei den
# anderen Modellen.
#
# Liest Prompts aus dem gemeinsamen PROMPTS_DIR (Batches/Unterordner
# werden unterstützt) und speichert die Bilder unter
# OUTPUT_DIR_FLUX2_KLEIN.

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
    WORKFLOW_FLUX2_KLEIN,
    PROMPTS_DIR,
    OUTPUT_DIR_FLUX2_KLEIN,
)

TEXT_MUSTER = ["*.txt"]

# Node-ID des Save-Nodes im flux2-klein-Workflow.
SAVE_NODE_ID = "9"


def get_batches_input():
    return get_batches(PROMPTS_DIR, TEXT_MUSTER)


if __name__ == "__main__":

    start_zeit = time.perf_counter()

    print("=== Workflow Bild generieren (flux2-klein) ===")

    test_connection()

    batches = get_batches_input()

    i = 0
    n = sum(len(get_batch_dateien(ordner, TEXT_MUSTER)) for _, ordner in batches)
    intialisierung_zeit = start_zeit

    for batch_name, batch_ordner in batches:

        if batch_name:
            print(f"\n--- Ordner: {batch_name} ---")

        ausgabe_ordner = ausgabe_ordner_fuer_batch(OUTPUT_DIR_FLUX2_KLEIN, batch_name)

        for prompt in get_batch_dateien(batch_ordner, TEXT_MUSTER):

            bezeichnung = f"{batch_name}/{prompt.name}" if batch_name else prompt.name
            print(f"\nVerarbeite: {bezeichnung} ({i + 1} von {n}) ")

            workflow = load_workflow(
                WORKFLOW_FLUX2_KLEIN
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
                SAVE_NODE_ID,
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
                SAVE_NODE_ID,
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
