# Explicación del código — Semana 15: Ingeniería del conocimiento

## Organización de bases de conocimiento en la empresa, dominios, aplicaciones, recursos humanos y herramientas de desarrollo

**Asignatura:** Inteligencia Artificial · Ingeniería de Sistemas · Décimo semestre.  
**Fuente oficial:** sílabo `IS 10 2040 INTELIGENCIA ARTIFICIAL (6).pdf`, página **3 de 4**, fila **Semana 15**.  
**Resultados de aprendizaje de la asignatura:** RAC1 (construcción de simulaciones con técnicas de IA) y RAC2 (diseño de herramientas basadas en IA), página 2 del sílabo.  
**Material de diseño y estilo pedagógico:** PPTX y `.md` de JSP de la Semana 10 proporcionados como **referencias de forma**, no como contenido de IA.

> **Distinción obligatoria:** El sílabo exige estudiar la organización del conocimiento empresarial, sus dominios, aplicaciones, recursos humanos y herramientas. **No prescribe Python, SQL, SQLite ni un producto específico.** La aplicación descrita a continuación es una **propuesta didáctica de laboratorio** para hacer tangible el tema. **No se presenta como un motor de IA ni como una solución empresarial lista para producción.**

## Objetivo de la clase

Diseñar y demostrar un **repositorio básico de conocimiento organizacional** que clasifique artículos por dominio, vincule aplicaciones y herramientas, asigne responsables expertos, conserve la fuente de información y permita publicar solamente contenido validado.

Al terminar, el estudiante podrá: (1) diferenciar datos, información y conocimiento; (2) reconocer el papel de los dominios, aplicaciones, personas y herramientas; (3) modelar relaciones entre componentes; (4) ejecutar un ejemplo verificable; (5) justificar la calidad y la gobernanza del conocimiento almacenado.

## 1. ¿Qué es una base de conocimiento empresarial?

Es un conjunto **estructurado de conocimientos reutilizables**, acompañado de contexto para recuperarlos, verificarlos y mantenerlos. Un artículo sin responsable, fuente, dominio o fecha puede ser difícil de encontrar y poco confiable. Organizar conocimiento significa saber **qué se sabe, para qué sirve, quién lo mantiene, dónde se aplica y cómo se consulta**.

| Elemento | ¿Qué contiene? | Ejemplo de aula |
|---|---|---|
| Dominio | Área o campo al que pertenece el conocimiento | Seguridad, Soporte TI |
| Aplicación | Sistema o proceso donde se utiliza | Portal interno, Mesa de ayuda |
| Recurso humano | Experto que mantiene o revisa el conocimiento | Analista de seguridad |
| Herramienta | Medio para capturar, consultar o gestionar conocimiento | Wiki, gestor de tickets |
| Artículo | Contenido útil, evidencia y estado de revisión | Solicitar restablecimiento de acceso |

**No confundir:** La *base de datos* guarda registros y relaciones; la *base de conocimiento* es el conjunto organizado de contenido y reglas de gestión. Una base de datos relacional puede ser el medio de almacenamiento de una base de conocimiento, pero no sustituye la validación, la contextualización ni la gestión de su vigencia.

## 2. Ciclo de vida del conocimiento

```text
Necesidad de la empresa
      ↓
Captura de una experiencia o documento
      ↓
Clasificación por dominio y aplicación
      ↓
Asignación de un experto y una fuente
      ↓
Revisión (BORRADOR → VALIDADO)
      ↓
Consulta por personas o aplicaciones
      ↓
Actualización, revisión y eventual retiro
```

La clasificación ayuda a encontrar información relevante; la validación y la revisión periódica ayudan a reducir información incorrecta u obsoleta. En el ejercicio **solo se muestran artículos VALIDADOS** en las consultas normales.

## 3. Arquitectura de la práctica

```text
Estudiante / programa Python
              ↓
       base_conocimiento.py
      ↙         ↓         ↘
   registrar  validar     buscar
              ↓
        SQLite (archivo)
              ↓
  ┌───────────────────────────────────┐
  │ dominio | aplicacion | experto    │
  │ herramienta | articulo           │
  └───────────────────────────────────┘
              ↓
Consulta con articulo + responsable + fuente
```

### Herramientas

- **Python 3** con la biblioteca estándar (`sqlite3`, `pathlib`, `datetime`, `unittest`). Es una **propuesta del laboratorio**.
- **SQLite**, motor relacional integrado en Python; evita configurar un servidor de base de datos para la demostración.
- Editor de texto o IDE y terminal.

No hace falta instalar paquetes de terceros. Si el curso utiliza otro lenguaje, se puede implementar el mismo modelo con otro motor relacional; no se exige trasladar literalmente esta tecnología.

### Estructura de archivos

```text
proyecto_ia_semana15/
├── sql/
│   ├── esquema.sql
│   └── datos.sql
├── src/
│   └── base_conocimiento.py
├── tests/
│   └── test_base_conocimiento.py
└── data/
    └── conocimiento.db       # Se crea al ejecutar
```

