import json

import numpy as np
import pandas as pd
from PIL import Image

from src.config import IMG_SIZE, PROCESSED_DIR, RAW_DIR


def load_class_map() -> dict:
    class_map_path = PROCESSED_DIR / "class_map.json"
    with open(class_map_path, "r", encoding="utf-8") as f:
        return json.load(f)


def dataset_disponible() -> bool:
    """True si existen las imagenes crudas de PlantVillage en RAW_DIR.

    Los CSV de `data/processed/` estan versionados, pero las imagenes no (ver
    .gitignore). Las semanas que entrenan o evaluan sobre las imagenes
    necesitan esta carpeta; las que solo usan el modelo guardado, no.
    """
    if not RAW_DIR.exists():
        return False
    return any(carpeta.is_dir() for carpeta in RAW_DIR.iterdir())


def aviso_dataset_ausente() -> str:
    """Mensaje accionable para cuando falta el dataset crudo."""
    return (
        "\n[FALTA EL DATASET] No se encontraron las imagenes crudas de\n"
        f"  PlantVillage en: {RAW_DIR}\n"
        "  Descarga el dataset y descomprimelo en data/raw/PlantVillage-Dataset/\n"
        "  de modo que las 38 carpetas de clases queden en raw/color/.\n"
        "  (Los CSV de data/processed/ ya estan, pero sin las imagenes no se\n"
        "  puede entrenar ni evaluar sobre el dataset.)\n"
    )


def load_split(csv_name: str) -> pd.DataFrame:
    csv_path = PROCESSED_DIR / csv_name
    return pd.read_csv(csv_path)


def load_images(df: pd.DataFrame, img_size: int = IMG_SIZE) -> np.ndarray:
    images = []
    errors = 0
    total = len(df)

    for idx, row in df.iterrows():
        img_path = RAW_DIR / row["filepath"]

        try:
            img = Image.open(img_path)
            img = img.convert("RGB")
            img = img.resize((img_size, img_size))
            img_array = np.array(img, dtype=np.float32) / 255.0
            images.append(img_array.flatten())
        except Exception as e:
            errors += 1
            if errors <= 5:
                print(f"  Error cargando {img_path}: {e}")

        if (idx + 1) % 5000 == 0 or (idx + 1) == total:
            print(f"  Imagenes cargadas: {idx + 1}/{total}")

    if errors > 0:
        print(f"  Total errores: {errors}/{total}")

    return np.array(images)


def preprocess_single_image(image_path: str, img_size: int = IMG_SIZE) -> np.ndarray:
    img = Image.open(image_path).convert("RGB")
    img = img.resize((img_size, img_size))
    img_array = np.array(img, dtype=np.float32) / 255.0
    return img_array.flatten()
