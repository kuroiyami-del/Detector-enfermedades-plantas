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

### Semana 10 - Reconocimiento de imagenes (histogramas, regiones y textura)

- **Area:** Vision por computador (procesamiento de imagenes).
- **Problema:** describir una hoja con un vector compacto a partir de su segmentacion, su histograma de intensidad y su textura.
- **Metodo:** `imagen -> escala de grises -> umbral de Otsu -> measure.label -> regiones (area > 50 px) -> histograma de intensidad (32 bins, density=True) -> textura LBP (radius=2, points=16, method="uniform") -> vector de 53 valores` con `scikit-image`.
- **Vector:** `3` (area media, desviacion estandar del area y cantidad de regiones) `+ 32` (histograma de intensidad) `+ 18` (histograma LBP) `= 53`.
- **Comparacion:** dos imagenes del dominio: `data/imagen_proyecto.png` (tomate con septoria) y `data/imagen_proyecto_2.png` (tomate sana, PlantVillage). La hoja enferma se fragmenta en 5 regiones de tamanos dispares; la sana forma una sola region homogenea.
- **Interfaz web:** al pulsar **Diagnosticar**, la pestana Semana 10 compara la imagen subida por el usuario contra la hoja sana de referencia (`data/imagen_proyecto_2.png`) y genera `artifacts/web_semana10_comparacion.png` con la figura de esa comparacion. La pestana tambien muestra el resumen del vector de 53 valores y la tabla comparativa de las imagenes.
- **Interfaz web (semanas 11, 13, 14, 15 y 16):** al pulsar **Diagnosticar**, Resultados incorpora las pestanas Semana 11, Semana 13, Semana 14, Semana 15 y Semana 16 junto a las demas. La Semana 11 lee y presenta `artifacts/benchmark.csv` (no reentrena), la Semana 13 razona con los hechos reales del diagnostico (categoria, confianza, plan A* y regiones visibles), la Semana 14 consulta la red semantica con la clase detectada, la Semana 15 muestra los articulos **validados** del repositorio de conocimiento que corresponden a la categoria detectada y la Semana 16 recupera la referencia validada que soporta el diagnostico (o se abstiene: nunca inventa). Enlaces equivalentes en el pie de pagina (`#footSemana11`, `#footSemana13`, `#footSemana14`, `#footSemana15`, `#footSemana16`) y endpoints `/api/semana11` (benchmark), `/api/semana13` (motor de reglas), `/api/semana14` (red semantica), `/api/semana15` (base de conocimiento) y `/api/semana16` (motor de referencia).
- **Artefactos:** `artifacts/semana10_features.npy` (vector e histogramas por imagen) y `artifacts/semana10_histograma.png` (figura comparativa).
- **Reporte:** `reports/semana10.md`.
- **Ejecucion:** `python -m src.semana10_texturas`

### Semana 11 - Benchmark de modelos

- **Area:** Evaluacion y seleccion de modelos de aprendizaje automatico.
- **Problema:** el proyecto usaba una MLP en la semana 08 y LogisticRegression en la semana 02, pero no existia una comparacion formal de accuracy y tiempo de entrenamiento sobre el mismo conjunto de datos que respaldara la eleccion del clasificador.
- **Metodo:** benchmark con 3 modelos sobre el mismo dataset y la misma division estratificada 80/20: `LogisticRegression` (`max_iter=500`), `RandomForestClassifier` (`n_estimators=150`, `n_jobs=-1`) y `MLPClassifier` (capas 128 y 64, `max_iter=100`). Se usan hasta 250 imagenes por clase de `data/raw/PlantVillage-Dataset/raw/color/` (9,402 imagenes, 38 clases), en grises 48x48 (2,304 caracteristicas), con 3 corridas y semillas 42, 43 y 44. El cronometro mide solo `fit()` y el accuracy se evalua sobre el mismo conjunto de prueba (7,521 entrenamiento / 1,881 prueba).
- **Resultados:** promedios de las 3 corridas:
  - `random_forest`: **0.4733 ± 0.0035** de accuracy y **7.5 s ± 0.1** de entrenamiento.
  - `mlp_classifier`: 0.3773 ± 0.0037 de accuracy y 50.6 s ± 10.9 de entrenamiento.
  - `logistic_regression`: 0.3073 ± 0.0000 de accuracy y 18.7 s ± 1.7 de entrenamiento.
