# Explicación de la Semana 14 - Inteligencia Artificial

## Ingeniería del conocimiento: representaciones del conocimiento y lingüística con redes semánticas

**Asignatura identificada en el sílabo:** Inteligencia Artificial (Ingeniería de Sistemas, décimo semestre).  
**Semana solicitada por el prompt maestro:** 14.  
**Referencia académica:** sílabo *IS 10 2040 INTELIGENCIA ARTIFICIAL*, página 3, tabla de contenidos temáticos.  
**Tema y alcance textuales del sílabo:** «Ingeniería del conocimiento – Representaciones del conocimiento y lingüística con redes semánticas».  
**Resultados de aprendizaje vinculados (página 2):** RAC1, construcción de simulaciones basadas en técnicas de IA; RAC2, diseño de herramientas computacionales que generan respuestas específicas. 

> **Separación de fuentes:** el sílabo define el tema y la semana, **pero no establece Python, una versión, un editor, una biblioteca ni un caso de negocio obligatorio**. El programa que sigue es una **propuesta pedagógica de laboratorio**, elegida para enseñar los conceptos de forma reproducible. El PowerPoint JSP y su explicación `.md` se usaron como referencias de diseño y estilo de enseñanza, NO como fuente de contenido de IA.

---

## 1. Objetivo de la clase

Al finalizar, el estudiante debe poder modelar conceptos y relaciones en una red semántica, transformar oraciones sencillas en triples, consultar la jerarquía `es_un` y explicar una inferencia por herencia **según reglas declaradas**. Además, debe identificar los límites de un analizador lingüístico basado en patrones.

### Resultado observable

Desde la consola, el estudiante construirá una red pequeña con los nodos `perro`, `mamifero`, `animal`, `gato` y `agua`. Tendrá que mostrar dos hechos inferidos:

- `perro es_un animal`, aunque no exista una arista directa entre esos nodos.
- `perro necesita agua` como propiedad heredada de `animal`, **bajo la regla didáctica de herencia definida en nuestro programa**.

La prueba negativa deberá indicar que `perro es_un ave` es falso **en este grafo y con los datos disponibles**, lo que no equivale a demostrar que algo sea falso en todo el mundo real.

---

## 2. Mapa conceptual de la Semana 14

```text
Oración: «Un perro es un mamífero»
            │
            ▼
NORMALIZACIÓN LINGÜÍSTICA (minúsculas y tildes)
            │
            ▼
RECONOCIMIENTO DE UN PATRÓN (no es comprensión libre de texto)
            │
            ▼
TRIPLE: (perro, es_un, mamifero)
            │
            ▼
RED SEMÁNTICA = nodos + relaciones etiquetadas
            │
            ▼
CONSULTA E INFERENCIA (recorrido del grafo)
            │
            ▼
RESPUESTA + EXPLICACIÓN DE LA RUTA
```

### Diferencia esencial

Un **dato** puede ser una cadena como `perro`. Una **relación** conecta dos conceptos: `(perro, es_un, mamifero)`. Una **regla de inferencia** permite derivar información no almacenada directamente, por ejemplo, transitividad de `es_un`.

---

## 3. Conceptos que el estudiante debe comprender

### 3.1 Ingeniería del conocimiento

Disciplina que analiza un dominio, identifica conceptos relevantes, define relaciones entre ellos y representa esa información para permitir consultas e inferencias. No consiste solamente en almacenar palabras: también exige definir el significado de las relaciones, los límites del dominio y cómo comprobar respuestas.

### 3.2 Representación del conocimiento

Es un modelo estructurado de entidades, categorías, propiedades y relaciones. Una representación permite que un programa trabaje con hechos de manera explícita y rastreable. Ejemplos de alternativas: reglas, lógica, marcos, ontologías y redes semánticas. En esta semana nos concentramos en **redes semánticas**.

### 3.3 Red semántica

Es un grafo en el que los **nodos** representan conceptos y las **aristas dirigidas y etiquetadas** describen relaciones.

```text
[perro] --es_un--> [mamifero] --es_un--> [animal]
                                          |
                                      necesita
                                          v
                                        [agua]
```

La etiqueta `es_un` representa pertenencia a una categoría o relación de subtipo **según el modelo**. La etiqueta `necesita` representa una propiedad. Son distintas y no pueden interpretarse automáticamente de la misma manera.

### 3.4 Lingüística y significado

