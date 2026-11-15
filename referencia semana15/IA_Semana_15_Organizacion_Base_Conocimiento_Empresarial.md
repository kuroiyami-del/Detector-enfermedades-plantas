**Inteligencia Artificial  |  Semana 15** 

#### **Semana 15** 

# **Ingeniería del conocimiento** 

Organización de bases de conocimiento en la empresa 

**Dominios Aplicaciones** 

**Recursos humanos** 

**Herramientas** 



<!-- Start of picture text -->
a<br><!-- End of picture text -->

Meta: modelar una base de conocimiento con dominios, personas, aplicaciones, herramientas y artículos validados. 

**01** 

Material docente editable · Base de conocimiento · 1 

**Inteligencia Artificial  |  Semana 15** 

## **Ruta de la clase** 

Qué se explica, qué se desarrolla y cómo se comprueba 

> **1** Entender datos, información y conocimiento @ **2** Identificar los dominios y las aplicaciones @ 

> **3** Relacionar expertos y herramientas e 

> **4** Diseñar el modelo y sus metadatos e 

> **5** Crear tablas y consultas SQL con SQLite e 



<!-- Start of picture text -->
1) v © , 9 v<br>Nc<br>— =<br>2 = "Gs<br>eo. ‘ eo. v eo . o<br>:— -~EIR- ©<br>—_<br><!-- End of picture text -->

> **6** Registrar, validar y consultar artículos @ 

Al final: repositorio de ejemplo, consulta visible y cinco pruebas automatizadas. 

**02** 

Material docente editable · Base de conocimiento · 2 

**Inteligencia Artificial  |  Semana 15** 

## **Modelo mental del conocimiento** 

Un artículo útil necesita contexto, responsable y un mecanismo de consulta 

###### **1. Captura** 

Se documenta una experiencia, solución o procedimiento. 

###### **2. Contextualización** 

Se define dominio, aplicación, fuente y experto. 

###### **3. Validación** 

El borrador es revisado antes de publicarse. 



<!-- Start of picture text -->
CONOCIMIENTO<br>DOMINIOS APLICACIONES PERSONAS HERRAMIENTAS<br>Áreas Sistemas Expertos Medios<br><!-- End of picture text -->

###### **4. Recuperación** 

Una consulta muestra conocimiento pertinente. 

Fuente  ·  Responsable  ·  Estado  ·  Fecha de revisión 

**03** 

Material docente editable · Base de conocimiento · 3 

**Inteligencia Artificial  |  Semana 15** 

## **Fundamentos: del dato al conocimiento** 

Estructura, contexto y criterio humano generan valor organizacional 

##### **DATO** 

“Error 403” sin interpretación; es un registro aislado. 

##### **INFORMACIÓN** 

- “El Portal interno respondió 403 por falta de permisos”. 

##### **CONOCIMIENTO** 

- “Validar rol asignado y solicitar permisos por canal autorizado”. 



<!-- Start of picture text -->
Capturar Clasificar Validar Consultar<br>experiencia dominio y app experto + fuente uso seguro<br><!-- End of picture text -->

Regla de clase: un registro sin fuente, responsable o estado puede resultar difícil de confiar y mantener. 

**04** 

Material docente editable · Base de conocimiento · 4 

**Inteligencia Artificial  |  Semana 15** 

## **Subtema 1 · Dominios de conocimiento** 

Un dominio agrupa conocimientos que pertenecen a una misma área 

###### **¿Qué es?** 

Categoría estable que agrupa conceptos, problemas, responsabilidades y artículos del área. 

###### **¿Para qué sirve?** 

Facilita búsquedas, responsables, estándares de clasificación y actualización. 

```
CREATE TABLE dominio (
    id INTEGER PRIMARY KEY,
    nombre TEXT NOT NULL UNIQUE
);
```



<!-- Start of picture text -->
Empresa<br>Conocimiento<br>Seguridad Soporte TI<br>acceso, MFA FAQ, incidentes<br><!-- End of picture text -->

###### **Ejemplo** 

El artículo “Solicitar restablecimiento de acceso” pertenece a Seguridad. 

**05** 

Material docente editable · Base de conocimiento · 5 

**Inteligencia Artificial  |  Semana 15** 

## **Subtema 2 · Aplicaciones y sistemas** 

El dominio indica el tema; la aplicación indica dónde se usa 

###### **Dominio Seguridad** 

Agrupa el conocimiento relacionado con acceso y protección de información. 

###### **Aplicación Portal interno** 

Sistema donde ese conocimiento puede ser necesario para resolver una solicitud. 

