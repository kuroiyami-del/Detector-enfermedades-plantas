import numpy as np
import sqlite3
import joblib
import networkx as nx
from PIL import Image
from sklearn.model_selection import train_test_split
from sklearn.neural_network import MLPClassifier
from sklearn.metrics import accuracy_score

from src.config import RAW_DIR, ARTIFACTS_DIR, RANDOM_STATE

# 6 categorias del dominio de la hoja de tomate: nombre y carpeta en PlantVillage.
CLASES = [
    ("healthy", "Tomato___healthy"),
    ("bacterial_spot", "Tomato___Bacterial_spot"),
    ("late_blight", "Tomato___Late_blight"),
    ("septoria", "Tomato___Septoria_leaf_spot"),
    ("spider_mites", "Tomato___Spider_mites Two-spotted_spider_mite"),
    ("leaf_mold", "Tomato___Leaf_Mold"),
]
TAMANO = 48
ARTIFACTS_DIR.mkdir(parents=True, exist_ok=True)
RUTA_MODELO = ARTIFACTS_DIR / "red_hojas.pkl"
RUTA_DB = ARTIFACTS_DIR / "evidencia_hojas.db"
RUTA_ONTOLOGIA = ARTIFACTS_DIR / "ontologia.graphml"


# Lee las fotos de tomate, las pasa a gris 48x48 y las convierte en listas de numeros.
def cargar_imagenes():
    X, y, nombres = [], [], []
    for clase_id, (clase, carpeta) in enumerate(CLASES):
        for imagen in sorted((RAW_DIR / carpeta).glob("*.jpg")):
            with Image.open(imagen) as im:
                pixeles = (
                    np.asarray(im.convert("L").resize((TAMANO, TAMANO)),
                               dtype=np.float32).ravel() / 255.0
                )
            X.append(pixeles)
            y.append(clase_id)
            nombres.append(f"{clase}/{imagen.name}")
    X = np.array(X)
    y = np.array(y)
    print(f"Imagenes cargadas: {X.shape[0]} | Caracteristicas por imagen: {X.shape[1]}")
    print(f"Clases: {[c for c, _ in CLASES]}")
    return X, y, nombres


# Entrena la red neuronal MLP, valida en prueba y guarda el modelo en artifacts/.
def entrenar_modelo(X, y, nombres):
    X_train, X_test, y_train, y_test, nombres_train, nombres_test = train_test_split(
        X, y, nombres, test_size=0.20, random_state=RANDOM_STATE, stratify=y
    )
    print(f"Entrenamiento: {len(X_train)} | Prueba: {len(X_test)}")

    model = MLPClassifier(hidden_layer_sizes=(128, 64), max_iter=1500,
                          random_state=RANDOM_STATE)
    model.fit(X_train, y_train)

    pred = model.predict(X_test)
    acc = accuracy_score(y_test, pred)
    print(f"[MODELO] Accuracy sobre el conjunto de prueba: {acc:.4f}")

    validar(y_test, pred, nombres_test)

    joblib.dump(model, RUTA_MODELO)
    print(f"[ARTEFACTO] Modelo guardado en artifacts/{RUTA_MODELO.name}")
    return y_test, pred, nombres_test


# Compara lo que predijo la red con la etiqueta real de cada foto de prueba.
def validar(y_test, pred, nombres_test):
    print("\n[VALIDACION] Real vs Predicha (primeras 12 muestras de prueba):")
    for nombre, real, p in zip(nombres_test[:12], y_test[:12], pred[:12]):
        marca = "OK" if real == p else "X"
        print(f"  {nombre:<30} real={CLASES[real][0]:<14} pred={CLASES[p][0]:<14} {marca}")

    print("\n[VALIDACION] Accuracy por clase:")
    for clase_id, (clase, _) in enumerate(CLASES):
        mascara = y_test == clase_id
        if mascara.sum() > 0:
            por_clase = accuracy_score(y_test[mascara], pred[mascara])
            print(f"  {clase:<16} acc={por_clase:.2f}  (n={int(mascara.sum())})")


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
            (nombre, CLASES[real][0], CLASES[p][0], int(real == p))
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

        print("\n[EVIDENCIA] Consulta de una enfermedad especifica:")
        for fila in con.execute(
            "SELECT COUNT(*), SUM(correcta) FROM predicciones "
            "WHERE categoria_real = 'late_blight'"
        ):
            print(f"  late_blight: total={fila[0]} correctas={fila[1]}")


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

    nx.write_graphml(G, RUTA_ONTOLOGIA)

    print(f"\n[ONTOLOGIA] Conceptos: {G.number_of_nodes()} | Relaciones: {G.number_of_edges()}")
    print("[ONTOLOGIA] Relaciones (frases):")
    for rel, origen, destino in sorted(
        (rel, origen, destino) for origen, destino, rel in G.edges(data="rel")
    ):
        print(f"  {rel}  {origen} --- {destino}")


# Ejecuta el flujo completo: fotos -> prediccion -> evidencia -> ontologia.
def run():
    print("=" * 70)
    print("SEMANA 08 - RED NEURONAL + EVIDENCIA + ONTOLOGIA")
    print("=" * 70)
    print("  Flujo: foto de hoja -> red neuronal (MLP) -> prediccion")
    print("         -> SQLite (evidencia) -> ontologia (significado)\n")

    X, y, nombres = cargar_imagenes()
    y_test, pred, nombres_test = entrenar_modelo(X, y, nombres)
    guardar_evidencia(y_test, pred, nombres_test)
    crear_ontologia()
    print("\n[FLUJO] Imagen de hoja -> modelo_red (prediccion) -> "
          "SQLite (evidencia) -> ontologia (significado)")

    print("\n" + "=" * 70)
    print("Semana 08 completada.")
    print("=" * 70)


if __name__ == "__main__":
    run()