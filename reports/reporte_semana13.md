# Semana 13 - Ingenieria del conocimiento: motor de inferencia

**Proyecto:** PlantAI - Deteccion de enfermedades en plantas con Inteligencia Artificial  
**Modulo:** `src/semana13_conocimiento.py`  
**Reporte generado:** 2026-11-03  
**Comando:** `python src/semana13_conocimiento.py --reporte`  
**Tema:** reglas proposicionales, encadenamiento hacia adelante y trazabilidad.

---

## 1. Descripcion del dominio y problema

PlantAI ya diagnostica una hoja: la semana 02 predice la clase y su confianza,
la semana 03 la convierte en categoria taxonomica, las semanas 09/10 aportan
evidencia visual y la semana 04 entrega un plan de recuperacion A* o confirma
que la meta es inalcanzable. El problema que resuelve este modulo es el paso
siguiente: decidir que hacer con ese diagnostico.

La funcionalidad elegida es el **triaje fitosanitario y la decision de manejo**.
Es natural para el proyecto porque reutiliza sus salidas reales y porque la
decision debe ser explicable y auditable. La conclusion esperada en los casos
principales es `manejo_inmediato`.

## 2. Conceptos y hechos

- **Hecho inicial:** dato que se recibe antes de razonar.
- **Hecho derivado:** dato que produce una regla al dispararse.
- **Hecho no demostrado:** hecho que no se pudo deducir con los hechos
  disponibles; no significa que sea falso.
- **Regla de produccion:** `P ∧ Q → R`.
- **Encadenamiento hacia adelante:** aplicar reglas desde los hechos hasta que
  no aparezcan hechos nuevos.
- **Traza:** registro ordenado de las reglas ejecutadas.

| Caso | Hechos iniciales | Origen en el proyecto |
|---|---|---|
| A | `categoria_fungica`, `confianza_alta`, `danio_foliar_visible`, `plan_disponible`, `plan_tres_acciones` | Pipeline real sobre `data/imagen_proyecto.png` (septoria) |
| B | `categoria_viral`, `confianza_alta`, `danio_foliar_visible`, `meta_inalcanzable` | Taxonomia semanal 03 y grafo de la semana 04 (virus sin cura) |

Hechos derivados en el caso A: `enfermedad_foliar_confirmada`, `manejo_inmediato`, `tratamiento_planificado`.

Hechos derivados en el caso B: `cuarentena_y_contencion`, `manejo_integrado`, `plan_de_contencion`.

Hecho no demostrado en el caso B: `manejo_inmediato`. No esta en el conjunto final y
no se afirma que sea falso.

## 3. Matriz de reglas

| Regla | Premisas | Conclusion |
|---|---|---|
| **R1** | `categoria_fungica` ∧ `confianza_alta` ∧ `danio_foliar_visible` | `enfermedad_foliar_confirmada` |
| **R2** | `categoria_bacteriana` ∧ `confianza_alta` ∧ `danio_foliar_visible` | `enfermedad_foliar_confirmada` |
| **R3** | `categoria_plaga` ∧ `confianza_alta` ∧ `danio_foliar_visible` | `enfermedad_foliar_confirmada` |
| **R4** | `enfermedad_foliar_confirmada` ∧ `plan_disponible` | `tratamiento_planificado` |
| **R5** | `plan_tres_acciones` ∧ `tratamiento_planificado` | `manejo_inmediato` |
| **R6** | `categoria_viral` ∧ `confianza_alta` ∧ `danio_foliar_visible` | `cuarentena_y_contencion` |
| **R7** | `cuarentena_y_contencion` ∧ `meta_inalcanzable` | `plan_de_contencion` |
| **R8** | `categoria_viral` ∧ `plan_de_contencion` | `manejo_integrado` |
| **R9** | `categoria_sana` ∧ `confianza_alta` | `monitoreo_preventivo` |
| **R10** | `categoria_desconocida` | `revision_experta` |

La cadena del caso A es **R1 -> R4 -> R5**. La conclusion de R1
(`enfermedad_foliar_confirmada`) es premisa de R4; la conclusion de R4
(`tratamiento_planificado`) es premisa de R5. Se cumplen tres pasos de
encadenamiento hasta `manejo_inmediato`.

## 4. Resultados y trazas reales

### Caso A

```text
======================================================================
ESCENARIO A: tomate con septoria, confianza alta y plan de recuperacion de 3 acciones
======================================================================
Hechos iniciales (5):
  - categoria_fungica
  - confianza_alta
  - danio_foliar_visible
  - plan_disponible
  - plan_tres_acciones

Reglas ejecutadas (3):
  1. R1: categoria_fungica, confianza_alta, danio_foliar_visible => enfermedad_foliar_confirmada
  2. R4: enfermedad_foliar_confirmada, plan_disponible => tratamiento_planificado
  3. R5: plan_tres_acciones, tratamiento_planificado => manejo_inmediato

Hechos derivados (3):
  - enfermedad_foliar_confirmada
  - manejo_inmediato
  - tratamiento_planificado

Hechos finales (8):
  categoria_fungica, confianza_alta, danio_foliar_visible, enfermedad_foliar_confirmada, manejo_inmediato, plan_disponible, plan_tres_acciones, tratamiento_planificado

Resultado:
  DEMOSTRADA: manejo_inmediato esta en los hechos finales.
```

