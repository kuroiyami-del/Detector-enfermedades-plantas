# Semana 10 — Reconocimiento de imágenes: segmentación, regiones y textura

Área: visión por computador (procesamiento de imágenes).
Tema: segmentación por histogramas (umbral de Otsu), etiquetado de regiones
(`measure.label`) y textura con patrones binarios locales (LBP).

## Imágenes usadas

| Imagen | Ruta | Descripción | Tamaño |
|---|---|---|---|
| Hoja de tomate con septoria | `data/imagen_proyecto.png` | Imagen de entrada del proyecto (la misma de la semana 09) | 256 × 256 RGB |
| Hoja de tomate sana | `data/imagen_proyecto_2.png` | Imagen de PlantVillage descargada para la comparación | 256 × 256 RGB |

La segunda imagen se obtuvo de **PlantVillage** (repositorio
`spMohanty/PlantVillage-Dataset`, clase `Tomato___healthy`), porque en el
repositorio `data/raw/` está ignorado por Git y no contiene las fotos del
dataset. Así la comparación queda dentro del dominio del proyecto (hojas de
tomate de PlantVillage) y no con las imágenes genéricas `data.coins()` /
`data.brick()` de la guía de clase.

## Flujo ejecutado

```
python -m src.semana10_texturas
```

Pipeline de cada imagen:

```
imagen -> escala de grises -> umbral de Otsu -> measure.label
       -> filtro de área (> 50 px) -> histograma de intensidad (32 bins)
       -> textura LBP (R=2, P=16, method="uniform") -> vector de 53 valores
```

## Interpretación del histograma de intensidad

El histograma se calcula con **32 intervalos** y `density=True`, por lo que el
área bajo la curva suma 1 y dos imágenes de distinto contenido se comparan en
la misma escala. En ambas hojas el grueso de los píxeles se concentra en la
zona media-alta de intensidad (la hoja, que es la parte más brillante sobre el
fondo):

- **Septoria:** el pico está en el intervalo 17 con densidad **6.482**; la
  distribución decae rápido hacia intensidades bajas (fondo) y es más ancha en
  la zona media, coherente con una hoja con manchas que rompen la uniformidad.
- **Sana:** el pico está en el intervalo 15 con densidad **5.425** y la
  distribución es más suave en torno al pico, sin colas laterales tan marcadas
  como las de la hoja enferma.

En los dos casos el histograma confirma que la hoja (brillante) y el fondo
(oscuro) sí se separan en el canal de intensidad, aunque de forma imperfecta:
por eso Otsu funciona como primer corte, pero necesita el filtro de área para
quedarse solo con las regiones grandes.

## Regiones y filtro de área

| Imagen | Umbral Otsu | Regiones totales | Regiones > 50 px | Descartadas | Área media (px) | Desviación estándar (px) |
|---|---|---|---|---|---|---|
| Tomate con septoria | 0.4202 | 684 | **5** | 679 | 8215.40 | 16284.81 |
| Tomate sana | 0.3890 | 496 | **1** | 495 | 42565.00 | 0.00 |

**¿Fue adecuado el filtro?** Sí, para separar señal de ruido: en la hoja con
septoria el umbral crudo fragmenta la imagen en 684 etiquetas, casi todas
micromarcas del fondo, y al exigir más de 50 px quedan solo 5 regiones grandes.
En la hoja sana queda una única región (la hoja completa, 42565 px), que es el
resultado esperado. La desviación estándar tan alta en la enferma (16284.81)
frente a la sana (0.00) es informativa: la hoja con manchas se parte en regiones
de tamaños muy distintos, mientras que la sana forma un bloque homogéneo.

## Efecto de cambiar el umbral

Se probó el umbral de Otsu y desplazamientos de ±0.05 y ±0.10:

| Imagen | Umbral | Regiones totales | Regiones > 50 px | Área media (px) |
|---|---|---|---|---|
| Septoria | 0.3202 | 70 | 1 | 59255.0 |
| Septoria | 0.3702 | 145 | 2 | 26501.5 |
| Septoria | **0.4202** | **684** | **5** | **8215.4** |
| Septoria | 0.4702 | 1091 | 6 | 4786.0 |
| Septoria | 0.5202 | 1319 | 19 | 489.3 |
| Sana | 0.2890 | 177 | 2 | 29120.0 |
| Sana | 0.3390 | 680 | 4 | 12594.8 |
| Sana | **0.3890** | **496** | **1** | **42565.0** |
| Sana | 0.4390 | 723 | 7 | 3968.0 |
| Sana | 0.4890 | 2126 | 19 | 321.8 |

