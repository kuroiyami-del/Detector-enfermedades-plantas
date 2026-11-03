import matplotlib

matplotlib.use("Agg")

from pathlib import Path

import matplotlib.pyplot as plt
import numpy as np
from skimage import color, feature, filters, io, measure

from src.config import ARTIFACTS_DIR

RAIZ = Path(__file__).resolve().parent.parent
RUTA_SALIDA_FEATURES = ARTIFACTS_DIR / "semana10_features.npy"
RUTA_SALIDA_HISTOGRAMA = ARTIFACTS_DIR / "semana10_histograma.png"

# Imagen de referencia (hoja sana de PlantVillage) contra la que la interfaz
# web compara la imagen que sube el usuario en la pestana Semana 10.
IMAGEN_REFERENCIA = RAIZ / "data" / "imagen_proyecto_2.png"

# Las dos imagenes del dominio que se comparan por defecto en consola. La
# primera es la hoja de tomate con septoria que ya usa la semana 09; la segunda
# es una hoja de tomate sana de PlantVillage, para contrastar regiones,
# histograma y textura.
IMAGENES = (
    ("Tomate con septoria", RAIZ / "data" / "imagen_proyecto.png"),
    ("Tomate sana", IMAGEN_REFERENCIA),
)

# Una region con menos area que esto se considera ruido y no se cuenta.
AREA_MINIMA = 50
# Numero de intervalos del histograma de intensidad.
BINS_INTENSIDAD = 32
# Parametros de la textura LBP (patrones binarios locales).
LBP_RADIUS = 2
LBP_POINTS = 16
LBP_METHOD = "uniform"


# Carga la imagen y la pasa a escala de grises.
def cargar_imagen(ruta):
    imagen = io.imread(ruta)
    if np.issubdtype(imagen.dtype, np.integer):
        imagen = imagen.astype(float) / 255.0
    if imagen.ndim == 2:
        return imagen
    if imagen.shape[2] == 4:
        imagen = color.rgba2rgb(imagen)
    return color.rgb2gray(imagen)


# Otsu corta la imagen y separa la hoja del fondo.
def calcular_umbral_otsu(gris):
    umbral = float(filters.threshold_otsu(gris))
    mascara = gris > umbral
    return umbral, mascara


# Numera cada grupo de pixeles conectados de la hoja.
def etiquetar_regiones(mascara):
    etiquetas, total = measure.label(mascara, return_num=True)
    return etiquetas, int(total)


# Cuenta las regiones grandes: area media y variacion.
def estadisticas_regiones(etiquetas):
    areas = np.array([region.area for region in measure.regionprops(etiquetas)])
    areas = areas[areas > AREA_MINIMA]
    if areas.size == 0:
        return {"cantidad": 0, "area_media": 0.0, "area_desviacion": 0.0,
                "areas": areas}
    return {
        "cantidad": int(areas.size),
        "area_media": float(areas.mean()),
        "area_desviacion": float(areas.std()),
        "areas": areas,
    }


# Cuenta cuanto hay de cada tono de gris.
def histograma_intensidad(gris):
    histograma, _ = np.histogram(gris, bins=BINS_INTENSIDAD, density=True)
    return histograma


# Compara cada pixel con sus vecinos para medir la textura.
def textura_lbp(gris):
    # LBP compara valores entre pixeles vecinos: en una imagen float 0..1
    # diferencias minimas de redondeo cambiarian el patron. Por eso se pasa a
    # enteros 0..255, que es el tipo recomendado por scikit-image.
    gris_uint8 = np.clip(gris * 255.0, 0, 255).astype(np.uint8)
    lbp = feature.local_binary_pattern(
        gris_uint8, P=LBP_POINTS, R=LBP_RADIUS, method=LBP_METHOD
    )
    num_bins = LBP_POINTS + 2
    histograma, _ = np.histogram(
        lbp, bins=num_bins, range=(0, num_bins), density=True
    )
    return lbp, histograma


# Une todos los numeros y forma la ficha de 53 valores.
def construir_vector(estadisticas, hist_intensidad, hist_lbp):
    return np.concatenate([
        np.array([estadisticas["area_media"],
                  estadisticas["area_desviacion"],
                  float(estadisticas["cantidad"])]),
        np.asarray(hist_intensidad, dtype=float),
        np.asarray(hist_lbp, dtype=float),
    ])


# Ejecuta todo el proceso completo para una sola imagen.
def analizar_imagen(ruta, nombre=None):
    gris = cargar_imagen(ruta)
    umbral, mascara = calcular_umbral_otsu(gris)
    etiquetas, total = etiquetar_regiones(mascara)
    estadisticas = estadisticas_regiones(etiquetas)
    hist_intensidad = histograma_intensidad(gris)
    _, hist_lbp = textura_lbp(gris)
    vector = construir_vector(estadisticas, hist_intensidad, hist_lbp)
    return {
        "nombre": nombre or Path(ruta).name,
        "ruta": str(ruta),
        "gris": gris,
        "umbral_otsu": umbral,
        "total_regiones": total,
        "regiones": estadisticas,
        "histograma_intensidad": hist_intensidad,
        "histograma_lbp": hist_lbp,
        "vector": vector,
        "dimension": int(vector.size),
    }