En lingüística, una oración expresa relaciones entre unidades del lenguaje. Para un laboratorio sencillo podemos dividir la oración en **sujeto, relación y objeto**: «Un perro es un mamífero» → `(perro, es_un, mamifero)`.

No obstante, el lenguaje natural presenta negación, plurales, ambigüedad, referencias, contexto y relaciones complejas. El código de esta clase **no** resuelve esos fenómenos: reconoce únicamente dos patrones predefinidos. Debe explicarse expresamente esta diferencia.

### 3.5 Inferencia y herencia

Si el grafo declara `perro es_un mamifero` y `mamifero es_un animal`, la transitividad definida para `es_un` permite responder `perro es_un animal`. Si `animal necesita agua`, nuestro motor didáctico permite **heredar** esa propiedad a `perro`. La herencia depende de supuestos del dominio: no cualquier relación debe propagarse a los descendientes.

### 3.6 Datos explícitos y datos inferidos

**Explícito**: el triple se guardó mediante `agregar()`. **Inferido**: se dedujo recorriendo varios enlaces y aplicando una regla del modelo. En el informe el estudiante debe distinguir ambos.

---

## 4. Herramientas y requisitos

**Propuesta pedagógica**, no exigencia textual del sílabo:

- Python 3.10 o superior para ejecutar anotaciones de tipos modernas; preferible una versión estable instalada en el equipo.
- Editor de código a elección y terminal.
- Solo biblioteca estándar: `re`, `unicodedata` y `unittest`. No se necesitan API, conectividad externa ni servicios de pago.
- Sistema operativo Windows, macOS o Linux.

No hay instalaciones mediante `pip` en este ejemplo.

### Estructura de archivos

```text
semana14-redes-semanticas/
├── red_semantica.py        # normalización, parser y consultas sobre el grafo
├── main.py                 # carga de frases y demostración en consola
└── test_red_semantica.py   # pruebas automatizadas con unittest
```

Los archivos se guardan juntos en la misma carpeta. No uses el nombre de `main.py` como nombre de la biblioteca para evitar conflictos de importación.

---

## 5. Secuencia de desarrollo guiado

1. Crear la carpeta del ejercicio dentro del repositorio académico que ya se está usando.
2. Crear `red_semantica.py`; comenzar por normalización e interpretación.
3. Implementar la clase `RedSemantica`, almacenamiento de triples y consultas.
4. Crear `main.py` con cuatro oraciones de ejemplo.
5. Ejecutar y comprobar la salida; explicar qué hechos están guardados y cuáles son inferidos.
6. Crear `test_red_semantica.py` y ejecutar las pruebas.
7. Sustituir el dominio de animales por conceptos propios del proyecto, sin copiar literalmente los ejemplos.
8. Documentar el resultado y guardar el avance en el repositorio.

---

## 6. Código completo, organizado por archivo

Las siguientes versiones son coherentes entre sí y fueron probadas con la biblioteca estándar de Python. Las líneas exactas que se comentan en la siguiente sección pertenecen a estos archivos.

### Archivo `red_semantica.py` - código completo

```python
"""Red semantica didactica con parser de oraciones restringido."""

import re
import unicodedata


def normalizar(texto: str) -> str:
    """Pasa a minusculas y elimina tildes para comparar terminos."""
    base = unicodedata.normalize("NFD", texto.casefold().strip())
    return "".join(c for c in base if unicodedata.category(c) != "Mn")


def interpretar(oracion: str) -> tuple[str, str, str]:
    """Acepta dos estructuras fijas de oraciones en espanol."""
    texto = normalizar(oracion).strip(" .!?")
    patrones = [
        (r"(?:un|una|el|la) (\w+) es (?:un|una) (\w+)", "es_un"),
        (r"(?:un|una|el|la) (\w+) necesita (\w+)", "necesita"),
    ]
    for patron, relacion in patrones:
        coincidencia = re.fullmatch(patron, texto)
        if coincidencia:
            sujeto, objeto = coincidencia.groups()
            return sujeto, relacion, objeto
    raise ValueError("Oracion fuera de los patrones admitidos")


class RedSemantica:
    """Guarda triples y permite consultar jerarquias y propiedades."""

    def __init__(self) -> None:
        self.aristas: dict[str, list[tuple[str, str]]] = {}

    def agregar(self, sujeto: str, relacion: str, objeto: str) -> None:
        if relacion not in {"es_un", "necesita"}:
            raise ValueError("Relacion no admitida")
        triple = (relacion, objeto)
        vecinos = self.aristas.setdefault(sujeto, [])
        if triple not in vecinos:
            vecinos.append(triple)

    def es_un(self, origen: str, categoria: str) -> bool:
        pendientes = [origen]
        visitados: set[str] = set()
        while pendientes:
            actual = pendientes.pop()
            if actual == categoria:
                return True
            if actual in visitados:
                continue
            visitados.add(actual)
            for relacion, destino in self.aristas.get(actual, []):
                if relacion == "es_un":
                    pendientes.append(destino)
        return False

    def necesidades(self, concepto: str) -> list[str]:
        pendientes = [concepto]
        visitados: set[str] = set()
        resultados: set[str] = set()
        while pendientes:
            actual = pendientes.pop()
            if actual in visitados:
                continue
            visitados.add(actual)
            for relacion, destino in self.aristas.get(actual, []):
                if relacion == "es_un":
                    pendientes.append(destino)
                elif relacion == "necesita":
                    resultados.add(destino)
        return sorted(resultados)
```


