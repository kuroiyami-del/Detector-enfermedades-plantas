"""
Semana 02 - Entrenamiento basico para deteccion de enfermedades en plantas.

Adapta los conceptos del ejemplo del profesor (Iris + LogisticRegression)
a un dataset de imagenes de plantas.

Las imagenes se cargan desde los CSV ya separados en data/processed/,
se redimensionan a un tamano fijo y se aplanan en vectores de特征
para poder aplicar un modelo de regresion logistica con StandardScaler.
"""

import json
import time
from pathlib import Path

import numpy as np
import pandas as pd
from PIL import Image
from sklearn.linear_model import LogisticRegression
from sklearn.metrics import accuracy_score, confusion_matrix
from sklearn.pipeline import make_pipeline
from sklearn.preprocessing import StandardScaler

ROOT = Path(__file__).resolve().parent.parent
DATA_DIR = ROOT / "data"
RAW_DIR = DATA_DIR / "raw" / "PlantVillage-Dataset" / "raw" / "color"
PROCESSED_DIR = DATA_DIR / "processed"

RANDOM_STATE = 42
IMG_SIZE = 64  # Las imagenes se redimensionan a 64x64 pixels


def load_class_map() -> dict:
    """Carga el mapa de clases desde class_map.json."""
    class_map_path = PROCESSED_DIR / "class_map.json"
    with open(class_map_path, "r", encoding="utf-8") as f:
        return json.load(f)


def load_split(csv_name: str) -> pd.DataFrame:
    """Carga un CSV de split (train, test o val)."""
    csv_path = PROCESSED_DIR / csv_name
    return pd.read_csv(csv_path)


def load_images(df: pd.DataFrame, img_size: int = IMG_SIZE) -> np.ndarray:
    """
    Carga las imagenes listadas en el DataFrame, las redimensiona
    y las aplana en vectores unidimensionales.

    Cada imagen pasa de (img_size, img_size, 3) a un vector de
    tamano img_size * img_size * 3.
    """
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


def main():
    print("=" * 70)
    print("SEMANA 02 - ENTRENAMIENTO: Enfermedades en Plantas")
    print("=" * 70)

    class_map = load_class_map()
    num_classes = len(class_map)
    print(f"\nClases detectadas: {num_classes}")
    print(f"Tamano de imagen: {IMG_SIZE}x{IMG_SIZE}x3 = {IMG_SIZE * IMG_SIZE * 3} features")

    # --- Cargar datos de entrenamiento ---
    print("\n--- Cargando conjunto de ENTRENAMIENTO ---")
    train_df = load_split("train.csv")
    print(f"Muestras en train.csv: {len(train_df)}")

    # Contar muestras por clase en entrenamiento
    train_counts = train_df["class_name"].value_counts()
    print("Distribucion de clases (entrenamiento, top 10):")
    for class_name, count in train_counts.head(10).items():
        print(f"  {class_name}: {count}")
    print(f"  ... y {len(train_counts) - 10} clases mas" if len(train_counts) > 10 else "")

    print("\nCargando imagenes de entrenamiento...")
    t0 = time.time()
    X_train = load_images(train_df)
    y_train = train_df["label"].values
    print(f"Tiempo de carga: {time.time() - t0:.1f}s")

    # --- Cargar datos de prueba ---
    print("\n--- Cargando conjunto de PRUEBA ---")
    test_df = load_split("test.csv")
    print(f"Muestras en test.csv: {len(test_df)}")

    test_counts = test_df["class_name"].value_counts()
    print("Distribucion de clases (prueba, top 10):")
    for class_name, count in test_counts.head(10).items():
        print(f"  {class_name}: {count}")

    print("\nCargando imagenes de prueba...")
    t0 = time.time()
    X_test = load_images(test_df)
    y_test = test_df["label"].values
    print(f"Tiempo de carga: {time.time() - t0:.1f}s")

    # --- Resumen de la separacion ---
    print("\n--- Resumen de la separacion ---")
    print(f"Muestras de entrenamiento: {len(X_train)}")
    print(f"Muestras de prueba: {len(X_test)}")
    print(f"Total: {len(X_train) + len(X_test)}")
    print(f"Proporcion train/test: {len(X_train)/(len(X_train)+len(X_test))*100:.1f}% / "
          f"{len(X_test)/(len(X_train)+len(X_test))*100:.1f}%")

    # --- Entrenamiento del modelo ---
    print("\n--- Entrenando modelo ---")
    print("Modelo: StandardScaler + LogisticRegression")
    print("(Igual estructura que el ejemplo del profesor con Iris)")

    model = make_pipeline(
        StandardScaler(),
        LogisticRegression(
            max_iter=1000,
            random_state=RANDOM_STATE,
            multi_class="multinomial",
            solver="lbfgs",
        ),
    )

    t0 = time.time()
    model.fit(X_train, y_train)
    print(f"Tiempo de entrenamiento: {time.time() - t0:.1f}s")

    # --- Prediccion y evaluacion ---
    print("\n--- Evaluacion en conjunto de prueba ---")
    t0 = time.time()
    pred = model.predict(X_test)
    print(f"Tiempo de prediccion: {time.time() - t0:.1f}s")

    accuracy = accuracy_score(y_test, pred)
    print(f"\nAccuracy: {accuracy:.3f} ({accuracy * 100:.2f}%)")

    print("\nMatriz de confusion:")
    cm = confusion_matrix(y_test, pred)
    print(cm)

    # --- Mostrar clases con sus nombres ---
    idx_to_class = {v: k for k, v in class_map.items()}
    print("\n--- Clases del dataset ---")
    for idx in sorted(idx_to_class.keys()):
        count_train = int((y_train == idx).sum())
        count_test = int((y_test == idx).sum())
        print(f"  [{idx:2d}] {idx_to_class[idx]:55s}  train: {count_train:5d}  test: {count_test:5d}")

    print("\n" + "=" * 70)
    print("Entrenamiento completado.")
    print("=" * 70)


if __name__ == "__main__":
    main()
