import heapq

from src.semana03_taxonomia import classify_class

DEFAULT_CLASS = "Tomato___Late_blight"
META = "healthy"
ESTADO_INICIAL = "enfermedad_avanzada"

H = {
    "healthy": 0,
    "en_recuperacion": 2,
    "enfermedad_activa": 4,
    "enfermedad_avanzada": 6,
}

TRATAMIENTOS = {
    "Enfermedades fungicas": {
        "enfermedad_avanzada": [
            ("podar_rama_afectada", "enfermedad_activa", 3),
            ("aplicar_fungicida_fuerte", "en_recuperacion", 6),
        ],
        "enfermedad_activa": [
            ("aplicar_fungicida", "en_recuperacion", 2),
        ],
        "en_recuperacion": [
            ("aplicar_fungicida", META, 3),
            ("seguimiento_semanal", META, 4),
        ],
    },
    "Plagas": {
        "enfermedad_avanzada": [
            ("podar_rama_afectada", "enfermedad_activa", 3),
            ("aplicar_acaricida", "en_recuperacion", 4),
        ],
        "enfermedad_activa": [
            ("aplicar_acaricida", "en_recuperacion", 2),
        ],
        "en_recuperacion": [
            ("repetir_acaricida", META, 2),
            ("seguimiento_semanal", META, 4),
        ],
    },
    "Enfermedades bacterianas": {
        "enfermedad_avanzada": [
            ("podar_rama_afectada", "enfermedad_activa", 3),
            ("aplicar_bactericida", "en_recuperacion", 6),
        ],
        "enfermedad_activa": [
            ("aplicar_bactericida", "en_recuperacion", 2),
        ],
        "en_recuperacion": [
            ("repetir_bactericida", META, 3),
        ],
    },
    "Enfermedades virales": {
        "enfermedad_avanzada": [
            ("podar_ramas_sintomaticas", "enfermedad_activa", 2),
        ],
        "enfermedad_activa": [
            ("manejo_integrado", "en_recuperacion", 3),
        ],
        "en_recuperacion": [
            ("seguimiento_y_aislamiento", "en_recuperacion", 2),
        ],
    },
    "Sin clasificar": {
        "enfermedad_avanzada": [
            ("poda_y_tratamiento_general", "enfermedad_activa", 3),
            ("tratamiento_generico", "en_recuperacion", 7),
        ],
        "enfermedad_activa": [
            ("tratamiento_generico", "en_recuperacion", 3),
        ],
        "en_recuperacion": [
            ("tratamiento_generico", META, 4),
        ],
    },
}


def astar(grafo, inicio):
    frontier = [(H[inicio], inicio)]
    cost = {inicio: 0}
    came_from = {inicio: None}
    expanded = 0

    while frontier:
        _, current = heapq.heappop(frontier)
        if current == META:
            break
        expanded += 1

        for accion, nxt, step in grafo.get(current, []):
            nuevo = cost[current] + step
            if nxt not in cost or nuevo < cost[nxt]:
                cost[nxt] = nuevo
                came_from[nxt] = (current, accion, step)
                heapq.heappush(frontier, (nuevo + H[nxt], nxt))

    if META not in came_from:
        return None, expanded, cost

    pasos = []
    current = META
    while came_from[current] is not None:
        origen, accion, step = came_from[current]
        pasos.append((origen, accion, step, current))
        current = origen
    pasos.reverse()

    return pasos, expanded, cost


def show_tratamientos(grafo):
    print(f"\n  {'Estado actual':20s} {'Tratamiento (accion)':30s} {'Estado siguiente':18s} {'Costo'}")
    print("  " + "-" * 85)
    for estado, acciones in grafo.items():
        for accion, nxt, step in acciones:
            print(f"  {estado:20s} {accion:30s} {nxt:18s} {step}")


