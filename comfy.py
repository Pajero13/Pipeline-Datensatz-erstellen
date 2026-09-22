# comfy.py
import json
import subprocess
import sys
import time
import hashlib
from datetime import datetime
from pathlib import Path

import requests

from config import COMFY_URL, PROMPT_FILE

# Verzeichnis, in dem die Einstellungs-Protokolle der Pipeline-Skripte
# gespeichert werden.
AUSGABE_DIR = Path(
    r"C:\Users\Andrin\Documents\Maturaarbeit_W11WS16\parktisches_Experiment\Datensatz\Ausgabedateien"
)


def test_connection():

    try:

        response = requests.get(f"{COMFY_URL}/system_stats")

        if response.status_code == 200:

            print("✅ Verbindung zu ComfyUI erfolgreich.")

        else:

            print("❌ ComfyUI antwortet mit:", response.status_code)

    except Exception as e:

        print("❌ Verbindung fehlgeschlagen")

        print(e)


def load_workflow(path: str) -> dict:
    with open(path, "r", encoding="utf-8") as f:
        return json.load(f)


def set_image_path(workflow: dict, node_id: str, image_path: str) -> dict:

    workflow[node_id]["inputs"]["image"] = image_path

    return workflow

def submit_workflow(workflow: dict) -> str:

    payload = {
        "prompt": workflow
    }

    response = requests.post(
        f"{COMFY_URL}/prompt",
        json=payload
    )

    if response.status_code != 200:

        print(response.text)

        response.raise_for_status()

    data = response.json()

    return data["prompt_id"]

def wait_until_finished(prompt_id: str):

    while True:

        response = requests.get(
            f"{COMFY_URL}/history/{prompt_id}"
        )

        data = response.json()

        if prompt_id in data:
            return data[prompt_id]

        time.sleep(1)

def get_prompt_text(history):

    try:

        return history["outputs"]["15"]["text"][0]

    except Exception:

        return None
    
def set_prompt(
    workflow: dict,
    node_id: str,
    prompt: str
) -> dict:

    workflow[node_id]["inputs"]["text"] = prompt

    return workflow

def set_image(workflow: dict, node_id: str, image_name: str) -> dict:

    workflow[node_id]["inputs"]["image"] = image_name

    return workflow

def set_filename(workflow: dict, node_id: str, filename: str) -> dict:

    workflow[node_id]["inputs"]["filename_prefix"] = filename

    return workflow

def set_output_path(workflow: dict, node_id: str, path: str) -> dict:

    workflow[node_id]["inputs"]["output_path"] = path

    return workflow

def set_text_directory(
    workflow: dict,
    node_id: str,
    directory: str
) -> dict:

    workflow[node_id]["inputs"]["root_dir"] = directory

    return workflow


def set_text_output_path(
    workflow: dict,
    node_id: str,
    path: str
) -> dict:

    workflow[node_id]["inputs"]["output_file_path"] = path

    return workflow

def set_text_filename(
    workflow: dict,
    node_id: str,
    filename: str
) -> dict:

    workflow[node_id]["inputs"]["file_name"] = filename

    return workflow

def set_custom_prompt(
    workflow: dict,
    node_id: str,
    custom_prompt: str
) -> dict:

    workflow[node_id]["inputs"]["custom_prompt"] = custom_prompt

    return workflow

def set_noise_seed(
    workflow: dict,
    node_id: str,
    seed: int
) -> dict:
    
    workflow[node_id]["inputs"]["noise_seed"] = seed

    return workflow

def generate_seed_from_filename(filename: str) -> int:
    hash_object = hashlib.md5(filename.encode())
    seed = int(hash_object.hexdigest(), 16) % (2**31 - 1)
    return seed

def _dateien_in_ordner(ordner, muster: list[str]) -> list:
    ordner = Path(ordner)
    dateien = []
    for m in muster:
        dateien.extend(ordner.glob(m))
    return sorted(dateien)


def get_batches(basis_ordner, muster: list[str]) -> list:
    """
    Ermittelt die zu verarbeitenden 'Batches' in einem Basisordner.

    - Liegen im Basisordner direkt passende Dateien, wird der
      Basisordner selbst als ein Batch zurückgegeben (Batch-Name "").
      Dadurch funktioniert es weiterhin ohne Unterordner.
    - Für jeden Unterordner des Basisordners, der passende Dateien
      enthält, wird ein eigener Batch mit dem Namen des Unterordners
      zurückgegeben. So können mehrere Ordner gleichzeitig in den
      Eingabeordner kopiert und einzeln verarbeitet werden.

    Rückgabe: Liste von (batch_name, ordner_pfad)-Tupeln.
    """
    basis_ordner = Path(basis_ordner)
    batches = []

    if not basis_ordner.exists():
        return batches

    if _dateien_in_ordner(basis_ordner, muster):
        batches.append(("", basis_ordner))

    for eintrag in sorted(basis_ordner.iterdir()):
        if eintrag.is_dir() and _dateien_in_ordner(eintrag, muster):
            batches.append((eintrag.name, eintrag))

    return batches


def get_batch_dateien(ordner, muster: list[str]) -> list:
    """Gibt die zu einem Batch-Ordner passenden Dateien sortiert zurück."""
    return _dateien_in_ordner(ordner, muster)