- **Decision:** se selecciona **RandomForestClassifier** por obtener el mayor accuracy y el menor tiempo de entrenamiento; la integracion al pipeline queda propuesta y la MLP se conserva como referencia de accuracy maximo.
- **Relacion con las semanas previas:** compara la MLP de la semana 08 con la LogisticRegression usada en la semana 02 y propone a RandomForest como clasificador del pipeline; la decision aun no esta integrada en `main.py` ni en `server.py`.
- **Artefactos:** `artifacts/benchmark.csv` (detalle de las 9 corridas: 3 modelos x 3 semillas).
- **Reporte:** `reports/semana11_adr.md`.
- **Ejecucion:** `python -m src.semana11_benchmark`

### Semana 13 - Ingenieria del conocimiento: motor de inferencia

- **Area:** Ingenieria del conocimiento (sistemas logicos y motor de inferencia).
- **Problema:** PlantAI ya diagnostica la hoja, pero no decide que hacer con ese diagnostico. Faltaba una politica explicable para elegir entre manejo inmediato, cuarentena/contencion, revision experta o monitoreo preventivo.
- **Metodo:** motor de reglas proposicionales (tipo Horn) con encadenamiento hacia adelante. Los hechos salen de las semanas 02 (clase y confianza), 03 (categoria taxonomica), 09/10 (dano foliar visible) y 04 (plan disponible o meta inalcanzable). La cadena del caso A es R1 -> R4 -> R5: `enfermedad_foliar_confirmada`, luego `tratamiento_planificado` y finalmente `manejo_inmediato`.
- **Escenarios:** A) tomate con septoria, confianza alta, dano foliar visible y plan A* de 3 acciones; B) caso viral con meta inalcanzable, donde se disparan R6-R8 pero falta `plan_disponible` para R4/R5.
- **Resultado:** en A se demuestra `manejo_inmediato`; en B queda **NO DEMOSTRADA con los hechos disponibles** y se deriva `manejo_integrado`. No demostrado no significa falso.
- **Contenido del modulo:** motor, reglas, escenarios, 9 pruebas `unittest`, presentacion por consola y generacion del reporte, todo en `src/semana13_conocimiento.py`.
- **Reporte:** `reports/reporte_semana13.md` (se genera con `python src/semana13_conocimiento.py --reporte`).
- **Ejecucion:** `python -m src.semana13_conocimiento`
- **Pruebas:** `python -m unittest src.semana13_conocimiento -v`

### Semana 14 - Ingenieria del conocimiento: redes semanticas

- **Area:** Representaciones del conocimiento y linguistica (redes semanticas).
- **Problema:** la taxonomia de la semana 03 vive en diccionarios de codigo y no puede consultarse ni explicarse por si misma. Se necesita una representacion donde cada concepto, su jerarquia y sus propiedades queden explicitos y justificados.
- **Metodo:** red semantica (nodos = conceptos, aristas dirigidas y etiquetadas = relaciones). Un analizador linguistico restringido convierte oraciones en espanol en triples `(sujeto, relacion, objeto)`: solo acepta dos patrones (`X es Y`, `X necesita Y`) y rechaza cualquier otra oracion con `ValueError` en lugar de inventar un triple. `normalizar()` unifica mayusculas y tildes.
- **Inferencia:** regla de transitividad de `es_un` (recorrido del grafo con control de ciclos) y regla didactica de herencia de `necesita` (un concepto hereda la propiedad de sus categorias superiores).
- **Escenario:** taxonomia PlantAI completa, donde `septoria es_un estado_fitosanitario` se demuestra con la ruta `septoria -> enfermedad_fungica -> problema_foliar -> estado_fitosanitario` y las necesidades (`tratamiento`, `inspeccion`) se heredan de `problema_foliar`. La consulta negativa (`septoria es_un hoja_sana -> False`) muestra que no hay evidencia en la red: False no es falsedad universal.
- **Integracion:** al diagnosticar una imagen, `server.py` agrega el triple `(clase detectada, es_un, categoria)` de las semanas 02/03 y consulta la red real de esa planta.
- **Contenido del modulo:** normalizacion, parser, red semantica, escenarios, presentacion por consola y generacion del reporte, todo en `src/semana14_redes_semanticas.py`.
- **Reporte:** `reports/reporte_semana14.md` (se genera con `python src/semana14_redes_semanticas.py --reporte`).
- **Ejecucion:** `python -m src.semana14_redes_semanticas`

