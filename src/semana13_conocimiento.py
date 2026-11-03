"""Semana 13 - Ingenieria del conocimiento: sistemas logicos y motor de inferencia.

DOMINIO ELEGIDO
===============

Triaje fitosanitario y decision de manejo posterior al diagnostico por imagen
del proyecto PlantAI.

El proyecto ya produce un diagnostico: la semana 02 clasifica la imagen y
calcula una confianza, la semana 03 convierte la clase en una categoria
taxonomica, las semanas 09/10 aportan evidencia visual de la hoja y la semana
04 entrega un plan de recuperacion A* o confirma que la meta es inalcanzable.
Lo que falta es una politica explicable para decidir que hacer con ese
diagnostico: manejo inmediato, cuarentena/contencion, revision experta o
monitoreo preventivo. Esa decision es conocimiento del dominio, no una tarea
de aprendizaje automatico, y por eso se modela con reglas y trazas.

Se eligio esta funcionalidad porque usa directamente las salidas reales del
pipeline y permite demostrar una cadena de inferencia de tres pasos:

    R1: categoria fungica + confianza alta + dano visible
        -> enfermedad_foliar_confirmada
    R4: enfermedad_foliar_confirmada + plan_disponible
        -> tratamiento_planificado
    R5: tratamiento_planificado + plan_tres_acciones
        -> manejo_inmediato

CONCEPTOS PRINCIPALES
=====================

- Hecho inicial: dato que se recibe antes de razonar (clase, confianza,
  evidencia visual o resultado de A*).
- Hecho derivado: dato que produce una regla al dispararse.
- Hecho no demostrado: hecho que no esta en el conjunto final porque no se
  pudo deducir. No implica que sea falso.
- Regla de produccion: P ^ Q -> R. Si todas las premisas estan presentes, se
  concluye R.
- Encadenamiento hacia adelante: se parte de los hechos y se aplican reglas
  hasta que no aparecen hechos nuevos.
- Traza: registro ordenado de las reglas ejecutadas y de las premisas usadas.

VOCABULARIO CONTROLADO
======================

Hechos iniciales:
  categoria_fungica, categoria_bacteriana, categoria_plaga, categoria_viral,
  categoria_sana, categoria_desconocida, confianza_alta,
  danio_foliar_visible, plan_disponible, plan_tres_acciones,
  meta_inalcanzable.

Hechos derivados:
  enfermedad_foliar_confirmada, tratamiento_planificado, manejo_inmediato,
  cuarentena_y_contencion, plan_de_contencion, manejo_integrado,
  monitoreo_preventivo, revision_experta.

Conclusion esperada en los escenarios principales: manejo_inmediato.

MATRIZ DE REGLAS
================

| Regla | Premisas | Conclusion |
|---|---|---|
| R1 | categoria_fungica, confianza_alta, danio_foliar_visible | enfermedad_foliar_confirmada |
| R2 | categoria_bacteriana, confianza_alta, danio_foliar_visible | enfermedad_foliar_confirmada |
| R3 | categoria_plaga, confianza_alta, danio_foliar_visible | enfermedad_foliar_confirmada |
| R4 | enfermedad_foliar_confirmada, plan_disponible | tratamiento_planificado |
| R5 | tratamiento_planificado, plan_tres_acciones | manejo_inmediato |
| R6 | categoria_viral, confianza_alta, danio_foliar_visible | cuarentena_y_contencion |
| R7 | cuarentena_y_contencion, meta_inalcanzable | plan_de_contencion |
| R8 | plan_de_contencion, categoria_viral | manejo_integrado |
| R9 | categoria_sana, confianza_alta | monitoreo_preventivo |
| R10 | categoria_desconocida | revision_experta |

Todas las reglas son positivas (tipo Horn): no usan negacion, probabilidades,
prioridades ni excepciones. La regla R5 cierra la cadena de tres pasos del
caso A. En el caso B se disparan R6, R7 y R8, pero no R4/R5 porque falta
plan_disponible; por eso manejo_inmediato queda NO DEMOSTRADA.

LIMITACIONES
============

- Un solo caso a la vez: los hechos no tienen variables ni identificadores de
  planta.
- Sin logica de primer orden: no hay cuantificadores ni relaciones entre
  plantas.
- Sin negacion: no se representa "no hay dano"; simplemente falta el hecho.
- Sin incertidumbre: la confianza numerica se abstrae a confianza_alta.
- Sin prioridades ni excepciones: solo se evita duplicar conclusiones.
- Sin tiempo: no se modela la evolucion de la enfermedad ni el efecto de un
  tratamiento ya aplicado.
- No es aprendizaje automatico: las reglas se escriben a mano.
- Verificacion != validacion: las pruebas comprueban que el codigo implementa
  las reglas; validar que las reglas reflejan la agronomia real requiere
  especialistas, literatura o datos de campo.
- Los hechos se preparan a partir de las salidas de las otras semanas; la
  integracion automatica al pipeline queda como trabajo futuro.
"""

