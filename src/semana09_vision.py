

import matplotlib

matplotlib.use("Agg")

from pathlib import Path

import matplotlib.pyplot as plt
import numpy as np
from skimage import color, feature, filters, io, measure, segmentation

from src.config import ARTIFACTS_DIR

RAIZ = Path(__file__).resolve().parent.parent
RUTA_IMAGEN = RAIZ / "data" / "imagen_proyecto.png"
RUTA_SALIDA = ARTIFACTS_DIR / "semana09_vision.png"

# Valores de sigma que se comparan para evidenciar el efecto del suavizado.
SIGMAS = (0.5, 1.0, 2.0, 3.0)
# Las regiones mas pequenas que esto se consideran ruido y se descartan.
AREA_MINIMA = 300


# Carga la imagen del proyecto como RGB, escala de grises y HSV en rango 0..1.
def cargar_imagen():
    rgb = io.imread(RUTA_IMAGEN)
    if np.issubdtype(rgb.dtype, np.integer):
        rgb = rgb.astype(float) / 255.0
    return rgb, color.rgb2gray(rgb), color.rgb2hsv(rgb)


# Caracteristicas de la imagen: intensidad, color y densidad de bordes.
# La mas util para el problema es la saturacion, porque separa la hoja
# (verde saturada) del fondo (gris neutro) donde el brillo no alcanza.
def extraer_caracteristicas(rgb, gris, hsv, pixeles_de_borde):
    alto, ancho = gris.shape
    return {
        "dimensiones": (alto, ancho),
        "intensidad": {
            "media": float(gris.mean()),
            "desviacion": float(gris.std()),
            "minimo": float(gris.min()),
            "maximo": float(gris.max()),
        },
        "color": {
            "rojo": float(rgb[..., 0].mean()),
            "verde": float(rgb[..., 1].mean()),
            "azul": float(rgb[..., 2].mean()),
            "tono": float(hsv[..., 0].mean()),
            "saturacion": float(hsv[..., 1].mean()),
            "brillo": float(hsv[..., 2].mean()),
        },
        "bordes": {
            "pixeles": int(pixeles_de_borde),
            "porcentaje": float(pixeles_de_borde / gris.size * 100),
        },
    }


# Aplica Canny con distintos sigma. El sigma controla el suavizado previo:
# valores bajos conservan el detalle fino y el ruido, valores altos eliminan
# ruido pero pueden borrar los bordes finos de las lesiones.
def barrido_sigma(gris):
    bordes = {sigma: feature.canny(gris, sigma=sigma) for sigma in SIGMAS}
    conteo = {sigma: int(mascara.sum()) for sigma, mascara in bordes.items()}
    return bordes, conteo


# Segmenta la hoja del fondo aplicando Otsu sobre el canal de saturacion.
# Devuelve el umbral, la mascara binaria y el detalle de por que se eligio
# este canal en lugar de la escala de grises.
def segmentar_hoja(gris, hsv):
    saturacion = hsv[..., 1]
    return (
        float(filters.threshold_otsu(saturacion)),
        saturacion > filters.threshold_otsu(saturacion),
        {
            "gris": float(filters.threshold_otsu(gris)),
            "saturacion": float(filters.threshold_otsu(saturacion)),
            "brillo": float(filters.threshold_otsu(hsv[..., 2])),
        },
    )


# Etiqueta las regiones conectadas de la mascara y descarta las micromarcas.
# Cada region real aporta area, caja contenedora, centroide y solidez: las
# tres ultimas son caracteristicas de forma y posicion del objeto.
def analizar_regiones(mascara):
    etiquetas, total = measure.label(mascara, return_num=True)
    regiones = []
    for region in measure.regionprops(etiquetas):
        if region.area < AREA_MINIMA:
            continue
        fila_ini, col_ini, fila_fin, col_fin = (int(v) for v in region.bbox)
        area_caja = max((fila_fin - fila_ini) * (col_fin - col_ini), 1)
        regiones.append({
            "etiqueta": int(region.label),
            "area": int(region.area),
            "bbox": (fila_ini, col_ini, fila_fin, col_fin),
            "centroide": (round(float(region.centroid[0]), 1),
                          round(float(region.centroid[1]), 1)),
            "solidez": round(float(region.area) / area_caja, 3),
        })
    regiones.sort(key=lambda r: r["area"], reverse=True)
    return etiquetas, total, regiones