### Semana 15 - Ingenieria del conocimiento: base de conocimiento

- **Area:** Organizacion del conocimiento empresarial (ingenieria del conocimiento).
- **Problema:** el conocimiento fitosanitario del proyecto estaba repartido entre codigo, reportes y comentarios de consola. Sin contexto es dificil de encontrar, de confiar y de mantener: un articulo sin dominio, responsable, fuente ni estado no es confiable.
- **Metodo:** repositorio de conocimiento sobre **SQLite** con cinco tablas relacionales: `dominio` (area tematica), `aplicacion` (sistema o proceso donde se usa), `experto` (recurso humano responsable), `herramienta` (medio de captura o consulta) y `articulo` (el contenido con estado editorial `BORRADOR` / `VALIDADO`). Las consultas solo muestran lo **validado**: un borrador existe en la base pero no se publica.
- **Dominios del proyecto:** Diagnostico foliar, Manejo fitosanitario y Calidad de datos (sustituyen a los ejemplos Seguridad y Soporte TI del material de la clase).
- **Escenario:** se registra un articulo de manejo como borrador (no aparece en la busqueda), el experto lo valida y recien entonces se publica; ademas se comprueban los errores de integridad referencial y de articulo inexistente.
- **Puente con el diagnostico:** `articulos_para_categoria(categoria)` devuelve el conocimiento validado que corresponde a la categoria de la semana 03 ("Enfermedades fungicas", "Plantas sanas"...) del caso real.
- **Contenido del modulo:** esquema, datos, conexion con claves foraneas, busqueda, registro, validacion, 5 pruebas `unittest`, presentacion por consola y generacion del reporte, todo en `src/semana15_base_conocimiento.py`.
- **Artefactos:** `artifacts/conocimiento.db` (repositorio con los datos de ejemplo) y `sql/esquema.sql` + `sql/datos.sql`.
- **Interfaz web:** pestana **Semana 15 · Base de conocimiento** en `index.html` y endpoint `/api/semana15` en `server.py`; al diagnosticar una imagen muestra los articulos validados del dominio asociado a la categoria detectada.
- **Material de referencia:** `referencia semana15/` (material de la clase usado como guia de forma y contenido).
- **Reporte:** `reports/reporte_semana15.md` (se genera con `python src/semana15_base_conocimiento.py --reporte`).
- **Ejecucion:** `python -m src.semana15_base_conocimiento`
- **Pruebas:** `python -m unittest src.semana15_base_conocimiento -v` (o `python -m unittest discover -s tests -v`)

### Semana 16 - Diseno de sistemas inteligentes: motor de referencia