def ausgabe_ordner_fuer_batch(basis_ordner, batch_name: str):
    """
    Liefert (und erstellt bei Bedarf) den Ausgabeordner für einen Batch:
    Batch-Name "" -> Basisordner selbst; sonst Basisordner/Batch-Name.
    """
    basis_ordner = Path(basis_ordner)
    ziel = basis_ordner / batch_name if batch_name else basis_ordner
    ziel.mkdir(parents=True, exist_ok=True)
    return ziel


def format_dauer(dauer_sekunden: float) -> str:
    """Formatiert eine Sekundenanzahl als 'X Stunden, Y Minuten, Z Sekunden'."""
    stunden = int(dauer_sekunden // 3600)
    minuten = int((dauer_sekunden % 3600) // 60)
    sekunden = dauer_sekunden % 60
    return f"{stunden} Stunden, {minuten} Minuten, {sekunden:.0f} Sekunden"


def print_time(start_zeit,end_zeit,initialisierung):
    text = format_dauer(end_zeit - start_zeit)
    print()
    if initialisierung:
        print(f"Davon  {text} für die Initilasierung und das erste Bild.")
    else:
        print(f"Dauer: {text}")


_ZEITEN_DATEI = AUSGABE_DIR / "_zeiten_zwischenspeicher.json"


def erstbild_dauer_speichern(dauer_sekunden: float):
    """
    Speichert die Dauer bis zum ersten Bild zwischen (in einer
    kleinen JSON-Datei unter AUSGABE_DIR), damit das aufrufende
    pipeline_alle_workflows_*.py-Skript - ein separater Prozess - sie
    anschliessend ins JSON-Protokoll übernehmen kann.
    """
    AUSGABE_DIR.mkdir(parents=True, exist_ok=True)
    _ZEITEN_DATEI.write_text(
        json.dumps({"dauer_erstes_bild_sekunden": dauer_sekunden}),
        encoding="utf-8",
    )


def erstbild_dauer_laden():
    """
    Liest die von erstbild_dauer_speichern() hinterlegte Dauer bis
    zum ersten Bild (formatiert wie format_dauer()) und löscht die
    Zwischendatei danach wieder. Gibt None zurück, falls keine
    Zwischendatei vorhanden ist.
    """
    if not _ZEITEN_DATEI.exists():
        return None
    daten = json.loads(_ZEITEN_DATEI.read_text(encoding="utf-8"))
    _ZEITEN_DATEI.unlink()
    return format_dauer(daten["dauer_erstes_bild_sekunden"])


def bild_fuer_prompt_generieren(
    workflow_pfad: str,
    save_node_id: str,
    prompt_pfad,
    ausgabe_ordner,
    prompt_node_id: str = "6",
    seed_node_id: str = "25",
):
    """
    Erzeugt genau ein Bild für eine Prompt-Datei: lädt den Workflow,
    setzt Prompt-Text, Output-Pfad, einen aus dem Dateinamen
    abgeleiteten Seed und den Dateinamen, sendet den Workflow an
    ComfyUI und wartet auf Fertigstellung.

    Deckt den Block ab, der bisher in jeder
    workflow_bild_generieren_*.py-Datei innerhalb der Schleife
    wortwörtlich identisch stand (nur Workflow-Pfad und Save-Node-ID
    unterschieden sich). Die Schleife selbst, Fortschrittsausgaben und
    Zeitmessung bleiben bewusst in den jeweiligen Dateien.
    """
    workflow = load_workflow(workflow_pfad)

    prompt_text = prompt_pfad.read_text(encoding="utf-8")

    workflow = set_prompt(workflow, prompt_node_id, prompt_text)

    workflow = set_output_path(workflow, save_node_id, str(ausgabe_ordner))

    seed = generate_seed_from_filename(prompt_pfad.name)

    workflow = set_noise_seed(workflow, seed_node_id, seed)

    workflow = set_filename(workflow, save_node_id, prompt_pfad.stem)

    prompt_id = submit_workflow(workflow)

    wait_until_finished(prompt_id)


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


def workflow_ausfuehren(script_name: str):
    print(f"\n>>> Starte {script_name} ...\n")
    ergebnis = subprocess.run([sys.executable, script_name])
    if ergebnis.returncode != 0:
        raise RuntimeError(
            f"{script_name} wurde mit Fehlercode {ergebnis.returncode} beendet."
        )


def protokoll_speichern(protokoll: dict, name, modell_praefix: str = "einstellungen") -> Path:
    """
    Speichert das Protokoll-dict als JSON unter AUSGABE_DIR.
    Dateiname: <name>.json falls angegeben, sonst
    <modell_praefix>_<Zeitstempel>.json.
    """
    AUSGABE_DIR.mkdir(parents=True, exist_ok=True)

    if name:
        dateiname = name if name.lower().endswith(".json") else f"{name}.json"
    else:
        zeitstempel = datetime.now().strftime("%Y-%m-%d_%H-%M-%S")
        dateiname = f"{modell_praefix}_{zeitstempel}.json"

    pfad = AUSGABE_DIR / dateiname
    pfad.write_text(json.dumps(protokoll, indent=2, ensure_ascii=False), encoding="utf-8")
    return pfad
