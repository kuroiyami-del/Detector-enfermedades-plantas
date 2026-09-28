# Explicación del código - Semana 8: Representaciones del reconocimiento

En esta práctica se integran tres elementos que cumplen funciones diferentes dentro de un sistema de Inteligencia Artificial:

1. **Reconocimiento mediante redes neuronales artificiales**
2. **Base de datos de imágenes y metadatos**
3. **Ontologías para representar significado y relaciones**

La idea principal de la semana es comprender que un sistema de reconocimiento no debería quedarse únicamente en producir una predicción.

El flujo completo que se busca construir es:

```text
IMAGEN
   ↓
RED NEURONAL
   ↓
PREDICCIÓN
   ↓
BASE DE DATOS / EVIDENCIA
   ↓
ONTOLOGÍA / SIGNIFICADO
```

Dicho de una manera sencilla:

> La red neuronal intenta reconocer qué hay en la imagen, la base de datos permite dejar evidencia de los datos utilizados y la ontología permite expresar qué significa el resultado dentro del dominio del problema.

El archivo trabajado en clase es:

```text
src/semana08_red_ontologia.py
```

---

# 1. Importación de librerías

El código comienza importando las herramientas necesarias.

```python
from pathlib import Path
import pickle
import sqlite3
import networkx as nx
from sklearn.datasets import load_digits
from sklearn.model_selection import train_test_split
from sklearn.neural_network import MLPClassifier
from sklearn.metrics import accuracy_score
```

Cada importación tiene una responsabilidad diferente.

---

## 1.1. `Path`

```python
from pathlib import Path
```

`Path` pertenece a la librería estándar de Python y permite trabajar con rutas de archivos y carpetas.

En lugar de escribir manualmente rutas como:

```text
C:/proyecto/artifacts/modelo.pkl
```

podemos construirlas de una forma independiente del sistema operativo.

Por ejemplo:

```python
ROOT / "artifacts"
```

puede representar una carpeta llamada `artifacts` dentro del proyecto.

### Ejemplo cotidiano

Podemos imaginar `Path` como una dirección postal.

```text
País → Ciudad → Calle → Casa
```

En un proyecto:

```text
Proyecto → artifacts → modelo_mlp.pkl
```

---

## 1.2. `pickle`

```python
import pickle
```

`pickle` permite guardar objetos de Python en un archivo.

En esta práctica se utiliza para guardar el modelo neuronal ya entrenado.

El archivo generado será:

```text
modelo_mlp.pkl
```

La ventaja es que después podemos cargar el modelo sin necesidad de entrenarlo nuevamente desde cero.

### Ejemplo cotidiano

Entrenar el modelo es parecido a estudiar para un examen.

Guardar el modelo sería parecido a guardar los apuntes y resultados obtenidos para poder utilizarlos después.

---

## 1.3. `sqlite3`

```python
import sqlite3
```

`sqlite3` permite trabajar con bases de datos SQLite directamente desde Python.

SQLite guarda toda la base de datos dentro de un solo archivo.

En esta práctica se generará:

```text
imagenes.db
```

La base almacenará metadatos de algunas imágenes.

---

## 1.4. `networkx`

```python
import networkx as nx
```

`NetworkX` es una librería de Python utilizada para trabajar con grafos.

Un grafo está compuesto principalmente por:

```text
NODOS
RELACIONES
```

Por ejemplo:

```text
modelo_mlp → reconoce → digito
```

En esta práctica se utiliza para construir una representación sencilla de una ontología.

La parte:

```python
as nx
```

crea un nombre corto.

En lugar de escribir:

```python
networkx.DiGraph()
```

podemos escribir:

```python
nx.DiGraph()
```

---

## 1.5. `load_digits`

```python
from sklearn.datasets import load_digits
```

`load_digits` carga un conjunto de datos incluido en **scikit-learn** con imágenes de dígitos escritos a mano.

Las clases posibles son:

```text
0 1 2 3 4 5 6 7 8 9
```

Cada imagen tiene un tamaño de:

```text
8 × 8 píxeles
```

Por lo tanto cada imagen puede representarse mediante:

```text
64 valores numéricos
```

porque:

```text
8 × 8 = 64
```

---

## 1.6. `train_test_split`

```python
from sklearn.model_selection import train_test_split
```

Esta función permite dividir los datos en dos grupos principales:

```text
ENTRENAMIENTO
PRUEBA
```

El conjunto de entrenamiento sirve para que el modelo aprenda.

El conjunto de prueba sirve para revisar si el modelo puede reconocer datos que no utilizó durante el entrenamiento.

---

## 1.7. `MLPClassifier`

```python
from sklearn.neural_network import MLPClassifier
```

`MLPClassifier` implementa una red neuronal conocida como **Multilayer Perceptron**, o perceptrón multicapa.

En esta práctica se utiliza para clasificar imágenes de dígitos.

Conceptualmente el proceso es:

```text
64 valores de entrada
        ↓
CAPA OCULTA
        ↓
CLASE PREDICHA
        ↓
0, 1, 2, ..., 9
```

---

## 1.8. `accuracy_score`

```python
from sklearn.metrics import accuracy_score
```

`accuracy_score` permite medir qué proporción de predicciones fueron correctas.

La idea puede expresarse como:

```text
                 predicciones correctas
Accuracy = --------------------------------
                  total de predicciones
```

Por ejemplo, si un modelo clasifica correctamente 90 imágenes de 100:

```text
Accuracy = 90 / 100
Accuracy = 0.90
```

Eso equivale a:

```text
90 %
```

---

# 2. Definición de la carpeta principal del proyecto

El siguiente bloque organiza dónde se guardarán los archivos generados.

```python
ROOT = Path(__file__).resolve().parent.parent
ARTIFACTS = ROOT / "artifacts"
ARTIFACTS.mkdir(parents=True, exist_ok=True)
```

Vamos línea por línea.

---

## 2.1. `__file__`

Dentro de:

```python
Path(__file__)
```

`__file__` representa el archivo Python que se está ejecutando.

En este caso sería algo similar a:

```text
src/semana08_red_ontologia.py
```

