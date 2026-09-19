import numpy as np
from PIL import Image

from src.semana04_busqueda import TRATAMIENTOS, META, ESTADO_INICIAL, astar


# Vector de referencia de una hoja sana: (verdor, amarillez, proporcion de manchas).
HOJA_SANA = np.array([0.85, 0.10, 0.05])


# Convierte una imagen RGB 64x64 en el vector (verdor, amarillez, manchas).
# El vector real de la hoja se compara en la parte numerica de la semana 07.
def extraer_vector_hoja(image_path):
    img = np.asarray(Image.open(image_path).convert("RGB").resize((64, 64)),
                     dtype=float)
    suma = img.sum(axis=2) + 1e-6
    verdor = float(np.mean(img[..., 1] / suma))
    amarillez = float(np.mean(np.clip((img[..., 0] - img[..., 2]) / suma, 0, None)))
    manchas = float(np.std(img.mean(axis=2)) / 255.0)
    return [round(verdor, 3), round(amarillez, 3), round(manchas, 3)]


# Distancia euclidiana del vector de una hoja al vector de la hoja sana.
# A mayor distancia, mayor sospecha de enfermedad (representacion numerica).
def distancia_hoja_sana(vector):
    return float(np.linalg.norm(np.asarray(vector, dtype=float) - HOJA_SANA))


# Muestra la representacion numerica de una hoja: vector y distancia a sana.
def mostrar_vector(vector):
    redondo = [round(v, 3) for v in vector]
    print(f"  Vector de la hoja (verdor, amarillez, manchas): {redondo}")
    print(f"  Distancia a hoja sana (euclidiana): {distancia_hoja_sana(vector):.3f}")


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
    print("SEMANA 07 - REPRESENTACIONES DEL CONOCIMIENTO")
    print("=" * 70)

    print("\n--- 1. Representacion numerica: una hoja como vector de numeros ---")
    print("  Hoja sana de referencia (verdor, amarillez, manchas):",
          [float(round(v, 3)) for v in HOJA_SANA])
    print("  Ejemplo hipotetico de hoja enferma:")
    mostrar_vector([0.45, 0.55, 0.70])

    categoria = "Enfermedades fungicas"

    print("\n--- 2. Representacion simbolica (hechos y reglas de la semana 05) ---")
    hechos = {"manchas_presentes", "moho_visible", "hojas_amarillas"}
    reglas = [
        ({"manchas_presentes", "moho_visible"}, "sospecha_fungica"),
        ({"patron_mosaico", "hojas_amarillas"}, "sospecha_viral"),
        ({"insectos_visibles"}, "sospecha_plaga"),
    ]
    conclusion = "sin clasificar"
    print(f"  Hechos: {sorted(hechos)}")
    for condiciones, resultado in reglas:
        if condiciones.issubset(hechos):
            conclusion = resultado
            break
    print(f"  Reglas evaluadas: {[r[1] for r in reglas]}")
    print(f"  Conclusion simbolica: {conclusion}")

    print("\n--- 3. Definicion del automata (se construye desde la semana 04) ---")
    print("  Estados: enfermedad_avanzada, enfermedad_activa, en_recuperacion, healthy")
    print("  Simbolos: tratamientos  |  Estado inicial: enfermedad_avanzada  |  Meta: healthy")
    transiciones = construir_dfa(categoria)
    for (estado, accion), siguiente in sorted(transiciones.items()):
        print(f"    {estado:22s} --{accion:25s}--> {siguiente}")

    print("\n--- 4. El plan de A* (semana 04) es aceptado por el automata ---")
    plan, expanded, cost = astar(TRATAMIENTOS[categoria], ESTADO_INICIAL)
    total = cost[META]
    acciones = [accion for _, accion, _, _ in plan]
    aceptado, estado_final, pasos = validar_secuencia(categoria, acciones)
    for origen, accion, siguiente in pasos:
        print(f"    {origen:22s} --{accion:25s}--> {siguiente}")
    print(f"  Estado final: {estado_final}  |  Aceptada: {aceptado}  (costo del plan: {total})")

    print("\n--- 5. Secuencias rechazadas (casos didacticos) ---")
    for acciones in (["aplicar_fungicida"],
                     ["podar_rama_afectada"],
                     ["podar_rama_afectada", "podar_rama_afectada"]):
        aceptado, estado_final, pasos = validar_secuencia(categoria, acciones)
        print(f"    {str(acciones):55s} estado final: {estado_final:20s} aceptada: {aceptado}")

    print("\n--- 6. Enfermedades virales: meta inalcanzable (igual que A*) ---")
    acciones = ["podar_ramas_sintomaticas", "manejo_integrado",
                "seguimiento_y_aislamiento", "seguimiento_y_aislamiento"]
    aceptado, estado_final, pasos = validar_secuencia("Enfermedades virales", acciones)
    for origen, accion, siguiente in pasos:
        print(f"    {origen:22s} --{accion:25s}--> {siguiente}")
    print("  El automata nunca llega a healthy: coincide con la meta inalcanzable de A*.")

    print("\n--- 7. Planta sana: secuencia vacia aceptada ---")
    aceptado, estado_final, pasos = validar_secuencia("Plantas sanas", [])
    print(f"    Secuencia vacia -> estado {estado_final}  |  Aceptada: {aceptado}")
    aceptado, estado_final, pasos = validar_secuencia("Plantas sanas", ["aplicar_fungicida"])
    print(f"    Tratar una planta sana -> {estado_final}  |  Aceptada: {aceptado}")

    print("\n--- Conclusion ---")
    print("  La hoja se representa de 3 formas complementarias:")
    print("   - Numerica: distancia a la hoja sana (semana 07).")
    print("   - Simbolica: hechos + reglas concluyen sospecha (semana 05).")
    print("   - Automata: valida que una secuencia de tratamientos")
    print("     (semana 04) termina en la meta healthy.")

    print("\n" + "=" * 70)
    print("Semana 07 completada.")
    print("=" * 70)


if __name__ == "__main__":
    run()