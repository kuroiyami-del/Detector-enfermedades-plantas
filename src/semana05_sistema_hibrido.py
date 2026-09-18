import re
import unicodedata

from src.semana03_taxonomia import DISEASE_CATEGORIES
from src.semana04_busqueda import (
    ESTADO_INICIAL,
    H,
    META,
    TRATAMIENTOS,
    astar,
)

LEXICON = {
    "Enfermedades fungicas": [
        "mancha", "manchas", "moho", "oxido", "mildiu", "podredumbre",
        "pudricion", "hongos", "fungicida", "rust", "blight", "scab",
        "mildew", "mold", "spot", "rot", "esca", "measles", "leaf scorch",
    ],
    "Enfermedades bacterianas": [
        "bacteriana", "bacterianas", "bactericida", "acuosa", "acuosas",
        "exudado", "halo", "bacterial",
    ],
    "Enfermedades virales": [
        "viral", "virales", "mosaico", "amarillamiento", "enrollamiento",
        "enanismo", "virus", "greening",
    ],
    "Plagas": [
        "plaga", "plagas", "insecto", "insectos", "acaro", "acaros",
        "pulgon", "pulgones", "oruga", "orugas", "mosca blanca",
        "minador", "minadores", "telarana", "mites", "spider mites",
    ],
    "Plantas sanas": [
        "sana", "sano", "sanas", "sanos", "verde", "verdes", "sin manchas",
        "sin sintomas", "crecimiento normal", "healthy",
    ],
}

ASTAR_TERMS = {
    "plan", "planificar", "planes", "ruta", "rutas", "camino", "caminos",
    "recorrido", "recuperacion", "curar", "tratamiento", "tratamientos",
    "optimizar", "optimo", "optima", "costo", "costos", "busqueda",
    "navegacion", "grafo", "nodo", "nodos", "heuristica", "distancia",
    "enfermedad avanzada", "enfermedad activa", "en recuperacion",
}

CASOS_RUTAS = {
    "recuperacion": {
        "id": "recuperacion",
        "titulo": "Ruta optima de recuperacion de la planta",
        "detalle": (
            "A* recorre el grafo de estados de salud (enfermedad_avanzada -> enfermedad_activa "
            "-> en_recuperacion -> healthy) y calcula la secuencia de tratamientos de menor costo."
        ),
    },
    "viral_contencion": {
        "id": "viral_contencion",
        "titulo": "Ruta de contencion (enfermedades virales)",
        "detalle": (
            "Para virales no existe transicion hacia 'healthy' (meta inalcanzable); A* calcula "
            "la ruta de contencion de menor costo (poda, manejo integrado, aislamiento)."
        ),
    },
    "sana": {
        "id": "sana",
        "titulo": "Planta sana: ruta vacia",
        "detalle": "Si la meta (healthy) ya esta alcanzada, A* no recorre nada: plan vacio y costo 0.",
    },
    "navegacion": {
        "id": "navegacion",
        "titulo": "Calculo de rutas de navegacion (mapas / GPS)",
        "detalle": (
            "A* es el algoritmo clasico para hallar el camino de menor costo entre dos puntos de "
            "un mapa (calles, caminos, terrenos) usando una heuristica como la distancia."
        ),
    },
    "logistica": {
        "id": "logistica",
        "titulo": "Optimizacion de rutas de distribucion (logistica)",
        "detalle": (
            "A* elige la ruta mas barata para un vehiculo o mensajero entre un origen y un destino "
            "cuando el costo por tramo (tiempo, combustible, distancia) esta definido."
        ),
    },
    "pathfinding": {
        "id": "pathfinding",
        "titulo": "Pathfinding en mapas/rejillas (robots, drones, videojuegos)",
        "detalle": (
            "En grids y grafos ponderados A* guia al agente evitando obstaculos y minimizando el "
            "costo del desplazamiento."
        ),
    },
}

