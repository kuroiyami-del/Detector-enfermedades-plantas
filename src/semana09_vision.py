import matplotlib

matplotlib.use("Agg")

from pathlib import Path

import matplotlib.pyplot as plt
import numpy as np
from skimage import color, feature, filters, io, measure, morphology, segmentation

from src.config import ARTIFACTS_DIR

RAIZ = Path(__file__).resolve().parent.parent
RUTA_IMAGEN = RAIZ / "data" / "imagen_proyecto.png"
RUTA_SALIDA = ARTIFACTS_DIR / "semana09_vision.png"

# Valores de sigma que se comparan para evidenciar el efecto del suavizado.
SIGMAS = (0.5, 1.0, 2.0, 3.0)
# Las regiones mas pequenas que esto se consideran ruido y se descartan.
AREA_MINIMA = 300
# Sigma que se usa para la caracteristica de densidad de bordes. Se declara
# aqui para no repetir el valor 1.0 en el calculo y en la impresion.
SIGMA_BORDES = 1.0


# Carga una imagen como RGB, escala de grises y HSV en rango 0..1.
# Acepta cualquier archivo porque tambien la usa el diagnostico con la imagen
# que sube el usuario: una imagen en escala de grises o con canal alfa se
# convierte a RGB para que el resto del pipeline sea identico.
#
# Todas las conversiones de entrada se dejan visibles aqui, en un solo lugar:
#   1. lectura del archivo;
#   2. normalizacion a float en el rango 0..1;
#   3. garantia de tres canales (RGB);
#   4. conversion a escala de grises, que representa la intensidad;
#   5. conversion a HSV, que permite trabajar tono, saturacion y brillo.
def cargar_imagen(ruta=RUTA_IMAGEN):
    rgb = io.imread(ruta)
    if np.issubdtype(rgb.dtype, np.integer):
        rgb = rgb.astype(float) / 255.0
    if rgb.ndim == 2:
        rgb = np.dstack([rgb] * 3)
    elif rgb.shape[2] == 4:
        rgb = color.rgba2rgb(rgb)
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
# Devuelve las mascaras de borde de cada sigma y cuantos pixeles marco cada una.
def barrido_sigma(gris):
    bordes = {sigma: feature.canny(gris, sigma=sigma) for sigma in SIGMAS}
    conteo = {sigma: int(mascara.sum()) for sigma, mascara in bordes.items()}
    return bordes, conteo


# Segmenta la hoja del fondo aplicando Otsu sobre el canal de saturacion.
# Devuelve el umbral, la mascara binaria y el detalle de por que se eligio
# este canal en lugar de la escala de grises.
def segmentar_hoja(gris, hsv):
    # Otsu separa el objeto del fondo calculando el umbral que maximiza la
    # separacion entre dos grupos de pixeles. Aqui se usa la SATURACION porque
    # la hoja es verde saturada y el fondo es gris neutro: el brillo no
    # distingue bien porque la sombra tambien es oscura.
    saturacion = hsv[..., 1]
    umbral = float(filters.threshold_otsu(saturacion))
    mascara = saturacion > umbral
    return (
        umbral,
        mascara,
        {
            # Estos otros dos umbrales no se usan para segmentar: se calculan
            # y se muestran como evidencia de por que la saturacion es mejor.
            "gris": float(filters.threshold_otsu(gris)),
            "saturacion": umbral,
            "brillo": float(filters.threshold_otsu(hsv[..., 2])),
        },
    )


# Cierra los huecos de la mascara y descarta el ruido para que la hoja cuente
# como una sola region. Sin este paso la segmentacion queda fragmentada: en la
# imagen de la demostracion se etiquetan 14 regiones, y el promedio sobre el
# conjunto de prueba es de 143 regiones, con un bbox de la region mayor que ya
# no describe la hoja entera.
def limpiar_mascara(mascara):
    # closing: dilatacion seguida de erosion, une interrupciones y cierra huecos.
    limpio = morphology.closing(mascara, morphology.disk(3))
    # remove_small_holes: rellena huecos interiores menores a 500 pixeles.
    limpio = morphology.remove_small_holes(limpio, max_size=500)
    # remove_small_objects: descarta micromarcas sueltas menores a AREA_MINIMA.
    return morphology.remove_small_objects(limpio, max_size=AREA_MINIMA)