### Archivo `main.py` - código completo

```python
"""Demostracion de redes semanticas para la Semana 14."""

from red_semantica import RedSemantica, interpretar


def main() -> None:
    red = RedSemantica()
    oraciones = [
        "Un perro es un mamífero.",
        "Un mamífero es un animal.",
        "Un animal necesita agua.",
        "Un gato es un mamífero.",
    ]
    for oracion in oraciones:
        sujeto, relacion, objeto = interpretar(oracion)
        red.agregar(sujeto, relacion, objeto)
        print(f"Hecho: ({sujeto}, {relacion}, {objeto})")

    print("¿Perro es un animal?:", red.es_un("perro", "animal"))
    print("Necesidades de perro:", red.necesidades("perro"))
    print("¿Perro es un ave?:", red.es_un("perro", "ave"))


if __name__ == "__main__":
    main()
```


### Archivo `test_red_semantica.py` - código completo

```python
"""Pruebas del motor didactico."""

import unittest

from red_semantica import RedSemantica, interpretar


class PruebasRedSemantica(unittest.TestCase):
    def setUp(self) -> None:
        self.red = RedSemantica()
        self.red.agregar("perro", "es_un", "mamifero")
        self.red.agregar("mamifero", "es_un", "animal")
        self.red.agregar("animal", "necesita", "agua")

    def test_transitividad(self) -> None:
        self.assertTrue(self.red.es_un("perro", "animal"))

    def test_herencia(self) -> None:
        self.assertEqual(self.red.necesidades("perro"), ["agua"])

    def test_sin_relacion_no_infiere(self) -> None:
        self.assertFalse(self.red.es_un("perro", "ave"))

    def test_interpretacion_linguistica(self) -> None:
        self.assertEqual(
            interpretar("Un perro es un mamífero."),
            ("perro", "es_un", "mamifero"),
        )

    def test_oracion_no_admitida(self) -> None:
        with self.assertRaises(ValueError):
            interpretar("Los perros corren muy rápido.")

    def test_ciclos_no_bloquean(self) -> None:
        self.red.agregar("animal", "es_un", "perro")
        self.assertFalse(self.red.es_un("perro", "ave"))
        self.assertEqual(self.red.necesidades("perro"), ["agua"])


if __name__ == "__main__":
    unittest.main()
```


---

## 7. Explicación línea por línea, como material de clase

Los números corresponden a las líneas reales de los tres archivos anteriores. Las líneas en blanco solo separan bloques y no ejecutan operaciones.


### 7.1. Archivo `red_semantica.py`


**Línea 1.** `"""Red semantica didactica con parser de oraciones restringido."""`

Docstring del módulo: aclara que se trata de un ejercicio didáctico y que el analizador de lenguaje está restringido.


**Línea 3.** `import re`

Importa expresiones regulares de la biblioteca estándar. Se usan para comprobar que una oración siga exactamente un patrón.


**Línea 4.** `import unicodedata`

Importa las herramientas Unicode para eliminar tildes de la representación interna sin modificar el archivo original.


**Línea 7.** `def normalizar(texto: str) -> str:`

Declara `normalizar`, que recibe una cadena y devuelve otra cadena. Su objetivo es reducir variaciones superficiales del texto.


**Línea 8.** `    """Pasa a minusculas y elimina tildes para comparar terminos."""`

Documenta el objetivo de la función: conversión a minúsculas y eliminación de tildes para comparar símbolos.


**Línea 9.** `    base = unicodedata.normalize("NFD", texto.casefold().strip())`