## 4. Modelo de relaciones

```text
dominio (1) ─────< (N) aplicacion
    │
    └───────────< (N) articulo (N) >──── (1) experto
                          │
                          ├── (0..1) aplicacion
                          └── (0..1) herramienta
```

La notación `(1) ─< (N)` significa que un dominio puede agrupar varias aplicaciones y artículos. En el ejemplo, **cada artículo** tiene exactamente un dominio y un experto; una aplicación y una herramienta son opcionales. El modelo es intencionalmente sencillo: en un sistema real podrían existir **muchos expertos o dominios por artículo**, permisos, categorías y versiones de contenido.

| Campo de `articulo` | Significado | Regla de clase |
|---|---|---|
| `titulo` | Nombre que identifica el contenido | No vacío; único dentro de cada dominio |
| `contenido` | Descripción o procedimiento documentado | No vacío |
| `dominio_id` | Área responsable del conocimiento | Debe existir en `dominio` |
| `aplicacion_id` | Sistema al que ayuda el artículo | Opcional; debe existir si se informa |
| `experto_id` | Responsable de revisión | Obligatorio; debe existir |
| `herramienta_id` | Herramienta asociada | Opcional |
| `fuente` | Procedencia de la información | Obligatoria |
| `fecha_revision` | Fecha de referencia o revisión | Texto ISO AAAA-MM-DD en el ejemplo |
| `estado` | Condición editorial del artículo | BORRADOR o VALIDADO |

## 5. Preparación de la práctica

1. Crea la estructura de carpetas anterior dentro del repositorio del proyecto de la asignatura.
2. Copia el contenido de los archivos que se muestra a continuación sin alterar sus nombres.
3. Desde la carpeta raíz, ejecuta `python src/base_conocimiento.py`.
4. Verifica que se crea `data/conocimiento.db` y que aparece al menos un artículo validado de Seguridad.
5. Ejecuta `python -m unittest discover -s tests -v`.
6. Revisa las salidas y redacta un análisis de organización, calidad y límites del modelo.

---

# PARTE A — Código completo y explicación detallada

## 6. Archivo `sql/esquema.sql`

Este archivo **define las tablas y las relaciones**; no almacena por sí mismo los artículos. `REFERENCES` conecta claves externas con las tablas de origen y el `CHECK` impide estados fuera del conjunto permitido.

### Archivo completo: `sql/esquema.sql`

```sql
PRAGMA foreign_keys = ON;

CREATE TABLE IF NOT EXISTS dominio (
    id INTEGER PRIMARY KEY,
    nombre TEXT NOT NULL UNIQUE
);

CREATE TABLE IF NOT EXISTS aplicacion (
    id INTEGER PRIMARY KEY,
    nombre TEXT NOT NULL UNIQUE,
    dominio_id INTEGER NOT NULL REFERENCES dominio(id)
);

CREATE TABLE IF NOT EXISTS experto (
    id INTEGER PRIMARY KEY,
    nombre TEXT NOT NULL,
    cargo TEXT NOT NULL
);

CREATE TABLE IF NOT EXISTS herramienta (
    id INTEGER PRIMARY KEY,
    nombre TEXT NOT NULL UNIQUE,
    finalidad TEXT NOT NULL
);

CREATE TABLE IF NOT EXISTS articulo (
    id INTEGER PRIMARY KEY,
    titulo TEXT NOT NULL,
    contenido TEXT NOT NULL,
    dominio_id INTEGER NOT NULL REFERENCES dominio(id),
    aplicacion_id INTEGER REFERENCES aplicacion(id),
    experto_id INTEGER NOT NULL REFERENCES experto(id),
    herramienta_id INTEGER REFERENCES herramienta(id),
    fuente TEXT NOT NULL,
    fecha_revision TEXT NOT NULL,
    estado TEXT NOT NULL DEFAULT 'BORRADOR'
        CHECK (estado IN ('BORRADOR', 'VALIDADO')),
    UNIQUE (titulo, dominio_id)
);

CREATE INDEX IF NOT EXISTS idx_articulo_dominio_estado
ON articulo(dominio_id, estado);
```

### Explicación línea por línea: `esquema.sql`

| Líneas | ¿Qué hace? | ¿Por qué se necesita? |
|---|---|---|
| 1 | Activa las claves foráneas en la conexión. | Impide referencias a dominios o expertos inexistentes. En Python se reitera en cada conexión. |
| 3–6 | Crea `dominio`, con identificador y nombre único. | Define la clasificación principal. |
| 8–12 | Crea `aplicacion`, asociada obligatoriamente a un dominio. | Ubica el sistema donde se utiliza el conocimiento. |
| 14–18 | Crea `experto` con nombre y cargo. | Permite atribuir la responsabilidad del contenido. |
| 20–24 | Crea `herramienta` con nombre y finalidad. | Registra los medios tecnológicos usados. |
| 26–41 | Crea `articulo`, sus campos y referencias. | Vincula contenido, contexto, responsable, fuente y estado. |
| `estado` + `CHECK` | Restringe los estados a `BORRADOR` y `VALIDADO`. | Permite un flujo mínimo de publicación. |
| `UNIQUE(titulo, dominio_id)` | Impide repetir el mismo título en un dominio. | Evita duplicidad literal; **no** detecta duplicados semánticos. |
| Últimas dos líneas | Crea índice para dominio + estado. | Optimiza el patrón de búsqueda de artículos validados. |

