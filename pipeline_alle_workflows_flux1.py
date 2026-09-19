# pipeline_alle_workflows.py
#
# Führt die drei Workflows der Pipeline automatisch nacheinander aus:
#   1. workflow_bild_skalieren.py
#   2. workflow_prompt_generieren.py
#   3. workflow_bild_generieren.py
#
# Vor jedem Workflow werden die relevanten Einstellungen sowie die
# gefundenen Batches (Unterordner) aus der zugehörigen Workflow-JSON
# bzw. den Eingabeordnern ausgelesen, ausgegeben und am Ende der
# Pipeline gesammelt als JSON-Protokoll gespeichert unter:
#   C:\Users\Andrin\Documents\Maturaarbeit_W11WS16\parktisches_Experiment\Datensatz\Ausgabedateien
#
# Name der Protokoll-Datei:
#   - ohne Angabe: Zeitstempel, z.B. einstellungen_2026-09-15_14-30-00.json
#   - mit "--name <bezeichnung>": <bezeichnung>.json
#
# Beispiel: python pipeline_alle_workflows.py --name testlauf_1
#
# WICHTIG: Die einzelnen Workflows werden als separate Prozesse
# gestartet (subprocess), genau so, wie du sie bisher einzeln mit
# "python workflow_....py" gestartet hast. Es wird nichts an den
# bestehenden Dateien verändert.

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
    WORKFLOW_FLUX,
    INPUT_DIR,
    PREPROCESSED_DIR,
    PROMPTS_DIR,
)

# Verzeichnis, in dem die Einstellungs-Protokolle gespeichert werden
AUSGABE_DIR = Path(
    r"C:\Users\Andrin\Documents\Maturaarbeit_W11WS16\parktisches_Experiment\Datensatz\Ausgabedateien"
)

# Node-IDs der Einstellungen, die pro Workflow protokolliert werden.

NODES_SKALIEREN = {
    "resize_mod": ("2", "resize_mode"),
    "output_mode": ("2", "output_mode"),
}

NODES_QWEN = {
    "modellname": ("14", "model_name"),
}

NODES_FLUX = {
    "modellname": ("12", "unet_name"),
    "sample_steps": ("17", "steps"),
    "breite": ("5", "width"),
    "hoehe": ("5", "height"),
    "scheduler": ("17", "scheduler"),
    "sampler_name": ("16", "sampler_name"),
}

# Datei-Muster, mit denen die Batch-Ordner (Unterordner in input/
# preprocessed/prompts) je Workflow-Stufe erkannt werden.
BILD_MUSTER = ["*.jpg", "*.jpeg"]
PNG_MUSTER = ["*.png"]
TXT_MUSTER = ["*.txt"]


def parse_args():
    parser = argparse.ArgumentParser(
        description="Führt die komplette Bild-Pipeline (skalieren, Prompt "
        "generieren, Bild generieren) nacheinander aus."
    )
    parser.add_argument(
        "--name",
        default=None,
        help="Optionaler Name für die Protokoll-Datei (ohne Endung, .json "
        "wird automatisch angehängt). Ohne Angabe wird ein Zeitstempel "
        "verwendet.",
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
    return {
        "basis_ordner": str(basis_ordner),
        "batches": eintraege,
    }


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


def dateiname_bestimmen(name: str | None) -> str:
    if not name:
        zeitstempel = datetime.now().strftime("%Y-%m-%d_%H-%M-%S")
        return f"einstellungen_{zeitstempel}.json"
    return name if name.lower().endswith(".json") else f"{name}.json"


def protokoll_speichern(protokoll: dict, name: str | None) -> Path:
    AUSGABE_DIR.mkdir(parents=True, exist_ok=True)
    pfad = AUSGABE_DIR / dateiname_bestimmen(name)
    pfad.write_text(
        json.dumps(protokoll, indent=2, ensure_ascii=False),
        encoding="utf-8",
    )
    return pfad


if __name__ == "__main__":

    args = parse_args()

    protokoll = {
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

    # --- 3. Bild generieren ---
    workflow = load_workflow(WORKFLOW_FLUX)
    einstellungen = einstellungen_auslesen(workflow, NODES_FLUX)
    batch_info = batches_erfassen(PROMPTS_DIR, TXT_MUSTER)
    print(block_formatieren("Workflow: Bild generieren", einstellungen))
    print("--- Batches (prompts) ---")
    print(batches_als_text(batch_info))
    protokoll["workflows"].append({
        "workflow": "Bild generieren",
        "einstellungen": einstellungen,
        "batches": batch_info,
    })

    workflow_ausfuehren("workflow_bild_generieren_flux1.py")

    protokoll["ende"] = datetime.now().isoformat(timespec="seconds")

    pfad = protokoll_speichern(protokoll, args.name)
    print(f"\nProtokoll gespeichert unter: {pfad}")

    print("\n=== Gesamte Pipeline abgeschlossen ===")
