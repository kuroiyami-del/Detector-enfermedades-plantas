# Semana 16 - Motor de referencia (arquitectura de sistemas inteligentes)

**Proyecto:** PlantAI - Deteccion de enfermedades en plantas con Inteligencia Artificial  
**Modulo:** `src/semana16_motor_referencia.py`  
**Reporte generado:** 2026-11-16  
**Comandos:** `python -m src.semana16_motor_referencia` | `--reporte` | `--pruebas`  
**Tema:** diseno de sistemas inteligentes: arquitectura y motor de referencia.  
**Material de referencia:** `referencia semana16/` (guia y presentacion de clase).

## 1. Arquitectura del sistema

El sistema responde preguntas del usuario usando unicamente conocimiento
**validado** del proyecto. Los seis componentes viven en un solo modulo y se
relacionan asi:

```text
Pregunta (consola o web)
    |
    v
1. Interfaz ---------------> recibe el texto crudo del usuario
    |
    v
2. Normalizador -----------> minusculas, sin tildes, palabras unicas
    |
    v
3. Motor de referencia <--+--> 4. Base de conocimiento
    |                     |        (referencias desde la semana 15)
    v                     |
5. Generador de resp. ----+
    |
    v
Respuesta + ID + fuente -------> 6. Control de calidad
(o abstencion: SIN_DATOS /       (8 pruebas + 5 escenarios)
 SIN_REFERENCIA, nunca inventa)
```

| Componente | Responsabilidad | Como se relaciona |
|---|---|---|
| 1. Interfaz | Recibe la pregunta escrita por el usuario (consola o web). | Entrega el texto crudo al normalizador. |
| 2. Normalizador | Convierte el texto a minusculas, quita tildes y extrae palabras unicas. | Entrega el conjunto de palabras al motor. |
| 3. Base de conocimiento | Guarda las referencias con id, titulo, claves, respuesta, fuente y validacion (semana 15). | Provee los registros que consulta el motor. |
| 4. Motor de referencia | Filtra los borradores, cuenta coincidencias y elige la mejor referencia. | Devuelve la referencia elegida al generador de respuestas. |
| 5. Generador de respuestas | Arma el mensaje final con el id y la fuente; no crea texto nuevo. | Entrega la respuesta trazable a la interfaz. |
| 6. Control de calidad | Pruebas unittest y escenarios que demuestran el comportamiento. | Verifica el resultado de los cinco componentes anteriores. |

Diferencia clave para la sustentacion: un **motor de inferencia** aplica
reglas y deriva conclusiones nuevas; este **motor de referencia** recupera una
referencia ya existente y muestra de donde salio. El termino oficial del
silabo es "motor de referencia".

## 2. Organizacion de las referencias

Cada referencia tiene identificador unico, titulo, palabras clave, respuesta,
fuente y estado de validacion. La base se construye leyendo los articulos del
repositorio de la **semana 15** (`artifacts/conocimiento.db`) y agregandoles
las palabras clave del dominio: el articulo 5 esta en BORRADOR y nace con
`validada=False`, asi que el motor lo ignora aunque coincida con la consulta.

| ID | Titulo | Palabras clave | Validada | Fuente |
|---|---|---|---|---|
| REF-001 | Registro de evidencia visual del diagnostico | evidencia, guardar, panel, captura | si | Reporte semanal del proyecto |
| REF-002 | Protocolo de manejo de septoria en tomate | septoria, manchas, fungicida, tratamiento, hojas | si | Manual interno de manejo fitosanitario |
| REF-003 | Criterio de clasificacion taxonomica | categoria, clase, clasificacion, taxonomia | si | Taxonomia de la semana 03 |
| REF-004 | Protocolo de contencion de problemas virales | virus, viral, cura, contencion, vectores | si | Manual interno de manejo fitosanitario |
| REF-005 | Revision de la calidad del dataset PlantVillage | calidad, dataset, distribucion, revision | NO (borrador) | Metadatos del dataset |

## 3. Escenarios probados

| Caso | Consulta | Estado | Referencia |
|---|---|---|---|
| A | Cual es el tratamiento para las manchas? | ENCONTRADA | REF-002 |
| B | Como es la calidad del dataset? | SIN_REFERENCIA | - |
| C | Cuanto cuesta el agua de riego? | SIN_REFERENCIA | - |
| D | (vacia) | SIN_DATOS | - |
| E | Hay cura para el virus? | ENCONTRADA | REF-004 |

El motor **no inventa respuestas**: el caso B coincide con un borrador y el
caso C esta fuera del conocimiento; en ambos el estado es `SIN_REFERENCIA`. La
puntuacion de coincidencias es un conteo de palabras en comun, no una
probabilidad ni un porcentaje de confianza.

## 4. Ejecucion de la demostracion