---

## 2.2. `Path(__file__)`

```python
Path(__file__)
```

convierte la ruta del archivo actual en un objeto `Path`.

Esto permite utilizar operaciones para navegar entre carpetas.

---

## 2.3. `.resolve()`

```python
Path(__file__).resolve()
```

obtiene la ruta absoluta del archivo.

Por ejemplo, podría producir algo parecido a:

```text
/home/usuario/proyecto/src/semana08_red_ontologia.py
```

---

## 2.4. `.parent`

La expresión completa es:

```python
ROOT = Path(__file__).resolve().parent.parent
```

El primer `.parent` sube desde el archivo hasta la carpeta `src`.

```text
semana08_red_ontologia.py
        ↓
src
```

El segundo `.parent` sube desde `src` hasta la raíz del proyecto.

```text
src
 ↓
proyecto
```

Por eso `ROOT` representa la carpeta principal del proyecto.

---

## 2.5. Carpeta `artifacts`

```python
ARTIFACTS = ROOT / "artifacts"
```

crea una ruta hacia una carpeta llamada:

```text
artifacts
```

La intención es almacenar allí los resultados generados por la práctica.

Por ejemplo:

```text
artifacts/
├── modelo_mlp.pkl
├── imagenes.db
└── ontologia.graphml
```

---

## 2.6. Crear la carpeta si no existe

```python
ARTIFACTS.mkdir(parents=True, exist_ok=True)
```

`mkdir()` significa crear carpeta.

La opción:

```python
parents=True
```

permite crear también carpetas superiores necesarias.

La opción:

```python
exist_ok=True
```

indica que no debe producirse un error si la carpeta ya existe.

En lenguaje cotidiano:

> Cree la carpeta `artifacts` si todavía no existe. Si ya existe, continúe normalmente.

---

# 3. Carga del conjunto de imágenes

El siguiente código carga las imágenes y sus etiquetas.

```python
X, y = load_digits(return_X_y=True)
```

Aquí aparecen dos variables muy importantes:

```text
X
y
```

---

## ¿Qué contiene `X`?

`X` contiene las características utilizadas como entrada para el modelo.

Cada fila representa una imagen.

Cada imagen está convertida en 64 valores.

Conceptualmente:

```text
X = [
    imagen_1,
    imagen_2,
    imagen_3,
    ...
]
```

Una imagen podría verse internamente así:

```text
[0, 0, 5, 13, 9, ..., 0]
```

Estos números representan intensidades de los píxeles.

---

## ¿Qué contiene `y`?

`y` contiene la respuesta correcta de cada imagen.

Por ejemplo:

```text
Imagen 0 → etiqueta 0
Imagen 1 → etiqueta 1
Imagen 2 → etiqueta 2
...
```

Conceptualmente:

```text
X = imagen

y = respuesta correcta
```

Esto permite que el algoritmo aprenda una relación entre:

```text
PATRÓN DE PÍXELES → DÍGITO
```

---

## ¿Qué hace `return_X_y=True`?

Normalmente `load_digits()` puede devolver un objeto con varias propiedades.

Al utilizar:

```python
return_X_y=True
```

le estamos diciendo:

> Devuélvame directamente los datos de entrada y las etiquetas.

Por eso podemos escribir:

```python
X, y = ...
```

---

# 4. División entre entrenamiento y prueba

El siguiente bloque separa los datos.

```python
X_train, X_test, y_train, y_test = train_test_split(
    X, y, test_size=0.25, random_state=42, stratify=y
)
```

Este es uno de los conceptos más importantes de Machine Learning.

---

## Variables generadas

Se crean cuatro grupos:

```text
X_train = imágenes utilizadas para entrenar
X_test  = imágenes utilizadas para probar

y_train = respuestas correctas de entrenamiento
y_test  = respuestas correctas de prueba
```

La relación es:

```text
X_train ↔ y_train
X_test  ↔ y_test
```

---

## `test_size=0.25`

```python
test_size=0.25
```

significa que aproximadamente el 25 % de los datos se utilizará para prueba.

El resto se utilizará para entrenamiento.

Conceptualmente:

```text
75 % → entrenamiento
25 % → prueba
```

### Ejemplo para explicar en el tablero

Imagine 100 imágenes.

```text
100 imágenes
   │
   ├── 75 → entrenamiento
   │
   └── 25 → prueba
```

Las 75 imágenes enseñan al modelo.

Las 25 restantes permiten comprobar si realmente aprendió.

---

## ¿Por qué no usar las mismas imágenes para entrenar y probar?

Porque podríamos confundir:

```text
MEMORIZAR
```

con:

```text
APRENDER A GENERALIZAR
```

Un estudiante puede memorizar exactamente diez preguntas.

Pero si el examen utiliza preguntas nuevas sobre el mismo tema, podremos saber si realmente comprendió.

Lo mismo ocurre con un modelo.

---

## `random_state=42`

```python
random_state=42
```

permite reproducir la misma división de los datos en distintas ejecuciones.

Sin una semilla fija, la selección de datos podría cambiar cada vez.

Con:

```text
42
```

la práctica puede reproducirse con mayor facilidad.

El número 42 no tiene un significado matemático especial dentro del modelo. Es simplemente una semilla elegida para controlar la aleatoriedad.

---

## `stratify=y`

```python
stratify=y
```

intenta conservar una distribución similar de las clases en entrenamiento y prueba.

Por ejemplo, si el dataset contiene dígitos del 0 al 9, queremos evitar que por azar un grupo quede con demasiados ejemplos de una clase y pocos de otra.

La idea es mantener una representación equilibrada de las etiquetas.

---

# 5. Creación de la red neuronal MLP

El modelo se crea con:

```python
model = MLPClassifier(
    hidden_layer_sizes=(64,),
    max_iter=400,
    random_state=42
)
```

Aquí todavía no se ha entrenado el modelo.

Solamente se está configurando la red neuronal.

---

## 5.1. `MLPClassifier`

`MLPClassifier` crea una red neuronal para clasificación.

El objetivo es aprender una función parecida a:

```text
64 características de una imagen
           ↓
         MODELO
           ↓
      dígito 0..9
```

