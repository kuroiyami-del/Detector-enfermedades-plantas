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


# ---------------------------------------------------------------------------
# 1. CONFIGURACION Y CONSTANTES
# Aqui se_declaran los parametros academicos de la semana: tamano de imagen,
# arquitectura de la red y rutas de los artefactos que se generan.
# ---------------------------------------------------------------------------

# Todas las clases de PlantVillage: cada carpeta de RAW_DIR es una categoria.
CLASES = sorted(carpeta.name for carpeta in RAW_DIR.iterdir() if carpeta.is_dir())

# Cada imagen se convierte en una matriz de 48 x 48 pixeles. Al aplanar esa
# matriz quedan 48 * 48 = 2304 caracteristicas, que son las entradas de la red.
TAMANO_IMAGEN = 48

# Cada cuantas imagenes se informa el avance de la carga.
PASO_PROGRESO = 5000

# Arquitectura de la red: una capa oculta de 128 neuronas y otra de 64.
CAPAS_OCULTAS = (128, 64)
# Techo de iteraciones del entrenamiento; ambos se reportan al terminar.
MAX_ITER = 1500
# Parte del dataset reservada para la evaluacion (el 80% restante se entrena).
PORCION_PRUEBA = 0.20
# Cuantas clases con peor accuracy se muestran al final de la evaluacion.
NUMERO_PEORES_CLASES = 6

ARTIFACTS_DIR.mkdir(parents=True, exist_ok=True)
RUTA_MODELO = ARTIFACTS_DIR / "red_hojas.pkl"
RUTA_DB = ARTIFACTS_DIR / "evidencia_hojas.db"
RUTA_ONTOLOGIA = ARTIFACTS_DIR / "ontologia.graphml"


# ---------------------------------------------------------------------------
# 2. PREPARACION DE DATOS
# El flujo es:  imagen -> escala de grises -> 48x48 -> vector de 2304 numeros
# ---------------------------------------------------------------------------

# Muestra el avance de la carga: cuantas imagenes van, a que velocidad y
# cuanto tiempo falta aproximadamente.
def mostrar_progreso_avance(cargadas, total, inicio):
    transcurrido = time.time() - inicio
    velocidad = cargadas / transcurrido
    restante = (total - cargadas) / velocidad
    print(f"  cargando... {cargadas}/{total} | "
          f"{transcurrido / 60:.1f} min | {velocidad:.0f} img/s | "
          f"faltan ~{restante / 60:.1f} min", flush=True)


# Convierte una imagen en el vector de entrada de la red.
# Se pasa a escala de grises ("L"), se redimensiona a 48x48 y se aplana con
# ravel(), de modo que la matriz 48x48 queda como una fila de 2304 numeros.
# Cada numero se divide entre 255 para quedar en el rango 0..1.
def vectorizar_imagen(ruta):
    with Image.open(ruta) as foto:
        pixeles = np.asarray(
            foto.convert("L").resize((TAMANO_IMAGEN, TAMANO_IMAGEN)),
            dtype=np.float32)
    return pixeles.ravel() / 255.0


# Lee las fotos de las 38 clases de PlantVillage y arma el dataset.
# El orden de lectura es alfabetico por carpeta y, dentro de cada carpeta,
# alfabetico por archivo. Ese orden fija las etiquetas, por eso se respeta.
def cargar_imagenes():
    # Un solo recorrido del disco: se listan los archivos una vez y esa misma
    # lista sirve tanto para contarlos como para leerlos despues.
    archivos_por_clase = [
        sorted((RAW_DIR / carpeta).glob("*.jpg")) for carpeta in CLASES
    ]
    total = sum(len(archivos) for archivos in archivos_por_clase)
    print(f"Clases: {len(CLASES)} | Imagenes a cargar: {total}", flush=True)
    print(f"Clases: {CLASES}", flush=True)

    # X = matriz de caracteristicas (una fila por imagen, 2304 columnas)
    # y = vector de etiquetas (el id numerico de la clase de cada imagen)
    # nombres = ruta de cada imagen, para poder mostrar la evidencia despues
    X, y, nombres = [], [], []
    inicio = time.time()
    for clase_id, carpeta in enumerate(CLASES):
        for archivo in archivos_por_clase[clase_id]:
            X.append(vectorizar_imagen(archivo))
            y.append(clase_id)
            nombres.append(f"{carpeta}/{archivo.name}")
            if len(X) % PASO_PROGRESO == 0:
                mostrar_progreso_avance(len(X), total, inicio)

    X = np.array(X)
    y = np.array(y)
    print(f"Imagenes cargadas: {X.shape[0]} | "
          f"Caracteristicas por imagen: {X.shape[1]} | "
          f"{(time.time() - inicio) / 60:.1f} min", flush=True)
    return X, y, nombres