- **Area:** Diseno de sistemas inteligentes (arquitectura y motor de referencia).
- **Problema:** PlantAI diagnostica la planta y guarda conocimiento validado (semana 15), pero no tiene un componente que responda preguntas del usuario con ese conocimiento de forma trazable.
- **Arquitectura:** los 6 componentes de la practica en un solo modulo: 1) Interfaz, 2) Normalizador, 3) Base de conocimiento, 4) Motor de referencia, 5) Generador de respuestas y 6) Control de calidad (8 pruebas `unittest` + 5 escenarios).
- **Referencias:** cada una con identificador (`REF-00X`), titulo, palabras clave, respuesta, fuente y bandera `validada`; se construyen desde los articulos del repositorio de la semana 15 (`artifacts/conocimiento.db`), sin reescribir su contenido.
- **Regla de oro:** solo responden referencias validadas; el articulo 5 esta en `BORRADOR` y nunca responde aunque sus claves coincidan. El motor nunca inventa respuestas: se abstiene con `SIN_DATOS` (consulta vacia) o `SIN_REFERENCIA` (sin cobertura o solo borradores).
- **Sustentacion:** un motor de referencia NO es un motor de inferencia: no aplica reglas ni deriva conclusiones nuevas, recupera la referencia mas pertinente y entrega su id y su fuente. La puntuacion es un conteo de palabras en comun, no una probabilidad.
- **Puente con el diagnostico:** `pregunta_desde_clase()` convierte la clase detectada (semana 02) en pregunta; la web muestra la referencia validada que soporta el diagnostico, o la abstencion si no hay evidencia.
- **Contenido del modulo:** normalizador, construccion de la base, motor, generador, 5 escenarios, 8 pruebas `unittest`, consola interactiva (`--consola`) y generacion del reporte (`--reporte`), todo en `src/semana16_motor_referencia.py`.
- **Interfaz web:** pestana **Semana 16 · Motor de referencia** en `index.html` y endpoint `/api/semana16` en `server.py`; al diagnosticar una imagen consulta el motor con la clase detectada.
- **Material de referencia:** `referencia semana16/` (guia y presentacion de la clase).
- **Reporte:** `reports/reporte_semana16.md` (se genera con `python src/semana16_motor_referencia.py --reporte`).
- **Ejecucion:** `python -m src.semana16_motor_referencia`
- **Pruebas:** `python -m unittest src.semana16_motor_referencia -v` (o `python -m unittest discover -s tests -v`)

## Estructura del proyecto