---

## 5.2. `hidden_layer_sizes=(64,)`

```python
hidden_layer_sizes=(64,)
```

indica que se utilizará una capa oculta con 64 neuronas.

Una forma sencilla de dibujarlo es:

```text
ENTRADA                 CAPA OCULTA               SALIDA
64 valores  ─────────→  64 neuronas  ─────────→  clase 0..9
```

El paréntesis:

```text
(64,)
```

representa una tupla de Python con un solo elemento.

Aquí ese único elemento indica el tamaño de la única capa oculta definida explícitamente.

---

## 5.3. ¿Qué hace una neurona artificial?

Una neurona combina entradas con pesos.

Una forma simplificada es:

```text
z = x1*w1 + x2*w2 + ... + b
```

Donde:

```text
x = entrada
w = peso
b = sesgo
```

Después se aplica una función de activación.

---

## Ejemplo reproducible en tablero

Supongamos:

```text
x1 = 0.8
x2 = 0.6

w1 = 0.7
w2 = 0.5

b = -0.4
```

Calculamos:

```text
z = x1*w1 + x2*w2 + b
```

Sustituyendo:

```text
z = 0.8*0.7 + 0.6*0.5 - 0.4
```

Entonces:

```text
z = 0.56 + 0.30 - 0.40
z = 0.46
```

La idea didáctica es:

> Una neurona no observa una imagen como una persona. Recibe números, aplica pesos y genera una señal.

Muchas neuronas combinadas pueden aprender patrones más complejos.

---

## 5.4. `max_iter=400`

```python
max_iter=400
```

establece un máximo de iteraciones para el proceso de entrenamiento.

Durante el entrenamiento la red modifica sus pesos buscando reducir el error.

De manera conceptual:

```text
Predice
  ↓
Compara con respuesta real
  ↓
Calcula error
  ↓
Ajusta pesos
  ↓
Vuelve a intentar
```

`max_iter=400` limita cuántas iteraciones puede utilizar el entrenamiento.

No significa necesariamente que siempre deba utilizar las 400.

---

## 5.5. `random_state=42`

```python
random_state=42
```

controla componentes aleatorios del entrenamiento y ayuda a que la práctica sea reproducible.

---

# 6. Entrenamiento de la red neuronal

La línea que realmente entrena el modelo es:

```python
model.fit(X_train, y_train)
```

`fit()` significa ajustar o entrenar.

La red recibe:

```text
X_train = imágenes de entrenamiento
y_train = respuestas correctas
```

Podemos leer la instrucción así:

> Modelo, aprenda a relacionar estas imágenes con estas etiquetas.

---

## Ejemplo cotidiano

Imagine que enseñamos a un niño varias tarjetas.

```text
Imagen de 0 → “esto es cero”
Imagen de 1 → “esto es uno”
Imagen de 2 → “esto es dos”
```

Después de observar muchos ejemplos, esperamos que pueda clasificar una imagen nueva.

`fit()` representa esa etapa de aprendizaje.

---

# 7. Realizar predicciones

Después del entrenamiento aparece:

```python
pred = model.predict(X_test)
```

`predict()` utiliza el modelo ya entrenado para clasificar datos.

El modelo recibe:

```text
X_test
```

que contiene imágenes que fueron reservadas para prueba.

El resultado queda almacenado en:

```python
pred
```

Conceptualmente:

```text
X_test
  ↓
model.predict()
  ↓
pred
```

Por ejemplo:

```text
Respuesta real:     5  2  8  1  3
Predicción modelo:  5  2  8  1  9
```

Aquí cuatro de las cinco respuestas serían correctas.

---

# 8. Cálculo del accuracy

El código muestra la precisión con:

```python
print("Accuracy MLP:", round(accuracy_score(y_test, pred), 4))
```

Vamos a separarlo.

---

## 8.1. `accuracy_score(y_test, pred)`

```python
accuracy_score(y_test, pred)
```

compara:

```text
y_test = respuestas reales
pred   = respuestas generadas por el modelo
```

Si ambas coinciden muchas veces, el accuracy será alto.

---

## 8.2. `round(..., 4)`

```python
round(accuracy_score(y_test, pred), 4)
```

redondea el resultado a cuatro posiciones decimales.

Por ejemplo:

```text
0.962222...
```

se muestra como:

```text
0.9622
```

---

## 8.3. Interpretación del resultado

En la ejecución de referencia del código del PPT se obtiene:

```text
Accuracy MLP: 0.9622
```

Esto puede interpretarse aproximadamente como:

```text
96.22 % de predicciones correctas
```

Es importante explicar a los estudiantes que un accuracy alto no significa automáticamente que el modelo sea perfecto.

Todavía debemos preguntar:

- ¿Qué datos utilizó?
- ¿Qué clases confunde?
- ¿Qué ocurre con imágenes diferentes a las del dataset?
- ¿El conjunto de prueba representa el problema real?
- ¿Podemos reproducir el experimento?

---

# 9. Guardar el modelo entrenado

Después se utiliza:

```python
with (ARTIFACTS / "modelo_mlp.pkl").open("wb") as file:
    pickle.dump(model, file)
```

Este bloque guarda el modelo dentro de un archivo.

---

## 9.1. Construcción de la ruta

```python
ARTIFACTS / "modelo_mlp.pkl"
```

produce una ruta similar a:

```text
artifacts/modelo_mlp.pkl
```

---

## 9.2. `.open("wb")`

```python
.open("wb")
```

abre el archivo en modo escritura binaria.

Las letras significan:

```text
w = write = escribir
b = binary = binario
```

---

## 9.3. `as file`

```python
as file
```

crea una variable temporal llamada `file` que representa el archivo abierto.

---

## 9.4. `pickle.dump()`

```python
pickle.dump(model, file)
```

serializa el objeto `model` y lo escribe dentro del archivo.

Después de ejecutar el código debería existir:

```text
artifacts/modelo_mlp.pkl
```

### Idea para explicar en clase

Antes:

```text
Modelo entrenado → solamente en memoria RAM
```

Después de `pickle.dump()`:

```text
Modelo entrenado → archivo modelo_mlp.pkl
```

---

# 10. Base de datos de imágenes

La siguiente sección crea una base de datos SQLite.

```python
with sqlite3.connect(ARTIFACTS / "imagenes.db") as con:
    con.execute(
        "CREATE TABLE IF NOT EXISTS images("
        "id INTEGER PRIMARY KEY, label INTEGER, split TEXT)"
    )
    con.execute("DELETE FROM images")
    con.executemany(
        "INSERT INTO images(id,label,split) VALUES(?,?,?)",
        [(i, int(y[i]), "dataset") for i in range(20)],
    )
    con.commit()
```

La base de datos generada será:

```text
artifacts/imagenes.db
```

---

# 11. Abrir la base de datos SQLite

La primera línea es:

```python
with sqlite3.connect(ARTIFACTS / "imagenes.db") as con:
```

`sqlite3.connect()` abre una conexión con una base de datos.

Si el archivo todavía no existe, SQLite puede crearlo.

La variable:

```python
con
```

representa la conexión.

Conceptualmente:

```text
Python
  ↓
conexión
  ↓
imagenes.db
```

---

# 12. Crear la tabla `images`

El siguiente bloque es:

```python
con.execute(
    "CREATE TABLE IF NOT EXISTS images("
    "id INTEGER PRIMARY KEY, label INTEGER, split TEXT)"
)
```

La instrucción SQL resultante es equivalente a:

```sql
CREATE TABLE IF NOT EXISTS images(
    id INTEGER PRIMARY KEY,
    label INTEGER,
    split TEXT
)
```

---

## ¿Qué significa `CREATE TABLE`?

```sql
CREATE TABLE
```

significa crear una tabla.

La tabla se llama:

```text
images
```

---

## ¿Qué significa `IF NOT EXISTS`?

```sql
IF NOT EXISTS
```

significa:

> Cree la tabla solamente si todavía no existe.

Esto evita un error al ejecutar nuevamente el programa.

---

## Campo `id`

```sql
id INTEGER PRIMARY KEY
```

`id` es un identificador numérico único.

Ejemplo:

```text
0
1
2
3
...
```

`PRIMARY KEY` significa que se utiliza como clave principal de la tabla.

---

## Campo `label`

```sql
label INTEGER
```

almacena la etiqueta real asociada al ejemplo.

Por ejemplo:

```text
5
```

significa que la imagen corresponde al dígito 5.

---

## Campo `split`

```sql
split TEXT
```

es un campo de texto pensado para describir la partición o el grupo al que pertenece el registro.

En el código del PPT todos los primeros veinte registros reciben literalmente el valor:

```text
dataset
```

Es decir, el código actual **no guarda aquí si una imagen quedó en entrenamiento o prueba**. Guarda solamente el texto `dataset`.

Este detalle es importante para explicarlo exactamente como está implementado.

---

# 13. Limpiar registros anteriores

La siguiente línea es:

```python
con.execute("DELETE FROM images")
```

Esta instrucción elimina los registros existentes dentro de la tabla.

La estructura de la tabla permanece.

Es decir:

```text
ANTES
images
├── fila 1
├── fila 2
└── fila 3
```

Después de:

```sql
DELETE FROM images
```

queda:

```text
images
└── sin registros
```

La intención en esta práctica es poder ejecutar el ejercicio varias veces sin acumular las mismas filas.

---

# 14. Insertar veinte registros

El siguiente bloque es:

```python
con.executemany(
    "INSERT INTO images(id,label,split) VALUES(?,?,?)",
    [(i, int(y[i]), "dataset") for i in range(20)],
)
```

Aquí se insertan veinte filas.

---

## 14.1. Instrucción SQL

```python
"INSERT INTO images(id,label,split) VALUES(?,?,?)"
```

significa:

> Inserte un registro en las columnas `id`, `label` y `split`.

Los signos:

```text
?
?
?
```

son parámetros que serán reemplazados por valores.

---

## 14.2. `executemany()`

```python
con.executemany(...)
```

permite ejecutar la misma instrucción de inserción varias veces.

En lugar de escribir 20 instrucciones `INSERT`, se genera una colección de 20 filas y se insertan juntas.

---

# 15. Comprensión de lista

La expresión:

```python
[(i, int(y[i]), "dataset") for i in range(20)]
```

crea los datos que serán insertados.

Esta sintaxis se llama **list comprehension** o comprensión de lista.

Vamos a separarla.

---

## `range(20)`

```python
range(20)
```

genera valores desde:

```text
0
```

hasta:

```text
19
```

Es decir, veinte posiciones.

---

## `for i in range(20)`

```python
for i in range(20)
```

recorre esos veinte índices.

---

## `y[i]`

```python
y[i]
```

busca la etiqueta correspondiente a la posición `i`.

Por ejemplo:

```text
i = 15
```

entonces:

```python
y[15]
```

representa la etiqueta real del ejemplo número 15.

---

## `int(y[i])`

```python
int(y[i])
```

convierte la etiqueta a un entero de Python antes de almacenarla.

---

## Tupla generada

Cada elemento tiene esta forma:

```python
(i, int(y[i]), "dataset")
```

que corresponde a:

```text
(id, label, split)
```

Por ejemplo, conceptualmente podría producir:

```text
(0, 0, "dataset")
(1, 1, "dataset")
(2, 2, "dataset")
...
```

---

# 16. Confirmar los cambios

La línea:

```python
con.commit()
```

confirma los cambios realizados en la base de datos.

Podemos interpretarlo como:

> Guarde definitivamente las operaciones realizadas durante esta conexión.

Después de ejecutar el bloque debe existir:

```text
artifacts/imagenes.db
```

---

# 17. Consulta para explicar en el tablero

Con los datos registrados podemos formular preguntas mediante SQL.

Por ejemplo:

```sql
SELECT label, COUNT(*)
FROM images
GROUP BY label;
```

Esta consulta responde:

> ¿Cuántos registros existen por cada etiqueta?

La estructura puede explicarse así:

```text
SELECT label, COUNT(*)
```

selecciona la etiqueta y cuenta filas.

