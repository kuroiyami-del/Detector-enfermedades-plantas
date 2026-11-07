# Semana 14 - Ingenieria del conocimiento: red semantica de la taxonomia PlantAI.
# Convierte oraciones en triples, guarda esas relaciones en un grafo y responde
# consultas distinguiendo hechos explicitos de inferidos. Solo biblioteca estandar.

import re
import sys
import unicodedata
from datetime import date
from pathlib import Path


RAIZ = Path(__file__).resolve().parent.parent
RUTA_REPORTE = RAIZ / "reports" / "reporte_semana14.md"

# Consulta objetivo: hecho que la red concluye sin tener arista directa.
ORIGEN_OBJETIVO = "septoria"
DESTINO_OBJETIVO = "estado_fitosanitario"

# Oracion fuera del parser: debe producir ValueError, nunca un triple.
EJEMPLO_RECHAZADO = "La minadora invade rapidamente el cultivo."

# Unicas relaciones que admite el modelo.
RELACIONES = ("es_un", "necesita")


# Pasa a minusculas y quita tildes: "Septoria" pasa a ser "septoria".
def normalizar(texto: str) -> str:
    base = unicodedata.normalize("NFD", texto.casefold().strip())
    return "".join(c for c in base if unicodedata.category(c) != "Mn")


# Convierte una oracion "X es Y" o "X necesita Y" en triple; rechaza lo demas.
def interpretar(oracion: str) -> tuple[str, str, str]:
    texto = normalizar(oracion).strip(" .!?")
    patrones = [
        (r"(?:un|una|el|la) (\w+) es (?:un|una) (\w+)", "es_un"),
        (r"(?:un|una|el|la) (\w+) necesita (\w+)", "necesita"),
    ]
    for patron, relacion in patrones:
        parejas = re.fullmatch(patron, texto)
        if parejas:
            sujeto, objeto = parejas.groups()
            return sujeto, relacion, objeto
    raise ValueError("Oracion fuera de los patrones admitidos")


# Texto legible de un hecho: "septoria --es_un--> enfermedad_fungica".
def triple_texto(sujeto: str, relacion: str, objeto: str) -> str:
    return f"{sujeto} --{relacion}--> {objeto}"


# Guarda una arista en la red sin duplicados; solo admite las relaciones de
# RELACIONES y levanta ValueError si llega otra.
def agregar(red: dict, sujeto: str, relacion: str, objeto: str) -> None:
    if relacion not in RELACIONES:
        raise ValueError("Relacion no admitida")
    vecinos = red.setdefault(normalizar(sujeto), [])
    destino = (relacion, normalizar(objeto))
    if destino not in vecinos:
        vecinos.append(destino)


# Construye la red desde oraciones y anota las que el parser rechazo.
def crear_red(oraciones: list[str]) -> tuple[dict, list[str]]:
    red: dict = {}
    rechazadas: list[str] = []
    for oracion in oraciones:
        try:
            sujeto, relacion, objeto = interpretar(oracion)
        except ValueError:
            rechazadas.append(oracion)
            continue
        agregar(red, sujeto, relacion, objeto)
    return red, rechazadas


# Recorre las aristas "es_un" en anchura y devuelve la ruta mas corta;
# None si el destino no se alcanza desde el origen.
def camino(red: dict, origen: str, destino: str) -> list[str] | None:
    inicio = normalizar(origen)
    meta = normalizar(destino)
    pendientes: list[list[str]] = [[inicio]]
    visitados: set[str] = {inicio}
    while pendientes:
        ruta = pendientes.pop(0)
        actual = ruta[-1]
        if actual == meta:
            return ruta
        for relacion, vecino in red.get(actual, []):
            if relacion == "es_un" and vecino not in visitados:
                visitados.add(vecino)
                pendientes.append(ruta + [vecino])
    return None


# Reune los hechos de la red, ordenados y en formato legible.
def triples_de(red: dict) -> list[dict]:
    hechos = [
        {"sujeto": sujeto, "relacion": relacion, "objeto": destino,
         "texto": triple_texto(sujeto, relacion, destino)}
        for sujeto, vecinos in red.items()
        for relacion, destino in vecinos
    ]
    return sorted(hechos, key=lambda t: (t["sujeto"], t["relacion"], t["objeto"]))


# Recorre los ancestros "es_un" de un concepto y junta sus "necesita":
# devuelve (valores, ancestros).
def necesidades(red: dict, concepto: str) -> tuple[list[str], list[str]]:
    pendientes: list[str] = [normalizar(concepto)]
    visitados: set[str] = set()
    valores: set[str] = set()
    ancestros: set[str] = set()
    while pendientes:
        actual = pendientes.pop()
        if actual in visitados:
            continue
        visitados.add(actual)
        for relacion, destino in red.get(actual, []):
            if relacion == "es_un":
                pendientes.append(destino)
            elif relacion == "necesita":
                valores.add(destino)
                if actual != normalizar(concepto):
                    ancestros.add(actual)
    return sorted(valores), sorted(ancestros)