Las líneas `id INTEGER PRIMARY KEY` identifican registros. Las líneas `NOT NULL` exigen datos. Las líneas `REFERENCES` conectan tablas. Los campos opcionales **no** llevan `NOT NULL`: es posible documentar un conocimiento que aplique a un dominio completo y no a una aplicación específica.

## 7. Archivo `sql/datos.sql`

Este archivo introduce datos **ficticios** para que el ejercicio produzca un resultado verificable. Los nombres no representan personas o sistemas reales de ninguna organización.

### Archivo completo: `sql/datos.sql`

```sql
INSERT OR IGNORE INTO dominio (id, nombre) VALUES
    (1, 'Seguridad'), (2, 'Soporte TI');

INSERT OR IGNORE INTO aplicacion (id, nombre, dominio_id) VALUES
    (1, 'Portal interno', 1), (2, 'Mesa de ayuda', 2);

INSERT OR IGNORE INTO experto (id, nombre, cargo) VALUES
    (1, 'Laura Gomez', 'Analista de seguridad'),
    (2, 'Diego Rojas', 'Coordinador de soporte');

INSERT OR IGNORE INTO herramienta (id, nombre, finalidad) VALUES
    (1, 'Wiki corporativa', 'Documentar conocimiento'),
    (2, 'Gestor de tickets', 'Registrar solicitudes');

INSERT OR IGNORE INTO articulo
    (id, titulo, contenido, dominio_id, aplicacion_id, experto_id,
     herramienta_id, fuente, fecha_revision, estado)
VALUES
    (1, 'Solicitar restablecimiento de acceso',
     'Contactar al canal autorizado de soporte y verificar identidad.',
     1, 1, 1, 1, 'Politica interna de acceso', '2026-10-15', 'VALIDADO'),
    (2, 'Borrador de FAQ de soporte',
     'Texto pendiente de revision por el experto asignado.',
     2, 2, 2, 2, 'Borrador de mesa de ayuda', '2026-10-20', 'BORRADOR');
```

### Explicación línea por línea: `datos.sql`

| Bloque | Lectura didáctica |
|---|---|
| `INSERT OR IGNORE INTO dominio` | Si la fila no existe, registra Seguridad y Soporte TI. Evita errores al ejecutar dos veces los datos de ejemplo. |
| `INSERT OR IGNORE INTO aplicacion` | Registra Portal interno vinculado a Seguridad y Mesa de ayuda vinculado a Soporte TI. |
| `INSERT OR IGNORE INTO experto` | Crea dos responsables ficticios con sus cargos, como representantes del recurso humano. |
| `INSERT OR IGNORE INTO herramienta` | Distingue una herramienta para documentación y otra para solicitudes. |
| `INSERT OR IGNORE INTO articulo` | Crea un artículo publicado y un borrador para comparar visibilidad. |
| `1, 'Solicitar restablecimiento de acceso'` | El artículo 1 pertenece al dominio 1, referencia la aplicación 1, la persona 1 y la herramienta 1; su estado es `VALIDADO`. |
| `2, 'Borrador de FAQ de soporte'` | El artículo 2 pertenece a Soporte TI y conserva estado `BORRADOR`. No debe verse en la búsqueda pública. |

**Advertencia:** `INSERT OR IGNORE` solo sirve aquí para facilitar la repetición del ejercicio. No es una estrategia completa de sincronización o migración de información empresarial.

## 8. Archivo `src/base_conocimiento.py`

Este archivo concentra **acceso a SQLite y reglas de publicación**. El programa no razona semánticamente: aplica relaciones SQL y reglas explícitas de negocio.

### Archivo completo: `src/base_conocimiento.py`

