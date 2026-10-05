import numpy as np
from PIL import Image

from src.semana04_busqueda import TRATAMIENTOS, META, ESTADO_INICIAL, astar


# ---------------------------------------------------------------------------
# DATOS DE REFERENCIA DEL DOMINIO
# Son los datos que alimentan las tres representaciones del conocimiento.
# ---------------------------------------------------------------------------

# Vector de una hoja sana de referencia: (verdor, amarillez, proporcion de manchas).
# Es el punto de comparacion de la representacion numerica.
VECTOR_HOJA_SANA = np.array([0.85, 0.10, 0.05])

# Categoria usada en las demostraciones de esta semana.
CATEGORIA_DEMO = "Enfermedades fungicas"

# Vector hipotetico de una hoja enferma, para ilustrar la comparacion numerica.
VECTOR_HOJA_ENFERMA_EJEMPLO = [0.45, 0.55, 0.70]

# Secuencias mal formadas que el automata debe rechazar (casos didacticos).
SECUENCIAS_RECHAZADAS = [
    ["aplicar_fungicida"],
    ["podar_rama_afectada"],
    ["podar_rama_afectada", "podar_rama_afectada"],
]

# Contencion de una enfermedad viral. Se repite la accion de seguimiento a
# proposito para comprobar que el automata nunca llega a la meta 'healthy'.
SECUENCIA_VIRAL = [
    "podar_ramas_sintomaticas",
    "manejo_integrado",
    "seguimiento_y_aislamiento",
    "seguimiento_y_aislamiento",
]


# ---------------------------------------------------------------------------
# 1. REPRESENTACION NUMERICA
# La hoja se describe con numeros: un vector (verdor, amarillez, manchas) y su
# distancia euclidiana al vector de una hoja sana.
# ---------------------------------------------------------------------------

# Convierte una imagen RGB 64x64 en el vector (verdor, amarillez, manchas).
# Cada componente resume una caracteristica observable de la hoja.
def extraer_vector_hoja(image_path):
    img = np.asarray(Image.open(image_path).convert("RGB").resize((64, 64)),
                     dtype=float)
    suma = img.sum(axis=2) + 1e-6
    verdor = float(np.mean(img[..., 1] / suma))
    amarillez = float(np.mean(np.clip((img[..., 0] - img[..., 2]) / suma, 0, None)))
    manchas = float(np.std(img.mean(axis=2)) / 255.0)
    return [round(verdor, 3), round(amarillez, 3), round(manchas, 3)]


# Distancia euclidiana del vector de una hoja al vector de la hoja sana:
#   distancia = raiz( (v1 - s1)^2 + (v2 - s2)^2 + (v3 - s3)^2 )
# Distancia pequena -> hoja parecida a la sana -> menor sospecha de enfermedad.
# Distancia grande   -> hoja distinta de la sana  -> mayor sospecha de enfermedad.
def distancia_hoja_sana(vector):
    return float(np.linalg.norm(np.asarray(vector, dtype=float) - VECTOR_HOJA_SANA))


# Muestra la representacion numerica de una hoja: su vector y su distancia a sana.
def mostrar_vector_hoja(vector):
    print(f"  Vector de la hoja (verdor, amarillez, manchas): "
          f"{[round(valor, 3) for valor in vector]}")
    print(f"  Distancia a hoja sana (euclidiana): {distancia_hoja_sana(vector):.3f}")


# ---------------------------------------------------------------------------
# 2. REPRESENTACION SIMBOLICA
# La hoja tambien se describe con simbolos: hechos (sintomas observados) y reglas
# SI -> ENTONCES que los combinan para concluir una sospecha.
# El proceso completo es:  HECHOS -> REGLAS -> CONCLUSION
# ---------------------------------------------------------------------------

# Sintomas observados en una hoja, expresados como hechos (etiquetas) del
# dominio real del proyecto (deteccion de enfermedades en plantas).
HECHOS_POR_CATEGORIA = {
    "Enfermedades fungicas": {
        "esporas_en_borde", "manchas_concentricas", "marchitamiento_localizado",
    },
    "Enfermedades bacterianas": {
        "manchas_angulares", "halo_amarillento", "exudado_acuoso",
    },
    "Enfermedades virales": {
        "patron_mosaico", "enrollamiento_hoja", "enanismo_planta",
    },
    "Plagas": {
        "telarana_fina", "punteado_clorotico", "mordeduras_visibles",
    },
    "Plantas sanas": {
        "follaje_uniforme", "sin_signos_de_dano",
    },
}

# Reglas simbolicas: SI (conjunto de condiciones) ENTONCES conclusion.
REGLAS_SIMBOLICAS = [
    ({"esporas_en_borde", "manchas_concetricas"}, "sospecha_fungica"),
    ({"manchas_angulares", "halo_amarillento", "exudado_acuoso"},
     "sospecha_bacteriana"),
    ({"patron_mosaico", "enrollamiento_hoja"}, "sospecha_viral"),
    ({"telarana_fina", "punteado_clorotico"}, "sospecha_acaros"),
    ({"follaje_uniforme", "sin_signos_de_dano"}, "planta_sana"),
]