# Guarda la figura comparativa entre las dos imagenes.
def generar_figura(resultados, salida):
    fig, axes = plt.subplots(len(resultados), 3,
                             figsize=(13, 4.2 * len(resultados)))
    if len(resultados) == 1:
        axes = np.array([axes])

    for fila, resultado in enumerate(resultados):
        gris = resultado["gris"]
        hist_int = resultado["histograma_intensidad"]
        hist_lbp = resultado["histograma_lbp"]

        axes[fila, 0].imshow(gris, cmap="gray")
        axes[fila, 0].set_title(
            f"{resultado['nombre']}\nOtsu={resultado['umbral_otsu']:.4f} | "
            f"{resultado['regiones']['cantidad']} regiones", fontsize=10)
        axes[fila, 0].axis("off")

        axes[fila, 1].bar(np.arange(hist_int.size), hist_int,
                          width=0.9, color="#025050")
        axes[fila, 1].set_title(
            f"Histograma de intensidad ({BINS_INTENSIDAD} bins, density=True)",
            fontsize=10)
        axes[fila, 1].set_xlabel("Intensidad")
        axes[fila, 1].set_ylabel("Densidad")

        axes[fila, 2].bar(np.arange(hist_lbp.size), hist_lbp,
                          width=0.9, color="#bfb33b")
        axes[fila, 2].set_title(
            f"Histograma LBP (R={LBP_RADIUS}, P={LBP_POINTS}, "
            f"method='{LBP_METHOD}')", fontsize=10)
        axes[fila, 2].set_xlabel("Patron LBP")
        axes[fila, 2].set_ylabel("Densidad")

    fig.suptitle("Semana 10 - Segmentacion, histograma de intensidad y textura LBP",
                 fontsize=13)
    fig.tight_layout()
    salida.parent.mkdir(parents=True, exist_ok=True)
    fig.savefig(salida, dpi=150)
    plt.close(fig)


# Guarda las fichas de las imagenes en un archivo .npy.
def guardar_features(resultados, salida):
    datos = {
        "dimension": int(resultados[0]["vector"].size),
        "area_minima": AREA_MINIMA,
        "bins_intensidad": BINS_INTENSIDAD,
        "lbp": {"radius": LBP_RADIUS, "points": LBP_POINTS,
                "method": LBP_METHOD},
        "imagenes": [
            {
                "nombre": r["nombre"],
                "ruta": r["ruta"],
                "umbral_otsu": r["umbral_otsu"],
                "total_regiones": r["total_regiones"],
                "cantidad_regiones": r["regiones"]["cantidad"],
                "area_media": r["regiones"]["area_media"],
                "area_desviacion": r["regiones"]["area_desviacion"],
                "histograma_intensidad": r["histograma_intensidad"],
                "histograma_lbp": r["histograma_lbp"],
                "vector": r["vector"],
                "dimension": r["dimension"],
            }
            for r in resultados
        ],
    }
    salida.parent.mkdir(parents=True, exist_ok=True)
    np.save(salida, datos, allow_pickle=True)
    return datos


# Muestra el resumen de cada imagen en consola.
def imprimir_resumen(resultados):
    for resultado in resultados:
        regiones = resultado["regiones"]
        print(f"\n[IMAGEN] {resultado['nombre']}")
        print(f"  ruta            : {resultado['ruta']}")
        print(f"  Umbral Otsu     : {resultado['umbral_otsu']:.4f}")
        print(f"  Regiones totales: {resultado['total_regiones']}")
        print(f"  Regiones area>{AREA_MINIMA}px: {regiones['cantidad']} "
              f"(descartadas: {resultado['total_regiones'] - regiones['cantidad']})")
        print(f"  Area media      : {regiones['area_media']:.2f} px")
        print(f"  Desviacion area : {regiones['area_desviacion']:.2f} px")
        print(f"  Histograma int. : {resultado['histograma_intensidad'].size} bins")
        print(f"  Histograma LBP  : {resultado['histograma_lbp'].size} bins")
        print(f"  DIMENSION DEL VECTOR: {resultado['dimension']}")


# Coordina el proceso, guarda artefactos y muestra resultados.
def run():
    print("=" * 70)
    print("SEMANA 10 - RECONOCIMIENTO DE IMAGENES: HEURISTICAS DE TEXTURA")
    print("=" * 70)
    print("  Flujo: imagen -> Otsu -> measure.label -> regiones")
    print("         -> histograma de intensidad -> textura LBP -> vector\n")

    resultados = [analizar_imagen(ruta, nombre) for nombre, ruta in IMAGENES]

    imprimir_resumen(resultados)

    print(f"\n[VECTOR] Parte 1: 3 valores (area media, desviacion, cantidad)")
    print(f"[VECTOR] Parte 2: {BINS_INTENSIDAD} valores (histograma intensidad)")
    print(f"[VECTOR] Parte 3: {LBP_POINTS + 2} valores (histograma LBP)")
    dimension = resultados[0]["dimension"]
    print(f"[VECTOR] Dimension total: 3 + {BINS_INTENSIDAD} + "
          f"{LBP_POINTS + 2} = {dimension}")

    guardar_features(resultados, RUTA_SALIDA_FEATURES)
    generar_figura(resultados, RUTA_SALIDA_HISTOGRAMA)

    print(f"\n[ARTEFACTO] Guardado: {RUTA_SALIDA_FEATURES.relative_to(RAIZ)}")
    print(f"[ARTEFACTO] Guardado: {RUTA_SALIDA_HISTOGRAMA.relative_to(RAIZ)}")

    print("\n" + "=" * 70)
    print("Semana 10 completada.")
    print("=" * 70)


if __name__ == "__main__":
    run()
