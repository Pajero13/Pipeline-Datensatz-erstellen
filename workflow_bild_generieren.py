from comfy import (
    test_connection,
    load_workflow,
    set_prompt,
    set_filename,
    submit_workflow,
    wait_until_finished,
    set_output_path,
    set_noise_seed,
    generate_seed_from_filename,
)

from config import (
    WORKFLOW_FLUX,
    PROMPTS_DIR,
    OUTPUT_DIR,
)

from pathlib import Path

def get_prompts():

    return sorted(Path(PROMPTS_DIR).glob("*.txt"))

if __name__ == "__main__":

    print("=== Workflow Bild generieren ===")

    test_connection()

    i = 0
    n = len(get_prompts())

    for prompt in get_prompts():

        print(f"\nVerarbeite: {prompt.name} ({i + 1} von {n}) ")

        workflow = load_workflow(
            WORKFLOW_FLUX
        )

        prompt_text = prompt.read_text(
            encoding="utf-8"
        )

        workflow = set_prompt(
            workflow,
            "6",
            prompt_text
        )

        workflow = set_output_path(
            workflow,
            "26",
            OUTPUT_DIR
        )
        
        seed = generate_seed_from_filename(prompt.name)
        
        workflow = set_noise_seed(
            workflow, 
            "25", 
            seed
        )

        workflow = set_filename(
            workflow,
            "26",
            prompt.stem
        )

        prompt_id = submit_workflow(
            workflow
        )

        wait_until_finished(
            prompt_id
        )

        i += 1

    print("✓ Fertig")