from __future__ import annotations

import io
import sys
import unittest
from dataclasses import dataclass
from datetime import date
from pathlib import Path


RAIZ = Path(__file__).resolve().parent.parent
RUTA_REPORTE = RAIZ / "reports" / "reporte_semana13.md"

# Conclusion que se quiere demostrar en los escenarios de la sustentacion.
OBJETIVO = "manejo_inmediato"


@dataclass(frozen=True)
class Regla:
    """Regla de produccion: si todas las premisas estan, se concluye."""

    nombre: str
    premisas: frozenset[str]
    conclusion: str


@dataclass(frozen=True)
class ResultadoEscenario:
    """Resultado completo de ejecutar un escenario."""

    nombre: str
    descripcion: str
    hechos_iniciales: frozenset[str]
    hechos_finales: frozenset[str]
    derivados: frozenset[str]
    trazas: tuple[str, ...]
    objetivo: str
    resultado: str


def construir_reglas() -> list[Regla]:
    """Construye las reglas originales del dominio PlantAI.

    Las reglas combinan la categoria taxonomica (semana 03), la confianza del
    clasificador (semana 02), la evidencia visual (semanas 09/10) y el
    resultado de la planificacion A* (semana 04).
    """

    return [
        Regla(
            "R1",
            frozenset({"categoria_fungica", "confianza_alta", "danio_foliar_visible"}),
            "enfermedad_foliar_confirmada",
        ),
        Regla(
            "R2",
            frozenset({"categoria_bacteriana", "confianza_alta", "danio_foliar_visible"}),
            "enfermedad_foliar_confirmada",
        ),
        Regla(
            "R3",
            frozenset({"categoria_plaga", "confianza_alta", "danio_foliar_visible"}),
            "enfermedad_foliar_confirmada",
        ),
        Regla(
            "R4",
            frozenset({"enfermedad_foliar_confirmada", "plan_disponible"}),
            "tratamiento_planificado",
        ),
        Regla(
            "R5",
            frozenset({"tratamiento_planificado", "plan_tres_acciones"}),
            "manejo_inmediato",
        ),
        Regla(
            "R6",
            frozenset({"categoria_viral", "confianza_alta", "danio_foliar_visible"}),
            "cuarentena_y_contencion",
        ),
        Regla(
            "R7",
            frozenset({"cuarentena_y_contencion", "meta_inalcanzable"}),
            "plan_de_contencion",
        ),
        Regla(
            "R8",
            frozenset({"plan_de_contencion", "categoria_viral"}),
            "manejo_integrado",
        ),
        Regla(
            "R9",
            frozenset({"categoria_sana", "confianza_alta"}),
            "monitoreo_preventivo",
        ),
        Regla(
            "R10",
            frozenset({"categoria_desconocida"}),
            "revision_experta",
        ),
    ]