# Conclusion que se obtiene cuando ninguna regla se cumple.
SIN_CONCLUIR = "sin_concluir"

# Traduccion de cada conclusion simbolica a lenguaje natural.
SIGNIFICADO_CONCLUSION = {
    "sospecha_fungica":    "Enfermedad fungica",
    "sospecha_bacteriana": "Enfermedad bacteriana",
    "sospecha_viral":      "Enfermedad viral",
    "sospecha_acaros":     "Plaga de acaros",
    "planta_sana":         "Planta sana",
    "sin_concluir":        "Sospecha no concluyente",
}


# Evalua los hechos observados contra las reglas SI -> ENTONCES.
# Una regla se aplica cuando todos sus sintomas estan presentes (issubset).
# Gana la primera regla que se cumple; si ninguna, la Conclusion es sin_concluir.
def aplicar_reglas(hechos):
    reglas_evaluadas = []
    conclusion = SIN_CONCLUIR
    for condiciones, resultado in REGLAS_SIMBOLICAS:
        aplica = condiciones.issubset(hechos)
        reglas_evaluadas.append((condiciones, resultado, aplica))
        if aplica and conclusion == SIN_CONCLUIR:
            conclusion = resultado
    return reglas_evaluadas, conclusion


# HECHOS -> REGLAS -> CONCLUSION para una categoria de planta.
# Devuelve los hechos, cada regla evaluada (aplicada o no), la conclusion

def representacion_simbolica(categoria):
    hechos = HECHOS_POR_CATEGORIA.get(categoria, set())
    reglas, conclusion = aplicar_reglas(hechos)
    return {
        "categoria": categoria,
        "hechos": sorted(hechos),
        "reglas": reglas,
        "conclusion": conclusion,
        "significado": SIGNIFICADO_CONCLUSION.get(conclusion, conclusion),
    }


# Muestra el proceso simbolico: hechos, cada regla aplicada o no, y conclusion.
def mostrar_representacion_simbolica(info):
    print(f"  Categoria: {info['categoria']}")
    print(f"  Hechos observados: {info['hechos']}")
    for condiciones, resultado, aplica in info["reglas"]:
        estado = "APLICADA" if aplica else "no aplicada"
        print(f"    SI {sorted(condiciones)} ENTONCES {resultado:<20s} [{estado}]")
    print(f"  Conclusion simbolica: {info['conclusion']} ({info['significado']})")


# ---------------------------------------------------------------------------
# 3. AUTOMATA FINITO DETERMINISTA (DFA)
# El autómata se construye con el grafo de tratamientos de la semana 04.
# Su regla fundamental es:  estado actual + accion = estado siguiente
# ---------------------------------------------------------------------------

# Crea la tabla de transiciones del DFA para una categoria de planta.
# La clave es (estado actual, accion) y el valor es el estado siguiente.
def crear_transiciones_dfa(categoria):
    transiciones = {}
    if categoria == "Plantas sanas":
        # Una planta sana no admite tratamientos: el automata se queda sin
        # transiciones, y por eso su unica secuencia valida es la vacia.
        return transiciones
    for estado, acciones in TRATAMIENTOS[categoria].items():
        for accion, siguiente, _costo in acciones:
            transiciones[(estado, accion)] = siguiente
    return transiciones


# Ejecuta el automata sobre una secuencia de tratamientos.
# Proceso: estado inicial -> leer accion -> buscar transicion -> cambiar estado.
# Si una accion no tiene transicion valida, la secuencia se rechaza.
# Se acepta solo si el automata termina en la meta 'healthy'.
# Devuelve (aceptado, estado final, pasos).
def validar_secuencia(categoria, acciones):
    transiciones = crear_transiciones_dfa(categoria)
    # En una planta sana el estado inicial ya es la meta 'healthy'.
    # En una planta enferma se parte de 'enfermedad_avanzada'.
    estado = META if categoria == "Plantas sanas" else ESTADO_INICIAL
    pasos = []
    for accion in acciones:
        estado_anterior = estado
        if (estado, accion) not in transiciones:
            pasos.append((estado_anterior, accion, "NO PERMITIDA"))
            return False, estado, pasos
        estado = transiciones[(estado, accion)]
        pasos.append((estado_anterior, accion, estado))
    return estado == META, estado, pasos


# ---------------------------------------------------------------------------
# 4. DEMOSTRACIONES
# Cada funcion muestra una parte del dominio y deja ver:
# que datos entran, que proceso se realiza y que resultado se obtiene.
# ---------------------------------------------------------------------------

# Imprime un recorrido del automata: estado --accion--> estado siguiente.
def mostrar_pasos(pasos):
    for estado, accion, siguiente in pasos:
        print(f"    {estado:22s} --{accion:25s}--> {siguiente}")


# Imprime la tabla de transiciones del automata.
def mostrar_transiciones(transiciones):
    for (estado, accion), siguiente in sorted(transiciones.items()):
        print(f"    {estado:22s} --{accion:25s}--> {siguiente}")


