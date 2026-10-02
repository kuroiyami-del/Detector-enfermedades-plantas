import sys
import time

import numpy as np
import sqlite3
import joblib
import networkx as nx
from PIL import Image
from sklearn.model_selection import train_test_split
from sklearn.neural_network import MLPClassifier
from sklearn.metrics import accuracy_score

from src.config import RAW_DIR, ARTIFACTS_DIR, RANDOM_STATE

# Todas las clases de PlantVillage: cada carpeta de RAW_DIR es una categoria.
CLASES = sorted(carpeta.name for carpeta in RAW_DIR.iterdir() if carpeta.is_dir())
TAMANO = 48
# Cada cuantas imagenes se informa el avance de la carga.
PASO_PROGRESO = 5000
# Arquitectura y techo de iteraciones de la red; ambos se reportan al terminar.
CAPAS_OCULTAS = (128, 64)
MAX_ITER = 1500
ARTIFACTS_DIR.mkdir(parents=True, exist_ok=True)
RUTA_MODELO = ARTIFACTS_DIR / "red_hojas.pkl"
RUTA_DB = ARTIFACTS_DIR / "evidencia_hojas.db"
RUTA_ONTOLOGIA = ARTIFACTS_DIR / "ontologia.graphml"


# Lee las fotos de todas las plantas, las pasa a gris 48x48 y las convierte en listas de numeros.
def cargar_imagenes():
    total = sum(1 for carpeta in CLASES
                for _ in (RAW_DIR / carpeta).glob("*.jpg"))
    print(f"Clases: {len(CLASES)} | Imagenes a cargar: {total}", flush=True)
    print(f"Clases: {CLASES}", flush=True)

    X, y, nombres = [], [], []
    inicio = time.time()
    for clase_id, carpeta in enumerate(CLASES):
        for imagen in sorted((RAW_DIR / carpeta).glob("*.jpg")):
            with Image.open(imagen) as im:
                pixeles = (
                    np.asarray(im.convert("L").resize((TAMANO, TAMANO)),
                               dtype=np.float32).ravel() / 255.0
                )
            X.append(pixeles)
            y.append(clase_id)
            nombres.append(f"{carpeta}/{imagen.name}")
            if len(X) % PASO_PROGRESO == 0:
                transcurrido = time.time() - inicio
                velocidad = len(X) / transcurrido
                restante = (total - len(X)) / velocidad
                print(f"  cargando... {len(X)}/{total} | "
                      f"{transcurrido / 60:.1f} min | {velocidad:.0f} img/s | "
                      f"faltan ~{restante / 60:.1f} min", flush=True)
    X = np.array(X)
    y = np.array(y)
    print(f"Imagenes cargadas: {X.shape[0]} | "
          f"Caracteristicas por imagen: {X.shape[1]} | "
          f"{(time.time() - inicio) / 60:.1f} min", flush=True)
    return X, y, nombres


# Devuelve el modelo guardado si existe y es compatible con el codigo actual,
# o None si hay que entrenarlo. Entrenar la red completa lleva poco mas de hora
# y media, asi que solo se repite cuando de verdad hace falta.
def modelo_reutilizable():
    if not RUTA_MODELO.exists():
        return None

    try:
        modelo = joblib.load(RUTA_MODELO)
    except Exception as error:
        print(f"[MODELO] No se pudo leer {RUTA_MODELO.name}: {error}")
        return None

    esperado = TAMANO * TAMANO
    entradas = getattr(modelo, "n_features_in_", None)
    salidas = getattr(modelo, "n_outputs_", None)
    clases = list(getattr(modelo, "classes_", []))

    problemas = []
    if entradas != esperado:
        problemas.append(f"esperaba {esperado} caracteristicas, tiene {entradas}")
    if salidas != len(CLASES):
        problemas.append(f"esta entrenado para {salidas} clases, "
                         f"hay {len(CLASES)} carpetas en RAW_DIR")
    if clases != list(range(len(CLASES))):
        problemas.append("el orden de clases no coincide con las carpetas de RAW_DIR")

    if problemas:
        print("[MODELO] El modelo guardado no sirve para el codigo actual:")
        for problema in problemas:
            print(f"  - {problema}")
        return None

    print(f"[MODELO] {RUTA_MODELO.name} es compatible: {salidas} clases, "
          f"{entradas} caracteristicas, entrenado con {modelo.n_iter_} iteraciones")
    return modelo


