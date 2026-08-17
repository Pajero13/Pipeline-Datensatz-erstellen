from comfy import (
    test_connection,
    load_workflow,
    submit_workflow,
    wait_until_finished,
    set_image_path,
    set_text_filename,
    set_text_output_path,
    set_custom_prompt,
    print_time,
    time,
)

from config import (
    WORKFLOW_QWEN,
    PREPROCESSED_DIR,
    PROMPTS_DIR,
    QWEN_CUSTOM_PROMPT,
)

from pathlib import Path

def get_images():

    return sorted(Path(PREPROCESSED_DIR).glob("*.png"))

if __name__ == "__main__":

    start_zeit = time.perf_counter()

    print("=== Workflow Prompt generieren ===")

    test_connection()

    custom_prompt = Path(
        QWEN_CUSTOM_PROMPT
    ).read_text(
        encoding="utf-8"
    )

    i = 0
    n = len(get_images())

    for image in get_images():

        print(f"\nVerarbeite: {image.name} ({i + 1} von {n}) ")

        workflow = load_workflow(
            WORKFLOW_QWEN
        )

        workflow = set_custom_prompt(
        workflow,
        "14",
        custom_prompt
        )
        workflow = set_image_path(
            workflow,
            "17",
            str(image.resolve())
        )

        workflow = set_text_output_path(
            workflow,
            "22",
            PROMPTS_DIR
        )

        workflow = set_text_filename(
            workflow,
            "22",
            image.stem
        )

        prompt_id = submit_workflow(workflow)

        wait_until_finished(
            prompt_id
        )

        i += 1

end_zeit = time.perf_counter()
print_time(start_zeit,end_zeit,False)