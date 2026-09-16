# ordner_leeren.py
#
# Leert die vier Arbeitsordner der Pipeline (löscht deren gesamten
# Inhalt inkl. Unterordnern/Batches), die Ordner selbst bleiben
# bestehen:
#   - input
#   - preprocessed
#   - prompts
#   - output
#
# Fragt vor dem Löschen zur Sicherheit nach Bestätigung. Mit dem
# Flag --yes (oder -y) wird ohne Rückfrage sofort gelöscht, z.B.
# für den Einsatz in einem automatisierten Ablauf:
#   python ordner_leeren.py --yes

import shutil
import sys
from pathlib import Path

from config import (
    INPUT_DIR,
    PREPROCESSED_DIR,
    PROMPTS_DIR,
    OUTPUT_DIR,
)

ORDNER = {
    "input": Path(INPUT_DIR),
    "preprocessed": Path(PREPROCESSED_DIR),
    "prompts": Path(PROMPTS_DIR),
    "output": Path(OUTPUT_DIR),
}


def anzahl_eintraege(ordner: Path) -> int:
    if not ordner.exists():
        return 0
    return sum(1 for _ in ordner.iterdir())


def ordner_leeren(ordner: Path):
    if not ordner.exists():
        print(f"  {ordner} existiert nicht, wird übersprungen.")
        return

    for eintrag in ordner.iterdir():
        if eintrag.is_dir():
            shutil.rmtree(eintrag)
        else:
            eintrag.unlink()


if __name__ == "__main__":

    bestaetigt = "--yes" in sys.argv or "-y" in sys.argv

    print("Folgende Ordner werden komplett geleert (der Ordner selbst bleibt bestehen):\n")
    for name, pfad in ORDNER.items():
        print(f"  {name}: {pfad}  ({anzahl_eintraege(pfad)} Einträge)")

    if not bestaetigt:
        antwort = input(
            "\nWirklich ALLE Inhalte dieser Ordner unwiderruflich löschen? (ja/nein): "
        )
        bestaetigt = antwort.strip().lower() in ("ja", "j", "yes", "y")

    if not bestaetigt:
        print("Abgebrochen, es wurde nichts gelöscht.")
        sys.exit(0)

    for name, pfad in ORDNER.items():
        print(f"\nLeere {name} ({pfad}) ...")
        ordner_leeren(pfad)

    print("\n=== Alle Ordner geleert ===")
