# pipeline_alle_workflows_flux2_klein.py
#
# Wie pipeline_alle_workflows_flux1.py, aber der dritte Schritt
# nutzt das flux2-klein-Modell (workflow_bild_generieren_flux2_klein.py,
# Ergebnisse unter OUTPUT_DIR_FLUX2_KLEIN).
#
# Beispiel: python pipeline_alle_workflows_flux2_klein.py --name testlauf_klein_1

import argparse
from datetime import datetime

from comfy import (
    load_workflow,
    einstellungen_auslesen,
    batches_erfassen,
    workflow_ausfuehren,
    protokoll_speichern,
)
from config import (
    WORKFLOW_BILD_SKALIEREN,
    WORKFLOW_QWEN,
    WORKFLOW_FLUX2_KLEIN,
    INPUT_DIR,
    PREPROCESSED_DIR,
    PROMPTS_DIR,
)

NODES_SKALIEREN = {
    "resize_mod": ("2", "resize_mode"),
    "output_mode": ("2", "output_mode"),
}

NODES_QWEN = {
    "modellname": ("14", "model_name"),
}

# Hinweis: flux2-klein hat kein eigenes "scheduler"-Feld (der
# Flux2Scheduler-Node kennt nur steps/width/height), daher wird hier
# kein Scheduler protokolliert.
NODES_FLUX2_KLEIN = {
    "modellname": ("68", "unet_name"),
    "sample_steps": ("48", "steps"),
    "breite": ("47", "width"),
    "hoehe": ("47", "height"),
    "sampler_name": ("16", "sampler_name"),
}

BILD_MUSTER = ["*.jpg", "*.jpeg"]
PNG_MUSTER = ["*.png"]
TXT_MUSTER = ["*.txt"]


def parse_args():
    parser = argparse.ArgumentParser(
        description="Führt die komplette Bild-Pipeline mit flux2-klein aus."
    )
    parser.add_argument(
        "--name",
        default=None,
        help="Optionaler Name für die Protokoll-Datei (ohne Endung). "
        "Ohne Angabe wird ein Zeitstempel verwendet.",
    )
    return parser.parse_args()


if __name__ == "__main__":

    args = parse_args()

    protokoll = {
        "modell": "flux2-klein",
        "start": datetime.now().isoformat(timespec="seconds"),
        "ende": None,
        "workflows": [],
    }

    # --- 1. Bild skalieren ---
    workflow = load_workflow(WORKFLOW_BILD_SKALIEREN)
    protokoll["workflows"].append({
        "workflow": "Bild skalieren",
        "einstellungen": einstellungen_auslesen(workflow, NODES_SKALIEREN),
        "batches": batches_erfassen(INPUT_DIR, BILD_MUSTER),
    })

    workflow_ausfuehren("workflow_bild_skalieren.py")

    # --- 2. Prompt generieren ---
    workflow = load_workflow(WORKFLOW_QWEN)
    protokoll["workflows"].append({
        "workflow": "Prompt generieren",
        "einstellungen": einstellungen_auslesen(workflow, NODES_QWEN),
        "batches": batches_erfassen(PREPROCESSED_DIR, PNG_MUSTER),
    })

    workflow_ausfuehren("workflow_prompt_generieren.py")

    # --- 3. Bild generieren (flux2-klein) ---
    workflow = load_workflow(WORKFLOW_FLUX2_KLEIN)
    protokoll["workflows"].append({
        "workflow": "Bild generieren (flux2-klein)",
        "einstellungen": einstellungen_auslesen(workflow, NODES_FLUX2_KLEIN),
        "batches": batches_erfassen(PROMPTS_DIR, TXT_MUSTER),
    })

    workflow_ausfuehren("workflow_bild_generieren_flux2_klein.py")

    protokoll["ende"] = datetime.now().isoformat(timespec="seconds")

    pfad = protokoll_speichern(protokoll, args.name, modell_praefix="einstellungen_flux2_klein")
    print(f"\nProtokoll gespeichert unter: {pfad}")

    print("\n=== Gesamte Pipeline (flux2-klein) abgeschlossen ===")
