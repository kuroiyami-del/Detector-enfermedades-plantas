import time

import numpy as np
import pandas as pd
from PIL import Image
from sklearn.ensemble import RandomForestClassifier
from sklearn.linear_model import LogisticRegression
from sklearn.model_selection import train_test_split
from sklearn.neural_network import MLPClassifier

from src.config import ARTIFACTS_DIR, RANDOM_STATE, RAW_DIR


# ---------------------------------------------------------------------------
# 1. CONFIGURACION Y CONSTANTES
# ---------------------------------------------------------------------------

# Cada carpeta de RAW_DIR es una clase de PlantVillage.
CLASES = sorted(carpeta.name for carpeta in RAW_DIR.iterdir() if carpeta.is_dir())

# Grises 48x48: 2304 caracteristicas, igual que la semana 08.
TAMANO_IMAGEN = 48

# Maximo de imagenes por clase para que el benchmark corra en minutos.
IMAGENES_POR_CLASE = 250
PORCION_PRUEBA = 0.20

# 3 corridas con semillas 42, 43 y 44: variaciones reales entre corridas.
NUMERO_CORRIDAS = 3
SEMILLA_BASE = RANDOM_STATE

# Artefacto de la semana.
RUTA_BENCHMARK = ARTIFACTS_DIR / "benchmark.csv"


# ---------------------------------------------------------------------------
# 2. PREPARACION DE DATOS (mismo dataset y misma division para los 3 modelos)
# ---------------------------------------------------------------------------

# Grises 48x48, aplana la matriz y normaliza a 0..1.
def vectorizar_imagen(ruta):
    with Image.open(ruta) as foto:
        pixeles = np.asarray(
            foto.convert("L").resize((TAMANO_IMAGEN, TAMANO_IMAGEN)),
            dtype=np.float32)
    return pixeles.ravel() / 255.0


# Hasta IMAGENES_POR_CLASE fotos por clase, con su id como etiqueta.
def cargar_dataset():
    archivos_por_clase = [
        sorted((RAW_DIR / carpeta).glob("*.jpg"))[:IMAGENES_POR_CLASE]
        for carpeta in CLASES
    ]
    total = sum(len(archivos) for archivos in archivos_por_clase)
    print(f"Clases: {len(CLASES)} | Imagenes por clase: {IMAGENES_POR_CLASE} "
          f"| Imagenes a cargar: {total}", flush=True)

    X, y = [], []
    inicio = time.time()
    for clase_id, carpeta in enumerate(CLASES):
        for archivo in archivos_por_clase[clase_id]:
            X.append(vectorizar_imagen(archivo))
            y.append(clase_id)

    X = np.array(X)
    y = np.array(y)
    print(f"Imagenes cargadas: {X.shape[0]} | "
          f"Caracteristicas por imagen: {X.shape[1]} | "
          f"{(time.time() - inicio) / 60:.1f} min", flush=True)
    return X, y


# Division estratificada 80/20 calculada una sola vez.
def dividir_datos(X, y):
    X_train, X_test, y_train, y_test = train_test_split(
        X, y, test_size=PORCION_PRUEBA,
        random_state=RANDOM_STATE, stratify=y
    )
    print(f"Division una sola vez -> Entrenamiento: {len(X_train)} | "
          f"Prueba: {len(X_test)}", flush=True)
    return X_train, X_test, y_train, y_test


# ---------------------------------------------------------------------------
# 3. MODELOS DEL BENCHMARK
# ---------------------------------------------------------------------------

# Instancias nuevas por corrida; la semilla cambia en cada corrida.
def crear_modelos(semilla):
    return {
        "logistic_regression": LogisticRegression(max_iter=500,
                                                  random_state=semilla),
        "random_forest": RandomForestClassifier(n_estimators=150,
                                                n_jobs=-1,
                                                random_state=semilla),
        # Arquitectura de la semana 08: capas 128 y 64.
        "mlp_classifier": MLPClassifier(hidden_layer_sizes=(128, 64),
                                        max_iter=100,
                                        random_state=semilla),
    }


# Entrena midiendo solo el fit() y calcula accuracy sobre el test fijo.
def entrenar_y_medir(nombre, semilla, corrida, datos):
    X_train, X_test, y_train, y_test = datos
    modelo = crear_modelos(semilla)[nombre]

    print(f"  corrida {corrida} | {nombre} | entrenando...", flush=True)
    inicio = time.perf_counter()
    modelo.fit(X_train, y_train)
    tiempo = time.perf_counter() - inicio

    accuracy = modelo.score(X_test, y_test)
    print(f"  corrida {corrida} | {nombre} | "
          f"accuracy={accuracy:.4f} | tiempo={tiempo:.1f}s", flush=True)
    return {"corrida": corrida,
            "modelo": nombre,
            "accuracy": accuracy,
            "tiempo_entrenamiento_s": tiempo}


# ---------------------------------------------------------------------------
# 4. EJECUCION DEL BENCHMARK
# ---------------------------------------------------------------------------

# 3 corridas x 3 modelos; instancia y semilla nuevas en cada corrida.
def ejecutar_corridas(datos):
    filas = []
    for corrida in range(1, NUMERO_CORRIDAS + 1):
        semilla = SEMILLA_BASE + corrida - 1
        print(f"\n[CORRIDA {corrida}/{NUMERO_CORRIDAS}] semilla={semilla}",
              flush=True)
        for nombre in ["logistic_regression", "random_forest",
                       "mlp_classifier"]:
            filas.append(entrenar_y_medir(nombre, semilla, corrida, datos))
    return filas


# Guarda el detalle de corridas en artifacts/benchmark.csv.
def guardar_csv(filas):
    tabla = pd.DataFrame(filas)
    tabla.to_csv(RUTA_BENCHMARK, index=False)
    print(f"\n[ARTEFACTO] {ARTIFACTS_DIR.name}/{RUTA_BENCHMARK.name} "
          f"({len(tabla)} filas)")


# Promedio y desviacion por modelo, mas la diferencia contra el mejor.
def mostrar_resumen(filas):
    tabla = pd.DataFrame(filas)
    resumen = tabla.groupby("modelo").agg(
        accuracy_promedio=("accuracy", "mean"),
        accuracy_desviacion=("accuracy", "std"),
        tiempo_promedio_s=("tiempo_entrenamiento_s", "mean"),
        tiempo_desviacion_s=("tiempo_entrenamiento_s", "std"),
    )
    resumen["diferencia_vs_mejor"] = (
        resumen["accuracy_promedio"] - resumen["accuracy_promedio"].max())
    resumen = resumen.sort_values("accuracy_promedio", ascending=False)

    print("\n[RESUMEN] Benchmark de 3 corridas por modelo:")
    print(resumen.to_string(float_format=lambda valor: f"{valor:.4f}"))
    return resumen


def run():
    print("=" * 70)
    print("SEMANA 11 - BENCHMARK DE MODELOS")
    print("=" * 70)
    print("  Proyecto: deteccion de enfermedades en plantas (PlantVillage)")
    print("  Modelos: LogisticRegression | RandomForest | MLPClassifier")
    print(f"  Corridas: {NUMERO_CORRIDAS} (semillas "
          f"{SEMILLA_BASE}..{SEMILLA_BASE + NUMERO_CORRIDAS - 1})")

    X, y = cargar_dataset()
    datos = dividir_datos(X, y)

    filas = ejecutar_corridas(datos)

    guardar_csv(filas)
    mostrar_resumen(filas)

    print("\n" + "=" * 70)
    print("Semana 11 completada.")
    print("=" * 70)


if __name__ == "__main__":
    run()
