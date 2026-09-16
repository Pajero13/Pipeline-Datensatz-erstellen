# comfy.py
import requests
import json
import time
import hashlib
import time
from config import COMFY_URL
from config import COMFY_URL, PROMPT_FILE

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
    

def set_image(workflow: dict, image_name: str) -> dict:

    workflow["13"]["inputs"]["image"] = image_name

    return workflow

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

def set_filename(workflow: dict, node_id: str, filename: str) -> dict:

    workflow[node_id]["inputs"]["filename_prefix"] = filename

    return workflow

def set_text_directory(
    workflow: dict,
    node_id: str,
    directory: str
) -> dict:

    workflow[node_id]["inputs"]["root_dir"] = directory

    return workflow


def set_text_filename(
    workflow: dict,
    node_id: str,
    filename: str
) -> dict:

    workflow[node_id]["inputs"]["file"] = filename

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
    from pathlib import Path

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
    from pathlib import Path

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
    from pathlib import Path

    basis_ordner = Path(basis_ordner)
    ziel = basis_ordner / batch_name if batch_name else basis_ordner
    ziel.mkdir(parents=True, exist_ok=True)
    return ziel


def print_time(start_zeit,end_zeit,initialisierung):
    dauer_sekunden = end_zeit - start_zeit
    stunden = int(dauer_sekunden // 3600)
    minuten = int((dauer_sekunden % 3600) // 60)
    sekunden = dauer_sekunden % 60
    print()
    if initialisierung:
        print(f"Davon  {stunden} Stunden, {minuten} Minuten, {sekunden:.0f} Sekunden für die Initilasierung und das erste Bild.")
    else:
        print(f"Dauer: {stunden} Stunden, {minuten} Minuten, {sekunden:.0f} Sekunden")