EXPLICACION_ASTAR = (
    "A* (A-estrella) es un algoritmo de busqueda informada en grafos: expande nodos segun "
    "f(n) = g(n) + h(n), donde g(n) es el costo acumulado desde el inicio y h(n) una "
    "heuristica admisible (que nunca sobrestima) del costo restante hasta la meta. Gracias a "
    "ello garantiza encontrar la ruta (camino) de costo minimo, por lo que es la opcion natural "
    "para el calculo o planificacion de rutas/caminos cuando el problema se modela como un grafo "
    "ponderado con estado inicial, estado meta, transiciones con costo y una heuristica valida."
)

SOLUCION_POR_CATEGORIA = {
    "Enfermedades fungicas": (
        "Aplicar fungicida (fuerte si el estado es avanzado), podar las ramas afectadas y "
        "mejorar la ventilacion y el drenaje. Hacer seguimiento semanal hasta confirmar la "
        "recuperacion."
    ),
    "Enfermedades bacterianas": (
        "Aplicar bactericida, erradicar parcialmente el tejido afectado y controlar el riego "
        "para evitar el exceso de humedad en el cultivo."
    ),
    "Enfermedades virales": (
        "No existe cura quimica total: erradicar las plantas infectadas, controlar los vectores "
        "(pulgones, mosca blanca) y aplicar manejo integrado (poda de ramas sintomaticas, "
        "seguimiento y aislamiento)."
    ),
    "Plagas": (
        "Aplicar acaricida o insecticida segun la plaga detectada, instalar trampas pegajosas y "
        "favorecer el control biologico con depredadores naturales."
    ),
    "Plantas sanas": (
        "No requiere tratamiento: mantener riego adecuado, nutricion balanceada y monitoreo "
        "regular del cultivo."
    ),
    "Sin clasificar": (
        "No se pudo asociar la consulta a una categoria de la base de conocimiento (semanas "
        "03/04). Describa los sintomas con mayor detalle o suba una foto para el diagnostico "
        "por imagen."
    ),
}

DEFAULT_CONSULTAS = [
    "Las hojas de mi tomate tienen manchas marrones y algo de moho. Quiero el plan de recuperacion.",
    "Veo insectos verdes pequenos en el enves de las hojas. Cual es el mejor recorrido de tratamiento?",
    "Las hojas se ponen amarillas con patron de mosaico. Necesito la ruta optima de tratamientos.",
    "Necesito la ruta mas corta entre dos puntos del cultivo conociendo el costo de cada tramo.",
    "Mis plantas estan sanas, sin manchas y con las hojas verdes.",
]


def normalize(text: str) -> str:
    text = text.strip().lower()
    text = unicodedata.normalize("NFD", text)
    text = "".join(ch for ch in text if unicodedata.category(ch) != "Mn")
    text = re.sub(r"[^a-z0-9 ]+", " ", text)
    return re.sub(r"\s+", " ", text).strip()


def _candidatos(q: str) -> list:
    tokens = [t for t in q.split() if t]
    candidatos = list(tokens)
    candidatos += [f"{tokens[i]} {tokens[i + 1]}" for i in range(len(tokens) - 1)]
    return candidatos


def extraer_palabras_clave(consulta: str) -> dict:
    q = normalize(consulta)
    encontradas = {}
    for termino in _candidatos(q):
        if termino in ASTAR_TERMS:
            encontradas.setdefault(termino, "A*/rutas")
            continue
        for concepto, palabras in LEXICON.items():
            if termino in palabras:
                encontradas.setdefault(termino, concepto)
    return encontradas


FUERTES_ENFERMEDAD = {
    "Enfermedades fungicas": (
        "moho", "oxido", "mildiu", "podredumbre", "pudricion", "hongos", "fungicida",
    ),
    "Enfermedades bacterianas": (
        "bactericida", "bacteriana", "bacterianas", "exudado", "halo", "acuosas",
    ),
    "Enfermedades virales": (
        "mosaico", "enrollamiento", "enanismo", "virus", "greening", "amarillamiento",
    ),
    "Plagas": (
        "insecto", "insectos", "acaro", "acaros", "pulgon", "pulgones", "oruga",
        "orugas", "mosca blanca", "minador", "minadores", "telarana", "plaga", "plagas",
    ),
}

