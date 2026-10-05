# PlantAI - Deteccion de Enfermedades en Plantas con Inteligencia Artificial

## Descripcion

Proyecto de la asignatura de Inteligencia Artificial que busca desarrollar una solucion para la deteccion o clasificacion de enfermedades en plantas a partir de imagenes. El proyecto se construye progresivamente a medida que avanzan las semanas de clase.

## Problema

La identificacion de enfermedades en cultivos es un proceso que requiere conocimiento especializado. Los agricultores pueden pasar horas o dias detectando manualmente si una planta esta enferma, lo que retrasa el tratamiento y puede provocar perdidas en la cosecha. Este proyecto busca automatizar el diagnostico visual de plantas para detectar enfermedades de forma rapida y accesible.

## Objetivo general

Desarrollar un sistema de Inteligencia Artificial capaz de clasificar imagenes de plantas en funcion de su estado de salud, diferenciando entre plantas sanas y plantas con diferentes tipos de enfermedades.

## Dataset

El proyecto utiliza el dataset **PlantVillage**, un conjunto de imagenes de hojas de plantas utilizado comunmente en investigaciones de clasificacion de enfermedades.

### Organizacion actual

- **Total de imagenes:** 54,304
- **Total de clases:** 38
- **Formato de imagenes:** JPG (escala de color RGB)
- **Ubicacion de imagenes crudas:** `data/raw/PlantVillage-Dataset/raw/color/`

### Separacion de datos

Los datos se encuentran separados en los archivos CSV dentro de `data/processed/`:

| Conjunto | Archivo | Muestras | Proporcion |
|----------|---------|----------|------------|
| Entrenamiento | `train.csv` | 38,092 | 70.1% |
| Prueba | `test.csv` | 7,967 | 14.7% |
| Validacion | `val.csv` | 8,247 | 15.2% |

## Avances realizados

### Semana 02 - Entrenamiento

- **Separacion de datos:** Conjuntos de entrenamiento y prueba en `data/processed/`.
- **Transformacion de imagenes:** Reduccion a 64x64 pixels y aplanamiento en vectores.
- **Modelo:** Pipeline de `StandardScaler + LogisticRegression`.
- **Evaluacion:** Accuracy y matriz de confusion.
- **Accuracy actual:** 66.00% (0.660)

### Semana 03 - Taxonomia de Inteligencia Artificial

- **Area principal:** Vision por computador (analisis de imagenes de plantas).
- **Area complementaria:** Aprendizaje automatico (modelo clasificador).
- **Justificacion:** El nucleo del proyecto es interpretar imagenes y entrenar un modelo con datos etiquetados.

### Semana 04 - Busqueda en espacio de estados (plan de recuperacion)

- **Area:** Busqueda informada en espacio de estados.
- **Problema:** planificar la secuencia de tratamientos de menor costo que lleve a una planta del estado enfermo detectado hacia el estado sano.
- **Estado inicial:** la enfermedad detectada por el clasificador de las semanas 02/03.
- **Metodo:** A* con f(n) = g(n) + h(n); g(n) acumula el esfuerzo de los tratamientos y h(n) es una heuristica admisible (estimacion optimista del esfuerzo restante).
- **Modelo:** grafo didactico de estados de salud (enfermedad avanzada / activa / en recuperacion / sana) con tratamientos segun el tipo de enfermedad.
- **Casos:** si el diagnostico es una planta sana, el plan es vacio; si la enfermedad es viral, el modelo reporta meta inalcanzable (sin cura, solo contencion).
- **Ejecucion:** `python -m src.semana04_busqueda`

### Semana 05 - Sistema hibrido

- **Area:** Sistemas hibridos (combinacion de tecnicas de IA).
- **Problema:** responder consultas de texto sobre problemas de plantas combinando varias tecnicas.
- **Metodo:** el sistema procesa cada consulta con 3 tecnicas: reglas de conocimiento (palabras clave), similitud de coseno con TF-IDF sobre una base de conocimiento (`data/base_conocimiento.txt`) y un clasificador LogisticRegression entrenado con descripciones etiquetadas.
- **Salida:** para cada consulta muestra las reglas activadas, el documento de evidencia mas parecido, su similitud y la clasificacion (fungica, viral, plaga o sana).
- **Ejecucion:** `python -m src.semana05_sistema_hibrido`

### Semana 07 - Representaciones