```python
"""Repositorio de conocimiento empresarial: ejercicio pedagogico Semana 15."""
from datetime import date
from contextlib import contextmanager
from pathlib import Path
import sqlite3

RAIZ = Path(__file__).resolve().parent.parent
RUTA_DB = RAIZ / "data" / "conocimiento.db"


@contextmanager
def conectar(ruta=RUTA_DB):
    ruta = Path(ruta)
    ruta.parent.mkdir(parents=True, exist_ok=True)
    conexion = sqlite3.connect(ruta)
    conexion.row_factory = sqlite3.Row
    conexion.execute("PRAGMA foreign_keys = ON")
    try:
        yield conexion
        conexion.commit()
    except Exception:
        conexion.rollback()
        raise
    finally:
        conexion.close()


def inicializar(ruta=RUTA_DB):
    with conectar(ruta) as conexion:
        conexion.executescript((RAIZ / "sql" / "esquema.sql").read_text(encoding="utf-8"))
        conexion.executescript((RAIZ / "sql" / "datos.sql").read_text(encoding="utf-8"))


def buscar_articulos(dominio, ruta=RUTA_DB):
    consulta = """
        SELECT a.id, a.titulo, a.contenido, d.nombre AS dominio,
               p.nombre AS responsable, ap.nombre AS aplicacion,
               h.nombre AS herramienta, a.fuente, a.fecha_revision
        FROM articulo a
        JOIN dominio d ON d.id = a.dominio_id
        JOIN experto p ON p.id = a.experto_id
        LEFT JOIN aplicacion ap ON ap.id = a.aplicacion_id
        LEFT JOIN herramienta h ON h.id = a.herramienta_id
        WHERE d.nombre = ? AND a.estado = 'VALIDADO'
        ORDER BY a.titulo
    """
    with conectar(ruta) as conexion:
        filas = conexion.execute(consulta, (dominio,)).fetchall()
        return [dict(fila) for fila in filas]


def registrar_articulo(titulo, contenido, dominio_id, experto_id, fuente,
                       aplicacion_id=None, herramienta_id=None, ruta=RUTA_DB):
    if not titulo.strip() or not contenido.strip() or not fuente.strip():
        raise ValueError("Titulo, contenido y fuente son obligatorios")
    with conectar(ruta) as conexion:
        cursor = conexion.execute(
            """INSERT INTO articulo
               (titulo, contenido, dominio_id, aplicacion_id, experto_id,
                herramienta_id, fuente, fecha_revision, estado)
               VALUES (?, ?, ?, ?, ?, ?, ?, ?, 'BORRADOR')""",
            (titulo, contenido, dominio_id, aplicacion_id, experto_id,
             herramienta_id, fuente, date.today().isoformat()),
        )
        return cursor.lastrowid


def validar_articulo(articulo_id, ruta=RUTA_DB):
    with conectar(ruta) as conexion:
        cursor = conexion.execute(
            "UPDATE articulo SET estado = 'VALIDADO' WHERE id = ?",
            (articulo_id,),
        )
        if cursor.rowcount == 0:
            raise ValueError("Articulo no encontrado")


if __name__ == "__main__":
    inicializar()
    print("Articulos validados del dominio Seguridad:")
    for articulo in buscar_articulos("Seguridad"):
        print("-", articulo["titulo"], "| responsable:", articulo["responsable"])
```

### Explicación línea por línea de `base_conocimiento.py`

Se omiten exclusivamente las líneas vacías; cada instrucción con contenido tiene una explicación. Las líneas que solo cierran paréntesis pertenecen a la llamada indicada arriba.