# Entrena la red neuronal MLP, valida en prueba y guarda el modelo en artifacts/.
def entrenar_modelo(X, y, nombres, modelo=None):
    inicio = time.time()
    X_train, X_test, y_train, y_test, nombres_train, nombres_test = train_test_split(
        X, y, nombres, test_size=0.20, random_state=RANDOM_STATE, stratify=y
    )
    print(f"Entrenamiento: {len(X_train)} | Prueba: {len(X_test)} | "
          f"division en {time.time() - inicio:.1f} s", flush=True)

    if modelo is not None:
        print(f"\n[ENTRENO] Se reutiliza {RUTA_MODELO.name} "
              f"(se entreno con {modelo.n_iter_} iteraciones); no se ejecuta fit()",
              flush=True)
    else:
        print(f"\n[ENTRENO] MLP {CAPAS_OCULTAS} | max_iter={MAX_ITER} | "
              f"{len(X_train)} muestras x {X_train.shape[1]} caracteristicas",
              flush=True)
        inicio = time.time()
        modelo = MLPClassifier(hidden_layer_sizes=CAPAS_OCULTAS, max_iter=MAX_ITER,
                               random_state=RANDOM_STATE, verbose=True)
        modelo.fit(X_train, y_train)
        iteraciones = modelo.n_iter_
        print(f"\n[ENTRENO] Termino en {(time.time() - inicio) / 60:.1f} min | "
              f"iteraciones {iteraciones}/{MAX_ITER}"
              f"{' (convergio antes del techo)' if iteraciones < MAX_ITER else ' (llego al techo)'}",
              flush=True)
        joblib.dump(modelo, RUTA_MODELO)
        print(f"[ARTEFACTO] Modelo guardado en artifacts/{RUTA_MODELO.name}")

    pred = modelo.predict(X_test)
    acc = accuracy_score(y_test, pred)
    print(f"[MODELO] Accuracy sobre el conjunto de prueba: {acc:.4f}", flush=True)

    validar(y_test, pred, nombres_test)
    return y_test, pred, nombres_test


# Compara lo que predijo la red con la etiqueta real de cada foto de prueba.
def validar(y_test, pred, nombres_test):
    print("\n[VALIDACION] Real vs Predicha (primeras 12 muestras de prueba):")
    for nombre, real, p in zip(nombres_test[:12], y_test[:12], pred[:12]):
        marca = "OK" if real == p else "X"
        print(f"  {nombre:<38} real={CLASES[real]:<26} pred={CLASES[p]:<26} {marca}")

    print("\n[VALIDACION] Peores clases (menor accuracy):")
    por_clase = []
    for clase_id, clase in enumerate(CLASES):
        mascara = y_test == clase_id
        if mascara.sum() > 0:
            acc = accuracy_score(y_test[mascara], pred[mascara])
            por_clase.append((acc, clase, int(mascara.sum())))
    for acc, clase, n in sorted(por_clase)[:6]:
        print(f"  {clase:<38} acc={acc:.2f}  (n={n})")


