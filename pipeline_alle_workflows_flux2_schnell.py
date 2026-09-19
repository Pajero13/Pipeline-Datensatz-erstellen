# pipeline_alle_workflows_flux2_schnell.py
#
# Wie pipeline_alle_workflows.py, aber der dritte Schritt (Bild
# generieren) nutzt das flux2-schnell-Modell und speichert die
# Ergebnisse unter OUTPUT_DIR_FLUX2_SCHNELL.
#
# Name der Protokoll-Datei:
#   - ohne Angabe: Zeitstempel
#   - mit "--name <bezeichnung>": <bezeichnung>.json
#
# Beispiel: python pipeline_alle_workflows_flux2_schnell.py --name testlauf_schnell_1

import argparse
import json
import subprocess
import sys
from datetime import datetime
from pathlib import Path

from comfy import load_workflow, get_batches, get_batch_dateien
from config import (
    WORKFLOW_BILD_SKALIEREN,
    WORKFLOW_QWEN,
    WORKFLOW_FLUX2_SCHNELL,
    INPUT_DIR,
    PREPROCESSED_DIR,
    PROMPTS_DIR,
)

AUSGABE_DIR = Path(
    r"C:\Users\Andrin\Documents\Maturaarbeit_W11WS16\parktisches_Experiment\Datensatz\Ausgabedateien"
)

NODES_SKALIEREN = {
    "resize_mod": ("2", "resize_mode"),
    "output_mode": ("2", "output_mode"),
}

NODES_QWEN = {
    "modellname": ("14", "model_name"),
}

NODES_FLUX2_SCHNELL = {
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
        description="Führt die komplette Bild-Pipeline mit flux2-schnell aus."
    )
    parser.add_argument(
        "--name",
        default=None,
        help="Optionaler Name für die Protokoll-Datei (ohne Endung). "
        "Ohne Angabe wird ein Zeitstempel verwendet.",
    )
    return parser.parse_args()


def hole_einstellung(workflow: dict, node_id: str, feld: str):
    try:
        return workflow[node_id]["inputs"][feld]
    except KeyError:
        return f"nicht gefunden (Node {node_id} / Feld '{feld}')"


def einstellungen_auslesen(workflow: dict, node_map: dict) -> dict:
    return {
        label: hole_einstellung(workflow, node_id, feld)
        for label, (node_id, feld) in node_map.items()
    }


def block_formatieren(titel: str, einstellungen: dict) -> str:
    zeilen = [f"--- {titel} ---"]
    for label, wert in einstellungen.items():
        zeilen.append(f"{label}: {wert}")
    return "\n".join(zeilen)


def batches_erfassen(basis_ordner, muster: list) -> dict:
    batches = get_batches(basis_ordner, muster)
    eintraege = [
        {
            "ordner": batch_name if batch_name else None,
            "anzahl_dateien": len(get_batch_dateien(batch_ordner, muster)),
        }
        for batch_name, batch_ordner in batches
    ]
    return {"basis_ordner": str(basis_ordner), "batches": eintraege}


def batches_als_text(batch_info: dict) -> str:
    zeilen = [f"Ordner: {batch_info['basis_ordner']}"]
    if not batch_info["batches"]:
        zeilen.append("  Keine passenden Dateien gefunden.")
    for eintrag in batch_info["batches"]:
        bezeichnung = eintrag["ordner"] if eintrag["ordner"] else "(kein Unterordner)"
        zeilen.append(f"  {bezeichnung}: {eintrag['anzahl_dateien']} Datei(en)")
    return "\n".join(zeilen)


def workflow_ausfuehren(script_name: str):
    print(f"\n>>> Starte {script_name} ...\n")
    ergebnis = subprocess.run([sys.executable, script_name])
    if ergebnis.returncode != 0:
        raise RuntimeError(
            f"{script_name} wurde mit Fehlercode {ergebnis.returncode} beendet."
        )


def dateiname_bestimmen(name) -> str:
    if not name:
        zeitstempel = datetime.now().strftime("%Y-%m-%d_%H-%M-%S")
        return f"einstellungen_flux2_schnell_{zeitstempel}.json"
    return name if name.lower().endswith(".json") else f"{name}.json"


def protokoll_speichern(protokoll: dict, name) -> Path:
    AUSGABE_DIR.mkdir(parents=True, exist_ok=True)
    pfad = AUSGABE_DIR / dateiname_bestimmen(name)
    pfad.write_text(json.dumps(protokoll, indent=2, ensure_ascii=False), encoding="utf-8")
    return pfad


if __name__ == "__main__":

    args = parse_args()

    protokoll = {
        "modell": "flux2-schnell",
        "start": datetime.now().isoformat(timespec="seconds"),
        "ende": None,
        "workflows": [],
    }

    # --- 1. Bild skalieren ---
    workflow = load_workflow(WORKFLOW_BILD_SKALIEREN)
    einstellungen = einstellungen_auslesen(workflow, NODES_SKALIEREN)
    batch_info = batches_erfassen(INPUT_DIR, BILD_MUSTER)
    print(block_formatieren("Workflow: Bild skalieren", einstellungen))
    print("--- Batches (input) ---")
    print(batches_als_text(batch_info))
    protokoll["workflows"].append({
        "workflow": "Bild skalieren",
        "einstellungen": einstellungen,
        "batches": batch_info,
    })

    workflow_ausfuehren("workflow_bild_skalieren.py")

    # --- 2. Prompt generieren ---
    workflow = load_workflow(WORKFLOW_QWEN)
    einstellungen = einstellungen_auslesen(workflow, NODES_QWEN)
    batch_info = batches_erfassen(PREPROCESSED_DIR, PNG_MUSTER)
    print(block_formatieren("Workflow: Prompt generieren", einstellungen))
    print("--- Batches (preprocessed) ---")
    print(batches_als_text(batch_info))
    protokoll["workflows"].append({
        "workflow": "Prompt generieren",
        "einstellungen": einstellungen,
        "batches": batch_info,
    })

    workflow_ausfuehren("workflow_prompt_generieren.py")

    # --- 3. Bild generieren (flux2-schnell) ---
    workflow = load_workflow(WORKFLOW_FLUX2_SCHNELL)
    einstellungen = einstellungen_auslesen(workflow, NODES_FLUX2_SCHNELL)
    batch_info = batches_erfassen(PROMPTS_DIR, TXT_MUSTER)
    print(block_formatieren("Workflow: Bild generieren (flux2-schnell)", einstellungen))
    print("--- Batches (prompts) ---")
    print(batches_als_text(batch_info))
    protokoll["workflows"].append({
        "workflow": "Bild generieren (flux2-schnell)",
        "einstellungen": einstellungen,
        "batches": batch_info,
    })

    workflow_ausfuehren("workflow_bild_generieren_flux2_schnell.py")

    protokoll["ende"] = datetime.now().isoformat(timespec="seconds")

    pfad = protokoll_speichern(protokoll, args.name)
    print(f"\nProtokoll gespeichert unter: {pfad}")

    print("\n=== Gesamte Pipeline (flux2-schnell) abgeschlossen ===")
