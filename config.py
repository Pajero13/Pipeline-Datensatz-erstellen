# config.py

COMFY_URL = "http://127.0.0.1:8188"

WORKFLOW_BILD_SKALIEREN = "workflows/workflow_bild_skalieren.json"

WORKFLOW_QWEN = "workflows/qwen_prompt.json"

WORKFLOW_FLUX = "workflows/flux1_generate_image.json"

WORKFLOW_FLUX2_SCHNELL = "workflows/flux2_schnell_generate_image.json"

WORKFLOW_FLUX2_KLEIN = "workflows/flux2_klein_generate_image.json"

TEMP_DIR = "temp"

INPUT_DIR = "input"

PROMPTS_DIR = r"C:\Users\Andrin\Documents\Maturaarbeit_W11WS16\parktisches_Experiment\Datensatz\Daten\Pipeline-Datensatz-erstellen\prompts"

PREPROCESSED_DIR = r"C:\Users\Andrin\Documents\Maturaarbeit_W11WS16\parktisches_Experiment\Datensatz\Daten\Pipeline-Datensatz-erstellen\preprocessed"

QWEN_CUSTOM_PROMPT = r"C:\Users\Andrin\Documents\Maturaarbeit_W11WS16\parktisches_Experiment\Datensatz\Daten\Pipeline-Datensatz-erstellen\config\qwen_custom_prompt.txt"

OUTPUT_DIR = r"C:\Users\Andrin\Documents\Maturaarbeit_W11WS16\parktisches_Experiment\Datensatz\Daten\Pipeline-Datensatz-erstellen\output"

# Eigene Unterordner innerhalb von OUTPUT_DIR, damit sich flux1,
# flux2-schnell und flux2-klein nicht gegenseitig überschreiben
# (gleiche Prompt-Dateinamen).
OUTPUT_DIR_FLUX1 = OUTPUT_DIR + r"\flux1"

OUTPUT_DIR_FLUX2_SCHNELL = OUTPUT_DIR + r"\flux2_schnell"

OUTPUT_DIR_FLUX2_KLEIN = OUTPUT_DIR + r"\flux2_klein"

LOG_DIR = "logs"

PROMPT_FILE = r"C:\Users\Andrin\Documents\Pinokio\api\comfy.git\app\output\prompt.txt"