```
CREATE TABLE aplicacion (
  id INTEGER PRIMARY KEY,
  nombre TEXT NOT NULL UNIQUE,
  dominio_id INTEGER NOT NULL
       REFERENCES dominio(id)
);
```



<!-- Start of picture text -->
Dominio Aplicación<br>Seguridad Portal interno<br>Dominio Aplicación<br>Soporte TI Mesa de ayuda<br><!-- End of picture text -->

El campo dominio_id enlaza cada aplicación con su dominio correspondiente. 

**06** 

Material docente editable · Base de conocimiento · 6 

**Inteligencia Artificial  |  Semana 15** 

## **Subtema 3 · Recursos humanos** 

Personas expertas sostienen la revisión y vigencia del conocimiento 

###### **Capturador** 

###### **Experto** 

Documenta experiencias o procedimientos. Revisa exactitud y completitud del contenido. 

**Consumidor** Consulta artículos aprobados para resolver tareas. 



<!-- Start of picture text -->
BORRADOR REVISIÓN<br>registrado experto responsable<br>SELECT a.titulo, p.nombre AS responsable<br>FROM articulo a<br>JOIN experto p ON p.id = a.experto_id;<br>producción.<br><!-- End of picture text -->



<!-- Start of picture text -->
VALIDADO<br>publicable<br><!-- End of picture text -->

El ejercicio modela validación editorial; no implementa autenticación ni permisos de producción. 

**07** 

Material docente editable · Base de conocimiento · 7 

**Inteligencia Artificial  |  Semana 15** 

## **Subtema 4 · Herramientas de desarrollo** 

Organizar el conocimiento requiere medios de captura, almacenamiento y consulta 

###### **Gestión del conocimiento** 

Wiki corporativa y gestor de tickets: documentan y conectan experiencias. 

###### **Desarrollo de software** 

Editor, Python y pruebas: construyen la demostración y verifican reglas. 

###### **Persistencia** 

SQLite: guarda tablas y relaciones sin necesidad de un servidor externo. 

**Personal** captura y revisa 

**Herramientas** wiki + tickets 

**Base de datos** SQLite + relaciones 

**Consulta** artículos validados 

Python y SQLite se emplean únicamente como entorno práctico propuesto. 

**08** 

Material docente editable · Base de conocimiento · 8 

**Inteligencia Artificial  |  Semana 15** 

## **Práctica guiada · repositorio empresarial** 

Crear las tablas, cargar datos y probar consulta y publicación 

> **1** Crear las carpetas sql/, src/, tests/ y data/ 

**3** Insertar registros ficticios en sql/datos.sql 

> **5** Buscar artículos validados con SQL JOIN 

> **7** Validar y comprobar su nueva visibilidad 

**2** Definir cinco tablas en sql/esquema.sql 

> **4** Implementar conexión con claves foráneas activas 

> **6** Registrar un artículo como BORRADOR 

> **8** Ejecutar cinco pruebas y documentar resultados 

Archivo principal: src/base_conocimiento.py · Ejecutar desde la raíz del proyecto. 

**09** 

Material docente editable · Base de conocimiento · 9 

**Inteligencia Artificial  |  Semana 15** 

## **Código comentado 1 · modelo SQL** 

Tablas relacionales, responsables y estado de publicación 

###### `CREATE TABLE articulo (` 

```
  id INTEGER PRIMARY KEY,
  titulo TEXT NOT NULL,
  contenido TEXT NOT NULL,
  dominio_id INTEGER NOT NULL
      REFERENCES dominio(id),
  experto_id INTEGER NOT NULL
      REFERENCES experto(id),
  fuente TEXT NOT NULL,
  estado TEXT NOT NULL DEFAULT 'BORRADOR'
      CHECK(estado IN ('BORRADOR', 'VALIDADO'))
);
```

###### **Relaciones** 

dominio_id y experto_id deben apuntar a registros existentes. 

###### **Estado** 

La creación comienza como BORRADOR; la publicación es posterior. 

###### **Fuente** 

Cada artículo tiene trazabilidad de procedencia; no se publica un texto anónimo. 

Fragmento didáctico. El esquema completo incluye aplicación, herramienta, fecha, unicidad e índice. 

**10** 

Material docente editable · Base de conocimiento · 10 

**Inteligencia Artificial  |  Semana 15** 

## **Código comentado 2 · recuperar y validar** 

El programa solo consulta artículos publicados y permite su validación 