# Aplica la segmentacion y, si se pide, la limpieza de la mascara.
# Es el unico lugar del modulo donde vive la secuencia segmentar -> limpiar,
# de modo que el comportamiento con y sin limpieza queda explicito en la
# llamada y no repetido en cada consumidor.
def segmentar_y_limpiar(gris, hsv, limpiar=True):
    umbral, mascara, umbrales = segmentar_hoja(gris, hsv)
    if limpiar:
        mascara = limpiar_mascara(mascara)
    return umbral, mascara, umbrales


# Etiqueta las regiones conectadas de la mascara y descarta las micromarcas.
# Cada region real aporta area, caja contenedora, centroide y solidez.
# El bbox y el centroide describen la posicion y el tamano de la region, y la
# solidez describe cuanto ocupa la region dentro de su propia caja.
def analizar_regiones(mascara):
    etiquetas, total = measure.label(mascara, return_num=True)
    regiones = []
    for region in measure.regionprops(etiquetas):
        if region.area < AREA_MINIMA:
            continue
        fila_ini, col_ini, fila_fin, col_fin = (int(borde) for borde in region.bbox)
        # El max evita dividir entre cero si el bbox llegara a tener area nula.
        area_caja = max((fila_fin - fila_ini) * (col_fin - col_ini), 1)
        regiones.append({
            "etiqueta": int(region.label),
            "area": int(region.area),
            "bbox": (fila_ini, col_ini, fila_fin, col_fin),
            "centroide": (round(float(region.centroid[0]), 1),
                          round(float(region.centroid[1]), 1)),
            # Solidez: cuanto de la caja contenedora ocupa realmente la region.
            # No es la solidez como area sobre envolvente convexa, sino la
            # razon area / area del bounding box, es decir, la densidad de la
            # region dentro de su rectangulo.
            "solidez": round(float(region.area) / area_caja, 3),
        })
    # Ordenar de mayor a menor area garantiza que regiones[0] sea siempre la
    # region principal, que es la que usan analizar_imagen y el diagnostico.
    regiones.sort(key=lambda region: region["area"], reverse=True)
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


# Panel 2x3 de una imagen arbitraria, para dejar evidencia del diagnostico.
def generar_panel(ruta, salida, limpiar=False):
    rgb, gris, hsv = cargar_imagen(ruta)
    bordes, conteo = barrido_sigma(gris)
    umbral, mascara, _ = segmentar_y_limpiar(gris, hsv, limpiar=limpiar)
    etiquetas, _, _ = analizar_regiones(mascara)
    generar_evidencia(rgb, bordes, mascara, etiquetas, conteo, umbral, salida)
    return salida


# Aplica el pipeline de vision a cualquier imagen y devuelve un resumen.
# Es el punto de entrada que reutiliza el diagnostico para procesar la imagen
# que sube el usuario, sin depender de data/imagen_proyecto.png.
def analizar_imagen(ruta, limpiar=True):
    rgb, gris, hsv = cargar_imagen(ruta)
    umbral, mascara, canales = segmentar_y_limpiar(gris, hsv, limpiar=limpiar)
    etiquetas, total, regiones = analizar_regiones(mascara)
    principal = regiones[0] if regiones else None
    return {
        "ruta": str(ruta),
        "gris": gris,
        "mascara": mascara,
        "etiquetas": etiquetas,
        "umbral": umbral,
        "canales": canales,
        "total_regiones": total,
        "regiones": regiones,
        "principal": principal,
        "cobertura": (principal["area"] / gris.size) if principal else 0.0,
    }


