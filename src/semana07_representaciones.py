from src.semana04_busqueda import TRATAMIENTOS, META, ESTADO_INICIAL, astar


# Convierte el grafo de tratamientos de la semana 04 en un automata.
# Devuelve un diccionario (estado, accion) -> estado siguiente.
def construir_dfa(categoria):
    transiciones = {}
    if categoria == "Plantas sanas":
        return transiciones
    for estado, acciones in TRATAMIENTOS[categoria].items():
        for accion, siguiente, costo in acciones:
            transiciones[(estado, accion)] = siguiente
    return transiciones


# Ejecuta el automata sobre una secuencia de tratamientos.
# Acepta si termina en healthy; devuelve aceptado, estado final y pasos.
def validar_secuencia(categoria, acciones):
    transiciones = construir_dfa(categoria)
    estado = META if categoria == "Plantas sanas" else ESTADO_INICIAL
    pasos = []
    for accion in acciones:
        anterior = estado
        if (estado, accion) not in transiciones:
            pasos.append((anterior, accion, "NO PERMITIDA"))
            return False, estado, pasos
        estado = transiciones[(estado, accion)]
        pasos.append((anterior, accion, estado))
    return estado == META, estado, pasos


# Muestra el automata y valida secuencias: plan de A*, rechazos, viral y sana.
def run():
    print("=" * 70)
    print("SEMANA 07 - REPRESENTACION DEL CONOCIMIENTO: AUTOMATA")
    print("=" * 70)

    categoria = "Enfermedades fungicas"

    print("\n--- 1. Definicion del automata (se construye desde la semana 04) ---")
    print("  Estados: enfermedad_avanzada, enfermedad_activa, en_recuperacion, healthy")
    print("  Simbolos: tratamientos  |  Estado inicial: enfermedad_avanzada  |  Meta: healthy")
    transiciones = construir_dfa(categoria)
    for (estado, accion), siguiente in sorted(transiciones.items()):
        print(f"    {estado:22s} --{accion:25s}--> {siguiente}")

    print("\n--- 2. El plan de A* (semana 04) es aceptado por el automata ---")
    plan, expanded, cost = astar(TRATAMIENTOS[categoria], ESTADO_INICIAL)
    total = cost[META]
    acciones = [accion for _, accion, _, _ in plan]
    aceptado, estado_final, pasos = validar_secuencia(categoria, acciones)
    for origen, accion, siguiente in pasos:
        print(f"    {origen:22s} --{accion:25s}--> {siguiente}")
    print(f"  Estado final: {estado_final}  |  Aceptada: {aceptado}  (costo del plan: {total})")

    print("\n--- 3. Secuencias rechazadas (casos didacticos) ---")
    for acciones in (["aplicar_fungicida"],
                     ["podar_rama_afectada"],
                     ["podar_rama_afectada", "podar_rama_afectada"]):
        aceptado, estado_final, pasos = validar_secuencia(categoria, acciones)
        print(f"    {str(acciones):55s} estado final: {estado_final:20s} aceptada: {aceptado}")

    print("\n--- 4. Enfermedades virales: meta inalcanzable (igual que A*) ---")
    acciones = ["podar_ramas_sintomaticas", "manejo_integrado",
                "seguimiento_y_aislamiento", "seguimiento_y_aislamiento"]
    aceptado, estado_final, pasos = validar_secuencia("Enfermedades virales", acciones)
    for origen, accion, siguiente in pasos:
        print(f"    {origen:22s} --{accion:25s}--> {siguiente}")
    print("  El automata nunca llega a healthy: coincide con la meta inalcanzable de A*.")

    print("\n--- 5. Planta sana: secuencia vacia aceptada ---")
    aceptado, estado_final, pasos = validar_secuencia("Plantas sanas", [])
    print(f"    Secuencia vacia -> estado {estado_final}  |  Aceptada: {aceptado}")
    aceptado, estado_final, pasos = validar_secuencia("Plantas sanas", ["aplicar_fungicida"])
    print(f"    Tratar una planta sana -> {estado_final}  |  Aceptada: {aceptado}")

    print("\n--- Conclusion ---")
    print("  A* (semana 04) busca la mejor secuencia de tratamientos.")
    print("  El automata (semana 07) representa el conocimiento de cuando")
    print("  una secuencia es valida y termina en la meta (healthy).")

    print("\n" + "=" * 70)
    print("Semana 07 completada.")
    print("=" * 70)


if __name__ == "__main__":
    run()