```
def buscar_articulos(dominio, ruta=RUTA_DB):
    consulta = '''
      SELECT a.titulo, p.nombre AS responsable
      FROM articulo a
      JOIN dominio d ON d.id = a.dominio_id
      JOIN experto p ON p.id = a.experto_id
      WHERE d.nombre = ?
        AND a.estado = 'VALIDADO'
    '''
    with conectar(ruta) as conexion:
        return conexion.execute(
            consulta, (dominio,)
        ).fetchall()
```

###### **Bloque 1 · Buscar** 

Filtra por dominio para recuperar información relevante. 

###### **Bloque 2 · JOIN** 

Une artículo, dominio y experto para dar contexto. 

###### **Bloque 3 · VALIDADO** 

Un borrador no aparece en la búsqueda habitual. 

###### **Bloque 4 · Parámetro** 

El signo ? evita concatenar directamente la entrada al SQL. 

**11** 

Material docente editable · Base de conocimiento · 11 

**Inteligencia Artificial  |  Semana 15** 

## **Pruebas y resultado esperado** 

Comprobar búsqueda, registro, publicación y manejo de errores 

###### **Caso válido · Seguridad** 

La consulta devuelve un artículo VALIDADO con experto y fuente. 

Base de conocimiento | Panel 

### **Artículos del dominio Seguridad** 

###### **Caso pendiente · Soporte TI** 

La consulta devuelve cero artículos porque el ejemplo tiene BORRADOR. 

###### **Caso límite · Dominio inexistente** 

**Título Estado** Solicitar restablecimiento de acceso **VALIDADO** 

###### **Responsable: Laura Gomez** 

Un dominio_id no registrado produce error de integridad referencial. 

Fuente: Política interna de acceso 

```
python src/base_conocimiento.py
python -m unittest discover -s tests -v
# Comprobación local: 5 pruebas, OK
```

**12** 

Material docente editable · Base de conocimiento · 12 

**Inteligencia Artificial  |  Semana 15** 

## **Errores frecuentes y correcciones** 

Guía para identificar fallos del modelo y la base de datos 

###### **No such table: articulo** 

Inicializar tablas antes de consultar. 

###### **No aparece artículo** 

Comprobar nombre del dominio y estado VALIDADO. 

###### **FOREIGN KEY failed** 

Revisar ids del dominio y del experto. 

###### **Faltan campos** 

Registrar título, contenido y fuente no vacíos. 

###### **UNIQUE constraint** 

Evitar repetir título en un mismo dominio. 

###### **No valida por id** 

Confirmar que el artículo exista antes de aprobar. 



Método de depuración: reproducir el fallo, localizar la tabla o función y volver a ejecutar las pruebas. 

**13** 

Material docente editable · Base de conocimiento · 13 

**Inteligencia Artificial  |  Semana 15** 

## **Entregable y revisión semanal** 

Cómo demostrar que la organización del conocimiento funciona 

###### **Esquema y datos** 

sql/esquema.sql y sql/datos.sql con dominios, aplicaciones, expertos y herramientas. 

###### **Programa** 

src/base_conocimiento.py con inicialización, búsqueda, registro y validación. 

###### **Pruebas** 

tests/test_base_conocimiento.py, consola y explicación de los resultados. 

###### **Coincide** 

###### **Realizado** 

###### **Funciona** 

Archivos y estructura existen. Pruebas pasan y consulta responde. Cubre dominios, apps, personas y herramientas. 

###### **Sustenta** 

Explica relaciones, filtros y límites. 

Adaptación: sustituir Seguridad y Soporte TI por dominios reales del proyecto, sin incorporar datos sensibles. 

```
git add sql src tests
git commit -m "Semana 15: base de conocimiento empresarial"
```

**14** 

Material docente editable · Base de conocimiento · 14 

**Inteligencia Artificial  |  Semana 15** 

## **Cierre de clase** 

La tecnología conserva registros; las personas convierten y mantienen saber útil 

###### **Organización** 

Dominios clasifican; aplicaciones sitúan el uso. 

###### **Responsabilidad** 

Expertos revisan y mantienen el conocimiento. 

###### **Herramientas** 

Capturan, guardan, buscan y entregan los artículos. 



<!-- Start of picture text -->
CONOCIMIENTO<br>DOMINIOS APLICACIONES PERSONAS HERRAMIENTAS<br>Áreas Sistemas Expertos Medios<br><!-- End of picture text -->

Fuente  ·  Responsable  ·  Estado  ·  Fecha de revisión 

Para debatir: ¿cómo comprobarías vigencia, autoría y seguridad si este repositorio se usara en una empresa real? 

**15** 

Material docente editable · Base de conocimiento · 15 