# Seccion 1: la hoja como vector de numeros y su distancia a la hoja sana.
def demostrar_representacion_numerica():
    print("\n--- 1. Representacion numerica: una hoja como vector de numeros ---")
    print("  Hoja sana de referencia (verdor, amarillez, manchas):",
          [float(round(valor, 3)) for valor in VECTOR_HOJA_SANA])
    print("  Ejemplo hipotetico de hoja enferma:")
    mostrar_vector_hoja(VECTOR_HOJA_ENFERMA_EJEMPLO)


# Seccion 2: los hechos de la categoria pasan por las reglas y dan una conclusion.
def demostrar_representacion_simbolica():
    print("\n--- 2. Representacion simbolica (hechos y reglas de la semana 05) ---")
    mostrar_representacion_simbolica(representacion_simbolica(CATEGORIA_DEMO))


# Seccion 3: tabla de transiciones del automata construida desde la semana 04.
def demostrar_definicion_del_automata():
    print("\n--- 3. Definicion del automata (se construye desde la semana 04) ---")
    print("  Estados: enfermedad_avanzada, enfermedad_activa, en_recuperacion, healthy")
    print("  Simbolos: tratamientos  |  Estado inicial: enfermedad_avanzada  |  Meta: healthy")
    transiciones = crear_transiciones_dfa(CATEGORIA_DEMO)
    mostrar_transiciones(transiciones)


# Seccion 4: el plan optimo que produce A* es una secuencia que el DFA acepta.
def demostrar_plan_de_astar_aceptado():
    print("\n--- 4. El plan de A* (semana 04) es aceptado por el automata ---")
    # A* planifica sobre el mismo grafo de tratamientos y devuelve sus acciones.
    plan, _expandidos, costo = astar(TRATAMIENTOS[CATEGORIA_DEMO], ESTADO_INICIAL)
    total = costo[META]
    acciones = [accion for _origen, accion, _costo, _siguiente in plan]
    # El plan se convierte en una secuencia y se valida en el automata.
    aceptado, estado_final, pasos = validar_secuencia(CATEGORIA_DEMO, acciones)
    mostrar_pasos(pasos)
    print(f"  Estado final: {estado_final}  |  Aceptada: {aceptado}  (costo del plan: {total})")


# Seccion 5: secuencias mal formadas que el automata debe rechazar.
def demostrar_secuencias_rechazadas():
    print("\n--- 5. Secuencias rechazadas (casos didacticos) ---")
    for acciones in SECUENCIAS_RECHAZADAS:
        aceptado, estado_final, _pasos = validar_secuencia(CATEGORIA_DEMO, acciones)
        print(f"    {str(acciones):55s} estado final: {estado_final:20s} "
              f"aceptada: {aceptado}")


# Seccion 6: en enfermedades virales la meta 'healthy' es inalcanzable,
# igual que en la busqueda A* de la semana 04.
def demostrar_enfermedades_virales():
    print("\n--- 6. Enfermedades virales: meta inalcanzable (igual que A*) ---")
    _aceptado, _estado_final, pasos = validar_secuencia(
        "Enfermedades virales", SECUENCIA_VIRAL)
    mostrar_pasos(pasos)
    print("  El automata nunca llega a healthy: coincide con la meta inalcanzable de A*.")


# Seccion 7: una planta sana ya esta en la meta, asi que su unica secuencia
# valida es la vacia; tratar una planta sana no es una transicion permitida.
def demostrar_planta_sana():
    print("\n--- 7. Planta sana: secuencia vacia aceptada ---")
    aceptado, estado_final, _pasos = validar_secuencia("Plantas sanas", [])
    print(f"    Secuencia vacia -> estado {estado_final}  |  Aceptada: {aceptado}")
    aceptado, estado_final, _pasos = validar_secuencia(
        "Plantas sanas", ["aplicar_fungicida"])
    print(f"    Tratar una planta sana -> {estado_final}  |  Aceptada: {aceptado}")


# Cierre: las tres representaciones son complementarias.
def mostrar_conclusion():
    print("\n--- Conclusion ---")
    print("  La hoja se representa de 3 formas complementarias:")
    print("   - Numerica: distancia a la hoja sana (semana 07).")
    print("   - Simbolica: hechos + reglas concluyen sospecha (semana 05).")
    print("   - Automata: valida que una secuencia de tratamientos")
    print("     (semana 04) termina en la meta healthy.")


def run():
    print("=" * 70)
    print("SEMANA 07 - REPRESENTACIONES DEL CONOCIMIENTO")
    print("=" * 70)

    demostrar_representacion_numerica()
    demostrar_representacion_simbolica()
    demostrar_definicion_del_automata()
    demostrar_plan_de_astar_aceptado()
    demostrar_secuencias_rechazadas()
    demostrar_enfermedades_virales()
    demostrar_planta_sana()
    mostrar_conclusion()

    print("\n" + "=" * 70)
    print("Semana 07 completada.")
    print("=" * 70)


if __name__ == "__main__":
    run()