# Imprime dimensiones, intensidad, color y densidad de bordes.
def imprimir_caracteristicas(caracteristicas, total_pixeles):
    alto, ancho = caracteristicas["dimensiones"]
    print("[DIMENSIONES] {}x{} px ({} pixeles)".format(alto, ancho, total_pixeles))

    print("\n[CARACTERISTICAS] Intensidad")
    for nombre, valor in caracteristicas["intensidad"].items():
        print(f"  {nombre:<12s} {valor:.4f}")

    print("\n[CARACTERISTICAS] Color (medias de canal)")
    for nombre, valor in caracteristicas["color"].items():
        print(f"  {nombre:<12s} {valor:.4f}")

    print("\n[CARACTERISTICAS] Bordes")
    bordes_info = caracteristicas["bordes"]
    print(f"  sigma={SIGMA_BORDES}     {bordes_info['pixeles']} px "
          f"({bordes_info['porcentaje']:.2f}% de la imagen)")


# Imprime el experimento de Canny: como cae la cantidad de pixeles de borde
# cuando sigma sube, porque el suavizado previo elimina el ruido.
def imprimir_barrido_sigma(conteo, total_pixeles):
    print("\n[CANNY] Efecto del parametro sigma")
    for sigma in SIGMAS:
        porcentaje = conteo[sigma] / total_pixeles * 100
        print(f"  sigma={sigma:<4} {conteo[sigma]:>6} px de borde ({porcentaje:5.2f}%)")


# Imprime los tres umbrales de Otsu para comparar los canales y dejar claro
# que la segmentacion se apoya en la saturacion.
def imprimir_otsu(umbrales, umbral, mascara):
    print("\n[OTSU] Umbrales automaticos por canal")
    for canal in ("gris", "brillo", "saturacion"):
        print(f"  {canal:<12s} {umbrales[canal]:.4f}")
    print(f"  Umbral usado sobre saturacion: {umbral:.4f}")
    print(f"  Pixeles por encima del umbral: {int(mascara.sum())} "
          f"({mascara.mean() * 100:.1f}% de la imagen)")


# Imprime las regiones conectas y cuanto se descarto por el filtro de area.
def imprimir_regiones(total, regiones, total_pixeles):
    print(f"\n[REGIONES] {total} regiones etiquetadas en total")
    print(f"[REGIONES] {len(regiones)} region(es) real(es) "
          f"(area >= {AREA_MINIMA} px)")
    for region in regiones:
        print(f"  region {region['etiqueta']:>3}: area={region['area']:>6} px "
              f"({region['area'] / total_pixeles * 100:5.2f}% de la imagen) "
              f"bbox={region['bbox']} centroide={region['centroide']} "
              f"solidez={region['solidez']}")

    descartadas = total - len(regiones)
    print(f"  {descartadas} regiones descartadas por area menor a {AREA_MINIMA} px")


# Ejecuta el pipeline completo e imprime la evidencia numerica.
# run() solo coordina: cada bloque del flujo vive en su propia funcion.
def run():
    print("=" * 70)
    print("SEMANA 09 - RECONOCIMIENTO DE IMAGENES")
    print("=" * 70)
    print(f"  Imagen: {RUTA_IMAGEN.relative_to(RAIZ)}")
    print("  Flujo: caracteristicas -> Canny -> Otsu -> regiones conectadas\n")

    rgb, gris, hsv = cargar_imagen()
    bordes, conteo = barrido_sigma(gris)
    # La demostracion usa la mascara SIN limpiar para mostrar el estado crudo
    # de la segmentacion. El diagnostico, en cambio, si la limpia.
    umbral, mascara, umbrales = segmentar_y_limpiar(gris, hsv, limpiar=False)
    etiquetas, total, regiones = analizar_regiones(mascara)
    caracteristicas = extraer_caracteristicas(rgb, gris, hsv, conteo[SIGMA_BORDES])

    imprimir_caracteristicas(caracteristicas, gris.size)
    imprimir_barrido_sigma(conteo, gris.size)
    imprimir_otsu(umbrales, umbral, mascara)
    imprimir_regiones(total, regiones, gris.size)

    generar_evidencia(rgb, bordes, mascara, etiquetas, conteo, umbral,
                      RUTA_SALIDA)
    print(f"\n[ARTEFACTO] Guardado: {RUTA_SALIDA.relative_to(RAIZ)}")

    print("\n" + "=" * 70)
    print("Semana 09 completada.")
    print("=" * 70)


if __name__ == "__main__":
    run()