- **Area:** Representacion del conocimiento.
- **Problema:** representar formalmente el conocimiento sobre el estado de salud de una hoja y sobre que secuencias de tratamientos la llevan a estar sana.
- **Metodo:** la hoja se representa de 3 formas complementarias:
  - **Numerica:** vector `(verdor, amarillez, proporcion de manchas)` comparado con la hoja sana de referencia mediante distancia euclidiana (a mayor distancia, mas alejada de sana). La funcion `extraer_vector_hoja()` obtiene el vector real de una imagen.
  - **Simbolica:** hechos (sintomas presentes) + reglas IF-THEN concluyen una sospecha (fungica, viral, plaga).
  - **Automata:** se construye un DFA a partir de `TRATAMIENTOS` (semana 04); acepta una secuencia si termina en `healthy`.
- **Salida:** vector numerico de la hoja y su distancia a la referencia sana, la conclusion simbolica, las tablas de transicion del automata, la validacion del plan optimo de A* (aceptado), secuencias rechazadas, el caso viral (meta inalcanzable) y la planta sana (secuencia vacia aceptada).
- **Relacion con A*:** A* (semana 04) encuentra la mejor secuencia; el automata (semana 07) representa el conocimiento de cuando una secuencia es valida.
- **Ejecucion:** `python -m src.semana07_representaciones`

### Semana 08 - Red neuronal + evidencia + ontologia

- **Area:** Redes neuronales y representacion del conocimiento.
- **Problema:** reconocer la variedad y estado de salud de una hoja a partir de su imagen y dejar evidencia verificable de cada prediccion.
- **Metodo:** red neuronal **MLP** (perceptron multicapa, `MLPClassifier` con capas de 128 y 64 neuronas) entrenada con las **38 categorias de PlantVillage** (todas las plantas y sus enfermedades). Las imagenes se pasan a escala de grises 48x48 (2304 caracteristicas) y se dividen 80/20.
- **Salida:** accuracy sobre prueba, tabla real-vs-predicha, evidencia de cada prediccion en una base de datos SQLite (`artifacts/evidencia_hojas.db`) y una ontologia (`artifacts/ontologia.graphml`) que describe las relaciones del dominio (imagen -> hoja -> sintoma -> enfermedad).
- **Artefactos:** `artifacts/red_hojas.pkl` (modelo), `evidencia_hojas.db` (base de datos), `ontologia.graphml` (grafo de conceptos).
- **Relacion con las semanas previas:** la MLP (semana 08) sustituye a la regresion logistica (semana 02); la ontologia complementa las representaciones de la semana 07.
- **Ejecucion:** `python -m src.semana08_red_ontologia`

### Semana 09 - Reconocimiento de imagenes

- **Area:** Vision por computador (procesamiento de imagenes).
- **Problema:** transformar una fotografia de hoja en informacion localizable: que pixeles son hoja, donde estan sus limites y cuanta superficie ocupa.
- **Metodo:** pipeline `caracteristicas -> bordes (Canny) -> umbral (Otsu) -> regiones conectadas` con `scikit-image`. Entrada `data/imagen_proyecto.png` (hoja de tomate con septoria de PlantVillage).
- **Hallazgo:** el umbral se calcula sobre el canal de **saturacion** y no sobre la escala de grises. En gris la hoja y el fondo se separan solo 0.015 de intensidad y Otsu fragmenta la imagen en 684 regiones; en saturacion el contraste es 0.144 y quedan 14. La guia de clase usa `data.coins()` en gris, por eso la adaptacion al dominio fue necesaria.
- **Salida:** umbral Otsu, barrido de Canny con cuatro valores de sigma, y las regiones etiquetadas con area, `bbox`, centroide y solidez.
- **Artefactos:** `artifacts/semana09_vision.png` (panel 2x3: original, tres sigma, mascara y regiones).
- **Relacion con las semanas previas:** la semana 07 estima manchas con la desviacion global de la imagen (un solo numero para toda la foto); la semana 09 la sustituye por una segmentacion que si ubica y mide. El `bbox` de la hoja sirve como recorte de region de interes antes de clasificar con la red de la semana 08.
- **Ejecucion:** `python -m src.semana09_vision`

## Estructura del proyecto