# ---------------------------------------------------------------------------
# 3. REUTILIZACION DEL MODELO YA ENTRENADO
# Entrenar la red completa lleva mas de 90 minutos, asi que el modelo se
# guarda en artifacts/red_hojas.pkl y se vuelve a usar mientras siga siendo
# compatible con el codigo actual.
# ---------------------------------------------------------------------------

# Carga el modelo guardado en artifacts/red_hojas.pkl.
# Devuelve None si el archivo no existe o si no se puede leer.
def cargar_modelo_guardado():
    if not RUTA_MODELO.exists():
        return None
    try:
        return joblib.load(RUTA_MODELO)
    except Exception as error:
        print(f"[MODELO] No se pudo leer {RUTA_MODELO.name}: {error}")
        return None


# Comprueba que el modelo guardado sirve para el codigo actual.
# Devuelve la lista de problemas encontrados: una lista vacia significa que
# el modelo es compatible y se puede reutilizar sin volver a entrenarlo.
def comprobar_compatibilidad(modelo):
    esperado = TAMANO_IMAGEN * TAMANO_IMAGEN
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
    return problemas


# Devuelve el modelo guardado si existe y es compatible con el codigo actual,
# o None si hay que entrenarlo.
def modelo_reutilizable():
    modelo = cargar_modelo_guardado()
    if modelo is None:
        return None

    problemas = comprobar_compatibilidad(modelo)
    if problemas:
        print("[MODELO] El modelo guardado no sirve para el codigo actual:")
        for problema in problemas:
            print(f"  - {problema}")
        return None

    print(f"[MODELO] {RUTA_MODELO.name} es compatible: {modelo.n_outputs_} clases, "
          f"{modelo.n_features_in_} caracteristicas, "
          f"entrenado con {modelo.n_iter_} iteraciones")
    return modelo


# ---------------------------------------------------------------------------
# 4. RED NEURONAL: ENTRENAMIENTO, PREDICCION Y EVALUACION
# ---------------------------------------------------------------------------

# Divide el dataset en entrenamiento (80%) y prueba (20%).
# stratify=y reparte las 38 clases de forma proporcional en las dos partes,
# para que la evaluacion sea representativa del conjunto completo.
def dividir_datos(X, y, nombres):
    inicio = time.time()
    X_train, X_test, y_train, y_test, nombres_train, nombres_test = train_test_split(
        X, y, nombres, test_size=PORCION_PRUEBA, random_state=RANDOM_STATE, stratify=y
    )
    print(f"Entrenamiento: {len(X_train)} | Prueba: {len(X_test)} | "
          f"division en {time.time() - inicio:.1f} s", flush=True)
    return X_train, X_test, y_train, y_test, nombres_train, nombres_test


# Crea la red neuronal y la entrena con fit().
# Concepto de IA: aprendizaje supervisado. fit() aprende los pesos de la red a
# partir de las imagenes (X_train) y de sus etiquetas conocidas (y_train).
# El modelo resultante se guarda en artifacts/red_hojas.pkl, y solo aqui se
# ejecuta joblib.dump(), es decir, unicamente cuando hubo un entrenamiento real.
def crear_y_entrenar_red(X_train, y_train):
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
    return modelo


# Compara lo que predijo la red con la etiqueta real de las primeras
# 12 imagenes de prueba, para ver a mano cuales acertó y cuales fallo.
def mostrar_real_vs_predicho(y_test, pred, nombres_test):
    print("\n[VALIDACION] Real vs Predicha (primeras 12 muestras de prueba):")
    for nombre, real, predicha in zip(nombres_test[:12], y_test[:12], pred[:12]):
        marca = "OK" if real == predicha else "X"
        print(f"  {nombre:<38} real={CLASES[real]:<26} "
              f"pred={CLASES[predicha]:<26} {marca}")


