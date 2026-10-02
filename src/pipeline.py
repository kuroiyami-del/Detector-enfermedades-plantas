import re
import sys
import tempfile
from pathlib import Path

from PIL import Image
from tkinter import Tk, filedialog

from src.config import ARTIFACTS_DIR, RAW_DIR
from src.data_loader import load_split
from src.semana02_entrenamiento import load_model, predict_single
from src.semana03_taxonomia import classify_class
from src.semana04_busqueda import TRATAMIENTOS, diagnose_recovery
from src import semana09_vision

# Clasificar solo el recorte de la hoja empeora el resultado: medido sobre 304
# imagenes de prueba (8 por clase, las 38 clases) el accuracy cae de 0.5757 con
# la imagen completa a 0.3191 recortando la region mayor, y a 0.3711 aun con la
# segmentacion ya limpiada. El motivo es que el modelo de la semana 02 se
# entreno sobre imagenes sin recortar, asi que quitar el fondo gris lo deja fuera
# de la distribucion que aprendio. Por defecto se clasifica la imagen completa y
# la semana 09 aporta evidencia, no recorte.
USAR_RECORTE = False


def print_header(image_path):
    print("=" * 60)
    print("  PlantAI - Diagnostico de enfermedades en plantas")
    print(f"  Imagen: {image_path}")
    print("=" * 60)


def print_step(n, title):
    print(f"\nPASO {n}: {title}")
    print("-" * 60)


def show_plan(plan, total, expanded):
    if plan is None:
        print("  Meta inalcanzable: no hay cura para enfermedades virales.")
        print("  Plan disponible: solo contencion y manejo.")
        return

    print(f"  Costo total: {total}  |  Nodos expandidos: {expanded}")
    print()
    for i, (origen, accion, step, nxt) in enumerate(plan, start=1):
        print(f"  {i}. {accion:30s} +{step}")


def ask_image():
    root = Tk()
    root.withdraw()
    path = filedialog.askopenfilename(
        title="Selecciona una foto de tu planta",
        filetypes=[("Imagenes", "*.jpg *.jpeg *.png *.bmp")],
    )
    root.destroy()
    return path


def recortar_hoja(image_path, principal, destino):
    # Recorta la hoja con la caja contenedora que hallo la segmentacion.
    # Si la region es demasiado pequena se descarta: recortarla dejaria una
    # imagen vacia o casi vacia que solo produciria ruido en el clasificador.
    fila_ini, col_ini, fila_fin, col_fin = principal["bbox"]
    if fila_fin - fila_ini < 8 or col_fin - col_ini < 8:
        return None
    with Image.open(image_path) as img:
        img.convert("RGB").crop((col_ini, fila_ini, col_fin, fila_fin)).save(destino)
    return destino


def nombre_panel(image_path):
    # Un panel por imagen, no un nombre fijo: si el diagnostico se repite sobre
    # otra foto el panel anterior no debe sobrescribirse ni quedar huerfano.
    limpio = re.sub(r"[^A-Za-z0-9._-]+", "_", Path(image_path).stem)
    return (limpio[:60] or "imagen").strip("_") or "imagen"


def paso_segmentacion(image_path):
    # Aplica el pipeline de la semana 09 (Otsu sobre saturacion + regiones)
    # a la imagen que se quiere diagnosticar, en vez de a una imagen fija.
    print_step(2, "Segmentacion de la hoja (semana 09)")
    info = semana09_vision.analizar_imagen(image_path)

    print(f"  Umbral Otsu sobre saturacion: {info['umbral']:.4f}")
    print(f"  Umbral Otsu sobre gris: {info['canales']['gris']:.4f}")
    print(f"  Regiones detectadas: {info['total_regiones']}")

    filas, columnas = info["gris"].shape
    if min(filas, columnas) < 32:
        print(f"  AVISO: la imagen mide {columnas}x{filas} px. Por debajo de 32 px "
              "por lado los bordes y el umbral no son fiables.")

    principal = info["principal"]
    if principal is None:
        print("  No se hallo una region de hoja sobre el area minima.")
        print("  Se usara la imagen completa para clasificar.")
    else:
        print(f"  Region principal: {principal['area']} px "
              f"({info['cobertura']:.1%} de la imagen)")
        print(f"  bbox={principal['bbox']} centroide={principal['centroide']} "
              f"solidez={principal['solidez']}")

    panel = ARTIFACTS_DIR / f"diagnostico_{nombre_panel(image_path)}.png"
    semana09_vision.generar_panel(image_path, panel, limpiar=True)
    print(f"  Evidencia visual: artifacts/{panel.name}")
    return info