SALUD_FUERTE = (
    "sanas", "sano", "sanos", "sin manchas", "sin sintomas", "sin signos",
    "crecimiento normal", "perfecta", "perfecto",
)

NOMBRES_ENFERMEDAD = tuple(FUERTES_ENFERMEDAD.keys())


def categoria_por_reglas(consulta: str, reglas: list) -> str | None:
    q = normalize(consulta)
    for cat in DISEASE_CATEGORIES:
        for kw in cat.keywords:
            if normalize(kw) in q:
                return cat.name
    for nombre in NOMBRES_ENFERMEDAD:
        for term in FUERTES_ENFERMEDAD[nombre]:
            if term in q:
                return nombre
    if "Plantas sanas" in reglas and any(t in q for t in SALUD_FUERTE):
        return "Plantas sanas"
    for nombre in (*NOMBRES_ENFERMEDAD, "Plantas sanas"):
        if nombre in reglas:
            return nombre
    return None


def determinar_aplicabilidad(consulta, categoria, reglas, intencion_ruta):
    casos = []
    razones = []
    ids = set()

    if categoria and categoria in TRATAMIENTOS:
        if categoria == "Enfermedades virales":
            caso = CASOS_RUTAS["viral_contencion"]
            razones.append(
                f"Activo la regla '{categoria}' (semana 03). Su grafo de la semana 04 no contiene "
                "transiciones hacia 'healthy', asi que A* aplica para hallar la ruta de contencion "
                "de menor costo (la meta de curacion es inalcanzable)."
            )
        else:
            caso = CASOS_RUTAS["recuperacion"]
            razones.append(
                f"Activo la regla '{categoria}' (semana 03). La semana 04 define su grafo de "
                "tratamientos (TRATAMIENTOS) y una heuristica H, por lo que A* aplica para calcular "
                "la ruta de recuperacion de menor costo."
            )
        casos.append(caso)
        ids.add(caso["id"])
    elif categoria == "Plantas sanas":
        casos.append(CASOS_RUTAS["sana"])
        ids.add("sana")
        razones.append(
            "Activo la regla 'Plantas sanas': la meta 'healthy' ya esta alcanzada, la ruta A* es "
            "vacia (costo 0) y no hay recorrido que calcular."
        )
    else:
        razones.append(
            "No se activo ninguna categoria de la base de conocimiento de las semanas 03/04."
        )

    if intencion_ruta:
        for key in ("navegacion", "logistica", "pathfinding"):
            caso = CASOS_RUTAS[key]
            if caso["id"] not in ids:
                casos.append(caso)
                ids.add(caso["id"])
        razones.append(
            "La consulta menciona conceptos de ruta/camino/recorrido/costo, dominio clasico de A* "
            "en el calculo de rutas o caminos sobre grafos ponderados."
        )

    aplica = any(
        cid in ("recuperacion", "viral_contencion", "navegacion", "logistica", "pathfinding")
        for cid in ids
    )

    if not reglas and not intencion_ruta:
        razones.append(
            "La consulta no contiene palabras clave del dominio; no puede determinarse si A* aplica."
        )
        aplica = False

    return aplica, casos, razones


def calcular_ruta(categoria: str | None) -> dict | None:
    if categoria is None or categoria not in TRATAMIENTOS:
        return None
    grafo = TRATAMIENTOS.get(categoria, TRATAMIENTOS["Sin clasificar"])
    plan, expanded, cost = astar(grafo, ESTADO_INICIAL)
    return {
        "categoria": categoria,
        "grafo": grafo,
        "plan": plan,
        "expanded": expanded,
        "total": cost.get(META, 0),
        "meta": META,
    }


