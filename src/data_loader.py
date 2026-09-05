import json

import numpy as np
import pandas as pd
from PIL import Image

from src.config import IMG_SIZE, PROCESSED_DIR, RAW_DIR


def load_class_map() -> dict:
    class_map_path = PROCESSED_DIR / "class_map.json"
    with open(class_map_path, "r", encoding="utf-8") as f:
        return json.load(f)


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