`casefold()` normaliza mayúsculas/minúsculas, `strip()` elimina espacios de los extremos y NFD separa caracteres base de marcas de acento.


**Línea 10.** `    return "".join(c for c in base if unicodedata.category(c) != "Mn")`

Reconstruye el texto ignorando caracteres Unicode de categoría `Mn` (marcas combinantes); por eso «mamífero» termina como «mamifero».


**Línea 13.** `def interpretar(oracion: str) -> tuple[str, str, str]:`

Declara `interpretar`, que recibe una oración y devuelve un triple de cadenas `(sujeto, relación, objeto)`.


**Línea 14.** `    """Acepta dos estructuras fijas de oraciones en espanol."""`

Explicita en la documentación que el analizador NO entiende lenguaje arbitrario: solo dos construcciones lingüísticas.


**Línea 15.** `    texto = normalizar(oracion).strip(" .!?")`

Normaliza la entrada y quita signos comunes de puntuación situados en los extremos, no en el interior.


**Línea 16.** `    patrones = [`

Inicia una lista de patrones admitidos por el experimento.


**Línea 17.** `        (r"(?:un|una|el|la) (\w+) es (?:un|una) (\w+)", "es_un"),`

El primer patrón admite artículos simples y frases como «un perro es un mamifero»; su etiqueta semántica será `es_un`.


**Línea 18.** `        (r"(?:un|una|el|la) (\w+) necesita (\w+)", "necesita"),`

El segundo patrón admite frases del tipo «un animal necesita agua» y usa la relación `necesita`.


**Línea 19.** `    ]`

Cierra la lista de patrones. Agregar una gramática más amplia exigiría nuevas reglas y pruebas.


**Línea 20.** `    for patron, relacion in patrones:`

Recorre los dos patrones y su etiqueta de relación correspondiente.


**Línea 21.** `        coincidencia = re.fullmatch(patron, texto)`

`re.fullmatch` verifica que TODA la oración encaje; una coincidencia parcial no basta.


**Línea 22.** `        if coincidencia:`

Comprueba si existe una coincidencia válida.


**Línea 23.** `            sujeto, objeto = coincidencia.groups()`

Extrae las dos capturas del patrón, interpretadas como sujeto y objeto.


**Línea 24.** `            return sujeto, relacion, objeto`

Devuelve un triple canónico que podrá almacenarse en el grafo.


**Línea 25.** `    raise ValueError("Oracion fuera de los patrones admitidos")`

Rechaza explícitamente oraciones no admitidas en vez de inventar relaciones o dar respuestas sin sustento.


**Línea 28.** `class RedSemantica:`

Declara la clase responsable de almacenar conceptos y aristas etiquetadas.


**Línea 29.** `    """Guarda triples y permite consultar jerarquias y propiedades."""`

Documenta la responsabilidad de la clase: triples, consultas de jerarquía y propiedades heredables.


**Línea 31.** `    def __init__(self) -> None:`

Constructor llamado al crear una nueva instancia de la red semántica.


**Línea 32.** `        self.aristas: dict[str, list[tuple[str, str]]] = {}`

Crea un diccionario vacío: cada clave es un nodo origen y cada valor es una lista de pares `(relación, destino)`.


**Línea 34.** `    def agregar(self, sujeto: str, relacion: str, objeto: str) -> None:`

Método para registrar un hecho explícito `(sujeto, relación, objeto)`.


**Línea 35.** `        if relacion not in {"es_un", "necesita"}:`

Restringe las etiquetas a las dos relaciones conocidas por el modelo didáctico.


**Línea 36.** `            raise ValueError("Relacion no admitida")`

Genera un error claro si una relación no tiene semántica definida aquí.


**Línea 37.** `        triple = (relacion, objeto)`

Forma el par destino-etiqueta que se guardará como arista saliente del sujeto.


**Línea 38.** `        vecinos = self.aristas.setdefault(sujeto, [])`

`setdefault` obtiene los vecinos existentes o crea una lista vacía si el concepto aún no aparece.


**Línea 39.** `        if triple not in vecinos:`

Evita almacenar dos veces exactamente la misma arista.


**Línea 40.** `            vecinos.append(triple)`

Agrega la arista que representa un hecho explícito.


**Línea 42.** `    def es_un(self, origen: str, categoria: str) -> bool:`

Define una consulta sobre jerarquía que devuelve verdadero si se puede llegar de `origen` a `categoria` por enlaces `es_un`.


**Línea 43.** `        pendientes = [origen]`

