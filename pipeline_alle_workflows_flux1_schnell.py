# pipeline_alle_workflows_flux1_schnell.py
#
# Wie pipeline_alle_workflows_flux1.py, aber der dritte Schritt
# nutzt das flux1-schnell-Modell (workflow_bild_generieren_flux1_schnell.py,
# Ergebnisse unter OUTPUT_DIR_FLUX1_SCHNELL).
#
# Beispiel: python pipeline_alle_workflows_flux1_schnell.py --name testlauf_schnell_1

import argparse
import time
from datetime import datetime

from comfy import (
    load_workflow,
    einstellungen_auslesen,
    batches_erfassen,
    workflow_ausfuehren,
    protokoll_speichern,
    format_dauer,
    erstbild_dauer_laden,
)
from config import (
    WORKFLOW_BILD_SKALIEREN,
    WORKFLOW_QWEN,
    WORKFLOW_FLUX1_SCHNELL,
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

NODES_FLUX1_SCHNELL = {
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
        description="Führt die komplette Bild-Pipeline mit flux1-schnell aus."
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

    pipeline_start = time.perf_counter()

    protokoll = {
        "modell": "flux1-schnell",
        "start": datetime.now().isoformat(timespec="seconds"),
        "ende": None,
        "gesamtdauer": None,
        "workflows": [],
    }

    # --- 1. Bild skalieren ---
    workflow = load_workflow(WORKFLOW_BILD_SKALIEREN)
    eintrag = {
        "workflow": "Bild skalieren",
        "einstellungen": einstellungen_auslesen(workflow, NODES_SKALIEREN),
        "batches": batches_erfassen(INPUT_DIR, BILD_MUSTER),
    }

    schritt_start = time.perf_counter()
    workflow_ausfuehren("workflow_bild_skalieren.py")
    eintrag["dauer"] = format_dauer(time.perf_counter() - schritt_start)

    protokoll["workflows"].append(eintrag)

    # --- 2. Prompt generieren ---
    workflow = load_workflow(WORKFLOW_QWEN)
    eintrag = {
        "workflow": "Prompt generieren",
        "einstellungen": einstellungen_auslesen(workflow, NODES_QWEN),
        "batches": batches_erfassen(PREPROCESSED_DIR, PNG_MUSTER),
    }

    schritt_start = time.perf_counter()
    workflow_ausfuehren("workflow_prompt_generieren.py")
    eintrag["dauer"] = format_dauer(time.perf_counter() - schritt_start)

    protokoll["workflows"].append(eintrag)

    # --- 3. Bild generieren (flux1-schnell) ---
    workflow = load_workflow(WORKFLOW_FLUX1_SCHNELL)
    eintrag = {
        "workflow": "Bild generieren (flux1-schnell)",
        "einstellungen": einstellungen_auslesen(workflow, NODES_FLUX1_SCHNELL),
        "batches": batches_erfassen(PROMPTS_DIR, TXT_MUSTER),
    }

    schritt_start = time.perf_counter()
    workflow_ausfuehren("workflow_bild_generieren_flux1_schnell.py")
    eintrag["dauer"] = format_dauer(time.perf_counter() - schritt_start)
    eintrag["dauer_erstes_bild"] = erstbild_dauer_laden()

    protokoll["workflows"].append(eintrag)

    protokoll["ende"] = datetime.now().isoformat(timespec="seconds")
    protokoll["gesamtdauer"] = format_dauer(time.perf_counter() - pipeline_start)

    pfad = protokoll_speichern(protokoll, args.name, modell_praefix="einstellungen_flux1_schnell")
    print(f"\nProtokoll gespeichert unter: {pfad}")

    print("\n=== Gesamte Pipeline (flux1-schnell) abgeschlossen ===")