```text
FROM images
```

indica que la información sale de la tabla `images`.

```text
GROUP BY label
```

agrupa los registros por etiqueta.

---

# 18. ¿Por qué guardar metadatos de imágenes?

La red neuronal responde algo parecido a:

```text
“Creo que esta imagen representa un 5.”
```

Pero en un sistema real también queremos responder:

```text
¿Qué imagen era?
¿Cuál era su etiqueta real?
¿De dónde salió?
¿Cuándo fue procesada?
¿Qué modelo produjo la predicción?
```

La base de datos ayuda a conservar evidencia y trazabilidad.

Una analogía sencilla es una biblioteca.

La ficha del catálogo no contiene necesariamente el libro completo.

Contiene información para identificarlo:

```text
Código
Título
Autor
Ubicación
```

De manera similar, una base de imágenes puede registrar metadatos de los archivos procesados.

---

# 19. Creación de la ontología como grafo

La siguiente parte del código utiliza NetworkX.

```python
G = nx.DiGraph()
```

Aquí se crea un grafo dirigido.

La variable se llama:

```text
G
```

---

## ¿Qué significa `DiGraph`?

```python
nx.DiGraph()
```

crea un **Directed Graph**, es decir, un grafo dirigido.

En un grafo dirigido la dirección de la relación importa.

Por ejemplo:

```text
modelo_mlp → reconoce → digito
```

no significa exactamente lo mismo que:

```text
digito → reconoce → modelo_mlp
```

La flecha expresa quién se relaciona con quién y en qué dirección.

---

# 20. Agregar relaciones al grafo

El código utiliza:

```python
G.add_edges_from([
    ("digito", "cero", {"rel": "tiene_clase"}),
    ("digito", "uno", {"rel": "tiene_clase"}),
    ("digito", "dos", {"rel": "tiene_clase"}),
    ("modelo_mlp", "digito", {"rel": "reconoce"}),
    ("imagen", "digito", {"rel": "representa"}),
    ("prediccion", "digito", {"rel": "asigna_clase"}),
    ("modelo_mlp", "prediccion", {"rel": "produce"}),
])
```

`add_edges_from()` permite agregar varias relaciones al grafo.

Cada relación tiene tres partes conceptuales:

```text
ORIGEN → RELACIÓN → DESTINO
```

En el código, técnicamente cada tupla tiene:

```python
(origen, destino, {"rel": "tipo_de_relacion"})
```

---

# 21. Primera relación ontológica

```python
("digito", "cero", {"rel": "tiene_clase"})
```

Puede leerse como:

```text
digito → tiene_clase → cero
```

En lenguaje natural:

> El concepto dígito tiene la clase cero.

---

# 22. Segunda relación

```python
("digito", "uno", {"rel": "tiene_clase"})
```

Se interpreta como:

```text
digito → tiene_clase → uno
```

---

# 23. Tercera relación

```python
("digito", "dos", {"rel": "tiene_clase"})
```

Se interpreta como:

```text
digito → tiene_clase → dos
```

Estas tres relaciones muestran que un concepto general puede relacionarse con conceptos más específicos.

---

# 24. Relación `modelo_mlp → reconoce → digito`

```python
("modelo_mlp", "digito", {"rel": "reconoce"})
```

Puede leerse como:

> El modelo MLP reconoce dígitos.

Aquí:

```text
modelo_mlp = origen
reconoce   = relación
digito     = destino
```

---

# 25. Relación `imagen → representa → digito`

```python
("imagen", "digito", {"rel": "representa"})
```

Se interpreta como:

> Una imagen representa un dígito.

Esto conecta el dato de entrada con el concepto del dominio.

---

# 26. Relación `prediccion → asigna_clase → digito`

```python
("prediccion", "digito", {"rel": "asigna_clase"})
```

Puede leerse como:

> Una predicción asigna una clase de dígito.

---

# 27. Relación `modelo_mlp → produce → prediccion`

```python
("modelo_mlp", "prediccion", {"rel": "produce"})
```

Se interpreta como:

> El modelo MLP produce una predicción.

---

# 28. Visualización conceptual de la ontología

Podemos dibujar una parte del grafo en el tablero así:

```text
modelo_mlp
    │
    ├── reconoce ───────→ digito
    │                       │
    │                       ├── tiene_clase → cero
    │                       ├── tiene_clase → uno
    │                       └── tiene_clase → dos
    │
    └── produce ─────────→ prediccion
                              │
                              └── asigna_clase → digito

imagen ─── representa ─────→ digito
```

La intención de este grafo es mostrar significado, no solamente almacenar valores.

---

# 29. ¿Qué es una ontología en este ejercicio?

En un sentido didáctico, la ontología permite representar:

```text
CONCEPTOS
+
RELACIONES CON SIGNIFICADO
```

Por ejemplo:

```text
imagen → representa → digito
modelo_mlp → reconoce → digito
modelo_mlp → produce → prediccion
```

La idea importante para los estudiantes es que la relación debería poder leerse como una frase comprensible.

Por ejemplo:

```text
prediccion → asigna_clase → factura
```

se puede leer como:

> La predicción asigna la clase factura.

En cambio una relación como:

```text
factura → dato → imagen
```

puede ser demasiado ambigua si no se define claramente qué significa `dato`.

---

# 30. Exportar la ontología a GraphML

El código utiliza:

```python
nx.write_graphml(G, ARTIFACTS / "ontologia.graphml")
```

`write_graphml()` guarda el grafo en un archivo GraphML.

El resultado será:

```text
artifacts/ontologia.graphml
```

GraphML es un formato basado en XML que permite representar grafos.

Esto deja evidencia persistente de la estructura creada en memoria.

---

# 31. Contar las relaciones

La siguiente línea es:

```python
print("Relaciones de ontología:", G.number_of_edges())
```

`number_of_edges()` cuenta las aristas o relaciones existentes en el grafo.

En el grafo base del PPT existen siete relaciones.

Por eso la salida esperada es:

```text
Relaciones de ontología: 7
```

---

# 32. Integración entre una predicción y la ontología

Después se utiliza este fragmento:

```python
ejemplo_id = 15
clase_predicha = int(model.predict([X[ejemplo_id]])[0])
concepto = f"digito_{clase_predicha}"
G.add_edge("prediccion_15", concepto, rel="asigna_clase")
G.add_edge("imagen_15", "prediccion_15", rel="genera")
print(ejemplo_id, clase_predicha, concepto)
```

Este bloque conecta una imagen específica con una predicción y con un concepto del grafo.

Es uno de los fragmentos más importantes para entender la integración de la semana.

---

# 33. Seleccionar una imagen concreta

```python
ejemplo_id = 15
```

Aquí se selecciona el ejemplo número 15 del dataset.

La variable:

```text
ejemplo_id
```

queda con el valor:

```text
15
```

Esto permite referirse a una observación específica.

---

# 34. Predecir la clase del ejemplo

La línea es:

```python
clase_predicha = int(model.predict([X[ejemplo_id]])[0])
```

Esta línea realiza varias operaciones.

Vamos desde adentro hacia afuera.

---

## 34.1. `X[ejemplo_id]`

```python
X[ejemplo_id]
```

busca la imagen ubicada en la posición 15.

Como:

```python
ejemplo_id = 15
```

la expresión equivale a:

```python
X[15]
```

---

## 34.2. `[X[ejemplo_id]]`

El código agrega corchetes externos:

```python
[X[ejemplo_id]]
```

Esto convierte la imagen individual en una colección con un solo ejemplo.

`predict()` espera recibir una estructura de muestras.

Conceptualmente:

```text
Una imagen
    ↓
[una imagen]
    ↓
predict()
```

---

## 34.3. `model.predict(...)`

```python
model.predict([X[ejemplo_id]])
```

pide al modelo que clasifique esa imagen.

El resultado es una colección que contiene una predicción.

Podría verse como:

```text
[5]
```

---

## 34.4. `[0]`

```python
model.predict([X[ejemplo_id]])[0]
```

extrae el primer resultado de la colección.

Si el resultado era:

```text
[5]
```

entonces:

```text
[0] → 5
```

---

## 34.5. `int(...)`

Finalmente:

```python
int(...)
```

convierte la clase a un entero de Python.

El valor queda almacenado en:

```python
clase_predicha
```

En la ejecución de referencia del código del PPT:

```text
clase_predicha = 5
```

---

# 35. Crear el nombre del concepto

La siguiente línea es:

```python
concepto = f"digito_{clase_predicha}"
```

Aquí se utiliza una **f-string**.

Las f-strings permiten insertar valores dentro de un texto.

Si:

```text
clase_predicha = 5
```

entonces:

```python
f"digito_{clase_predicha}"
```

produce:

```text
digito_5
```

Por lo tanto:

```python
concepto
```

queda almacenando:

```text
digito_5
```

---

# 36. Conectar la predicción con el concepto

La línea:

```python
G.add_edge("prediccion_15", concepto, rel="asigna_clase")
```

agrega una nueva relación al grafo.

Si:

```text
concepto = digito_5
```

la relación puede leerse como:

```text
prediccion_15 → asigna_clase → digito_5
```

En lenguaje natural:

> La predicción 15 asigna la clase dígito 5.

---

# 37. Conectar la imagen con la predicción

La siguiente línea es:

```python
G.add_edge("imagen_15", "prediccion_15", rel="genera")
```

crea la relación:

```text
imagen_15 → genera → prediccion_15
```

Ahora podemos seguir el recorrido:

```text
imagen_15
    ↓ genera
prediccion_15
    ↓ asigna_clase
digito_5
```

Este recorrido conecta:

```text
EVIDENCIA → RESULTADO → SIGNIFICADO
```

---

# 38. Mostrar el resultado de integración

La última línea del fragmento es:

```python
print(ejemplo_id, clase_predicha, concepto)
```

Con la ejecución de referencia, la salida es:

```text
15 5 digito_5
```

Lo podemos interpretar como:

```text
Ejemplo utilizado: 15
Clase predicha:     5
Concepto creado:    digito_5
```

---

# 39. Recorrido completo de la práctica

Podemos resumir todo el programa de esta manera:

```text
1. Cargar imágenes y etiquetas
          ↓
2. Dividir entrenamiento y prueba
          ↓
3. Crear la red neuronal
          ↓
4. Entrenar la red
          ↓
5. Predecir datos de prueba
          ↓
6. Medir accuracy
          ↓
7. Guardar el modelo
          ↓
8. Crear base SQLite
          ↓
9. Registrar metadatos
          ↓
10. Crear ontología
          ↓
11. Exportar GraphML
          ↓
12. Seleccionar una imagen
          ↓
13. Obtener su predicción
          ↓
14. Relacionar imagen, predicción y concepto
```

---

# 40. Diferencia entre las tres piezas

| Elemento | Pregunta principal | Ejemplo |
|---|---|---|
| Red neuronal | ¿Qué clase parece ser? | “La imagen parece un 5” |
| Base de datos | ¿Qué evidencia tengo registrada? | id, etiqueta y grupo del registro |
| Ontología | ¿Qué significa y cómo se relaciona? | predicción asigna_clase dígito_5 |

Una frase sencilla para recordar en clase es:

```text
MODELO RECONOCE
BASE REGISTRA
ONTOLOGÍA INTERPRETA
```

---

# 41. Archivos generados

Después de ejecutar la práctica deberían generarse al menos estos artefactos:

```text
artifacts/
├── modelo_mlp.pkl
├── imagenes.db
└── ontologia.graphml
```

### `modelo_mlp.pkl`

Contiene el modelo neuronal entrenado.

### `imagenes.db`

Contiene la base de datos SQLite con metadatos de imágenes.

### `ontologia.graphml`

Contiene el grafo ontológico exportado.

---

# 42. Resultado esperado en consola

En la ejecución de referencia del código incluido en el PPT se obtiene:

```text
Accuracy MLP: 0.9622
Relaciones de ontología: 7
15 5 digito_5
```

La primera línea indica el desempeño del clasificador sobre el conjunto de prueba.