| Línea | Código | Explicación |
|---:|---|---|
| 1 | `"""Repositorio de conocimiento empresarial: ejercicio pedagogico Semana 15."""` | Docstring: anuncia el objetivo didáctico del módulo. |
| 2 | `from datetime import date` | Importa la fecha del sistema para registrar la fecha del artículo. |
| 3 | `from contextlib import contextmanager` | Importa el decorador para implementar un gestor de contexto seguro. |
| 4 | `from pathlib import Path` | Importa una clase que permite construir rutas portables. |
| 5 | `import sqlite3` | Carga el controlador SQLite integrado en Python. |
| 7 | `RAIZ = Path(__file__).resolve().parent.parent` | Calcula la raíz del proyecto desde la ubicación del archivo Python. |
| 8 | `RUTA_DB = RAIZ / "data" / "conocimiento.db"` | Construye la ubicación por defecto del archivo de base de datos. |
| 11 | `@contextmanager` | Convierte la función en un gestor de contexto que cierra la conexión al terminar. |
| 12 | `def conectar(ruta=RUTA_DB):` | Declara la función que abre una conexión; recibe ruta alternativa para pruebas. |
| 13 | `    ruta = Path(ruta)` | Asegura que el argumento se trate como ruta de archivo. |
| 14 | `    ruta.parent.mkdir(parents=True, exist_ok=True)` | Crea la carpeta contenedora de la base si no existe. |
| 15 | `    conexion = sqlite3.connect(ruta)` | Abre o crea el archivo SQLite. |
| 16 | `    conexion.row_factory = sqlite3.Row` | Permite recuperar las filas utilizando nombres de columna. |
| 17 | `    conexion.execute("PRAGMA foreign_keys = ON")` | Activa la integridad referencial para esta conexión. |
| 18 | `    try:` | Inicia el control de errores de la transacción. |
| 19 | `        yield conexion` | Entrega la conexión temporalmente al bloque `with` que la solicitó. |
| 20 | `        conexion.commit()` | Confirma los cambios efectuados sin errores. |
| 21 | `    except Exception:` | Captura fallos para garantizar rollback y relanzar la excepción. |
| 22 | `        conexion.rollback()` | Deshace cambios pendientes si ocurrió un error. |
| 23 | `        raise` | Propaga la excepción al código que llamó la función. |
| 24 | `    finally:` | Ejecuta limpieza tanto en éxito como en error. |
| 25 | `        conexion.close()` | Cierra la conexión SQLite y libera el archivo. |
| 28 | `def inicializar(ruta=RUTA_DB):` | Define la preparación del esquema y datos iniciales. |
| 29 | `    with conectar(ruta) as conexion:` | Inicia el contexto de conexión administrado, con cierre garantizado al terminar. |
| 30 | `        conexion.executescript((RAIZ / "sql" / "esquema.sql").read_text(encoding="utf-8"))` | Lee y ejecuta las definiciones de tablas. |
| 31 | `        conexion.executescript((RAIZ / "sql" / "datos.sql").read_text(encoding="utf-8"))` | Lee y ejecuta la carga inicial reproducible. |
| 34 | `def buscar_articulos(dominio, ruta=RUTA_DB):` | Recibe el nombre del dominio para recuperar conocimiento publicado. |
| 35 | `    consulta = """` | Inicia la cadena SQL multilínea. |
| 36 | `        SELECT a.id, a.titulo, a.contenido, d.nombre AS dominio,` | Selecciona la información principal del artículo y del dominio. |
| 37 | `               p.nombre AS responsable, ap.nombre AS aplicacion,` | Incluye experto y aplicación con alias legibles. |
| 38 | `               h.nombre AS herramienta, a.fuente, a.fecha_revision` | Incluye herramienta, fuente y fecha de revisión. |
| 39 | `        FROM articulo a` | Define la tabla base de la consulta. |
| 40 | `        JOIN dominio d ON d.id = a.dominio_id` | Relaciona el artículo con su dominio obligatorio. |
| 41 | `        JOIN experto p ON p.id = a.experto_id` | Relaciona el artículo con su experto responsable. |
| 42 | `        LEFT JOIN aplicacion ap ON ap.id = a.aplicacion_id` | Añade la aplicación si existe; no elimina el artículo cuando es nula. |
| 43 | `        LEFT JOIN herramienta h ON h.id = a.herramienta_id` | Añade la herramienta solo cuando está informada. |
| 44 | `        WHERE d.nombre = ? AND a.estado = 'VALIDADO'` | Filtra por dominio y solo permite mostrar contenido validado; `?` evita concatenar entrada al SQL. |
| 45 | `        ORDER BY a.titulo` | Ordena los artículos por título. |
| 46 | `    """` | Finaliza una cadena SQL multilínea. |
| 47 | `    with conectar(ruta) as conexion:` | Inicia el contexto de conexión administrado, con cierre garantizado al terminar. |
| 48 | `        filas = conexion.execute(consulta, (dominio,)).fetchall()` | Ejecuta consulta parametrizada y trae todas las filas coincidentes. |
| 49 | `        return [dict(fila) for fila in filas]` | Convierte las filas SQLite a diccionarios fáciles de mostrar. |
| 52 | `def registrar_articulo(titulo, contenido, dominio_id, experto_id, fuente,` | Declara la función para crear conocimiento pendiente de revisión. |
| 53 | `                       aplicacion_id=None, herramienta_id=None, ruta=RUTA_DB):` | Hace opcionales aplicación y herramienta, e inyectable la ruta de base. |
| 54 | `    if not titulo.strip() or not contenido.strip() or not fuente.strip():` | Rechaza valores vacíos o de solo espacios en tres campos esenciales. |
| 55 | `        raise ValueError("Titulo, contenido y fuente son obligatorios")` | Devuelve un error entendible cuando faltan datos. |
| 56 | `    with conectar(ruta) as conexion:` | Inicia el contexto de conexión administrado, con cierre garantizado al terminar. |
| 57 | `        cursor = conexion.execute(` | Ejecuta una instrucción parametrizada dentro de la transacción. |
| 58 | `            """INSERT INTO articulo` | Comienza la instrucción SQL de inserción. |
| 59 | `               (titulo, contenido, dominio_id, aplicacion_id, experto_id,` | Envía valores Python en el orden de las columnas SQL. |
| 60 | `                herramienta_id, fuente, fecha_revision, estado)` | Completa columnas: herramienta, fuente, fecha y estado. |
| 61 | `               VALUES (?, ?, ?, ?, ?, ?, ?, ?, 'BORRADOR')""",` | Reserva parámetros para los valores y fuerza estado BORRADOR al crear. |
| 62 | `            (titulo, contenido, dominio_id, aplicacion_id, experto_id,` | Envía valores Python en el orden de las columnas SQL. |
| 63 | `             herramienta_id, fuente, date.today().isoformat()),` | Completa parámetros y agrega la fecha ISO del sistema. |
| 64 | `        )` | Cierra la llamada o el bloque argumental correspondiente. |
| 65 | `        return cursor.lastrowid` | Devuelve el id generado para identificar el nuevo artículo. |
| 68 | `def validar_articulo(articulo_id, ruta=RUTA_DB):` | Define la transición editorial de un artículo a VALIDADO. |
| 69 | `    with conectar(ruta) as conexion:` | Inicia el contexto de conexión administrado, con cierre garantizado al terminar. |
| 70 | `        cursor = conexion.execute(` | Ejecuta una instrucción parametrizada dentro de la transacción. |
| 71 | `            "UPDATE articulo SET estado = 'VALIDADO' WHERE id = ?",` | Actualiza el estado solo de un id específico. |
| 72 | `            (articulo_id,),` | Pasa un parámetro como tupla de un solo elemento. |
| 73 | `        )` | Cierra la llamada o el bloque argumental correspondiente. |
| 74 | `        if cursor.rowcount == 0:` | Comprueba si el id suministrado no modificó ninguna fila. |
| 75 | `            raise ValueError("Articulo no encontrado")` | Lanza un error explícito si la publicación no es posible. |
| 78 | `if __name__ == "__main__":` | Ejecuta la demostración solo si se abre el archivo como programa principal. |
| 79 | `    inicializar()` | Crea las tablas y carga los datos de ejemplo. |
| 80 | `    print("Articulos validados del dominio Seguridad:")` | Muestra el título de la consulta de demostración. |
| 81 | `    for articulo in buscar_articulos("Seguridad"):` | Recorre los registros validados de ese dominio. |
| 82 | `        print("-", articulo["titulo"], "\| responsable:", articulo["responsable"])` | Imprime título y experto responsable de cada resultado. |