def run(image_path=None, indice_muestra=0):
    model, class_map = load_model()

    class_real = None
    if image_path is None:
        test_df = load_split("test.csv")
        fila = test_df.iloc[indice_muestra]
        image_path = str(RAW_DIR / fila["filepath"])
        class_real = fila["class_name"]
        print("=" * 60)
        print("  MODO MUESTRA: no se indicó ninguna imagen.")
        print(f"  Se usa test.csv fila {indice_muestra}: {Path(image_path).name}")
        print(f"  Clase real de esa foto: {class_real}")
        print("  Para diagnosticar TU foto, pasa la ruta o usa el selector.")
        print("=" * 60)

    print_header(image_path)

    print_step(1, "Carga y preprocesamiento de imagen")
    img = Image.open(image_path)
    w, h = img.size
    print(f"  Tamano original: {w}x{h} RGB")
    print(f"  Preprocesada: 64x64 -> 12288 features")

    info = paso_segmentacion(image_path)

    print_step(3, "Clasificacion (semana 02)")
    with tempfile.TemporaryDirectory() as tmp:
        ruta_clasificacion = image_path
        if USAR_RECORTE and info["principal"] is not None:
            recorte = recortar_hoja(image_path, info["principal"],
                                    Path(tmp) / "recorte.png")
            if recorte is not None:
                ruta_clasificacion = str(recorte)
                print(f"  Region de interes: recorte de la hoja "
                      f"({info['principal']['area']} px de "
                      f"{info['cobertura']:.1%} de la imagen)")

        class_pred, confidence = predict_single(model, class_map, ruta_clasificacion)

    print(f"  Modelo: StandardScaler + LogisticRegression")
    print(f"  Clase detectada: {class_pred}")
    print(f"  Confianza: {confidence:.1%}")
    if class_real is not None:
        print(f"  Clase real: {class_real}")

    print_step(4, "Taxonomia (semana 03)")
    category = classify_class(class_pred)

    print_step(5, "Plan de recuperacion (semana 04)")
    plan, total, expanded, cat = diagnose_recovery(class_pred)

    if cat == "Plantas sanas":
        print("  La planta esta sana. No se requiere tratamiento.")
    else:
        grafo = TRATAMIENTOS.get(cat, TRATAMIENTOS["Sin clasificar"])
        print(f"\n  Grafo de tratamientos ({cat}):")
        for estado, acciones in grafo.items():
            for accion, nxt, step in acciones:
                print(f"    {estado:20s} --{accion:25s} (+{step})--> {nxt}")

        print(f"\n  Recorrido A*:")
        if plan:
            print(f"    inicio -> ", end="")
            for i, (origen, accion, step, nxt) in enumerate(plan):
                if i < len(plan) - 1:
                    print(f"{accion} (+{step}) -> ", end="")
                else:
                    print(f"{accion} (+{step}) -> {nxt}")
        show_plan(plan, total, expanded)

    print("\n" + "=" * 60)
    print("  Diagnostico completado")
    print("=" * 60)


def main():
    argumentos = sys.argv[1:]
    if argumentos and argumentos[0] == "--test":
        indice = int(argumentos[1]) if len(argumentos) > 1 else 0
        run(None, indice_muestra=indice)
        return

    if argumentos:
        run(argumentos[0])
        return

    image_path = ask_image()
    if not image_path:
        print("No se selecciono ninguna imagen.")
        return
    run(image_path)


if __name__ == "__main__":
    main()