def inferir(
    hechos_iniciales: set[str],
    reglas: list[Regla],
) -> tuple[set[str], list[str]]:
    """Aplica encadenamiento hacia adelante hasta que no haya cambios.

    - Copia los hechos iniciales para no mutar la entrada.
    - Una regla se dispara solo si todas sus premisas estan en los hechos y su
      conclusion todavia no esta. Esa condicion evita conclusiones duplicadas
      y garantiza la terminacion incluso con reglas ciclicas.
    - Cada disparo se registra en una traza con las premisas ordenadas.

    Devuelve ``(hechos_finales, trazas)``. Los hechos finales incluyen tanto
    los iniciales como los derivados.
    """

    hechos = set(hechos_iniciales)
    trazas: list[str] = []
    cambios = True

    while cambios:
        cambios = False
        for regla in reglas:
            if regla.premisas.issubset(hechos) and regla.conclusion not in hechos:
                hechos.add(regla.conclusion)
                premisas_ordenadas = ", ".join(sorted(regla.premisas))
                trazas.append(
                    f"{regla.nombre}: {premisas_ordenadas} => {regla.conclusion}"
                )
                cambios = True

    return hechos, trazas


def formatear_resultado(objetivo: str, hechos: set[str]) -> str:
    """Redacta el resultado sin confundir 'no demostrada' con 'falsa'."""

    if objetivo in hechos:
        return f"DEMOSTRADA: {objetivo} esta en los hechos finales."
    return (
        "NO DEMOSTRADA con los hechos disponibles: "
        f"{objetivo} no esta en los hechos finales."
    )


def ejecutar_escenario(
    nombre: str,
    descripcion: str,
    hechos_iniciales: set[str],
    reglas: list[Regla],
    objetivo: str,
) -> ResultadoEscenario:
    """Ejecuta un escenario y devuelve sus hechos, trazas y resultado."""

    hechos_finales, trazas = inferir(set(hechos_iniciales), reglas)
    derivados = hechos_finales - hechos_iniciales
    return ResultadoEscenario(
        nombre=nombre,
        descripcion=descripcion,
        hechos_iniciales=frozenset(hechos_iniciales),
        hechos_finales=frozenset(hechos_finales),
        derivados=frozenset(derivados),
        trazas=tuple(trazas),
        objetivo=objetivo,
        resultado=formatear_resultado(objetivo, hechos_finales),
    )


def renderizar_escenario(resultado: ResultadoEscenario) -> str:
    """Convierte un resultado en texto legible para consola y reporte."""

    lineas = [
        "=" * 70,
        f"ESCENARIO {resultado.nombre}: {resultado.descripcion}",
        "=" * 70,
        f"Hechos iniciales ({len(resultado.hechos_iniciales)}):",
    ]
    lineas.extend(f"  - {hecho}" for hecho in sorted(resultado.hechos_iniciales))

    lineas.append("")
    lineas.append(f"Reglas ejecutadas ({len(resultado.trazas)}):")
    if resultado.trazas:
        lineas.extend(
            f"  {numero}. {traza}"
            for numero, traza in enumerate(resultado.trazas, start=1)
        )
    else:
        lineas.append("  (ninguna)")

    lineas.append("")
    lineas.append(f"Hechos derivados ({len(resultado.derivados)}):")
    if resultado.derivados:
        lineas.extend(f"  - {hecho}" for hecho in sorted(resultado.derivados))
    else:
        lineas.append("  (ninguno)")

    lineas.append("")
    lineas.append(f"Hechos finales ({len(resultado.hechos_finales)}):")
    lineas.append("  " + ", ".join(sorted(resultado.hechos_finales)))

    lineas.append("")
    lineas.append("Resultado:")
    lineas.append(f"  {resultado.resultado}")

    return "\n".join(lineas)


def imprimir_escenario(resultado: ResultadoEscenario) -> None:
    """Imprime un escenario en consola."""

    print(renderizar_escenario(resultado))


def mostrar_reglas(reglas: list[Regla]) -> None:
    """Imprime la base de reglas en notacion legible."""

    print("\nBase de reglas:")
    for regla in reglas:
        premisas = " ^ ".join(sorted(regla.premisas))
        print(f"  {regla.nombre}: {premisas} -> {regla.conclusion}")


# ---------------------------------------------------------------------------
# HECHOS DE LOS DOS ESCENARIOS PRINCIPALES
# ---------------------------------------------------------------------------