### Lectura pedagógica de las funciones

- `conectar`: centraliza las configuraciones SQLite, crea una transacción, confirma, revierte y cierra recursos. **Punto crítico:** `PRAGMA foreign_keys = ON` debe activarse **en cada conexión**; colocarlo solo en `esquema.sql` no garantiza que otras conexiones lo utilicen.
- `inicializar`: crea tablas e incorpora datos ficticios. `CREATE TABLE IF NOT EXISTS` evita fallos en una ejecución repetida.
- `buscar_articulos`: relaciona cinco tablas. `JOIN` exige dominio y experto; `LEFT JOIN` conserva filas aunque la aplicación o herramienta no estén definidas. El estado `VALIDADO` es una **regla de publicación**, no una garantía por sí misma de calidad.
- `registrar_articulo`: recibe campos, valida los obligatorios y crea siempre un borrador. La fecha se obtiene del sistema. Una referencia a un experto inexistente provoca un error de integridad.
- `validar_articulo`: representa una aprobación mínima. **Limitación:** aquí no se verifica quién es la persona que aprueba. Para producción habría que gestionar identidad, permisos, auditoría y revisión de contenidos.

### ¿Por qué se usa `?` en SQL?

La consulta usa `WHERE d.nombre = ?` y después `(dominio,)`. SQLite separa los datos enviados del texto SQL. Esto evita errores por comillas y es una defensa básica frente a inyección SQL. **Nunca** se debe concatenar directamente texto de usuario dentro de una cadena SQL.

## 9. Archivo `tests/test_base_conocimiento.py`

La clase de pruebas usa una base **temporal independiente**. Por eso no modifica los datos del archivo real del estudiante.

### Archivo completo: `tests/test_base_conocimiento.py`

```python
"""Pruebas basicas usando una base temporal para no alterar los datos reales."""
from pathlib import Path
from tempfile import TemporaryDirectory
import sys
import sqlite3
import unittest

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "src"))
from base_conocimiento import (  # noqa: E402
    inicializar, buscar_articulos, registrar_articulo, validar_articulo
)


class PruebasConocimiento(unittest.TestCase):
    def setUp(self):
        self.temporal = TemporaryDirectory()
        self.ruta = Path(self.temporal.name) / "prueba.db"
        inicializar(self.ruta)

    def tearDown(self):
        self.temporal.cleanup()

    def test_solo_articulos_validados(self):
        self.assertEqual(len(buscar_articulos("Seguridad", self.ruta)), 1)
        self.assertEqual(len(buscar_articulos("Soporte TI", self.ruta)), 0)

    def test_ciclo_registro_validacion(self):
        articulo_id = registrar_articulo(
            "Guia de acceso", "Solicitar permiso por canal oficial", 1, 1,
            "Manual interno", aplicacion_id=1, herramienta_id=1, ruta=self.ruta
        )
        self.assertEqual(len(buscar_articulos("Seguridad", self.ruta)), 1)
        validar_articulo(articulo_id, self.ruta)
        self.assertEqual(len(buscar_articulos("Seguridad", self.ruta)), 2)

    def test_dato_obligatorio(self):
        with self.assertRaises(ValueError):
            registrar_articulo("", "Contenido", 1, 1, "Fuente", ruta=self.ruta)

    def test_referencia_inexistente(self):
        with self.assertRaises(sqlite3.IntegrityError):
            registrar_articulo("Articulo externo", "Texto", 99, 1, "Fuente", ruta=self.ruta)

    def test_id_no_existente(self):
        with self.assertRaises(ValueError):
            validar_articulo(999, self.ruta)


if __name__ == "__main__":
    unittest.main()
```

### Explicación de las pruebas por bloques y líneas relevantes