Inicializa una lista de nodos pendientes; actúa como pila de recorrido en profundidad.


**Línea 44.** `        visitados: set[str] = set()`

Crea un conjunto de nodos ya visitados para impedir ciclos infinitos.


**Línea 45.** `        while pendientes:`

Mantiene la búsqueda mientras queden conceptos pendientes.


**Línea 46.** `            actual = pendientes.pop()`

Extrae un nodo que debe analizarse.


**Línea 47.** `            if actual == categoria:`

Comprueba si el nodo alcanzado coincide con la categoría objetivo; el modelo trata esta consulta como reflexiva.


**Línea 48.** `                return True`

Devuelve `True` en cuanto encuentra una ruta válida.


**Línea 49.** `            if actual in visitados:`

Detecta si ya se exploró el nodo; evita repetir trabajos o quedar atrapado en ciclos.


**Línea 50.** `                continue`

Continúa con el siguiente nodo pendiente sin procesar nuevamente el actual.


**Línea 51.** `            visitados.add(actual)`

Marca el nodo como explorado.


**Línea 52.** `            for relacion, destino in self.aristas.get(actual, []):`

Obtiene todas las aristas salientes del nodo; usa lista vacía si no tiene entradas.


**Línea 53.** `                if relacion == "es_un":`

Permite recorrer SOLO relaciones `es_un`; no confunde `necesita` con jerarquía.


**Línea 54.** `                    pendientes.append(destino)`

Agrega el destino a la pila para seguir explorando la jerarquía.


**Línea 55.** `        return False`

Devuelve `False` si no se encontró ruta alguna en los datos disponibles; no constituye una negación ontológica universal.


**Línea 57.** `    def necesidades(self, concepto: str) -> list[str]:`

Define la consulta que hereda valores de la relación `necesita` desde los ancestros del concepto.


**Línea 58.** `        pendientes = [concepto]`

Comienza el recorrido desde el concepto solicitado.


**Línea 59.** `        visitados: set[str] = set()`

Controla los nodos visitados para no quedarse en una jerarquía circular.


**Línea 60.** `        resultados: set[str] = set()`

Almacena resultados sin repeticiones mediante un conjunto.


**Línea 61.** `        while pendientes:`

Repite el recorrido hasta procesar todas las categorías alcanzables.


**Línea 62.** `            actual = pendientes.pop()`

Extrae el siguiente concepto a revisar.


**Línea 63.** `            if actual in visitados:`

Verifica si ya se visitó.


**Línea 64.** `                continue`

Salta nodos repetidos para asegurar terminación.


**Línea 65.** `            visitados.add(actual)`

Registra el concepto actual como visitado.


**Línea 66.** `            for relacion, destino in self.aristas.get(actual, []):`

Recorre cada relación y destino que salen del concepto.


**Línea 67.** `                if relacion == "es_un":`

Si encuentra una relación jerárquica, continúa visitando una categoría superior.


**Línea 68.** `                    pendientes.append(destino)`

Agrega esa categoría a la pila, donde podrá aportar propiedades.


**Línea 69.** `                elif relacion == "necesita":`

Si el enlace expresa `necesita`, identifica una propiedad transferible según la regla de este ejemplo.


**Línea 70.** `                    resultados.add(destino)`

Agrega el valor heredado al conjunto de resultados.


**Línea 71.** `        return sorted(resultados)`

Ordena y devuelve los valores encontrados, con salida reproducible sin duplicados.


### 7.2. Archivo `main.py`


**Línea 1.** `"""Demostracion de redes semanticas para la Semana 14."""`

Docstring que identifica el objetivo docente de este archivo: ejecutar la demostración de la Semana 14.


**Línea 3.** `from red_semantica import RedSemantica, interpretar`

Importa el grafo y el analizador de oraciones desde `red_semantica.py`; ambos archivos deben estar en la misma carpeta.


**Línea 6.** `def main() -> None:`

Declara la función principal del programa, que organiza el ejemplo sin ejecutar nada al importar este archivo.


**Línea 7.** `    red = RedSemantica()`

Crea una nueva red semántica inicialmente vacía.


**Línea 8.** `    oraciones = [`

Abre la lista de enunciados que funcionarán como pequeña base de conocimiento.


**Línea 9.** `        "Un perro es un mamífero.",`

Primer hecho explícito: `perro es_un mamifero`.


**Línea 10.** `        "Un mamífero es un animal.",`

Segundo hecho explícito: `mamifero es_un animal`.


**Línea 11.** `        "Un animal necesita agua.",`