Subir el umbral (cortar a intensidades más altas) **fragmenta** la imagen en más
regiones y **encoge** el área media, porque el corte va dejando fuera píxeles de
la hoja y separando zonas. Bajarlo ocurre lo contrario: menos regiones y
regiones más grandes, hasta fusionar la hoja con zonas del fondo. El umbral de
Otsu queda en un punto intermedio razonable; por eso se usa como valor por
defecto y no un valor fijo.

## ¿Qué representa LBP?

LBP (*Local Binary Pattern*) es una medida de **textura**. Para cada píxel se
compara su intensidad con la de `points` vecinos situados a un radio `radius`;
cada comparación aporta un 0 (vecino más oscuro) o un 1 (vecino más claro), y el
patrón binario resultante se resume en un número. `method="uniform"` agrupa los
patrones con como mucho dos transiciones 0→1 (los más frecuentes en texturas
reales) y acumula todos los demás en una sola etiqueta. Con `points=16` hay
`16 + 2 = 18` valores posibles, y su histograma (`density=True`) describe qué
proporción de la imagen tiene cada tipo de textura: valores concentrados en los
patrones uniformes indican superficies lisas y regulares; una gran proporción
en la etiqueta no uniforme indica textura rugosa o con mucho detalle.

En ambas hojas la etiqueta no uniforme (índice 17) concentra la mayor masa:
**0.454** en la hoja con septoria y **0.500** en la sana. Es decir, en las dos
predomina una textura fina (nervaduras, borde de la hoja y, en la enferma, las
manchas) más que una superficie perfectamente lisa.

## Dimensión del vector de características

El vector concatena las tres partes y tiene **53 valores**:

```
[ área media (1) , desviación estándar del área (1) , cantidad de regiones (1) ]  =  3
[ histograma de intensidad, 32 bins ]                                            = 32
[ histograma LBP, 16 + 2 = 18 bins ]                                             = 18
                                                                        TOTAL    = 53
```

Guardado en `artifacts/semana10_features.npy` (un diccionario con el vector y los
histogramas de cada imagen). El programa imprime `DIMENSION DEL VECTOR: 53` para
las dos imágenes.

## Comparación de las dos imágenes

| Característica | Tomate con septoria | Tomate sana |
|---|---|---|
| Umbral de Otsu | 0.4202 | 0.3890 |
| Regiones totales | 684 | 496 |
| Regiones > 50 px | 5 | 1 |
| Área media | 8215.40 px | 42565.00 px |
| Desviación estándar del área | 16284.81 px | 0.00 px |
| Pico del histograma de intensidad | bin 17 → 6.482 | bin 15 → 5.425 |
| Etiqueta LBP no uniforme | 0.454 | 0.500 |
| Dimensión del vector | 53 | 53 |

Lectura conjunta: la hoja **sana** produce una única región grande y homogénea
(alta área media, desviación 0) y un histograma de intensidad más suave; la hoja
con **septoria** se rompe en varias regiones de tamaños muy dispares
(desviación muy alta) y su histograma tiene colas más marcadas por las manchas.
La textura LBP cambia menos entre ambas (ambas son hojas y comparten nervaduras y
borde), lo que indica que LBP por sí sola no separa sano/enfermo: aporta
información complementaria a las regiones y al histograma.

## Limitaciones

- El umbral de Otsu asume que la imagen tiene dos grupos de píxeles bien
  separados; con iluminación heterogénea o fondos complejos la segmentación se
  fragmenta (684 regiones en la hoja enferma) y depende mucho del filtro de área.
- El filtro de área es un valor fijo (50 px) pensado para imágenes de 256×256;
  en imágenes de otra resolución habría que reescalarlo.
- LBP con `uint8` cuantiza la intensidad a 256 niveles; cambios de brillo o de
  contraste afectan al histograma.
- El vector mezcla magnitudes con escalas muy distintas (área en miles de px y
  densidades entre 0 y 1); antes de alimentar un clasificador conviene
  normalizarlo (por ejemplo `StandardScaler`).

## Uso posterior en un clasificador

El vector de 53 valores es una representación compacta de cada hoja y se puede
usar como entrada de un clasificador (regresión logística o la MLP de la semana
08) para distinguir **sana vs. enferma**, o entre enfermedades. Para ello el
siguiente paso sería extraer este vector para todo el dataset etiquetado y
normalizarlo por columna. La ventaja frente a usar los píxeles crudos es que el
vector es pequeño y resume información interpretable (tamaño de las regiones,
distribución de intensidad y textura). Como se observó en la comparación, la
textura sola no basta: el mayor poder discriminativo está en las estadísticas de
regiones y en el histograma de intensidad.
