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

### Cultivos incluidos

El dataset incluye imagenes de los siguientes cultivos:

| Cultivo | Clases | Total imagenes |
|---------|--------|----------------|
| Apple (Manzana) | 4 | 4,171 |
| Blueberry (Arandano) | 1 | 1,502 |
| Cherry (Cereza) | 2 | 1,906 |
| Corn (Maiz) | 4 | 3,852 |
| Grape (Uva) | 4 | 4,062 |
| Orange (Naranja) | 1 | 5,507 |
| Peach (Durazno) | 2 | 2,657 |
| Pepper, bell (Pimiento) | 2 | 2,475 |
| Potato (Papa) | 3 | 2,152 |
| Raspberry (Frambuesa) | 1 | 371 |
| Soybean (Soja) | 1 | 5,090 |
| Squash (Calabaza) | 1 | 1,835 |
| Strawberry (Fresa) | 2 | 1,565 |
| Tomato (Tomate) | 10 | 18,160 |

### Ejemplo de clases

```
Apple___Apple_scab         (630 imagenes)
Apple___Black_rot          (621 imagenes)
Apple___Cedar_apple_rust   (275 imagenes)
Apple___healthy            (1,645 imagenes)
Tomato___Bacterial_spot    (2,127 imagenes)
Tomato___healthy           (1,591 imagenes)
...
```

### Separacion de datos

Los datos ya se encuentran separados en los archivos CSV dentro de `data/processed/`:

| Conjunto | Archivo | Muestras | Proporcion |
|----------|---------|----------|------------|
| Entrenamiento | `train.csv` | 38,092 | 70.1% |
| Prueba | `test.csv` | 7,967 | 14.7% |
| Validacion | `val.csv` | 8,247 | 15.2% |
| **Total** | | **54,306** | **100%** |

Los archivos CSV contienen las columnas: `filepath`, `label`, `class_name`, `crop`, `disease`.

## Avances realizados

### Semana 02 - Entrenamiento

Se implemento un script de entrenamiento basico que demuestra los conceptos fundamentales:

- **Separacion de datos:** Se utilizan los conjuntos de entrenamiento y prueba ya existentes en `data/processed/`.
- **Transformacion de imagenes:** Las imagenes se redimensionan a 64x64 pixels y se aplanan en vectores para poder ser procesadas por un modelo de scikit-learn.
- **Modelo:** Se aplica un pipeline de `StandardScaler + LogisticRegression`, siguiendo la misma estructura del ejemplo del profesor con el dataset Iris.
- **Evaluacion:** Se reporta el accuracy y la matriz de confusion en el conjunto de prueba.

Script: `src/semana02_entrenamiento.py`

### Semana 03 - Taxonomia de Inteligencia Artificial

Se genero un analisis de taxonomia que clasifica el proyecto dentro del area de Inteligencia Artificial:

- **Area principal:** Vision por computador (analisis de imagenes de plantas).
- **Area complementaria:** Aprendizaje automatico (entrenamiento de un modelo clasificador).
- **Justificacion:** El nucleo del problema es interpretar imagenes, y el enfoque utilizado es el aprendizaje a partir de datos etiquetados.

Reporte: `reports/semana03.md`

## Estructura del proyecto

```
plantas_enfermas/
├── data/
│   ├── raw/
│   │   └── PlantVillage-Dataset/
│   │       └── raw/
│   │           └── color/              # 38 carpetas con imagenes JPG
│   │               ├── Apple___Apple_scab/
│   │               ├── Apple___Black_rot/
│   │               ├── Tomato___Bacterial_spot/
│   │               └── ...
│   └── processed/
│       ├── class_map.json              # Mapeo de clases a IDs numericos
│       ├── train.csv                   # Conjunto de entrenamiento
│       ├── test.csv                    # Conjunto de prueba
│       └── val.csv                     # Conjunto de validacion
├── src/
│   └── semana02_entrenamiento.py       # Script de entrenamiento
├── reports/
│   └── semana03.md                     # Reporte de taxonomia de IA
├── requirements.txt                    # Dependencias del proyecto
└── README.md                           # Este archivo
```

## Tecnologias utilizadas

- **Python 3.11**
- **scikit-learn** - Modelos de machine learning y metricas de evaluacion
- **Pillow** - Carga y procesamiento de imagenes
- **numpy** - Operaciones con arreglos numericos
- **pandas** - Manipulacion de datos (lectura de CSVs)
- **tensorflow** - Framework de deep learning (disponible para avances futuros)

## Como ejecutar el proyecto

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

### Ejecutar el entrenamiento (Semana 02)

```
python src/semana02_entrenamiento.py
```

> **Nota:** La primera ejecucion puede tardar varios minutos dependiendo del hardware, ya que debe cargar y redimensionar las imagenes del dataset.
