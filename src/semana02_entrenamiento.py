import json
import time
from pathlib import Path

import joblib
import numpy as np
from sklearn.linear_model import LogisticRegression
from sklearn.metrics import accuracy_score, confusion_matrix
from sklearn.pipeline import make_pipeline
from sklearn.preprocessing import StandardScaler

from src.config import IMG_SIZE, MODELS_DIR, RANDOM_STATE
from src.data_loader import load_class_map, load_images, load_split, preprocess_single_image


def train_model():
    class_map = load_class_map()

    train_df = load_split("train.csv")
    X_train = load_images(train_df)
    y_train = train_df["label"].values

    model = make_pipeline(
        StandardScaler(),
        LogisticRegression(max_iter=1000, random_state=RANDOM_STATE, solver="lbfgs"),
    )
    model.fit(X_train, y_train)

    test_df = load_split("test.csv")
    X_test = load_images(test_df)
    y_test = test_df["label"].values
    pred = model.predict(X_test)
    accuracy = accuracy_score(y_test, pred)

    return model, class_map, accuracy


def save_model(model, class_map, accuracy):
    MODELS_DIR.mkdir(parents=True, exist_ok=True)

    joblib.dump(model, MODELS_DIR / "model.pkl")

    with open(MODELS_DIR / "class_map.json", "w", encoding="utf-8") as f:
        json.dump(class_map, f, indent=2, ensure_ascii=False)

    meta = {"accuracy": accuracy, "img_size": IMG_SIZE}
    with open(MODELS_DIR / "metadata.json", "w", encoding="utf-8") as f:
        json.dump(meta, f, indent=2)


def load_model():
    model = joblib.load(MODELS_DIR / "model.pkl")

    with open(MODELS_DIR / "class_map.json", "r", encoding="utf-8") as f:
        class_map = json.load(f)

    return model, class_map


def predict_single(model, class_map, image_path):
    img = preprocess_single_image(image_path)
    img = img.reshape(1, -1)

    pred = model.predict(img)[0]
    probs = model.predict_proba(img)[0]
    confidence = float(probs.max())

    idx_to_class = {v: k for k, v in class_map.items()}
    class_name = idx_to_class.get(pred, str(pred))

    return class_name, confidence


def run():
    print("=" * 70)
    print("SEMANA 02 - ENTRENAMIENTO: Enfermedades en Plantas")
    print("=" * 70)

    class_map = load_class_map()
    num_classes = len(class_map)
    print(f"\nClases detectadas: {num_classes}")
    print(f"Tamano de imagen: {IMG_SIZE}x{IMG_SIZE}x3 = {IMG_SIZE * IMG_SIZE * 3} features")

    print("\n--- Cargando conjunto de ENTRENAMIENTO ---")
    train_df = load_split("train.csv")
    print(f"Muestras en train.csv: {len(train_df)}")

    train_counts = train_df["class_name"].value_counts()
    print("Distribucion de clases (entrenamiento, top 10):")
    for class_name, count in train_counts.head(10).items():
        print(f"  {class_name}: {count}")
    if len(train_counts) > 10:
        print(f"  ... y {len(train_counts) - 10} clases mas")

    print("\nCargando imagenes de entrenamiento...")
    t0 = time.time()
    X_train = load_images(train_df)
    y_train = train_df["label"].values
    print(f"Tiempo de carga: {time.time() - t0:.1f}s")

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

    print("\n--- Resumen de la separacion ---")
    print(f"Muestras de entrenamiento: {len(X_train)}")
    print(f"Muestras de prueba: {len(X_test)}")
    total = len(X_train) + len(X_test)
    print(f"Total: {total}")
    print(f"Proporcion train/test: {len(X_train)/total*100:.1f}% / {len(X_test)/total*100:.1f}%")

    print("\n--- Entrenando modelo ---")
    print("Modelo: StandardScaler + LogisticRegression")

    model = make_pipeline(
        StandardScaler(),
        LogisticRegression(
            max_iter=1000,
            random_state=RANDOM_STATE,
            solver="lbfgs",
        ),
    )

    t0 = time.time()
    model.fit(X_train, y_train)
    print(f"Tiempo de entrenamiento: {time.time() - t0:.1f}s")

    print("\n--- Evaluacion en conjunto de prueba ---")
    t0 = time.time()
    pred = model.predict(X_test)
    print(f"Tiempo de prediccion: {time.time() - t0:.1f}s")

    accuracy = accuracy_score(y_test, pred)
    print(f"\nAccuracy: {accuracy:.3f} ({accuracy * 100:.2f}%)")

    print("\nMatriz de confusion:")
    print(confusion_matrix(y_test, pred))

    idx_to_class = {v: k for k, v in class_map.items()}
    print("\n--- Clases del dataset ---")
    for idx in sorted(idx_to_class.keys()):
        count_train = int((y_train == idx).sum())
        count_test = int((y_test == idx).sum())
        print(f"  [{idx:2d}] {idx_to_class[idx]:55s}  train: {count_train:5d}  test: {count_test:5d}")

    print("\n" + "=" * 70)
    print("Semana 02 completada.")
    print("=" * 70)