# Caso A: hoja de tomate con septoria (data/imagen_proyecto.png).
# - La semana 02 la clasifica como Tomato___Septoria_leaf_spot con 100.0%.
# - La semana 03 la convierte en categoria_fungica.
# - La semana 10 detecta 5 regiones mayores a 50 px (danio foliar visible).
# - A* encuentra un plan fungico de 3 acciones y costo 8 (plan disponible).
HECHOS_CASO_A = {
    "categoria_fungica",
    "confianza_alta",
    "danio_foliar_visible",
    "plan_disponible",
    "plan_tres_acciones",
}

# Caso B: caso viral real de la taxonomia y del grafo de la semana 04.
# - La clase Tomato___Tomato_mosaic_virus pertenece a categoria_viral.
# - La confianza del clasificador es alta.
# - Hay dano foliar visible, pero A* no tiene transicion hacia healthy:
#   astar() devuelve None y la meta es inalcanzable.
# Faltan plan_disponible y plan_tres_acciones, por eso R4/R5 no se disparan.
HECHOS_CASO_B = {
    "categoria_viral",
    "confianza_alta",
    "danio_foliar_visible",
    "meta_inalcanzable",
}


def ejecutar_casos(
    reglas: list[Regla],
) -> tuple[ResultadoEscenario, ResultadoEscenario]:
    """Ejecuta los dos casos principales con las salidas reales del proyecto."""

    caso_a = ejecutar_escenario(
        "A",
        "tomate con septoria, confianza alta y plan de recuperacion de 3 acciones",
        HECHOS_CASO_A,
        reglas,
        OBJETIVO,
    )
    caso_b = ejecutar_escenario(
        "B",
        "tomate con virus, confianza alta y meta inalcanzable para A*",
        HECHOS_CASO_B,
        reglas,
        OBJETIVO,
    )
    return caso_a, caso_b


def matriz_reglas_markdown(reglas: list[Regla]) -> str:
    """Devuelve la matriz de reglas en formato Markdown."""

    lineas = [
        "| Regla | Premisas | Conclusion |",
        "|---|---|---|",
    ]
    for regla in reglas:
        premisas = " ∧ ".join(f"`{premisa}`" for premisa in sorted(regla.premisas))
        lineas.append(f"| **{regla.nombre}** | {premisas} | `{regla.conclusion}` |")
    return "\n".join(lineas)


def ejecutar_pruebas() -> tuple[str, bool]:
    """Ejecuta las pruebas unittest del modulo y captura su salida real."""

    suite = unittest.defaultTestLoader.loadTestsFromTestCase(TestMotorInferencia)
    flujo = io.StringIO()
    resultado = unittest.TextTestRunner(stream=flujo, verbosity=2).run(suite)
    return flujo.getvalue(), resultado.wasSuccessful()