```
plantas_enfermas/
├── data/
│   ├── raw/PlantVillage-Dataset/raw/color/   # 38 carpetas con imagenes JPG
│   ├── processed/                             # CSVs y class_map.json
│   ├── imagen_proyecto.png                    # Imagen de entrada (semana 09)
│   └── base_conocimiento.txt                  # Base de conocimiento (semana 05)
├── src/
│   ├── __init__.py
│   ├── config.py                   # Constantes: paths, RANDOM_STATE, IMG_SIZE
│   ├── data_loader.py              # Funciones de carga de datos
│   ├── semana02_entrenamiento.py   # Entrenamiento y evaluacion
│   ├── semana03_taxonomia.py       # Taxonomia de IA
│   ├── semana04_busqueda.py        # Busqueda A* (plan de recuperacion)
│   ├── semana05_sistema_hibrido.py # Sistema hibrido (reglas + TF-IDF + ML)
│   ├── semana07_representaciones.py # Representaciones: numerica + simbolica + automata
│   ├── semana08_red_ontologia.py    # Red neuronal MLP + evidencia SQLite + ontologia
│   ├── semana09_vision.py          # Caracteristicas + Canny + Otsu + regiones
│   └── pipeline.py                 # Pipeline integrada image→prediccion→plan
├── main.py                         # Punto de entrada (CLI)
├── server.py                       # Backend web (Flask) que sirve index.html
├── index.html                      # Interfaz web (diagnostico + barra de semanas)
├── artifacts/                      # Artefactos semana 08/09 (modelo, BD, ontologia, panel)
├── requirements.txt
└── README.md
```

## Tecnologias utilizadas

- **Python 3.11**
- **scikit-learn** - Modelos de machine learning y metricas de evaluacion
- **scikit-image** - Deteccion de bordes (Canny), umbral (Otsu) y regiones conectadas
- **matplotlib** - Generacion de la evidencia visual (`artifacts/semana09_vision.png`)
- **Pillow** - Carga y procesamiento de imagenes
- **numpy** - Operaciones con arreglos numericos
- **pandas** - Manipulacion de datos (lectura de CSVs)
- **tensorflow** - Framework de deep learning (disponible para avances futuros)
- **Flask** - Backend web que sirve `index.html` y expone el diagnostico por HTTP

## Como ejecutar

### Requisitos previos

1. Tener Python 3.11 instalado.
2. Crear y activar el entorno virtual:
   ```
   py -3.11 -m venv .venv
   .\.venv\Scripts\activate
   ```
3. Instalar dependencias:
   ```
   pip install -r requirements.txt
   ```

### Ejecutar la interfaz web

```
.\.venv\Scripts\activate
python server.py
```

Luego abrir en el navegador: **http://127.0.0.1:5000**

La pagina `index.html` ofrece la misma interfaz de la anterior version de
escritorio: seleccionar una imagen, escribir sintomas y los botones
**Diagnosticar** (imagen) y **Consultar sintomas** (texto). Los resultados se
muestran en una barra lateral por semanas:

- **Caso A (imagen):** ejecuta las semanas 02, 03, 04, 07, 08 y 09 para esa
  planta. La semana 02 es la vista por defecto. La semana 05 no aparece.
- **Caso B (sintomas):** ejecuta la semana 05 (sistema hibrido) y la marca como
  la que se esta ejecutando.

Si se envia imagen y texto a la vez, cada boton mantiene su comportamiento
independiente: "Diagnosticar" usa la imagen e ignora el texto; "Consultar
sintomas" usa el texto e ignora la imagen.

El backend `server.py` solo importa y llama a las funciones de los modulos
`src/semanaXX.py`; no modifica su logica.

### Ejecutar el proyecto completo (consola)

```
.\.venv\Scripts\activate
python main.py
```

`python main.py` abre un selector de archivos para elegir la foto de una planta;
al seleccionarla, la consola muestra la prediccion completa: preprocesamiento,
clase detectada con confianza, taxonomia y plan de recuperacion (A*).

| Comando | Que hace |
|---|---|
| `python main.py` | Abre el selector de foto y predice (por defecto) |
| `python main.py ruta/imagen.jpg` | Predice directamente esa imagen |
| `python main.py --test` | Predice una imagen de ejemplo del test set (muestra clase real) |
| `python main.py --semanas` | Ejecuta las 6 semanas por separado |

### Ejecutar modulos individuales

```
.\.venv\Scripts\activate
python -m src.semana02_entrenamiento
python -m src.semana03_taxonomia
python -m src.semana04_busqueda
python -m src.semana05_sistema_hibrido
python -m src.semana07_representaciones
python -m src.semana08_red_ontologia
python -m src.semana09_vision
```

> **Nota:** Los modulos individuales deben ejecutarse con `python -m src.<nombre>` desde la raiz del proyecto. No usar `python src/<nombre>.py` porque los imports no funcionarian.

> **Nota:** La primera ejecucion de la semana 02 puede tardar varios minutos al cargar y redimensionar las imagenes del dataset.