### Caso B

```text
======================================================================
ESCENARIO B: tomate con virus, confianza alta y meta inalcanzable para A*
======================================================================
Hechos iniciales (4):
  - categoria_viral
  - confianza_alta
  - danio_foliar_visible
  - meta_inalcanzable

Reglas ejecutadas (3):
  1. R6: categoria_viral, confianza_alta, danio_foliar_visible => cuarentena_y_contencion
  2. R7: cuarentena_y_contencion, meta_inalcanzable => plan_de_contencion
  3. R8: categoria_viral, plan_de_contencion => manejo_integrado

Hechos derivados (3):
  - cuarentena_y_contencion
  - manejo_integrado
  - plan_de_contencion

Hechos finales (7):
  categoria_viral, confianza_alta, cuarentena_y_contencion, danio_foliar_visible, manejo_integrado, meta_inalcanzable, plan_de_contencion

Resultado:
  NO DEMOSTRADA con los hechos disponibles: manejo_inmediato no esta en los hechos finales.
```

## 5. Que se demostro y que quedo sin demostrar

- **Caso A:** se demostro `manejo_inmediato`. R1 confirma la enfermedad foliar, R4
  planifica el tratamiento y R5 habilita el manejo inmediato.
- **Caso B:** `manejo_inmediato` quedo **NO DEMOSTRADA con los hechos disponibles**.
  Se dispararon R6, R7 y R8, que derivan contencion y manejo integrado, pero
  falta `plan_disponible` para R4 y no existe `tratamiento_planificado` para R5.

"No demostrado" no es "falso": el motor trabaja con hechos positivos y no tiene
negacion explicita. Que `manejo_inmediato` no este en el conjunto final solo significa
que no puede deducirse con esos hechos; no afirma que sea falso ni que la accion
deba descartarse. Es una consecuencia del mundo abierto.

## 6. Resultado de las pruebas unittest

Comando equivalente desde la raiz del proyecto:

```text
python -m unittest src.semana13_conocimiento -v
```

Salida real capturada por el generador al ejecutar la misma suite:

```text
test_caso_a_demuestra_conclusion_y_tiene_tres_pasos (__main__.TestMotorInferencia.test_caso_a_demuestra_conclusion_y_tiene_tres_pasos) ... ok
test_caso_b_no_demuestra_conclusion (__main__.TestMotorInferencia.test_caso_b_no_demuestra_conclusion) ... ok
test_ciclo_de_reglas_termina_sin_duplicados (__main__.TestMotorInferencia.test_ciclo_de_reglas_termina_sin_duplicados) ... ok
test_conclusion_duplicada_solo_se_registra_una_vez (__main__.TestMotorInferencia.test_conclusion_duplicada_solo_se_registra_una_vez) ... ok
test_falta_plan_disponible_corta_la_cadena (__main__.TestMotorInferencia.test_falta_plan_disponible_corta_la_cadena) ... ok
test_hechos_iniciales_no_se_modifican (__main__.TestMotorInferencia.test_hechos_iniciales_no_se_modifican) ... ok
test_orden_y_contenido_de_la_traza (__main__.TestMotorInferencia.test_orden_y_contenido_de_la_traza) ... ok
test_planta_sana_genera_monitoreo_preventivo (__main__.TestMotorInferencia.test_planta_sana_genera_monitoreo_preventivo) ... ok
test_regla_no_se_dispara_si_falta_una_premisa (__main__.TestMotorInferencia.test_regla_no_se_dispara_si_falta_una_premisa) ... ok

----------------------------------------------------------------------
Ran 9 tests in 0.000s

OK
```

Estado: **OK: todas las pruebas pasaron.**

## 7. Limitaciones

- Un solo caso a la vez: los hechos no tienen variables ni identificadores.
- Sin logica de primer orden: no hay cuantificadores ni relaciones entre
  plantas.
- Sin negacion: no se representa "no hay dano"; simplemente falta el hecho.
- Sin incertidumbre: la confianza numerica se abstrae a `confianza_alta`.
- Sin prioridades ni excepciones: solo se evita duplicar conclusiones.
- Sin tiempo: no se modela la evolucion de la enfermedad ni el efecto de un
  tratamiento ya aplicado.
- No es aprendizaje automatico: las reglas se escriben a mano.
- Verificacion distinta de validacion: las pruebas verifican la
  implementacion; validar el dominio real requiere expertos, literatura o
  datos de campo.
- Los hechos se preparan a partir de las salidas de otras semanas; la
  integracion automatica al pipeline queda como trabajo futuro.

## 8. Relacion con el proyecto individual

```text
semana 02: clase predicha + confianza
        ↓
semana 03: categoria taxonomica
        ↓
semana 09/10: evidencia visual y regiones
        ↓
semana 04: plan disponible o meta inalcanzable
        ↓
semana 13: hechos -> reglas -> decision de manejo
```

El motor no depende de Flask, scikit-learn ni del dataset: solo usa la
biblioteca estandar. Por eso puede probarse de forma aislada y conectarse mas
adelante a `src/pipeline.py` o a `server.py` para mostrar la decision, las
reglas ejecutadas y la trazabilidad.
