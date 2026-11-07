# Semana 14 - Ingenieria del conocimiento: redes semanticas

**Proyecto:** PlantAI - Deteccion de enfermedades en plantas
**Modulo:** `src/semana14_redes_semanticas.py`
**Reporte generado:** 2026-11-06
**Comando:** `python src/semana14_redes_semanticas.py --reporte`
**Tema:** representaciones del conocimiento, linguistica (parser de oraciones)
e inferencia en una red semantica de la taxonomia del proyecto.

---

## 1. Dominio y problema

La semana 03 clasifica cada clase del dataset (septoria, virus, plaga...)
en categorias, pero esa taxonomia vive en codigo sin poder consultarse.
Esta semana la misma jerarquia se representa como **red semantica**:
nodos = conceptos, aristas dirigidas y etiquetadas = relaciones, y un
**parser linguistico restringido** que convierte oraciones en triples.

## 2. Conceptos

- **Triple:** `(sujeto, relacion, objeto)` (un hecho explicito).
- **Nodo:** concepto. **Arista:** relacion dirigida y etiquetada.
- **Relacion `es_un`:** jerarquia de categorias (admite transitividad).
- **Relacion `necesita`:** propiedad que se hereda (regla didactica).
- **Parser:** acepta solo `X es Y` y `X necesita Y`; otra oracion lanza
  `ValueError` en vez de inventar un triple.
- **Normalizacion:** `casefold()` + filtro de marcas Unicode: quita tildes.

## 3. Base de conocimiento (oraciones -> triples)

| Sujeto | Relación | Objeto |
|---|---|---|
| `enfermedad_bacteriana` | `es_un` | `problema_foliar` |
| `enfermedad_fungica` | `es_un` | `problema_foliar` |
| `enfermedad_viral` | `es_un` | `problema_foliar` |
| `hoja_sana` | `es_un` | `estado_fitosanitario` |
| `hoja_sana` | `necesita` | `monitoreo` |
| `minadora` | `es_un` | `plaga` |
| `mosaico` | `es_un` | `enfermedad_viral` |
| `plaga` | `es_un` | `problema_foliar` |
| `problema_foliar` | `es_un` | `estado_fitosanitario` |
| `problema_foliar` | `necesita` | `inspeccion` |
| `problema_foliar` | `necesita` | `tratamiento` |
| `septoria` | `es_un` | `enfermedad_fungica` |
| `tizon_bacteriano` | `es_un` | `enfermedad_bacteriana` |

La oracion `La minadora invade rapidamente el cultivo.` no calza con ningun patron: se rechaza
(`ValueError`), demostrando el limite del analizador.

## 4. Escenarios

### Escenario A (taxonomia completa)

```text
======================================================================
ESCENARIO A: taxonomia PlantAI completa: septoria como estado fitosanitario
======================================================================
Hechos registrados (13):
  enfermedad_bacteriana --es_un--> problema_foliar
  enfermedad_fungica --es_un--> problema_foliar
  enfermedad_viral --es_un--> problema_foliar
  hoja_sana --es_un--> estado_fitosanitario
  hoja_sana --necesita--> monitoreo
  minadora --es_un--> plaga
  mosaico --es_un--> enfermedad_viral
  plaga --es_un--> problema_foliar
  problema_foliar --es_un--> estado_fitosanitario
  problema_foliar --necesita--> inspeccion
  problema_foliar --necesita--> tratamiento
  septoria --es_un--> enfermedad_fungica
  tizon_bacteriano --es_un--> enfermedad_bacteriana

Consultas (5):
  1. ¿septoria es_un estado_fitosanitario? -> True
      ruta: septoria -> enfermedad_fungica -> problema_foliar -> estado_fitosanitario
  2. ¿septoria es_un hoja_sana? -> False
  3. ¿mosaico es_un problema_foliar? -> True
      ruta: mosaico -> enfermedad_viral -> problema_foliar
  4. ¿Que necesita septoria? -> ['inspeccion', 'tratamiento']
      heredado de problema_foliar: tratamiento, inspeccion
  5. ¿Que necesita hoja_sana? -> ['monitoreo']
```

## 5. Conclusiones

- El objetivo `septoria es_un estado_fitosanitario` se
  demuestra por **transitividad** con la ruta de 4 nodos
  `septoria -> enfermedad_fungica -> problema_foliar ->
  estado_fitosanitario`; la arista directa NO esta almacenada. Las
  necesidades (`inspeccion`, `tratamiento`) se **heredan** de
  `problema_foliar`.

## 6. Limitaciones

- Parser de dos patrones: no resuelve plural, negacion ni ambiguedad.
- Conceptos de una palabra (`\w+`): por eso se usa guion bajo.
- La herencia de `necesita` es una regla pedagogica del modelo.
- Sin negacion, incertidumbre ni tiempo: nodos estaticos.
- Verificacion != validacion: validar la jerarquia agronomica exige
  expertos y literatura.

## 7. Relacion con el proyecto

```text
semana 03: categoria taxonomica
semana 13: reglas de produccion -> que hacer
semana 14: red semantica  -> que ES cada concepto y que hereda
```

Al diagnosticar una imagen, `server.py` agrega el triple
`(clase detectada, es_un, categoria)` de las semanas 02/03 y consulta la
red real con esa planta. El modulo solo usa biblioteca estandar.