def generar_reporte(ruta: Path | None = None) -> Path:
    """Ejecuta los escenarios y las pruebas, y escribe el reporte Markdown."""

    reglas = construir_reglas()
    caso_a, caso_b = ejecutar_casos(reglas)
    salida_pruebas, pruebas_ok = ejecutar_pruebas()

    destino = ruta or RUTA_REPORTE
    destino.parent.mkdir(parents=True, exist_ok=True)

    estado_pruebas = "OK: todas las pruebas pasaron." if pruebas_ok else (
        "FALLO: alguna prueba no paso."
    )

    contenido = f"""# Semana 13 - Ingenieria del conocimiento: motor de inferencia

**Proyecto:** PlantAI - Deteccion de enfermedades en plantas con Inteligencia Artificial  
**Modulo:** `src/semana13_conocimiento.py`  
**Reporte generado:** {date.today().isoformat()}  
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
principales es `{OBJETIVO}`.

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
| A | {", ".join(f"`{h}`" for h in sorted(HECHOS_CASO_A))} | Pipeline real sobre `data/imagen_proyecto.png` (septoria) |
| B | {", ".join(f"`{h}`" for h in sorted(HECHOS_CASO_B))} | Taxonomia semanal 03 y grafo de la semana 04 (virus sin cura) |

Hechos derivados en el caso A: {", ".join(f"`{h}`" for h in sorted(caso_a.derivados))}.

Hechos derivados en el caso B: {", ".join(f"`{h}`" for h in sorted(caso_b.derivados))}.

Hecho no demostrado en el caso B: `{OBJETIVO}`. No esta en el conjunto final y
no se afirma que sea falso.

## 3. Matriz de reglas

{matriz_reglas_markdown(reglas)}

La cadena del caso A es **R1 -> R4 -> R5**. La conclusion de R1
(`enfermedad_foliar_confirmada`) es premisa de R4; la conclusion de R4
(`tratamiento_planificado`) es premisa de R5. Se cumplen tres pasos de
encadenamiento hasta `manejo_inmediato`.

## 4. Resultados y trazas reales

### Caso A

```text
{renderizar_escenario(caso_a)}
```

### Caso B

```text
{renderizar_escenario(caso_b)}
```

## 5. Que se demostro y que quedo sin demostrar

- **Caso A:** se demostro `{OBJETIVO}`. R1 confirma la enfermedad foliar, R4
  planifica el tratamiento y R5 habilita el manejo inmediato.
- **Caso B:** `{OBJETIVO}` quedo **NO DEMOSTRADA con los hechos disponibles**.
  Se dispararon R6, R7 y R8, que derivan contencion y manejo integrado, pero
  falta `plan_disponible` para R4 y no existe `tratamiento_planificado` para R5.

"No demostrado" no es "falso": el motor trabaja con hechos positivos y no tiene
negacion explicita. Que `{OBJETIVO}` no este en el conjunto final solo significa
que no puede deducirse con esos hechos; no afirma que sea falso ni que la accion
deba descartarse. Es una consecuencia del mundo abierto.

## 6. Resultado de las pruebas unittest

Comando equivalente desde la raiz del proyecto:

```text
python -m unittest src.semana13_conocimiento -v
```

Salida real capturada por el generador al ejecutar la misma suite:

```text
{salida_pruebas.rstrip()}
```

Estado: **{estado_pruebas}**

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
"""

    destino.write_text(contenido, encoding="utf-8")
    return destino