# Calcula el accuracy de cada clase por separado, ordena los resultados de
# menor a mayor y muestra las NUMERO_PEORES_CLASES con peor desempeño.
def mostrar_peores_clases(y_test, pred):
    print("\n[VALIDACION] Peores clases (menor accuracy):")
    accuracies_por_clase = []
    for clase_id, clase in enumerate(CLASES):
        mascara = y_test == clase_id
        if mascara.sum() > 0:
            acc = accuracy_score(y_test[mascara], pred[mascara])
            accuracies_por_clase.append((acc, clase, int(mascara.sum())))
    for acc, clase, muestras in sorted(accuracies_por_clase)[:NUMERO_PEORES_CLASES]:
        print(f"  {clase:<38} acc={acc:.2f}  (n={muestras})")


# Muestra como se comporte la red: ejemplos de acierto/error y las clases
# con peor accuracy.
def mostrar_evaluacion(y_test, pred, nombres_test):
    mostrar_real_vs_predicho(y_test, pred, nombres_test)
    mostrar_peores_clases(y_test, pred)


# Coordina el paso de aprendizaje automatico: divide los datos, reutiliza el
# modelo guardado o entrena uno nuevo, predice y evalua.
# modelo = None  -> hay que entrenar desde cero
# modelo != None -> el modelo ya existia y solo se reutiliza
def entrenar_modelo(X, y, nombres, modelo=None):
    X_train, X_test, y_train, y_test, nombres_train, nombres_test = dividir_datos(X, y, nombres)

    if modelo is None:
        modelo = crear_y_entrenar_red(X_train, y_train)
    else:
        print(f"\n[ENTRENO] Se reutiliza {RUTA_MODELO.name} "
              f"(se entreno con {modelo.n_iter_} iteraciones); no se ejecuta fit()",
              flush=True)

    # Prediccion: la red ya entrenada recibe las imagenes de prueba y devuelve
    # la clase que considera mas probable para cada una.
    pred = modelo.predict(X_test)

    # Accuracy: proporcion de imagenes de prueba cuya clase predicha coincide
    # con la etiqueta real. Es la metrica de evaluacion del modelo.
    acc = accuracy_score(y_test, pred)
    print(f"[MODELO] Accuracy sobre el conjunto de prueba: {acc:.4f}", flush=True)

    mostrar_evaluacion(y_test, pred, nombres_test)
    return y_test, pred, nombres_test


# ---------------------------------------------------------------------------
# 5. EVIDENCIA EN SQLITE
# Cada prediccion se guarda como una fila consultable. Esta es la parte de
# persistencia del flujo: el modelo produce la prediccion, la base de datos
# permite revisar despues que se predijo y si fue correcto.
# ---------------------------------------------------------------------------

# Crea la tabla de evidencia. Se borra la anterior para empezar de cero.
def crear_tabla_predicciones(con):
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


# Inserta una fila por cada imagen de prueba, con su clase real, la clase
# predicha y si la prediccion fue correcta (1) o no (0).
def insertar_predicciones(con, y_test, pred, nombres_test):
    filas = [
        (nombre, CLASES[real], CLASES[predicha], int(real == predicha))
        for nombre, real, predicha in zip(nombres_test, y_test, pred)
    ]
    con.executemany(
        "INSERT INTO predicciones(imagen, categoria_real, prediccion, correcta) "
        "VALUES(?,?,?,?)",
        filas,
    )
    con.commit()


# Consulta la evidencia almacenada: total de registros, aciertos, una muestra
# de filas y el conteo agrupado por clase real.
def consultar_evidencia(con):
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


# Guarda la evidencia de todas las predicciones en artifacts/evidencia_hojas.db.
def guardar_evidencia(y_test, pred, nombres_test):
    with sqlite3.connect(RUTA_DB) as con:
        crear_tabla_predicciones(con)
        insertar_predicciones(con, y_test, pred, nombres_test)
        consultar_evidencia(con)


# ---------------------------------------------------------------------------
# 6. ONTOLOGIA
# La ontologia aporta el significado de las predicciones: conecta la imagen de
# la hoja con su sintoma, la enfermedad y la categoria a la que pertenece.
# ---------------------------------------------------------------------------

