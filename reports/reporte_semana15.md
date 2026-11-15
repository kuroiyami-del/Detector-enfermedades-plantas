# Semana 15 - Ingenieria del conocimiento: base de conocimiento

**Proyecto:** PlantAI - Deteccion de enfermedades en plantas con Inteligencia Artificial  
**Modulo:** `src/semana15_base_conocimiento.py`  
**Reporte generado:** 2026-11-15  
**Comandos:** `python src/semana15_base_conocimiento.py` | `--reporte` | `--pruebas`  
**Tema:** organizacion de bases de conocimiento: dominios, aplicaciones,
recursos humanos, herramientas y articulos validados.

---

## 1. Descripcion del dominio y problema

El proyecto conoce mucho de fitosanitria, pero ese conocimiento esta
repartido: codigo de la semana 03, reportes de las semanas 13 y 14, salidas
de consola y comentarios. **Un conocimiento sin contexto es dificil de
encontrar, de confiar y de mantener.** Esta semana el problema a resolver es
la organizacion: saber que se sabe, para que sirve, quien lo mantiene, donde
se aplica y como se consulta.

La solucion propuesta es un **repositorio de conocimiento organizacional**
construido sobre SQLite: dominios que clasifican, aplicaciones que ubican el
uso, expertos responsables, herramientas de soporte y articulos que solo se
publican despues de ser validados.

## 2. Conceptos

- **Dominio:** area tematica que agrupa el conocimiento. En PlantAI:
  Diagnostico foliar, Manejo fitosanitario y Calidad de datos.
- **Aplicacion:** sistema o proceso donde se usa ese conocimiento (Pipeline
  PlantAI, Planificador A*, Dataset PlantVillage). El dominio dice *de que
  tema* trata; la aplicacion dice *donde se usa*.
- **Experto (recurso humano):** persona responsable de revisar y mantener el
  contenido. El modelo registra el rol, no la autenticacion.
- **Herramienta:** medio de captura, almacenamiento o consulta (Wiki del
  proyecto, Repositorio Git, Gestor de tickets). La herramienta **no es** el
  conocimiento: es el soporte para gestionarlo.
- **Articulo:** el contenido util, con contexto, responsable, fuente, fecha y
  estado editorial.

**Base de datos != base de conocimiento.** La base de datos guarda registros y
relaciones; la base de conocimiento es el contenido organizado con su
gobernanza (validacion, responsable y vigencia). SQLite es solo el soporte.

## 3. Modelo de relaciones

```text
dominio (1) ----< (N) aplicacion
    |
    +------------< (N) articulo (N) >---- (1) experto
                         |
                         +--- (0..1) aplicacion
                         +--- (0..1) herramienta
```

Cada articulo tiene **exactamente un** dominio y **un** experto responsable;
la aplicacion y la herramienta son opcionales. Es un modelo deliberadamente
sencillo: en un sistema real habria varios expertos por articulo, permisos,
versiones y categorias.

## 4. Esquema y datos

El esquema completo esta en `sql/esquema.sql` (cinco tablas, claves
foraneas, `CHECK` del estado, unicidad de titulo por dominio e indice por
`dominio_id, estado`) y los datos ficticios en `sql/datos.sql`.

| Dominio | Aplicacion | Experto responsable | Herramienta | Articulos |
|---|---|---|---|---|
| Diagnostico foliar | Pipeline PlantAI | Luis Torres (analista de imagenes) | Repositorio Git | 2 validados |
| Manejo fitosanitario | Planificador A* | Ana Rivera (ingeniera agronoma) | Gestor de tickets | 2 validados |
| Calidad de datos | Dataset PlantVillage | Marta Salas (tecnica de calidad) | Wiki del proyecto | 1 borrador |

El articulo de **Calidad de datos** esta en BORRADOR a proposito: existe en el
repositorio pero **no** aparece en la busqueda habitual.

## 5. Escenario ejecutado

```text
======================================================================
ESCENARIO A: ciclo de vida del conocimiento en Manejo fitosanitario
======================================================================

1) Organizacion por dominio (dominio -> aplicacion -> experto -> herramienta):
   - Calidad de datos: 0 validado(s) de 1 articulo(s)
   - Diagnostico foliar: 2 validado(s) de 2 articulo(s)
   - Manejo fitosanitario: 2 validado(s) de 2 articulo(s)

2) Articulos validados del dominio Manejo fitosanitario (consulta inicial):
   - Protocolo de contencion de problemas virales | responsable: Ana Rivera | aplicacion: Planificador A* | fuente: Manual interno de manejo fitosanitario
   - Protocolo de manejo de septoria en tomate | responsable: Ana Rivera | aplicacion: Planificador A* | fuente: Manual interno de manejo fitosanitario

3) Se registra el articulo 6 (nace como BORRADOR, no se publica).
   Articulos validados visibles: 2 (el borrador sigue oculto)

4) El experto lo valida y ahora si aparece en la busqueda:
   - Protocolo de contencion de problemas virales | responsable: Ana Rivera | aplicacion: Planificador A* | fuente: Manual interno de manejo fitosanitario
   - Protocolo de manejo de mosaico en tomate | responsable: Ana Rivera | aplicacion: Planificador A* | fuente: Manual interno de manejo fitosanitario
   - Protocolo de manejo de septoria en tomate | responsable: Ana Rivera | aplicacion: Planificador A* | fuente: Manual interno de manejo fitosanitario

5) Errores controlados (integridad y validacion):
   - dominio_id inexistente: sqlite3.IntegrityError: FOREIGN KEY constraint failed
   - articulo inexistente: ValueError: Articulo no encontrado

6) Contenido del repositorio:
   - 3 dominios, 3 aplicaciones, 3 expertos, 3 herramientas
   - 6 articulos: 5 validados y 1 en borrador
```