class TestMotorInferencia(unittest.TestCase):
    """Verifica el encadenamiento, las trazas y la terminacion del motor."""

    def setUp(self) -> None:
        self.reglas = construir_reglas()

    def test_caso_a_demuestra_conclusion_y_tiene_tres_pasos(self) -> None:
        hechos_finales, trazas = inferir(set(HECHOS_CASO_A), self.reglas)

        self.assertIn(OBJETIVO, hechos_finales)
        self.assertEqual(len(trazas), 3)
        self.assertEqual(
            trazas,
            [
                "R1: categoria_fungica, confianza_alta, danio_foliar_visible "
                "=> enfermedad_foliar_confirmada",
                "R4: enfermedad_foliar_confirmada, plan_disponible "
                "=> tratamiento_planificado",
                "R5: plan_tres_acciones, tratamiento_planificado "
                "=> manejo_inmediato",
            ],
        )
        self.assertIn("DEMOSTRADA", formatear_resultado(OBJETIVO, hechos_finales))

    def test_caso_b_no_demuestra_conclusion(self) -> None:
        hechos_finales, trazas = inferir(set(HECHOS_CASO_B), self.reglas)

        self.assertNotIn(OBJETIVO, hechos_finales)
        self.assertIn("cuarentena_y_contencion", hechos_finales)
        self.assertIn("plan_de_contencion", hechos_finales)
        self.assertIn("manejo_integrado", hechos_finales)
        self.assertEqual([traza.split(":")[0] for traza in trazas], ["R6", "R7", "R8"])
        self.assertIn(
            "NO DEMOSTRADA con los hechos disponibles",
            formatear_resultado(OBJETIVO, hechos_finales),
        )

    def test_hechos_iniciales_no_se_modifican(self) -> None:
        original = set(HECHOS_CASO_A)
        copia = set(original)

        hechos_finales, _trazas = inferir(original, self.reglas)

        self.assertEqual(original, copia)
        self.assertIsNot(hechos_finales, original)
        self.assertNotEqual(hechos_finales, original)

    def test_ciclo_de_reglas_termina_sin_duplicados(self) -> None:
        reglas_ciclicas = [
            Regla("R_ab", frozenset({"a"}), "b"),
            Regla("R_ba", frozenset({"b"}), "a"),
        ]

        hechos_finales, trazas = inferir({"a"}, reglas_ciclicas)

        self.assertEqual(hechos_finales, {"a", "b"})
        self.assertEqual(trazas, ["R_ab: a => b"])

    def test_regla_no_se_dispara_si_falta_una_premisa(self) -> None:
        hechos = set(HECHOS_CASO_A)
        hechos.remove("danio_foliar_visible")

        hechos_finales, _trazas = inferir(hechos, self.reglas)

        self.assertNotIn("enfermedad_foliar_confirmada", hechos_finales)
        self.assertNotIn("tratamiento_planificado", hechos_finales)
        self.assertNotIn(OBJETIVO, hechos_finales)

    def test_falta_plan_disponible_corta_la_cadena(self) -> None:
        hechos = set(HECHOS_CASO_A)
        hechos.remove("plan_disponible")

        hechos_finales, trazas = inferir(hechos, self.reglas)

        self.assertIn("enfermedad_foliar_confirmada", hechos_finales)
        self.assertNotIn("tratamiento_planificado", hechos_finales)
        self.assertNotIn(OBJETIVO, hechos_finales)
        self.assertEqual([traza.split(":")[0] for traza in trazas], ["R1"])

    def test_orden_y_contenido_de_la_traza(self) -> None:
        _hechos_finales, trazas = inferir(set(HECHOS_CASO_A), self.reglas)

        self.assertEqual(
            [traza.split(":")[0] for traza in trazas],
            ["R1", "R4", "R5"],
        )
        self.assertEqual(
            trazas[2],
            "R5: plan_tres_acciones, tratamiento_planificado => manejo_inmediato",
        )

    def test_conclusion_duplicada_solo_se_registra_una_vez(self) -> None:
        reglas = [
            Regla("R_primera", frozenset({"a"}), "x"),
            Regla("R_segunda", frozenset({"b"}), "x"),
        ]

        hechos_finales, trazas = inferir({"a", "b"}, reglas)

        self.assertIn("x", hechos_finales)
        self.assertEqual(len(trazas), 1)
        self.assertEqual(trazas[0], "R_primera: a => x")

    def test_planta_sana_genera_monitoreo_preventivo(self) -> None:
        hechos_finales, trazas = inferir(
            {"categoria_sana", "confianza_alta"}, self.reglas
        )

        self.assertIn("monitoreo_preventivo", hechos_finales)
        self.assertNotIn(OBJETIVO, hechos_finales)
        self.assertEqual(trazas, ["R9: categoria_sana, confianza_alta => monitoreo_preventivo"])


def run() -> None:
    """Ejecuta la demostracion completa de la Semana 13."""

    print("=" * 70)
    print("SEMANA 13 - INGENIERIA DEL CONOCIMIENTO: MOTOR DE INFERENCIA")
    print("=" * 70)
    print("  Proyecto: deteccion de enfermedades en plantas (PlantAI)")
    print("  Dominio: triaje fitosanitario y decision de manejo")
    print("  Estrategia: encadenamiento hacia adelante (reglas de Horn)")

    reglas = construir_reglas()
    print(f"\nReglas cargadas: {len(reglas)}")
    print(f"Objetivo a demostrar: {OBJETIVO}")
    mostrar_reglas(reglas)

    caso_a, caso_b = ejecutar_casos(reglas)
    for caso in (caso_a, caso_b):
        print("\n" + renderizar_escenario(caso))

    print("\n" + "=" * 70)
    print("Semana 13 completada.")
    print("=" * 70)


def main() -> None:
    """Punto de entrada: demostracion, pruebas o generacion del reporte."""

    argumentos = sys.argv[1:]

    if "--reporte" in argumentos:
        ruta = generar_reporte()
        print(f"Reporte generado: {ruta.relative_to(RAIZ)}")
        return

    if "--pruebas" in argumentos:
        salida, exitoso = ejecutar_pruebas()
        print(salida.rstrip())
        raise SystemExit(0 if exitoso else 1)

    run()


if __name__ == "__main__":
    main()