# Guarda cada prediccion en la base SQLite y muestra consultas de evidencia.
def guardar_evidencia(y_test, pred, nombres_test):
    with sqlite3.connect(RUTA_DB) as con:
        con.execute("DROP TABLE IF EXISTS predicciones")
        con.execute(
            "CREATE TABLE predicciones("
            "id INTEGER PRIMARY KEY AUTOINCREMENT,"
            "imagen TEXT,"
            "categoria_real TEXT,"
            "prediccion TEXT,"
            "correcta INTEGER,"
            "fecha TEXT DEFAULT (datetime('now','localtime')))"
        )
        filas = [
            (nombre, CLASES[real], CLASES[p], int(real == p))
            for nombre, real, p in zip(nombres_test, y_test, pred)
        ]
        con.executemany(
            "INSERT INTO predicciones(imagen, categoria_real, prediccion, correcta) "
            "VALUES(?,?,?,?)",
            filas,
        )
        con.commit()

        total = con.execute("SELECT COUNT(*) FROM predicciones").fetchone()[0]
        correctas = con.execute("SELECT SUM(correcta) FROM predicciones").fetchone()[0]
        print(f"\n[EVIDENCIA] Registros en base de datos: {total}")
        print(f"[EVIDENCIA] Predicciones correctas: {correctas} / {total}")

        print("\n[EVIDENCIA] Primeras 5 filas consultadas desde evidencia_hojas.db:")
        for fila in con.execute(
            "SELECT id, imagen, categoria_real, prediccion, correcta, fecha "
            "FROM predicciones ORDER BY id LIMIT 5"
        ):
            print(f"  {fila}")

        print("\n[EVIDENCIA] Conteo de predicciones por clase (primeras 5):")
        for fila in con.execute(
            "SELECT categoria_real, COUNT(*), SUM(correcta) "
            "FROM predicciones GROUP BY categoria_real ORDER BY categoria_real LIMIT 5"
        ):
            print(f"  {fila[0]:<38} total={int(fila[1]):<5} correctas={fila[2]}")


# Crea el grafo de conceptos del dominio y lo guarda como ontologia en GraphML.
def crear_ontologia():
    G = nx.DiGraph()
    conceptos = [
        "imagen_hoja", "hoja", "planta", "sintoma",
        "enfermedad", "categoria", "prediccion", "modelo_red",
    ]
    relaciones = [
        ("imagen_hoja", "hoja", "representa"),
        ("hoja", "planta", "pertenece"),
        ("hoja", "sintoma", "presenta"),
        ("sintoma", "enfermedad", "indica"),
        ("enfermedad", "categoria", "tiene"),
        ("modelo_red", "hoja", "reconoce"),
        ("modelo_red", "prediccion", "produce"),
        ("prediccion", "categoria", "asigna"),
    ]
    G.add_nodes_from(conceptos)
    for origen, destino, rel in relaciones:
        G.add_edge(origen, destino, rel=rel)

    # Cada clase de PlantVillage es un nodo hoja de la ontologia.
    for clase in CLASES:
        G.add_node(clase)
        G.add_edge("categoria", clase, rel="incluye")

    nx.write_graphml(G, RUTA_ONTOLOGIA)

    print(f"\n[ONTOLOGIA] Conceptos: {G.number_of_nodes()} | Relaciones: {G.number_of_edges()}")
    print("[ONTOLOGIA] Relaciones (frases):")
    for rel, origen, destino in sorted(
        (rel, origen, destino) for origen, destino, rel in G.edges(data="rel")
    ):
        print(f"  {rel}  {origen} --- {destino}")


# Ejecuta el flujo completo: fotos -> prediccion -> evidencia -> ontologia.
def run(forzar_entrenamiento=False):
    print("=" * 70)
    print("SEMANA 08 - RED NEURONAL + EVIDENCIA + ONTOLOGIA")
    print("=" * 70)
    print("  Flujo: foto de hoja -> red neuronal (MLP) -> prediccion")
    print("         -> SQLite (evidencia) -> ontologia (significado)\n")

    if forzar_entrenamiento:
        print("[MODELO] --force recibido: se reentrena aunque exista un modelo\n")
        modelo = None
    else:
        modelo = modelo_reutilizable()

    if modelo is not None:
        print("\n" + "!" * 70)
        print("  SE OMITE EL ENTRENAMIENTO: el modelo guardado es valido.")
        print("  Reentrenar la red desde cero tarda mas de 90 minutos.")
        print("  Para hacerlo igual, ejecuta:")
        print("      python -m src.semana08_red_ontologia --force")
        print("!" * 70 + "\n")

    X, y, nombres = cargar_imagenes()
    y_test, pred, nombres_test = entrenar_modelo(X, y, nombres, modelo)
    guardar_evidencia(y_test, pred, nombres_test)
    crear_ontologia()
    print("\n[FLUJO] Imagen de hoja -> modelo_red (prediccion) -> "
          "SQLite (evidencia) -> ontologia (significado)")

    print("\n" + "=" * 70)
    print("Semana 08 completada.")
    print("=" * 70)


if __name__ == "__main__":
    run(forzar_entrenamiento="--force" in sys.argv)