def diagnose_recovery(class_name):
    category = classify_class(class_name)

    if category == "Plantas sanas":
        return None, 0, 0, category

    grafo = TRATAMIENTOS.get(category, TRATAMIENTOS["Sin clasificar"])
    plan, expanded, cost = astar(grafo, ESTADO_INICIAL)
    total = cost.get(META, 0)

    return plan, total, expanded, category


def run():
    print("=" * 70)
    print("SEMANA 04 - BUSQUEDA EN ESPACIO DE ESTADOS: PLAN DE RECUPERACION")
    print("=" * 70)

    class_name = DEFAULT_CLASS
    category = classify_class(class_name)
    print(f"\nDiagnostico de ejemplo (salida del clasificador): {class_name}")
    print(f"Categoria (semana 03): {category}")

    if category == "Plantas sanas":
        print("\nLa planta esta sana: la meta ya esta alcanzada.")
        print("Plan de recuperacion: vacio (costo 0).")
        print("\n" + "=" * 70)
        print("Semana 04 completada.")
        print("=" * 70)
        return

    grafo = TRATAMIENTOS.get(category, TRATAMIENTOS["Sin clasificar"])

    print("\n--- Modelo: estados de salud y tratamientos aplicables ---")
    print("  Estados: enfermedad_avanzada, enfermedad_activa, en_recuperacion, healthy (meta)")
    show_tratamientos(grafo)

    plan, expanded, cost = astar(grafo, ESTADO_INICIAL)

    if plan is None:
        print("\n--- Resultado de A* ---")
        print("  Meta inalcanzable: en este modelo no hay transiciones hacia 'healthy'.")
        print("  Es el caso de las enfermedades virales: no existe cura agronomica total;")
        print("  el plan disponible es de contencion (poda de ramas sintomaticas, manejo")
        print("  integrado, aislamiento), no de recuperacion.")
        print(f"  Nodos expandidos: {expanded}")
        print("\n" + "=" * 70)
        print("Semana 04 completada.")
        print("=" * 70)
        return

    print("\n--- Recorrido encontrado por A* ---")
    print(f"  {ESTADO_INICIAL:22s} g=0  h={H[ESTADO_INICIAL]}  f={H[ESTADO_INICIAL]}")
    for origen, accion, step, nxt in plan:
        g = cost[nxt]
        print(f"  {origen:22s} --{accion} (+{step})--> {nxt:18s} g={g}  h={H[nxt]}  f={g + H[nxt]}")

    print("\n--- Plan optimo de recuperacion ---")
    for i, (origen, accion, step, nxt) in enumerate(plan, start=1):
        print(f"  {i}. {accion} ............ +{step}")
    print(f"  Costo total: {cost[META]}")
    print(f"  Nodos expandidos: {expanded}")

    print("\n--- Formulacion del problema ---")
    print("  Estado inicial: enfermedad detectada por el clasificador (" + category + ")")
    print("  Estados posibles: enfermedad_avanzada, enfermedad_activa, en_recuperacion, healthy")
    print("  Acciones/operadores: tratamientos del modelo para la categoria detectada")
    print("  Transiciones: aplicar (accion, costo) transforma el estado al siguiente")
    print("  Meta: alcanzar el estado 'healthy'")
    print("  Costo de camino g(n): esfuerzo acumulado de los tratamientos aplicados")
    print("  Heuristica h(n): estimacion optimista del esfuerzo restante hasta la meta (admisible)")
    print("  Criterio de seleccion: A* expande por f(n) = g(n) + h(n), garantizando el menor costo")

    print("\n--- Limitaciones del modelo ---")
    print("  - El grafo de estados y los costos son un modelo didactico definido a mano,")
    print("    no mediciones reales de campo ni de ensayos agronomicos.")
    print("  - La recuperacion real depende de la especie, el clima, la dosis y la") 
    print("    respuesta de cada planta.")
    print("  - A* planifica la accion de apoyo post-diagnostico; la deteccion de la")
    print("    enfermedad es responsabilidad del clasificador de la semana 02.")

    print("\n" + "=" * 70)
    print("Semana 04 completada.")
    print("=" * 70)


if __name__ == "__main__":
    run()