# Muestra las relaciones del grafo como frases, ordenadas de forma estable.
def mostrar_relaciones(grafo):
    print("[ONTOLOGIA] Relaciones (frases):")
    # Cada arista se pasa a un trio (relacion, origen, destino) y se ordena por
    # ese trio, para que la lista salga siempre en el mismo orden.
    relaciones = [(relacion, origen, destino)
                  for origen, destino, relacion in grafo.edges(data="rel")]
    for relacion, origen, destino in sorted(relaciones):
        print(f"  {relacion}  {origen} --- {destino}")


# Crea el grafo de conceptos del dominio y lo guarda como ontologia en GraphML.
# El grafo se arma en tres pasos: conceptos, relaciones entre conceptos y
# por ultimo las 38 clases de PlantVillage como nodos hoja de la ontologia.
def crear_ontologia():
    grafo = nx.DiGraph()

    # Conceptos generales: el vocabulario del dominio.
    conceptos = [
        "imagen_hoja", "hoja", "planta", "sintoma",
        "enfermedad", "categoria", "prediccion", "modelo_red",
    ]
    # Relaciones entre conceptos, cada una como (origen, destino, relacion).
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
    grafo.add_nodes_from(conceptos)
    for origen, destino, relacion in relaciones:
        grafo.add_edge(origen, destino, rel=relacion)

    # Cada clase de PlantVillage es un nodo hoja de la ontologia.
    for clase in CLASES:
        grafo.add_node(clase)
        grafo.add_edge("categoria", clase, rel="incluye")

    nx.write_graphml(grafo, RUTA_ONTOLOGIA)

    print(f"\n[ONTOLOGIA] Conceptos: {grafo.number_of_nodes()} | "
          f"Relaciones: {grafo.number_of_edges()}")
    mostrar_relaciones(grafo)


# ---------------------------------------------------------------------------
# 7. EJECUCION PRINCIPAL
# ---------------------------------------------------------------------------

# Decide si se reutiliza el modelo guardado o si hay que entrenar de nuevo.
# Con --force se ignora el modelo existente y se entrena nuevamente.
def obtener_modelo(forzar_entrenamiento):
    if forzar_entrenamiento:
        print("[MODELO] --force recibido: se reentrena aunque exista un modelo\n")
        return None

    modelo = modelo_reutilizable()
    if modelo is not None:
        print("\n" + "!" * 70)
        print("  SE OMITE EL ENTRENAMIENTO: el modelo guardado es valido.")
        print("  Reentrenar la red desde cero tarda mas de 90 minutos.")
        print("  Para hacerlo igual, ejecuta:")
        print("      python -m src.semana08_red_ontologia --force")
        print("!" * 70 + "\n")
    return modelo


def run(forzar_entrenamiento=False):
    print("=" * 70)
    print("SEMANA 08 - RED NEURONAL + EVIDENCIA + ONTOLOGIA")
    print("=" * 70)
    print("  Flujo: foto de hoja -> red neuronal (MLP) -> prediccion")
    print("         -> SQLite (evidencia) -> ontologia (significado)\n")

    # 1. Modelo: primero se decide si se reutiliza el modelo ya entrenado.
    #    Se hace antes de leer las imagenes para avisar cuanto antes si los mas
    #    de 90 minutos de entrenamiento se pueden evitar.
    modelo = obtener_modelo(forzar_entrenamiento)

    # 2. Datos: lectura de las imagenes de las 38 clases de PlantVillage.
    X, y, nombres = cargar_imagenes()

    # 3. Aprendizaje: reutiliza el modelo o entrena uno nuevo.
    # 4. Prediccion y evaluacion sobre el 20% de prueba, con accuracy
    #    global, ejemplos reales y las 6 peores clases.
    y_test, pred, nombres_test = entrenar_modelo(X, y, nombres, modelo)

    # 5. Evidencia: cada prediccion queda registrada en SQLite.
    guardar_evidencia(y_test, pred, nombres_test)

    # 6. Ontologia: los conceptos del dominio se guardan en GraphML.
    crear_ontologia()

    print("\n[FLUJO] Imagen de hoja -> modelo_red (prediccion) -> "
          "SQLite (evidencia) -> ontologia (significado)")

    print("\n" + "=" * 70)
    print("Semana 08 completada.")
    print("=" * 70)


if __name__ == "__main__":
    run(forzar_entrenamiento="--force" in sys.argv)