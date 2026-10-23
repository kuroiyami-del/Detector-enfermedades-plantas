# Semana 11 - Decision tecnica: benchmark de modelos

## Contexto del problema

El proyecto PlantAI clasifica imagenes de hojas (dataset PlantVillage, 38 clases
de plantas y enfermedades) para diagnosticar el estado de salud de una planta.
El modelo de clasificacion es el nucleo del pipeline: procesa la imagen, predice
la clase y a partir de esa clase las semanas 04 y 07 planifican el tratamiento.

Hasta la semana 08 el clasificador de imagenes era una red neuronal MLP
(`artifacts/red_hojas.pkl`), y en la semana 02 el clasificador de texto usaba
LogisticRegression. Nunca se compararon formalmente: no existia una medida comun
de accuracy y tiempo de entrenamiento que respaldara la eleccion. Esta semana se
corre un benchmark con tres modelos sobre el mismo conjunto de datos y la misma
division entrenamiento/prueba, para decidir con datos cual conviene al proyecto.

## Modelos comparados

| Modelo | Configuracion usada en el benchmark |
|---|---|
| LogisticRegression | `max_iter=500`, semilla por corrida |
| RandomForestClassifier | `n_estimators=150`, `n_jobs=-1`, semilla por corrida |
| MLPClassifier | capa oculta de 128 y 64 (arquitectura de la semana 08), `max_iter=100`, semilla por corrida |

Nombres en `artifacts/benchmark.csv`: `logistic_regression`, `random_forest`
y `mlp_classifier`.

### Condiciones del experimento

- **Mismo dataset y misma division para los 3 modelos.** La division
  entrenamiento (7,521) / prueba (1,881) se calcula una sola vez con
  `train_test_split(..., random_state=42, stratify=y)` y se reutiliza en las 3
  corridas de los 3 modelos.
- **Submuestreo estratificado:** 250 imagenes maximo por clase (9,402 en total,
  38 clases), en escala de grises 48x48 (2,304 caracteristicas por imagen),
  el mismo preprocesamiento del modulo de la semana 08. Gracias a esto el
  benchmark completo (9 entrenamientos: 3 corridas x 3 modelos) corre en
  minutos en una sola ejecucion.
- **3 corridas con semillas distintas (42, 43, 44):** en cada corrida los
  modelos se crean de nuevo (nunca se reutiliza un modelo ya entrenado); el
  cronometro mide solo el tiempo de `fit()` y el accuracy se evalua siempre
  sobre el mismo conjunto de prueba.

## Resultados obtenidos

Detalle por corrida (copiado de `artifacts/benchmark.csv`):

| corrida | modelo | accuracy | tiempo_entrenamiento_s |
|---|---|---|---|
| 1 | logistic_regression | 0.3073 | 17.76 |
| 1 | random_forest | 0.4763 | 7.55 |
| 1 | mlp_classifier | 0.3737 | 49.21 |
| 2 | logistic_regression | 0.3073 | 20.65 |
| 2 | random_forest | 0.4694 | 7.40 |
| 2 | mlp_classifier | 0.3769 | 40.53 |
| 3 | logistic_regression | 0.3073 | 17.76 |
| 3 | random_forest | 0.4742 | 7.57 |
| 3 | mlp_classifier | 0.3812 | 62.21 |

Resumen (promedio y desviacion estandar de las 3 corridas):

| Modelo | Accuracy | Tiempo entrenamiento | Diferencia vs. mejor accuracy |
|---|---|---|---|
| random_forest | **0.4733 ± 0.0035** | **7.5 s ± 0.1** | 0.000 (referencia) |
| mlp_classifier | 0.3773 ± 0.0037 | 50.6 s ± 10.9 | -0.096 |
| logistic_regression | 0.3073 ± 0.0000 | 18.7 s ± 1.7 | -0.166 |

### Analisis de las variaciones entre corridas

- **Random Forest** va de 0.4763 (semilla 42) a 0.4694 (semilla 43): una
  variacion total de 0.007. Es razonable porque el bosque muestrea datos y
  variables al azar en cada arbol, y depender de la semilla es de esperarse.
  Aun asi es pequena: todas las corridas del bosque quedaron por encima de
  todas las corridas de los otros dos modelos.
- **MLPClassifier** arranca con pesos iniciales distintos en cada corrida, por
  eso su accuracy va de 0.3737 a 0.3812. Su tiempo de entrenamiento vario
  bastante mas: de 40.5 s a 62.2 s (+53%), efecto conocido del optimizador adam
  ante una red sin converger tras 100 iteraciones.