La tabla de los articulos publicados al final del escenario:

| Titulo | Responsable | Aplicacion | Herramienta | Fuente | Fecha |
|---|---|---|---|---|---|
| Protocolo de contencion de problemas virales | Ana Rivera | Planificador A* | Gestor de tickets | Manual interno de manejo fitosanitario | 2026-11-07 |
| Protocolo de manejo de mosaico en tomate | Ana Rivera | Planificador A* | Gestor de tickets | Manual interno de manejo fitosanitario | 2026-11-15 |
| Protocolo de manejo de septoria en tomate | Ana Rivera | Planificador A* | Gestor de tickets | Manual interno de manejo fitosanitario | 2026-11-05 |

Los pasos son: **capturar** (registrar), **contextualizar** (dominio,
aplicacion, fuente y experto), **validar** (el experto aprueba) y **recuperar**
(la consulta devuelve solo lo publicado).

## 6. Resultado de las pruebas unittest

Desde la raiz del proyecto:

```text
python -m unittest src.semana15_base_conocimiento -v
python -m unittest discover -s tests -v
```

Salida real capturada por el generador del reporte:

```text
test_ciclo_registro_validacion (__main__.TestBaseConocimiento.test_ciclo_registro_validacion)
Un articulo nuevo nace como borrador y solo aparece tras validarlo. ... ok
test_dato_obligatorio (__main__.TestBaseConocimiento.test_dato_obligatorio)
No se registra un articulo sin titulo, contenido o fuente. ... ok
test_id_no_existente (__main__.TestBaseConocimiento.test_id_no_existente)
Validar un id que no existe informa el error. ... ok
test_referencia_inexistente (__main__.TestBaseConocimiento.test_referencia_inexistente)
Un dominio_id inexistente rompe la integridad referencial. ... ok
test_solo_articulos_validados (__main__.TestBaseConocimiento.test_solo_articulos_validados)
El validado se ve; el borrador sigue oculto. ... ok

----------------------------------------------------------------------
Ran 5 tests in 0.199s

OK
```

Estado: **OK: las cinco pruebas pasaron.**

Las cinco pruebas cubren: solo se muestran los validados, el ciclo
registro->validacion, los datos obligatorios, la integridad referencial y el
articulo inexistente. La suite usa una base temporal, asi que no altera los
datos del repositorio.

## 7. Adaptaciones respecto al material de la semana 15

| Material de la semana | En este proyecto | Motivo |
|---|---|---|
| `src/base_conocimiento.py` | `src/semana15_base_conocimiento.py` | Convencion `semanaXX_tema.py` del proyecto |
| `data/conocimiento.db` | `artifacts/conocimiento.db` | `data/` esta reservado al dataset; `artifacts/` ya guarda la BD de la semana 08 |
| Dominios Seguridad / Soporte TI | Diagnostico foliar / Manejo fitosanitario / Calidad de datos | Dominios reales del proyecto, sin datos sensibles |
| Wiki corporativa / Gestor de tickets | Wiki del proyecto / Repositorio Git / Gestor de tickets | Herramientas realmente usadas en PlantAI |
| Base de datos con `tests/` aparte | Pruebas dentro del modulo + `tests/test_base_conocimiento.py` que las reexporta | Permite `python -m unittest src.semana15_...` y `discover -s tests` |

## 8. Limitaciones

- **No hay autenticacion:** `validar_articulo` no comprueba quien aprueba;
  modela el flujo editorial, no los permisos de produccion.
- **No hay versionado:** un articulo corregido se sobreescribe; no se guarda
  historial de cambios.
- **No hay politica de revision periodica:** `fecha_revision` es un dato, no un
  aviso de obsolescencia.
- **Busqueda por coincidencia exacta:** se filtra por nombre de dominio; no
  hay busqueda semantica ni modelos de lenguaje.
- **Un solo experto y un solo dominio por articulo:** no se modelan relaciones
  many-to-many ni equipos.
- **Unicidad literal:** `UNIQUE (titulo, dominio_id)` evita el titulo repetido
  en un dominio, pero no detecta duplicados semanticos.
- **`INSERT OR IGNORE`:** solo facilita repetir la demo; no es una estrategia
  de sincronizacion de informacion empresarial.
- **Verificacion != validacion agronomica:** las pruebas verifican el
  codigo; validar un protocolo fitosanitario real exige expertos y literatura.

## 9. Relacion con el proyecto

```text
semana 03: taxonomia (categorias)
semana 04: plan A* de manejo
semana 13: reglas -> decision de manejo
semana 14: red semantica -> que es cada concepto
semana 15: repositorio -> donde vive, quien lo mantiene y como se publica
```

El puente con el diagnostico ya implementado es la funcion
`articulos_para_categoria(categoria)`: dada la categoria de la semana 03
("Enfermedades fungicas", "Plantas sanas"...) devuelve los articulos
**validados** del dominio que documenta ese manejo. El modulo solo usa la
biblioteca estandar, por lo que puede probarse aislado y conectarse despues a
`src/pipeline.py` o a `server.py`.