La segunda confirma que el grafo base tenía siete relaciones en el momento de hacer el conteo.

La tercera muestra el ejemplo seleccionado, la clase predicha y el concepto generado.

---

# 43. Observación docente importante sobre el orden del GraphML

En el código presentado en el PPT, esta línea aparece antes del bloque final de integración:

```python
nx.write_graphml(G, ARTIFACTS / "ontologia.graphml")
```

Después de guardar el archivo se agregan dos relaciones nuevas:

```python
G.add_edge("prediccion_15", concepto, rel="asigna_clase")
G.add_edge("imagen_15", "prediccion_15", rel="genera")
```

Por lo tanto, **tal como está escrito el código del PPT**, esas dos relaciones sí quedan agregadas al grafo `G` que está en memoria, pero no quedan incluidas en el archivo `ontologia.graphml` que ya había sido exportado anteriormente.

Este es un buen punto para explicar en clase la diferencia entre:

```text
OBJETO EN MEMORIA
```

y:

```text
ARCHIVO GUARDADO EN DISCO
```

Si se quisiera que el archivo final también contuviera esas relaciones, habría que volver a exportar el grafo después de agregarlas.

Por ejemplo, como mejora posterior:

```python
nx.write_graphml(G, ARTIFACTS / "ontologia.graphml")
```

al final del programa.

Esta observación no cambia el código original del PPT; solamente explica su comportamiento exacto.

---

# 44. Observación docente sobre el campo `split`

La tabla se define con:

```sql
split TEXT
```

pero la inserción utilizada en el PPT es:

```python
[(i, int(y[i]), "dataset") for i in range(20)]
```

Por eso todos esos registros reciben:

```text
dataset
```

No reciben literalmente:

```text
train
```

o:

```text
test
```

Esto puede utilizarse como pregunta para los estudiantes:

> Si quisiéramos auditar realmente qué imágenes pertenecieron a entrenamiento y cuáles a prueba, ¿qué deberíamos modificar en la estructura de almacenamiento?

---

# 45. Código completo de la práctica

A continuación se presenta unido el código trabajado en el PPT.

```python
from pathlib import Path
import pickle
import sqlite3
import networkx as nx
from sklearn.datasets import load_digits
from sklearn.model_selection import train_test_split
from sklearn.neural_network import MLPClassifier
from sklearn.metrics import accuracy_score

ROOT = Path(__file__).resolve().parent.parent
ARTIFACTS = ROOT / "artifacts"
ARTIFACTS.mkdir(parents=True, exist_ok=True)

X, y = load_digits(return_X_y=True)
X_train, X_test, y_train, y_test = train_test_split(
    X, y, test_size=0.25, random_state=42, stratify=y
)

model = MLPClassifier(
    hidden_layer_sizes=(64,),
    max_iter=400,
    random_state=42
)
model.fit(X_train, y_train)
pred = model.predict(X_test)
print("Accuracy MLP:", round(accuracy_score(y_test, pred), 4))

with (ARTIFACTS / "modelo_mlp.pkl").open("wb") as file:
    pickle.dump(model, file)

with sqlite3.connect(ARTIFACTS / "imagenes.db") as con:
    con.execute(
        "CREATE TABLE IF NOT EXISTS images("
        "id INTEGER PRIMARY KEY, label INTEGER, split TEXT)"
    )
    con.execute("DELETE FROM images")
    con.executemany(
        "INSERT INTO images(id,label,split) VALUES(?,?,?)",
        [(i, int(y[i]), "dataset") for i in range(20)],
    )
    con.commit()

G = nx.DiGraph()
G.add_edges_from([
    ("digito", "cero", {"rel": "tiene_clase"}),
    ("digito", "uno", {"rel": "tiene_clase"}),
    ("digito", "dos", {"rel": "tiene_clase"}),
    ("modelo_mlp", "digito", {"rel": "reconoce"}),
    ("imagen", "digito", {"rel": "representa"}),
    ("prediccion", "digito", {"rel": "asigna_clase"}),
    ("modelo_mlp", "prediccion", {"rel": "produce"}),
])

nx.write_graphml(G, ARTIFACTS / "ontologia.graphml")
print("Relaciones de ontología:", G.number_of_edges())

ejemplo_id = 15
clase_predicha = int(model.predict([X[ejemplo_id]])[0])
concepto = f"digito_{clase_predicha}"
G.add_edge("prediccion_15", concepto, rel="asigna_clase")
G.add_edge("imagen_15", "prediccion_15", rel="genera")
print(ejemplo_id, clase_predicha, concepto)
```

---

# 46. Resumen de instrucciones y funciones utilizadas

| Elemento | Qué hace | Para qué sirve en la práctica |
|---|---|---|
| `Path` | Maneja rutas | Ubicar la carpeta `artifacts` |
| `pickle` | Serializa objetos Python | Guardar el modelo entrenado |
| `sqlite3` | Gestiona SQLite | Crear la base `imagenes.db` |
| `networkx` | Trabaja con grafos | Construir la ontología |
| `load_digits()` | Carga imágenes y etiquetas | Obtener el dataset de dígitos |
| `train_test_split()` | Divide los datos | Separar entrenamiento y prueba |
| `MLPClassifier()` | Crea una red neuronal | Clasificar dígitos |
| `.fit()` | Entrena el modelo | Aprender patrones |
| `.predict()` | Genera predicciones | Reconocer clases |
| `accuracy_score()` | Compara predicción y realidad | Medir desempeño |
| `pickle.dump()` | Guarda un objeto | Crear `modelo_mlp.pkl` |
| `sqlite3.connect()` | Abre una base de datos | Crear/usar `imagenes.db` |
| `CREATE TABLE` | Crea una tabla | Definir `images` |
| `DELETE FROM` | Borra registros | Reiniciar los datos de práctica |
| `executemany()` | Ejecuta muchas inserciones | Registrar 20 metadatos |
| `commit()` | Confirma cambios | Persistir datos en SQLite |
| `nx.DiGraph()` | Crea un grafo dirigido | Representar conceptos y relaciones |
| `add_edges_from()` | Agrega varias relaciones | Crear la ontología base |
| `add_edge()` | Agrega una relación | Integrar imagen y predicción |
| `write_graphml()` | Exporta el grafo | Crear `ontologia.graphml` |
| `number_of_edges()` | Cuenta relaciones | Verificar el grafo |
| `f"..."` | Inserta valores en texto | Crear `digito_5`, etc. |