def answer(consulta: str) -> dict:
    q = normalize(consulta)
    palabras = extraer_palabras_clave(consulta)
    reglas = list(dict.fromkeys(palabras.values()))

    categoria = categoria_por_reglas(consulta, reglas)
    intencion_ruta = any(t in ASTAR_TERMS for t in _candidatos(q))

    aplica, casos, razones = determinar_aplicabilidad(consulta, categoria, reglas, intencion_ruta)
    ruta = calcular_ruta(categoria)

    explicacion = EXPLICACION_ASTAR
    if categoria and categoria in TRATAMIENTOS:
        explicacion += (
            "\nEn este proyecto la semana 04 modela la recuperacion como un problema de busqueda "
            "de rutas: estados = estados de salud, acciones = tratamientos con costo, meta = "
            f"'healthy' y heuristica h(n) = {H}. A continuacion se muestra la ruta que A* elige "
            "buscando el minimo costo."
        )
    elif categoria == "Plantas sanas":
        explicacion += "\nPara una planta sana el plan es vacio: la meta ya esta alcanzada."
    elif intencion_ruta:
        explicacion += (
            "\nEn general, A* calcula la ruta de menor costo entre dos nodos cuando el problema se "
            "modela como grafo ponderado; es el algoritmo estandar para la planificacion de rutas."
        )
    else:
        explicacion += (
            "\nLa consulta no activo reglas del dominio: describa sintomas de la planta o un "
            "problema de rutas/caminos para que el sistema evalue si A* aplica."
        )

    return {
        "consulta": consulta,
        "palabras_clave": list(palabras.keys()),
        "keywords_por_concepto": palabras,
        "reglas": reglas,
        "categoria": categoria,
        "intencion_ruta": intencion_ruta,
        "aplica_astar": aplica,
        "casos": casos,
        "razones": razones,
        "explicacion": explicacion,
        "ruta": ruta,
        "solucion": SOLUCION_POR_CATEGORIA.get(categoria or "Sin clasificar"),
    }


def show_ruta(ruta: dict) -> None:
    if ruta is None:
        return
    plan = ruta["plan"]
    if plan is None:
        print("  Ruta A*: meta 'healthy' inalcanzable (caso viral); solo existe plan de contencion.")
        return
    for origen, accion, step, nxt in plan:
        print(f"    {origen:24s} --{accion:26s} (+{step})--> {nxt}")
    print(f"    Costo total: {ruta['total']}   Nodos expandidos: {ruta['expanded']}")


def run():
    print("=" * 68)
    print("SEMANA 05 - SISTEMA HIBRIDO: APLICABILIDAD DE A* (RUTAS/CAMINOS)")
    print("=" * 68)
    print("Fuentes utilizadas:")
    print("  - Semana 03 (semana03_taxonomia.py): DISEASE_CATEGORIES, clasificacion por palabras clave")
    print("  - Semana 04 (semana04_busqueda.py) : TRATAMIENTOS (grafo), H (heuristica), astar()")
    print()

    for i, q in enumerate(DEFAULT_CONSULTAS, start=1):
        r = answer(q)
        print(f"CONSULTA {i}: {r['consulta']}")
        print(f"  Palabras clave extraidas : {', '.join(r['palabras_clave']) or 'ninguna'}")
        print(f"  Reglas activadas         : {', '.join(r['reglas']) or 'ninguna'}")
        print(f"  Categoria (semana 03)    : {r['categoria'] or 'sin clasificar'}")
        print(f"  Intencion de ruta        : {'SI' if r['intencion_ruta'] else 'no'}")
        print(f"  Aplica A*                : {'SI' if r['aplica_astar'] else 'NO'}")
        if r["casos"]:
            print("  Casos de uso (rutas/caminos):")
            for caso in r["casos"]:
                print(f"    - {caso['titulo']}")
        print(f"  Razon: {' '.join(r['razones'])}")
        if r["ruta"]:
            print("  Ruta A* calculada:")
            show_ruta(r["ruta"])
        print("  Explicacion:")
        print("   " + r["explicacion"].replace("\n", "\n   "))
        print()

    print("=" * 68)
    print(f"Consultas procesadas: {len(DEFAULT_CONSULTAS)}")
    print("=" * 68)


if __name__ == "__main__":
    run()