| Instrucción | Explicación |
|---|---|
| `TemporaryDirectory()` | Crea un directorio aislado para la prueba y evita alterar los datos de clase. |
| `self.ruta = Path(...) / "prueba.db"` | Define una base nueva para cada prueba. |
| `inicializar(self.ruta)` | Crea la estructura y datos iniciales antes de cada caso. |
| `tearDown()` / `cleanup()` | Elimina el directorio temporal luego de cada prueba. |
| `test_solo_articulos_validados` | Comprueba que el artículo validado aparece y el borrador queda oculto. |
| `test_ciclo_registro_validacion` | Crea un borrador, comprueba que no se publica aún, lo valida y comprueba que aparece. |
| `test_dato_obligatorio` | Verifica que no se puede registrar un artículo sin título. |
| `test_referencia_inexistente` | Verifica que no se acepta un `dominio_id` inexistente. |
| `test_id_no_existente` | Verifica que la validación de un artículo inexistente informa el error. |
| `unittest.main()` | Permite ejecutar las pruebas al abrir el archivo directamente. |

Las afirmaciones (`assertEqual`, `assertRaises`) constituyen evidencia reproducible. Un programa que muestra una salida correcta una sola vez no demuestra por sí solo que maneje errores.

---

# PARTE B — Ejecución y resultados

## 10. Comandos para ejecutar

Abre una terminal en la raíz del proyecto. Si el ejecutable de tu sistema es `python3`, sustitúyelo por ese nombre.

```bash
python --version
python src/base_conocimiento.py
python -m unittest discover -s tests -v
```

Resultado esperado en la consola al abrir el programa:

```text
Articulos validados del dominio Seguridad:
- Solicitar restablecimiento de acceso | responsable: Laura Gomez
```

La prueba debe indicar cinco casos correctos, con nombres de prueba y estado `ok`:

```text
test_ciclo_registro_validacion ... ok
test_dato_obligatorio ... ok
test_id_no_existente ... ok
test_referencia_inexistente ... ok
test_solo_articulos_validados ... ok

Ran 5 tests

OK
```

El **tiempo de ejecución** y el orden exacto de aparición pueden variar. Estos resultados sí se comprobaron en el entorno de preparación del material utilizando Python, SQLite y pruebas aisladas. **No se ha desplegado una aplicación empresarial ni un servicio remoto.**

### ¿Qué contiene la base de datos luego de ejecutar?

`data/conocimiento.db` almacena las cinco tablas y los datos ficticios. El artículo de Seguridad está validado; el de Soporte TI permanece en borrador. Se puede abrir el archivo con una herramienta SQLite o realizar consultas mediante Python.

### Consulta manual opcional

```bash
python -c "import sqlite3; c=sqlite3.connect('data/conocimiento.db'); print(c.execute('SELECT titulo, estado FROM articulo').fetchall()); c.close()"
```

Debería mostrar dos títulos y sus estados `VALIDADO` y `BORRADOR`.

## 11. Cómo interpretar el resultado

El resultado **no** demuestra que el sistema comprenda semánticamente el texto. Demuestra que es posible **organizar** conocimiento con metadatos y relaciones, asignar responsable humano, asociar herramientas y permitir la recuperación de contenido aprobado. Ésta es la conexión directa con el tema de la Semana 15 del sílabo.

Preguntas para el análisis del estudiante:

1. ¿Por qué un artículo necesita dominio y responsable?
2. ¿Qué diferencia hay entre el dominio `Seguridad` y la aplicación `Portal interno`?
3. ¿Por qué una herramienta no es equivalente al contenido que almacena?
4. ¿Qué riesgo aparece si un borrador puede ser consultado como si fuera una instrucción aprobada?
5. ¿Qué cambia si el artículo aplica a varias aplicaciones o tiene varios expertos?

## 12. Errores comunes y corrección

| Error observado | Causa probable | Acción para resolver |
|---|---|---|
| `ModuleNotFoundError` al ejecutar tests | Se intenta importar el módulo desde otra carpeta | Ejecutar `python -m unittest discover -s tests -v` desde la raíz indicada |
| `no such table: articulo` | Se realizó la búsqueda sin ejecutar `inicializar()` | Inicializar la base antes de buscar |
| `FOREIGN KEY constraint failed` | Se está registrando dominio/experto inexistente | Consultar los ids válidos y revisar relaciones |
| `UNIQUE constraint failed` | Se repite el mismo título en un dominio | Ajustar el título o modelar una nueva versión |
| La consulta devuelve lista vacía | Dominio escrito distinto o artículo en estado BORRADOR | Verificar filtros y aprobación |
| La base aparece en otra carpeta | Se ejecutó código con rutas relativas modificadas | Usar la ruta calculada con `__file__` y revisar la estructura |
| Error al editar SQL | Columnas o tablas no coinciden con el código Python | Mantener consistencia entre SQL, consultas y pruebas |

## 13. Adaptación al proyecto final

