# pipeline_alle_workflows_flux1.py
#
# Führt die drei Workflows der Pipeline mit dem flux1-Modell (dev)
# automatisch nacheinander aus:
#   1. workflow_bild_skalieren.py
#   2. workflow_prompt_generieren.py
#   3. workflow_bild_generieren_flux1.py
#
# Vor jedem Schritt werden die relevanten Node-Einstellungen sowie
# die gefundenen Batches (Unterordner) erfasst und am Ende der
# Pipeline gesammelt als JSON-Protokoll gespeichert (siehe
# comfy.AUSGABE_DIR).
#
# Name der Protokoll-Datei:
#   - ohne Angabe: Zeitstempel
#   - mit "--name <bezeichnung>": <bezeichnung>.json
#
# Beispiel: python pipeline_alle_workflows_flux1.py --name testlauf_1
#
# WICHTIG: Die einzelnen Workflows werden als separate Prozesse
# gestartet (subprocess), genau so, wie du sie bisher einzeln mit
# "python workflow_....py" gestartet hast.

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
    WORKFLOW_FLUX,
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

NODES_FLUX1 = {
    "modellname": ("12", "unet_name"),
    "sample_steps": ("17", "steps"),
    "breite": ("5", "width"),
    "hoehe": ("5", "height"),
    "scheduler": ("17", "scheduler"),
    "sampler_name": ("16", "sampler_name"),
}

BILD_MUSTER = ["*.jpg", "*.jpeg"]
PNG_MUSTER = ["*.png"]
TXT_MUSTER = ["*.txt"]


def parse_args():
    parser = argparse.ArgumentParser(
        description="Führt die komplette Bild-Pipeline mit flux1 (dev) aus."
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
        "modell": "flux1",
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

    # --- 3. Bild generieren (flux1) ---
    workflow = load_workflow(WORKFLOW_FLUX)
    protokoll["workflows"].append({
        "workflow": "Bild generieren (flux1)",
        "einstellungen": einstellungen_auslesen(workflow, NODES_FLUX1),
        "batches": batches_erfassen(PROMPTS_DIR, TXT_MUSTER),
    })

    workflow_ausfuehren("workflow_bild_generieren_flux1.py")

    protokoll["ende"] = datetime.now().isoformat(timespec="seconds")

    pfad = protokoll_speichern(protokoll, args.name, modell_praefix="einstellungen_flux1")
    print(f"\nProtokoll gespeichert unter: {pfad}")

    print("\n=== Gesamte Pipeline (flux1) abgeschlossen ===")
