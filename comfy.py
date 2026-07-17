import requests

from config import COMFY_URL


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