**Ejemplo de universidad:** dominios “Admisiones”, “Biblioteca”, “Registro académico”; aplicaciones “Portal estudiante” y “Sistema bibliotecario”; expertos “Coordinación académica” y “Bibliotecario”; herramientas “Wiki interna”; artículos “Proceso de matrícula” y “Reserva de material”.

**Ejemplo de empresa:** dominios “Talento humano”, “Seguridad”, “Operaciones”; aplicaciones “ERP” y “Mesa de ayuda”; responsables por proceso; herramientas documentales y repositorios de código.

Cada estudiante deberá explicar por qué sus categorías son apropiadas. No debe copiar el ejemplo ficticio sin adaptar el contenido al problema de su proyecto.

### Limitaciones y mejoras para un sistema real

- **Autorización:** solo personas con permiso deberían validar artículos o cambiar sus datos.
- **Versionamiento:** un artículo puede tener versiones y un historial de cambios.
- **Revisión periódica:** los conocimientos pueden dejar de estar vigentes; la fecha ayuda, pero no sustituye una política de actualización.
- **Búsqueda semántica:** esta práctica solo filtra por coincidencia exacta del dominio, no razona ni utiliza modelos de lenguaje.
- **Protección de datos:** evitar datos personales innecesarios y controlar contenidos confidenciales.
- **Escalabilidad:** índices, buscador, historial de auditoría y modelos muchos-a-muchos serían mejoras futuras.

Estas propuestas **no son subtemas adicionales atribuidos al sílabo**: son criterios para discutir el alcance de un repositorio empresarial.

## 14. Evidencias y revisión de la práctica

Entregable didáctico sugerido (no es una fecha ni una calificación oficial):

1. `sql/esquema.sql` con las cinco tablas.
2. `sql/datos.sql` con ejemplos ficticios.
3. `src/base_conocimiento.py` ejecutable.
4. `tests/test_base_conocimiento.py` con cinco pruebas.
5. Captura o salida de la consulta y de las pruebas.
6. Comentario breve sobre su adaptación al proyecto acumulativo.

**Realizado:** existen los archivos y se explica el modelo.  
**Funciona:** consulta y pruebas ejecutan correctamente.  
**Coincide:** los datos relacionan dominios, aplicaciones, personas, herramientas y artículos.  
**Sustenta:** el estudiante explica qué hace cada parte y qué limitaciones tiene.

Commit orientativo, si la clase utiliza control de versiones:

```bash
git add sql src tests
git commit -m "Semana 15: base de conocimiento empresarial"
```

## 15. Preguntas para la sustentación, con respuestas esperadas

**1. ¿Qué distingue una base de conocimiento de una base de datos?**  
La primera es un repositorio organizado de saber útil, con contexto y gobernanza; la segunda es una tecnología de almacenamiento que puede sostenerla.

**2. ¿Qué es un dominio de conocimiento?**  
Área temática u organizacional que permite clasificar contenidos y responsabilidades.

**3. ¿Por qué se relaciona un artículo con un experto?**  
Para asignar revisión, aclaraciones, actualización y rendición de cuentas sobre el contenido.

**4. ¿Qué son las aplicaciones en este modelo?**  
Los sistemas o procesos donde se usa o consulta el conocimiento; no equivalen al dominio.

**5. ¿Para qué se registran las herramientas?**  
Para conocer medios de captura, publicación y seguimiento de conocimiento; la herramienta no es el conocimiento mismo.

**6. ¿Por qué la consulta filtra por `VALIDADO`?**  
Para no publicar un borrador pendiente de revisión como si fuese contenido confiable.

**7. ¿Por qué `WHERE d.nombre = ?` es mejor que concatenar texto?**  
Porque usa parámetros y evita confundir datos de entrada con instrucciones SQL.

**8. ¿Qué ocurre si se registra `dominio_id=99` y no existe?**  
SQLite rechaza la operación por integridad referencial cuando está activo `PRAGMA foreign_keys = ON`.

**9. ¿Qué demuestra la prueba de registro y aprobación?**  
Que un artículo nuevo comienza como borrador, no aparece en la consulta validada y se publica solo después de aprobarlo.

**10. ¿Este programa implementa razonamiento de IA?**  
No. Es un ejemplo de organización y gobernanza del conocimiento, posible insumo para sistemas inteligentes posteriores.

## 16. Frase final para recordar

> **El conocimiento empresarial adquiere valor cuando se organiza por dominio, se vincula con las aplicaciones, tiene responsables humanos, utiliza herramientas apropiadas y cuenta con una fuente y un proceso de validación.**

### Fuentes y trazabilidad

- Sílabo `IS 10 2040 INTELIGENCIA ARTIFICIAL (6).pdf`, p. 3: tema oficial de Semana 15. p. 2: RAC1 y RAC2. p. 4: bibliografía general.
- PPTX de JSP de Semana 10 y explicación Markdown de JSP: exclusivamente **referencias visuales y pedagógicas**, no fuentes de los contenidos técnicos de esta Semana 15.
- Python y SQLite: **propuesta pedagógica complementaria**, probada localmente con cinco casos de `unittest`.