Tercer hecho explícito: `animal necesita agua`.


**Línea 12.** `        "Un gato es un mamífero.",`

Cuarto hecho explícito: `gato es_un mamifero`.


**Línea 13.** `    ]`

Cierra la lista de enunciados para el experimento.


**Línea 14.** `    for oracion in oraciones:`

Itera sobre cada oración en español.


**Línea 15.** `        sujeto, relacion, objeto = interpretar(oracion)`

Convierte cada frase admitida en el triple sujeto-relación-objeto.


**Línea 16.** `        red.agregar(sujeto, relacion, objeto)`

Registra el triple como arista del grafo; no infiere todavía.


**Línea 17.** `        print(f"Hecho: ({sujeto}, {relacion}, {objeto})")`

Muestra los hechos almacenados para que el estudiante compruebe la carga de conocimiento.


**Línea 19.** `    print("¿Perro es un animal?:", red.es_un("perro", "animal"))`

Consulta una relación transitiva: el motor encuentra `perro -> mamifero -> animal`.


**Línea 20.** `    print("Necesidades de perro:", red.necesidades("perro"))`

Consulta una propiedad heredada: encuentra `agua` en el nodo ancestro `animal`.


**Línea 21.** `    print("¿Perro es un ave?:", red.es_un("perro", "ave"))`

Consulta un caso sin camino `es_un` hacia `ave`; se espera `False` dentro del grafo.


**Línea 24.** `if __name__ == "__main__":`

Controla que la demostración se ejecute al invocarla como script, no al importarla como biblioteca.


**Línea 25.** `    main()`

Llama a la función principal para ejecutar la carga y las tres consultas.


### 7.3. Archivo `test_red_semantica.py`


**Línea 1.** `"""Pruebas del motor didactico."""`

Documenta que el archivo contiene pruebas automatizadas del motor didáctico.


**Línea 3.** `import unittest`

Importa el marco de pruebas estándar `unittest`.


**Línea 5.** `from red_semantica import RedSemantica, interpretar`

Importa la clase y el parser que se someterán a pruebas.


**Línea 8.** `class PruebasRedSemantica(unittest.TestCase):`

Define un conjunto de casos de prueba, heredando de `unittest.TestCase`.


**Línea 9.** `    def setUp(self) -> None:`

Define la preparación que se ejecutará antes de cada prueba.


**Línea 10.** `        self.red = RedSemantica()`

Crea un grafo nuevo para que las pruebas no dependan unas de otras.


**Línea 11.** `        self.red.agregar("perro", "es_un", "mamifero")`

Agrega un primer hecho jerárquico al escenario de prueba.


**Línea 12.** `        self.red.agregar("mamifero", "es_un", "animal")`

Agrega un segundo hecho para que exista una cadena de dos enlaces.


**Línea 13.** `        self.red.agregar("animal", "necesita", "agua")`

Agrega una propiedad al nodo general `animal`.


**Línea 15.** `    def test_transitividad(self) -> None:`

Define la prueba de transitividad de `es_un`.


**Línea 16.** `        self.assertTrue(self.red.es_un("perro", "animal"))`

Comprueba que el motor deduce correctamente `perro es_un animal`.


**Línea 18.** `    def test_herencia(self) -> None:`

Define la prueba de herencia de propiedades.


**Línea 19.** `        self.assertEqual(self.red.necesidades("perro"), ["agua"])`

Comprueba que `perro` hereda la necesidad `agua` de `animal`.


**Línea 21.** `    def test_sin_relacion_no_infiere(self) -> None:`

Define un caso negativo: no hay camino explícito o transitivo hacia `ave`.


**Línea 22.** `        self.assertFalse(self.red.es_un("perro", "ave"))`

Comprueba que la consulta regresa `False` para esa categoría desconocida en la red.


**Línea 24.** `    def test_interpretacion_linguistica(self) -> None:`

Define una prueba para la conversión de frases a triples.


**Línea 25.** `        self.assertEqual(`

Abre una aserción que compara resultado real con triple esperado.


**Línea 26.** `            interpretar("Un perro es un mamífero."),`

Entrega una oración con tilde al analizador.


**Línea 27.** `            ("perro", "es_un", "mamifero"),`

Indica el triple normalizado esperado; observe que `mamífero` se convierte en `mamifero`.


**Línea 28.** `        )`

Cierra la aserción con varios argumentos.


**Línea 30.** `    def test_oracion_no_admitida(self) -> None:`

Define un caso de entrada fuera de la gramática admitida.