```
plantas_enfermas/
├── data/
│   ├── raw/PlantVillage-Dataset/raw/color/   # 38 carpetas con imagenes JPG
│   ├── processed/                             # CSVs y class_map.json
│   ├── imagen_proyecto.png                    # Imagen de entrada (semana 09)
│   ├── imagen_proyecto_2.png                  # Segunda imagen de dominio (semana 10)
│   └── base_conocimiento.txt                  # Base de conocimiento (semana 05)
├── sql/                                       # Semana 15
│   ├── esquema.sql                            # 5 tablas: dominio, aplicacion, experto, herramienta, articulo
│   └── datos.sql                              # Datos ficticios del repositorio
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
│   ├── semana10_texturas.py        # Otsu + medidas de region + histograma + LBP
│   ├── semana11_benchmark.py       # Benchmark LogisticRegression / RandomForest / MLP
│   ├── semana13_conocimiento.py    # Semana 13: reglas + encadenamiento + pruebas + reporte
│   ├── semana14_redes_semanticas.py # Semana 14: red semantica + parser + inferencia
│   ├── semana15_base_conocimiento.py # Semana 15: repositorio de conocimiento (SQLite)
│   ├── semana16_motor_referencia.py  # Semana 16: arquitectura y motor de referencia
│   └── pipeline.py                 # Pipeline integrada image→prediccion→plan
├── tests/
│   ├── test_base_conocimiento.py   # Semana 15: cinco pruebas (descubribles con unittest)
│   └── test_motor.py               # Semana 16: ocho pruebas del motor de referencia
├── reports/                        # Reportes por semana (semana10.md, semana11_adr.md, reporte_semana13.md, reporte_semana14.md, reporte_semana15.md, reporte_semana16.md)
├── main.py                         # Punto de entrada (CLI)
├── server.py                       # Backend web (Flask) que sirve index.html
├── index.html                      # Interfaz web (diagnostico + barra de semanas)
├── artifacts/                      # Artefactos semana 08/09/10/11/15 (modelo, BD, ontologia, paneles, benchmark, conocimiento.db)
├── referencia semana15/             # Material de referencia de la semana 15
├── referencia semana16/             # Material de referencia de la semana 16
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
4. (Opcional, solo para las semanas 02, 08 y 11) Descargar el dataset
   **PlantVillage** y descomprimirlo en `data/raw/PlantVillage-Dataset/`,
   de modo que las 38 carpetas de clases queden en `raw/color/`. Los CSV de
   `data/processed/` ya estan versionados, pero esas tres semanas entrenan y
   evaluan sobre las imagenes: sin ellas avisan
   `[FALTA EL DATASET] ...` y terminan sin ejecutar. El resto del proyecto
   (incluida la interfaz web) funciona con los modelos guardados en
   `models/` y `artifacts/`.

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

- **Caso A (imagen):** ejecuta las semanas 02, 03, 04, 07, 08, 09, 10, 11, 13, 14, 15 y 16 para esa
  planta. La semana 02 es la vista por defecto y la semana 10 compara la imagen
  enviada contra la hoja sana de referencia. La semana 11 solo lee
  `artifacts/benchmark.csv` (no reentrena); la semana 13 razona sobre los hechos
  reales del diagnostico (categoria, confianza, plan A* y regiones), la semana 14
  consulta la red semantica con la clase detectada, la semana 15 muestra el
  conocimiento validado del dominio asociado a la categoria y la semana 16
  consulta el motor de referencia con la clase detectada y muestra la referencia
  validada que soporta el diagnostico (o la abstencion si no hay evidencia).
  La semana 05 no aparece.
- **Caso B (sintomas):** ejecuta la semana 05 (sistema hibrido) y la marca como
  la que se esta ejecutando; la semana 10 muestra la comparacion de ejemplo, la
  11 presenta el benchmark, la 13 los dos casos del motor de reglas, la 14 la
  red semantica de la taxonomia del proyecto, la 15 el repositorio de
  conocimiento y la 16 el motor de referencia con sus cinco escenarios.

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
| `python main.py --semanas` | Ejecuta las semanas por separado |

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
python -m src.semana10_texturas
python -m src.semana11_benchmark
python -m src.semana13_conocimiento
python -m src.semana14_redes_semanticas
python -m src.semana15_base_conocimiento
python -m src.semana16_motor_referencia
```

> **Nota:** Los modulos individuales deben ejecutarse con `python -m src.<nombre>` desde la raiz del proyecto. No usar `python src/<nombre>.py` porque los imports no funcionarian.

> **Nota:** La Semana 13 tambien se puede ejecutar directamente con `python src/semana13_conocimiento.py`, probar con `python -m unittest src.semana13_conocimiento -v` y regenerar su reporte con `python src/semana13_conocimiento.py --reporte`.

> **Nota:** La Semana 14 tambien se puede ejecutar directamente con `python src/semana14_redes_semanticas.py` y regenerar su reporte con `python src/semana14_redes_semanticas.py --reporte`.

> **Nota:** La Semana 15 tambien se puede ejecutar directamente con `python src/semana15_base_conocimiento.py`, regenerar su reporte con `python src/semana15_base_conocimiento.py --reporte` y ejecutar sus pruebas con `python -m unittest src.semana15_base_conocimiento -v` (o `python -m unittest discover -s tests -v`).

> **Nota:** La Semana 16 tambien se puede ejecutar directamente con `python src/semana16_motor_referencia.py`, abrir una consola interactiva de preguntas con `python src/semana16_motor_referencia.py --consola`, regenerar su reporte con `python src/semana16_motor_referencia.py --reporte` y ejecutar sus pruebas con `python -m unittest src.semana16_motor_referencia -v` (o `python -m unittest discover -s tests -v`).

> **Nota:** La primera ejecucion de la semana 02 puede tardar varios minutos al cargar y redimensionar las imagenes del dataset.