# Figura 2x3 con la evidencia visual: original, tres sigma, mascara y regiones.
def generar_evidencia(rgb, bordes, mascara, etiquetas, conteo, umbral, salida):
    fig, axes = plt.subplots(2, 3, figsize=(13, 8))

    paneles = [
        (rgb, None, "Original"),
        (bordes[0.5], "gray", f"Canny sigma=0.5 ({conteo[0.5]} px)"),
        (bordes[2.0], "gray", f"Canny sigma=2.0 ({conteo[2.0]} px)"),
        (bordes[3.0], "gray", f"Canny sigma=3.0 ({conteo[3.0]} px)"),
        (mascara, "gray", f"Mascara Otsu (umbral={umbral:.3f})"),
        (segmentation.mark_boundaries(rgb, etiquetas, color=(1.0, 0.0, 0.0)),
         None, "Regiones conectadas"),
    ]

    for ax, (imagen, cmap, titulo) in zip(axes.ravel(), paneles):
        ax.imshow(imagen, cmap=cmap)
        ax.set_title(titulo, fontsize=11)
        ax.axis("off")

    fig.suptitle("Semana 09 - Contornos (Canny), umbral (Otsu) y regiones",
                 fontsize=13)
    fig.tight_layout()
    salida.parent.mkdir(parents=True, exist_ok=True)
    fig.savefig(salida, dpi=160)
    plt.close(fig)


# Ejecuta el pipeline completo e imprime la evidencia numerica.
def run():
    print("=" * 70)
    print("SEMANA 09 - RECONOCIMIENTO DE IMAGENES")
    print("=" * 70)
    print(f"  Imagen: {RUTA_IMAGEN.relative_to(RAIZ)}")
    print("  Flujo: caracteristicas -> Canny -> Otsu -> regiones conectadas\n")

    rgb, gris, hsv = cargar_imagen()
    bordes, conteo = barrido_sigma(gris)
    umbral, mascara, umbrales = segmentar_hoja(gris, hsv)
    etiquetas, total, regiones = analizar_regiones(mascara)

    caracteristicas = extraer_caracteristicas(rgb, gris, hsv, conteo[1.0])
    alto, ancho = caracteristicas["dimensiones"]

    print("[DIMENSIONES] {}x{} px ({} pixeles)".format(alto, ancho, gris.size))

    print("\n[CARACTERISTICAS] Intensidad")
    for nombre, valor in caracteristicas["intensidad"].items():
        print(f"  {nombre:<12s} {valor:.4f}")

    print("\n[CARACTERISTICAS] Color (medias de canal)")
    for nombre, valor in caracteristicas["color"].items():
        print(f"  {nombre:<12s} {valor:.4f}")

    print("\n[CARACTERISTICAS] Bordes")
    bordes_info = caracteristicas["bordes"]
    print(f"  sigma=1.0     {bordes_info['pixeles']} px "
          f"({bordes_info['porcentaje']:.2f}% de la imagen)")

    print("\n[CANNY] Efecto del parametro sigma")
    for sigma in SIGMAS:
        porcentaje = conteo[sigma] / gris.size * 100
        print(f"  sigma={sigma:<4} {conteo[sigma]:>6} px de borde ({porcentaje:5.2f}%)")

    print("\n[OTSU] Umbrales automaticos por canal")
    for canal in ("gris", "brillo", "saturacion"):
        print(f"  {canal:<12s} {umbrales[canal]:.4f}")
    print(f"  Umbral usado sobre saturacion: {umbral:.4f}")
    print(f"  Pixeles por encima del umbral: {int(mascara.sum())} "
          f"({mascara.mean() * 100:.1f}% de la imagen)")

    print(f"\n[REGIONES] {total} regiones etiquetadas en total")
    print(f"[REGIONES] {len(regiones)} region(es) real(es) "
          f"(area >= {AREA_MINIMA} px)")
    for region in regiones:
        print(f"  region {region['etiqueta']:>3}: area={region['area']:>6} px "
              f"({region['area'] / gris.size * 100:5.2f}% de la imagen) "
              f"bbox={region['bbox']} centroide={region['centroide']} "
              f"solidez={region['solidez']}")

    descartadas = total - len(regiones)
    print(f"  {descartadas} regiones descartadas por area menor a {AREA_MINIMA} px")

    generar_evidencia(rgb, bordes, mascara, etiquetas, conteo, umbral,
                      RUTA_SALIDA)
    print(f"\n[ARTEFACTO] Guardado: {RUTA_SALIDA.relative_to(RAIZ)}")

    print("\n" + "=" * 70)
    print("Semana 09 completada.")
    print("=" * 70)


if __name__ == "__main__":
    run()