**Línea 31.** `        with self.assertRaises(ValueError):`

Declara que debe lanzarse un `ValueError` y no inventarse una relación.


**Línea 32.** `            interpretar("Los perros corren muy rápido.")`

Ejecuta la oración no admitida dentro del contexto que espera la excepción.


**Línea 34.** `    def test_ciclos_no_bloquean(self) -> None:`

Define una prueba de robustez ante ciclos en el grafo.


**Línea 35.** `        self.red.agregar("animal", "es_un", "perro")`

Introduce un enlace que devuelve de `animal` a `perro`, formando un ciclo conceptual incorrecto pero útil como prueba.


**Línea 36.** `        self.assertFalse(self.red.es_un("perro", "ave"))`

Comprueba que la consulta inexistente termina sin colgarse.


**Línea 37.** `        self.assertEqual(self.red.necesidades("perro"), ["agua"])`

Comprueba que la búsqueda de necesidades también termina y devuelve un resultado sin duplicados.


**Línea 40.** `if __name__ == "__main__":`

Evita ejecutar las pruebas por accidente al importar el archivo como módulo.


**Línea 41.** `    unittest.main()`

Inicia el ejecutor de pruebas si este archivo se lanzó directamente.


---

## 8. Ejecución paso a paso

En la terminal, entra a la carpeta del ejercicio. Los comandos se pueden ejecutar en Windows, macOS o Linux si `python` apunta a Python 3.10+.

```bash
python main.py
```

**Salida observada al ejecutar el ejemplo probado:**

```text
Hecho: (perro, es_un, mamifero)
Hecho: (mamifero, es_un, animal)
Hecho: (animal, necesita, agua)
Hecho: (gato, es_un, mamifero)
¿Perro es un animal?: True
Necesidades de perro: ['agua']
¿Perro es un ave?: False
```

**Cómo interpretar la salida:** las primeras cuatro líneas son hechos **expresamente registrados**; la pregunta sobre `animal` y la necesidad `agua` constituyen resultados **inferidos a través del grafo**. La respuesta `False` significa que el camino no puede probarse con este conjunto de hechos.

Para ejecutar pruebas automatizadas:

```bash
python -m unittest -v
```

**Verificación efectuada al preparar esta guía:** se ejecutaron seis pruebas con resultado `OK`, cubriendo transitividad, herencia, caso negativo, interpretación de una oración, rechazo de oración libre y protección ante ciclos. Esto no sustituye ejecutar las pruebas en el entorno particular de cada estudiante.

---

## 9. Pruebas que deben hacer los estudiantes

| Prueba | Acción | Resultado esperado | Concepto evaluado |
|---|---|---|---|
| 1. Jerarquía | Preguntar `es_un("perro", "animal")` | `True` | transitividad de `es_un` |
| 2. Propiedad heredada | Preguntar `necesidades("perro")` | `['agua']` | propagación configurada de propiedades |
| 3. Sin evidencia | Preguntar `es_un("perro", "ave")` | `False` | límites del conocimiento |
| 4. Acento | Interpretar «Un perro es un mamífero» | `(perro, es_un, mamifero)` | normalización lingüística |
| 5. Fuera de patrón | Interpretar «Los perros corren muy rápido» | `ValueError` | límites del analizador |
| 6. Ciclo | Añadir `animal es_un perro` | consultas terminan | control de nodos visitados |

**Interpretación responsable:** el ejemplo de herencia es una regla pedagógica configurada; en una ontología real deben revisarse excepciones y el significado exacto de las relaciones.

---

## 10. Errores frecuentes y cómo diagnosticarlos

| Problema | Causa probable | Acción de corrección |
|---|---|---|
| `ModuleNotFoundError: red_semantica` | Archivos en carpetas distintas o ejecución desde ruta diferente | Asegurar que `main.py` y `red_semantica.py` están en la misma carpeta |
| `ValueError` al introducir frase | La oración no coincide con alguno de los dos patrones | Verificar artículos, singular y verbos `es` o `necesita`; ampliar expresiones solo si el ejercicio lo exige |
| `False` inesperado en `es_un` | Falta una arista o se escribió una categoría diferente | Imprimir triples y revisar nombres normalizados |
| Error de versión en anotaciones de tipos | Python demasiado antiguo | Usar Python 3.10+ o adaptar tipos |
| Salidas repetidas | Se agregó dos veces el mismo hecho desde una implementación modificada | Verificar prevención de duplicados en `agregar()` |
| Herencia incorrecta | Se asumió una regla de dominio que no aplica | Limitar o redefinir qué relaciones pueden heredarse |

