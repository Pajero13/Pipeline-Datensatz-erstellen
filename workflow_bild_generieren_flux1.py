# workflow_bild_generieren_flux1.py
#
# Erzeugt Bilder mit dem flux1-Modell (dev) für alle Prompts in
# PROMPTS_DIR (Batches/Unterordner werden unterstützt) und speichert
# sie unter OUTPUT_DIR_FLUX1. Der Pro-Bild-Ablauf (Prompt/Seed/Output
# setzen, ComfyUI aufrufen, warten) steckt in
# comfy.bild_fuer_prompt_generieren().

from comfy import (
    test_connection,
    get_batches,
    get_batch_dateien,
    ausgabe_ordner_fuer_batch,
    bild_fuer_prompt_generieren,
    print_time,
    time,
)

from config import (
    WORKFLOW_FLUX,
    PROMPTS_DIR,
    OUTPUT_DIR_FLUX1,
)

TEXT_MUSTER = ["*.txt"]

# Node-ID des Save-Nodes im flux1-Workflow.
SAVE_NODE_ID = "26"


if __name__ == "__main__":

    start_zeit = time.perf_counter()

    print("=== Workflow Bild generieren (flux1) ===")

    test_connection()

    batches = get_batches(PROMPTS_DIR, TEXT_MUSTER)

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

            bild_fuer_prompt_generieren(
                workflow_pfad=WORKFLOW_FLUX,
                save_node_id=SAVE_NODE_ID,
                prompt_pfad=prompt,
                ausgabe_ordner=ausgabe_ordner,
            )

            if i == 1:
                intialisierung_zeit = time.perf_counter()
            i += 1

    end_zeit = time.perf_counter()
    print_time(start_zeit,end_zeit,False)
    print_time(start_zeit,intialisierung_zeit,True)