# Responde si "origen" es un "destino"; con la ruta como evidencia.
def consultar_es_un(red: dict, origen: str, destino: str) -> dict:
    ruta = camino(red, origen, destino)
    if ruta is None:
        texto = ("NO DEMOSTRADA: no hay ruta es_un en la red "
                 "(False no prueba falsedad universal).")
    elif len(ruta) > 1:
        texto = "DEMOSTRADA por transitividad: " + " --es_un--> ".join(ruta)
    else:
        texto = f"DEMOSTRADA como hecho directo: {ruta[0]}."
    return {
        "pregunta": f"¿{origen} es_un {destino}?",
        "tipo": "es_un",
        "origen": origen,
        "destino": destino,
        "respuesta": ruta is not None,
        "inferido": ruta is not None and len(ruta) > 1,
        "ruta": ruta,
        "valor_por_ancestro": None,
        "resultado": texto,
    }


# Responde que necesita "origen": separa lo propio de lo heredado por es_un.
def consultar_necesidades(red: dict, origen: str) -> dict:
    valores, ancestros = necesidades(red, origen)
    propias = {destino for relacion, destino in red.get(origen, [])
               if relacion == "necesita"}
    por_ancestro = {
        ancestro: [d for r, d in red.get(ancestro, [])
                   if r == "necesita" and d in valores]
        for ancestro in ancestros
    }

    if not valores:
        mensaje = "sin necesidades registradas"
    elif not ancestros:
        mensaje = f"propias del nodo: {', '.join(valores)}"
    else:
        mensaje = f"heredadas de {', '.join(ancestros)}: {', '.join(valores)}"

    return {
        "pregunta": f"¿Que necesita {origen}?",
        "tipo": "necesidades",
        "origen": origen,
        "destino": None,
        "respuesta": valores,
        "inferido": bool(set(valores) - propias),
        "ruta": None,
        "valor_por_ancestro": por_ancestro or None,
        "resultado": f"Respuesta {mensaje} (regla didactica de herencia).",
    }


# Elige la consulta a ejecutar segun el "tipo" registrado en el dict.
def ejecutar_consulta(red: dict, consulta: dict) -> dict:
    if consulta["tipo"] == "es_un":
        return consultar_es_un(red, consulta["origen"], consulta["destino"])
    if consulta["tipo"] == "necesidades":
        return consultar_necesidades(red, consulta["origen"])
    raise ValueError(f"Consulta no admitida: {consulta['tipo']}")


# Carga oraciones en una red nueva y responde las consultas del caso.
def ejecutar_escenario(nombre: str, descripcion: str, oraciones: list[str],
                       consultas: list[dict]) -> dict:
    red, rechazadas = crear_red(oraciones)
    return {
        "nombre": nombre,
        "descripcion": descripcion,
        "hechos": triples_de(red),
        "consultas": [ejecutar_consulta(red, c) for c in consultas],
        "rechazadas": rechazadas,
    }


# Oraciones del dominio PlantAI: jerarquia de la semana 03 y
# propiedades de manejo que se heredan.
ORACIONES_BASE = [
    "Una septoria es una enfermedad_fungica.",
    "Un tizon_bacteriano es una enfermedad_bacteriana.",
    "Un mosaico es una enfermedad_viral.",
    "Una minadora es una plaga.",
    "Una enfermedad_fungica es un problema_foliar.",
    "Una enfermedad_bacteriana es un problema_foliar.",
    "Una enfermedad_viral es un problema_foliar.",
    "Una plaga es un problema_foliar.",
    "Un problema_foliar es un estado_fitosanitario.",
    "Una hoja_sana es un estado_fitosanitario.",
    "Un problema_foliar necesita tratamiento.",
    "Un problema_foliar necesita inspeccion.",
    "Una hoja_sana necesita monitoreo.",
]

# Cinco consultas sobre la red: dos por transitividad (una sin evidencia),
# una correcta por dos saltos y dos de herencia de necesidades.
CONSULTAS_CASO_A = [
    {"tipo": "es_un", "origen": ORIGEN_OBJETIVO, "destino": DESTINO_OBJETIVO},
    {"tipo": "es_un", "origen": "septoria", "destino": "hoja_sana"},
    {"tipo": "es_un", "origen": "mosaico", "destino": "problema_foliar"},
    {"tipo": "necesidades", "origen": "septoria"},
    {"tipo": "necesidades", "origen": "hoja_sana"},
]