---

# 47. Preguntas para hacer durante la explicación

Estas preguntas permiten comprobar si los estudiantes realmente comprendieron el código.

### Pregunta 1

¿Por qué dividimos los datos entre entrenamiento y prueba?

**Respuesta esperada:** para medir si el modelo puede generalizar a datos que no utilizó para aprender.

### Pregunta 2

¿Qué diferencia existe entre `X` y `y`?

**Respuesta esperada:** `X` contiene las características de las imágenes y `y` contiene la clase real de cada ejemplo.

### Pregunta 3

¿Qué hace `model.fit()`?

**Respuesta esperada:** entrena la red utilizando los datos y etiquetas de entrenamiento.

### Pregunta 4

¿Qué hace `model.predict()`?

**Respuesta esperada:** utiliza el modelo entrenado para asignar una clase a nuevas muestras.

### Pregunta 5

¿Qué representa el accuracy?

**Respuesta esperada:** la proporción de predicciones correctas frente al total evaluado.

### Pregunta 6

¿Por qué guardamos el modelo con `pickle`?

**Respuesta esperada:** para poder reutilizar el modelo entrenado sin volver a entrenarlo cada vez.

### Pregunta 7

¿Qué diferencia existe entre la base de datos y la ontología?

**Respuesta esperada:** la base registra datos o evidencia; la ontología representa conceptos y relaciones con significado.

### Pregunta 8

¿Qué significa esta relación?

```text
modelo_mlp → produce → prediccion
```

**Respuesta esperada:** que el modelo MLP genera una predicción.

### Pregunta 9

¿Por qué una ontología utiliza relaciones con significado?

**Respuesta esperada:** porque no basta con conectar elementos; necesitamos expresar qué tipo de relación existe entre ellos.

### Pregunta 10

¿Qué recorrido conceptual representa este grafo?

```text
imagen_15 → genera → prediccion_15 → asigna_clase → digito_5
```

**Respuesta esperada:** conecta la evidencia de entrada con la predicción generada y con el concepto reconocido.

---

# 48. Ejercicio reproducible en el tablero: red neuronal

Puede escribirse:

```text
x1 = 0.8
x2 = 0.6
w1 = 0.7
w2 = 0.5
b  = -0.4
```

Después:

```text
z = x1*w1 + x2*w2 + b
```

Sustituyendo:

```text
z = 0.8*0.7 + 0.6*0.5 - 0.4
z = 0.56 + 0.30 - 0.40
z = 0.46
```

Pregunta para los estudiantes:

> ¿Qué ocurriría con la salida si uno de los pesos aumentara considerablemente?

La intención es introducir la idea de que los pesos representan la influencia que una señal tiene dentro del cálculo neuronal.

---

# 49. Ejercicio reproducible en el tablero: división de datos

Escribir:

```text
20 imágenes
```

Luego preguntar:

> Si usamos 75 % para entrenamiento y 25 % para prueba, ¿cuántas quedarían en cada grupo?

Resultado:

```text
Entrenamiento = 15
Prueba         = 5
```

Después preguntar:

> ¿Por qué sería incorrecto entrenar con las 20 y luego afirmar que se validó el aprendizaje usando exactamente esas mismas 20?

La idea es diferenciar entrenamiento de validación.

---

# 50. Ejercicio reproducible en el tablero: base de datos

Dibujar:

```text
images
+----+-------+---------+
| id | label | split   |
+----+-------+---------+
| 0  | 0     | dataset |
| 1  | 1     | dataset |
| 2  | 2     | dataset |
+----+-------+---------+
```

Después escribir:

```sql
SELECT label, COUNT(*)
FROM images
GROUP BY label;
```

Pregunta:

> ¿Qué información nueva aporta esta consulta frente a mirar una sola fila?

Respuesta esperada:

> Permite resumir cuántos registros existen para cada clase.

---

# 51. Ejercicio reproducible en el tablero: ontología

Escribir primero:

```text
Concepto A → relación → Concepto B
```

Después construir ejemplos:

```text
modelo → reconoce → documento
imagen → representa → documento
prediccion → asigna_clase → factura
```

Luego pedir a un estudiante que proponga una relación relacionada con su proyecto.

La relación debería poder leerse como una frase natural.

Por ejemplo:

```text
sensor → detecta → temperatura_alta
```

puede leerse como:

> El sensor detecta temperatura alta.

---

# 52. Adaptación al proyecto de cada estudiante

El código de clase utiliza dígitos porque permite concentrarse en la técnica.

En el proyecto de cada estudiante deben cambiar los conceptos genéricos por conceptos propios del dominio.

Por ejemplo, un proyecto relacionado con documentos podría utilizar:

```text
imagen_documento
factura
contrato
modelo_documental
prediccion_documental
```

Y relaciones como:

```text
modelo_documental → reconoce → factura
imagen_documento → representa → contrato
prediccion_documental → asigna_clase → factura
factura → pertenece_a → documento_financiero
```

La idea no es copiar literalmente la ontología de dígitos.

La intención es demostrar comprensión y adaptación.

---

# 53. Idea principal del ejercicio

La práctica de la semana 8 no consiste únicamente en entrenar una red neuronal.

El objetivo es comprender el ciclo completo:

```text
RECONOCER
+
REGISTRAR
+
INTERPRETAR
```

La red neuronal permite reconocer patrones.

La base de datos permite dejar evidencia persistente.

La ontología permite relacionar la predicción con conceptos del dominio.

Por eso el flujo final puede expresarse como:

```text
Entrada
  ↓
Modelo
  ↓
Predicción
  ↓
Evidencia
  ↓
Significado
```

Ese recorrido permite pasar de una salida puramente numérica a una representación que puede ser explicada, auditada y utilizada dentro de un sistema de Inteligencia Artificial más completo.
