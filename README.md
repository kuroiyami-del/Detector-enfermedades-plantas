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

## Estructura del proyecto

```
plantas_enfermas/
├── data/
│   ├── raw/PlantVillage-Dataset/raw/color/   # 38 carpetas con imagenes JPG
│   ├── processed/                             # CSVs y class_map.json
│   └── base_conocimiento.txt                  # Base de conocimiento (semana 05)
├── src/
│   ├── __init__.py
│   ├── config.py                   # Constantes: paths, RANDOM_STATE, IMG_SIZE
│   ├── data_loader.py              # Funciones de carga de datos
│   ├── semana02_entrenamiento.py   # Entrenamiento y evaluacion
│   ├── semana03_taxonomia.py       # Taxonomia de IA
│   ├── semana04_busqueda.py        # Busqueda A* (plan de recuperacion)
│   ├── semana05_sistema_hibrido.py # Sistema hibrido (reglas + TF-IDF + ML)
│   └── pipeline.py                 # Pipeline integrada image→prediccion→plan
├── main.py                         # Punto de entrada
├── requirements.txt
└── README.md
```

## Tecnologias utilizadas

- **Python 3.11**
- **scikit-learn** - Modelos de machine learning y metricas de evaluacion
- **Pillow** - Carga y procesamiento de imagenes
- **numpy** - Operaciones con arreglos numericos
- **pandas** - Manipulacion de datos (lectura de CSVs)
- **tensorflow** - Framework de deep learning (disponible para avances futuros)

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

### Ejecutar el proyecto completo

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
| `python main.py --semanas` | Ejecuta las 5 semanas por separado |

### Ejecutar modulos individuales

```
.\.venv\Scripts\activate
python -m src.semana02_entrenamiento
python -m src.semana03_taxonomia
python -m src.semana04_busqueda
python -m src.semana05_sistema_hibrido
```

> **Nota:** Los modulos individuales deben ejecutarse con `python -m src.<nombre>` desde la raiz del proyecto. No usar `python src/<nombre>.py` porque los imports no funcionarian.

> **Nota:** La primera ejecucion de la semana 02 puede tardar varios minutos al cargar y redimensionar las imagenes del dataset.