# Ejecuta el escenario A con la taxonomia completa del proyecto.
def ejecutar_caso() -> dict:
    return ejecutar_escenario(
        "A", "taxonomia PlantAI completa: septoria como estado fitosanitario",
        ORACIONES_BASE, CONSULTAS_CASO_A)


# Convierte un escenario en texto legible para consola y reporte.
def renderizar(escenario: dict) -> str:
    lineas = [
        "=" * 70,
        f"ESCENARIO {escenario['nombre']}: {escenario['descripcion']}",
        "=" * 70,
        f"Hechos registrados ({len(escenario['hechos'])}):",
    ]
    lineas += [f"  {t['texto']}" for t in escenario["hechos"]]

    if escenario["rechazadas"]:
        lineas.append(f"\nOraciones rechazadas ({len(escenario['rechazadas'])}):")
        lineas += [f"  - {r}" for r in escenario["rechazadas"]]

    lineas.append(f"\nConsultas ({len(escenario['consultas'])}):")
    for numero, consulta in enumerate(escenario["consultas"], start=1):
        linea = f"  {numero}. {consulta['pregunta']} -> {consulta['respuesta']}"
        lineas.append(linea)
        if consulta["ruta"]:
            lineas.append(f"      ruta: {' -> '.join(consulta['ruta'])}")
        if consulta["valor_por_ancestro"]:
            for ancestro, valores in consulta["valor_por_ancestro"].items():
                detalle = f"{', '.join(valores)}"
                lineas.append(f"      heredado de {ancestro}: {detalle}")
    return "\n".join(lineas)


# Ejecuta el escenario y escribe el reporte Markdown en reports/.
def generar_reporte(ruta: Path | None = None) -> Path:
    caso = ejecutar_caso()
    destino = ruta or RUTA_REPORTE
    destino.parent.mkdir(parents=True, exist_ok=True)

    def tabla(triples: list[dict]) -> str:
        lineas = ["| Sujeto | Relación | Objeto |", "|---|---|---|"]
        lineas += [f"| `{t['sujeto']}` | `{t['relacion']}` "
                   f"| `{t['objeto']}` |" for t in triples]
        return "\n".join(lineas)

    contenido = f"""# Semana 14 - Ingenieria del conocimiento: redes semanticas

**Proyecto:** PlantAI - Deteccion de enfermedades en plantas
**Modulo:** `src/semana14_redes_semanticas.py`
**Reporte generado:** {date.today().isoformat()}
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

{tabla(list(caso['hechos']))}

La oracion `{EJEMPLO_RECHAZADO}` no calza con ningun patron: se rechaza
(`ValueError`), demostrando el limite del analizador.

## 4. Escenarios

### Escenario A (taxonomia completa)

```text
{renderizar(caso)}
```

## 5. Conclusiones

- El objetivo `{ORIGEN_OBJETIVO} es_un {DESTINO_OBJETIVO}` se
  demuestra por **transitividad** con la ruta de 4 nodos
  `septoria -> enfermedad_fungica -> problema_foliar ->
  estado_fitosanitario`; la arista directa NO esta almacenada. Las
  necesidades (`inspeccion`, `tratamiento`) se **heredan** de
  `problema_foliar`.

## 6. Limitaciones

- Parser de dos patrones: no resuelve plural, negacion ni ambiguedad.
- Conceptos de una palabra (`\\w+`): por eso se usa guion bajo.
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
"""

    destino.write_text(contenido, encoding="utf-8")
    return destino


# Muestra en consola la red, el escenario y sus inferencias.
def run() -> None:
    print("=" * 70)
    print("SEMANA 14 - INGENIERIA DEL CONOCIMIENTO: REDES SEMANTICAS")
    print("=" * 70)
    print("  Proyecto: deteccion de enfermedades en plantas (PlantAI)")
    print("  Dominio: taxonomia fitosanitaria (semana 03) como red semantica")

    caso = ejecutar_caso()
    print(f"\nHechos registrados: {len(caso['hechos'])}")
    print(f"Objetivo: {ORIGEN_OBJETIVO} es_un {DESTINO_OBJETIVO}")
    print("\nBase de conocimiento:")
    print("\n".join(f"  {t['texto']}" for t in caso["hechos"]))

    print("\n" + renderizar(caso))
    print("\n" + "=" * 70)
    print("Semana 14 completada.")
    print("=" * 70)


# Punto de entrada: generacion del reporte con --reporte y demo sin argumentos.
def main() -> None:
    if "--reporte" in sys.argv[1:]:
        ruta = generar_reporte()
        print(f"Reporte generado: {ruta.relative_to(RAIZ)}")
        return
    run()


if __name__ == "__main__":
    main()