```text
======================================================================
ESCENARIOS: el motor responde con referencias validadas o se abstiene
======================================================================

Arquitectura (que hace cada componente):
   - 1. Interfaz: Recibe la pregunta escrita por el usuario (consola o web).
   - 2. Normalizador: Convierte el texto a minusculas, quita tildes y extrae palabras unicas.
   - 3. Base de conocimiento: Guarda las referencias con id, titulo, claves, respuesta, fuente y validacion (semana 15).
   - 4. Motor de referencia: Filtra los borradores, cuenta coincidencias y elige la mejor referencia.
   - 5. Generador de respuestas: Arma el mensaje final con el id y la fuente; no crea texto nuevo.
   - 6. Control de calidad: Pruebas unittest y escenarios que demuestran el comportamiento.

Base de conocimiento (construida desde la semana 15):
   - REF-001 [VALIDADA] Registro de evidencia visual del diagnostico
   - REF-002 [VALIDADA] Protocolo de manejo de septoria en tomate
   - REF-003 [VALIDADA] Criterio de clasificacion taxonomica
   - REF-004 [VALIDADA] Protocolo de contencion de problemas virales
   - REF-005 [BORRADOR (no responde)] Revision de la calidad del dataset PlantVillage

Caso A (consulta cubierta por una referencia validada):
   Consulta : Cual es el tratamiento para las manchas?
   Estado   : ENCONTRADA
   Respuesta: Aplicar el plan A* de tres acciones: retirar las hojas afectadas, tratar con fungicida y repetir el control a los 7 dias.
              Fuente: [REF-002] Protocolo de manejo de septoria en tomate - Manual interno de manejo fitosanitario (coincidencias: 2)

Caso B (consulta que solo coincide con un borrador):
   Consulta : Como es la calidad del dataset?
   Estado   : SIN_REFERENCIA
   Respuesta: No hay evidencia validada para esa pregunta; consulta con la persona responsable del cultivo.

Caso C (pregunta fuera del conocimiento disponible):
   Consulta : Cuanto cuesta el agua de riego?
   Estado   : SIN_REFERENCIA
   Respuesta: No hay evidencia validada para esa pregunta; consulta con la persona responsable del cultivo.

Caso D (consulta vacia):
   Consulta : (vacia)
   Estado   : SIN_DATOS
   Respuesta: Escribe una pregunta sobre el cuidado de tus plantas.

Caso E (consulta viral (solo contencion)):
   Consulta : Hay cura para el virus?
   Estado   : ENCONTRADA
   Respuesta: No hay cura quimica para los virus: retirar la planta infectada, controlar los vectores (pulgones y mosca blanca) y vigilar el cultivo durante 15 dias.
              Fuente: [REF-004] Protocolo de contencion de problemas virales - Manual interno de manejo fitosanitario (coincidencias: 2)
```

## 5. Resultado de las pruebas unittest

```text
python -m unittest src.semana16_motor_referencia -v
```

Salida real capturada por el generador del reporte:

```text
test_base_construida_desde_semana15 (__main__.TestMotorReferencia.test_base_construida_desde_semana15)
La base conserva los 5 articulos de la semana 15 y su estado. ... ok
test_consulta_con_referencia_validada (__main__.TestMotorReferencia.test_consulta_con_referencia_validada)
Una consulta cubierta devuelve ENCONTRADA y la referencia correcta. ... ok
test_consulta_vacia_pide_pregunta (__main__.TestMotorReferencia.test_consulta_vacia_pide_pregunta)
Sin palabras utiles el motor pide una consulta. ... ok
test_ignora_referencia_no_validada (__main__.TestMotorReferencia.test_ignora_referencia_no_validada)
El borrador coincide con la consulta, pero nunca responde. ... ok
test_no_inventa_respuestas (__main__.TestMotorReferencia.test_no_inventa_respuestas)
Una pregunta fuera del conocimiento se abstiene. ... ok
test_normalizacion_mayusculas_y_tildes (__main__.TestMotorReferencia.test_normalizacion_mayusculas_y_tildes)
Mayusculas, tildes y signos no deben impedir la coincidencia. ... ok
test_pregunta_desde_clase_diagnostico (__main__.TestMotorReferencia.test_pregunta_desde_clase_diagnostico)
La clase detectada en la web llega al motor y encuentra fuente. ... ok
test_respuesta_con_fuente_identificable (__main__.TestMotorReferencia.test_respuesta_con_fuente_identificable)
La respuesta proviene del registro y viaja con id y fuente. ... ok

----------------------------------------------------------------------
Ran 8 tests in 0.228s

OK
```

Estado: **OK: las ocho pruebas pasaron.**

## 6. Integracion con el proyecto

- La base de conocimiento es la de la **semana 15**: el motor solo agrega la
  busqueda y la recuperacion con trazabilidad (id + fuente).
- En la web (`index.html` + `server.py`), la pestana **Semana 16 - Motor de
  referencia** muestra la arquitectura, los escenarios y la base; al
  diagnosticar una imagen, la clase detectada (semana 02) se convierte en
  pregunta con `pregunta_desde_clase()` y el tab muestra la referencia
  validada que la soporta, o la abstencion si no hay evidencia.