- **LogisticRegression** dio el mismo accuracy en las tres corridas (0.3073,
  desviacion 0.0000): el solver lbfgs es determinista, de modo que la semilla
  no influye en su resultado. Emitio aviso de no convergencia con las 500
  iteraciones que se le dieron, y su limite no es el tiempo de computo
  (17.8 s promedio): un modelo lineal sobre pixeles crudos no logra
   representar sintomas que dependen de posiciones (manchas, lesiones); ese es
   un limite del modelo lineal, no del limite de iteraciones.

## Modelo seleccionado

**RandomForestClassifier con `n_estimators=150`.**

## Justificacion tecnica

1. **Gana en las dos metricas medidas:** obtiene el mayor accuracy (0.4733) y
   a la vez es el mas rapido (7.5 s): 6.7 veces mas ligero que el MLP y 2.7
   veces que LogisticRegression. Que gane precision y a la vez sea el mas
   barato no es comun; el benchmark lo demuestra sobre la misma division.
2. **Tiempo estable y barato de reentrenamiento:** sus 3 corridas duraron de
   7.4 a 7.6 s (desviacion de 0.09 s) bajo la misma division de datos; de los
   tres es el que menos se bloquea al reentrenarse entre semana de clase.
3. **Sin precondiciones:** LogReg quedo sin converger incluso en 500
   iteraciones y en la semana 02 necesito un `StandardScaler` previo; el RF no
   pide escalado ni exige condiciones de convergencia para terminar.
4. **Frente a su propio techo:** el MLP entrenado por completo (semana 08:
   1500 iteraciones, 54,304 imagenes, mas de 90 min) logro un accuracy mayor
   que este bosque, pero con un costo que no cabe en el ciclo del proyecto; con
   el techo de 100 iteraciones del benchmark pierde 0.096 de accuracy frente a
   unos 7.5 s del bosque. La pregunta tecnica no era cual modelo es mas exacto
   en abstracto, sino cual conviene al proyecto con recursos realistas, y ahi
   gana el bosque con margen.

### Ventajas y limitaciones de cada modelo

| Modelo | Ventajas | Limitaciones |
|---|---|---|
| LogisticRegression | Determinista (desviacion 0.0000); entrenamiento corto (18.7 s promedio); entrega probabilisticas por clase | Accuracy bajo (0.3073) para 38 clases; no converge con un limite razonable de iteraciones; necesita escalado (la semana 02 uso `StandardScaler` por eso) |
| RandomForestClassifier | Mejor accuracy (0.4733) y menor tiempo (7.5 s); estable entre corridas (accuracy ± 0.0035, tiempo ± 0.09 s); no necesita escalado; `predict_proba` disponible | No aprende incrementalmente: ante datos nuevos hay que reentrenar todo; 2,304 caracteristicas por imagen lo hacen algo pesado en memoria |
| MLPClassifier | Su techo de accuracy es el mas alto: entrenado por completo (semana 08, 1500 iteraciones y 54,304 imagenes) supera al bosque; captura patrones espaciales de pixeles (manchas, bordes de lesiones) | En condiciones iguales al benchmark usa 6.7 veces el tiempo del bosque (50.6 s vs 7.5 s); su entrenamiento completo tomo mas de 90 min; vario mas en tiempo entre corridas (± 10.9 s); sensible a la semilla de inicializacion |

## Aplicacion al proyecto final

Random Forest pasara al proyecto como el clasificador del pipeline
imagen -> prediccion -> plan de recuperacion, sin descartar el MLP:

1. **Integracion al pipeline (`src/pipeline.py`):** Random Forest consume el
   mismo vector de 2,304 caracteristicas que ya usan la semana 08 y la
   semana 09, y expone `predict_proba()`, que es el dato de "confianza" que
   hoy muestran `main.py` y `index.html`. Solo cambia la instancia del
   clasificador; nada del flujo de evidencia ni del plan de recuperacion se
   toca.
2. **Reentrenamiento de bajo costo:** las 7.5 s por corrida permiten
   reentrenar cada vez que se agreguen imagenes nuevas a PlantVillage, sin el
   bloqueo de 90+ min del entrenamiento completo de la semana 08.
3. **Analisis de clases confundidas:** Random Forest entrega la evaluacion por
   clase, con la que se detectan las clases con peor accuracy (por ejemplo,
   la misma enfermedad en etapas tempranas vs avanzadas) y se decide donde
   conviene recolectar mas imagenes.
4. **Vigilancia tecnica sobre el MLP:** el MLP no se elimina; queda como
   referencia de accuracy maximo. Si en semanas posteriores cambia la
   disponibilidad de computo y un entrenamiento completo vuelve a ser viable,
   se repite este benchmark con ambos modelos entrenados al tope.

Como cierre del ciclo: la clase predicha con su probabilidad es la entrada
del plan de recuperacion de la semana 04 (busqueda A*), de modo que la
seleccion de Random Forest fortalece todo el flujo de diagnostico del
proyecto.
