from pathlib import Path
from PIL import Image, ImageOps

from config import TEMP_DIR


def normalize_image(image_path: Path) -> Path:

    temp_dir = Path(TEMP_DIR)
    temp_dir.mkdir(exist_ok=True)

    output_path = temp_dir / f"{image_path.stem}.png"

    with Image.open(image_path) as image:

        image = ImageOps.exif_transpose(image)

        image.save(output_path)

    return output_path