---

## 11. Adaptación al proyecto final

**No se espera copiar la ontología de animales.** El estudiante puede modelar un dominio real pertinente a su proyecto: por ejemplo, `sensor es_un dispositivo`, `dispositivo requiere energia` o `incidente es_un evento`. Antes de implementar, debe justificar el significado de cada predicado y verificar si la transitividad o herencia es válida en ese dominio.

**Trabajo sugerido en clase (sin carácter de evaluación oficial adicional):** elegir 4 a 8 conceptos de un proyecto propio, representar al menos cinco triples, construir un diagrama de nodos y relaciones, y escribir dos consultas que requieran recorrer más de una arista. Agregar una frase que el analizador rechace y explicar por qué.

El estudiante debe entregar como evidencia: `red_semantica.py`, `main.py`, `test_red_semantica.py`, la salida de consola o una captura de ella, y un breve informe que distinga hechos explícitos de inferencias. El nombre del commit puede ser `semana14-redes-semanticas`; es solo una sugerencia, no una fecha o regla institucional.

---

## 12. Preguntas para impartir y sustentar la clase

**1. ¿Qué representa un nodo en una red semántica?** Un concepto o entidad del dominio modelado.

**2. ¿Qué representa una arista etiquetada?** Una relación definida entre dos conceptos, cuyo significado debe estar especificado.

**3. ¿Qué es un triple sujeto-relación-objeto?** Una representación estructurada del hecho «un concepto se relaciona con otro mediante un predicado».

**4. ¿Por qué puede deducirse que `perro es_un animal`?** Porque el ejemplo define transitividad para `es_un` y existe la ruta `perro → mamifero → animal`.

**5. ¿Por qué no todas las relaciones se pueden heredar?** Porque algunas describen hechos particulares, excepciones o contextos que no aplican universalmente a subcategorías.

**6. ¿Qué diferencia hay entre almacenar y deducir conocimiento?** Almacenar escribe explícitamente un triple; deducir calcula una conclusión aplicando reglas sobre los hechos existentes.

**7. ¿El parser comprende cualquier oración en español?** No. Solo reconoce dos patrones; fuera de ellos lanza un error controlado.

**8. ¿Qué evita que una jerarquía cíclica cuelgue el programa?** El conjunto `visitados`, que impide procesar indefinidamente un mismo nodo.

**9. ¿Qué significa `False` cuando no hay una ruta?** Que el resultado no está respaldado por esta red y por la regla definida; no prueba un hecho universal negativo.

**10. ¿Qué relación existe entre lingüística y redes semánticas?** Una oración puede servir como entrada para identificar elementos de significado y convertirlos en relaciones estructuradas, aunque un sistema completo requiere un análisis lingüístico mucho más amplio.

---

## 13. Guion docente sugerido

**Inicio:** muestre una oración y pregunte cómo la entendería una persona y cómo podría representarla un programa.

**Demostración visual:** dibuje tres nodos y dos aristas `es_un`. Pida que el grupo proponga una pregunta sobre el grafo.

**Laboratorio:** escriba junto con los estudiantes `normalizar()`, `interpretar()`, el método `agregar()` y las dos consultas.

**Validación:** compare hechos explícitos con inferencias y ejecute `unittest`.

**Discusión:** incorpore un enlace conceptual erróneo y explique por qué el programa puede terminar pero la información seguir siendo incorrecta.

**Cierre:** cada estudiante explica un caso de uso y una limitación del modelo.

> **Frase para recordar:** «La lingüística ayuda a extraer relaciones de las oraciones; la red semántica representa esas relaciones; la inferencia recorre el conocimiento representado bajo reglas explícitas».

---

## 14. Referencias y delimitación

- **Sílabo de Inteligencia Artificial, página 3:** texto oficial para la Semana 14: «Ingeniería del conocimiento – Representaciones del conocimiento y lingüística con redes semánticas».
- **Sílabo, página 2:** resultados de aprendizaje RAC1 y RAC2.
- **PPTX y Markdown de JSP adjuntos:** usados únicamente para reproducir la organización, diseño y profundidad de explicación, no el tema.
- **Python 3 y el microdominio de animales:** propuesta técnica de laboratorio diseñada para esta clase, no prescrita en el sílabo.

No se atribuyen al sílabo fechas de entrega, puntuaciones particulares de esta práctica o tecnologías que no aparezcan allí.
