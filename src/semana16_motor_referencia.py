from __future__ import annotations

import io
import re
import sys
import unicodedata
import unittest
from datetime import date
from pathlib import Path
from tempfile import TemporaryDirectory

try:
    from src.semana15_base_conocimiento import RUTA_DB, conectar, inicializar
except ImportError:  # ejecucion directa: python src/semana16_motor_referencia.py
    from semana15_base_conocimiento import RUTA_DB, conectar, inicializar


RAIZ = Path(__file__).resolve().parent.parent
RUTA_REPORTE = RAIZ / "reports" / "reporte_semana16.md"

# Mensajes de abstencion: el motor nunca inventa una respuesta.
MSJ_SIN_DATOS = "Escribe una pregunta sobre el cuidado de tus plantas."
MSJ_SIN_REFERENCIA = (
    "No hay evidencia validada para esa pregunta; consulta con la persona "
    "responsable del cultivo."
)

# Palabras clave por articulo del repositorio de la semana 15. Ya estan
# normalizadas (minusculas y sin tildes), igual que las devuelve normalizar().
PALABRAS_CLAVE = {
    1: ["evidencia", "guardar", "panel", "captura"],
    2: ["septoria", "manchas", "fungicida", "tratamiento", "hojas"],
    3: ["categoria", "clase", "clasificacion", "taxonomia"],
    4: ["virus", "viral", "cura", "contencion", "vectores"],
    5: ["calidad", "dataset", "distribucion", "revision"],
}

# Escenarios de demostracion: (caso, descripcion, consulta).
ESCENARIOS = [
    ("A", "consulta cubierta por una referencia validada",
     "Cual es el tratamiento para las manchas?"),
    ("B", "consulta que solo coincide con un borrador",
     "Como es la calidad del dataset?"),
    ("C", "pregunta fuera del conocimiento disponible",
     "Cuanto cuesta el agua de riego?"),
    ("D", "consulta vacia",
     "   "),
    ("E", "consulta viral (solo contencion)",
     "Hay cura para el virus?"),
]

# Descripcion de la arquitectura: cada componente, su responsabilidad y como
# se relaciona con el siguiente. La usan la consola, el reporte y la web.
COMPONENTES = [
    {"nombre": "1. Interfaz",
     "responsabilidad": "Recibe la pregunta escrita por el usuario (consola o web).",
     "relacion": "Entrega el texto crudo al normalizador."},
    {"nombre": "2. Normalizador",
     "responsabilidad": "Convierte el texto a minusculas, quita tildes y extrae palabras unicas.",
     "relacion": "Entrega el conjunto de palabras al motor."},
    {"nombre": "3. Base de conocimiento",
     "responsabilidad": "Guarda las referencias con id, titulo, claves, respuesta, fuente y validacion (semana 15).",
     "relacion": "Provee los registros que consulta el motor."},
    {"nombre": "4. Motor de referencia",
     "responsabilidad": "Filtra los borradores, cuenta coincidencias y elige la mejor referencia.",
     "relacion": "Devuelve la referencia elegida al generador de respuestas."},
    {"nombre": "5. Generador de respuestas",
     "responsabilidad": "Arma el mensaje final con el id y la fuente; no crea texto nuevo.",
     "relacion": "Entrega la respuesta trazable a la interfaz."},
    {"nombre": "6. Control de calidad",
     "responsabilidad": "Pruebas unittest y escenarios que demuestran el comportamiento.",
     "relacion": "Verifica el resultado de los cinco componentes anteriores."},
]


# ---------------------------------------------------------------------------
# COMPONENTE 2. NORMALIZADOR DE TEXTO
# ---------------------------------------------------------------------------

def normalizar(texto: str) -> set[str]:
    """Convierte el texto en palabras minusculas, sin tildes y sin repetir."""

    descompuesto = unicodedata.normalize("NFD", texto.casefold())
    sin_tildes = "".join(
        caracter for caracter in descompuesto
        if unicodedata.category(caracter) != "Mn"
    )
    return set(re.findall(r"[a-z0-9]+", sin_tildes))


# ---------------------------------------------------------------------------
# COMPONENTE 3. BASE DE CONOCIMIENTO (referencias desde la semana 15)
# ---------------------------------------------------------------------------

def construir_base(ruta: Path | str = RUTA_DB) -> list[dict]:
    """Convierte los articulos de la semana 15 en referencias con validacion.

    Cada referencia tiene los seis campos que pide la practica; el articulo 5
    esta en BORRADOR y nace con `validada=False` (control negativo del motor).
    """

    inicializar(ruta)  # crea el repositorio si falta (idempotente)
    with conectar(ruta) as conexion:
        filas = conexion.execute(
            "SELECT id, titulo, contenido, fuente, estado "
            "FROM articulo ORDER BY id"
        ).fetchall()

    referencias = []
    for fila in filas:
        referencias.append({
            "id": f"REF-{fila['id']:03d}",
            "titulo": fila["titulo"],
            "claves": list(PALABRAS_CLAVE.get(fila["id"], [])),
            "respuesta": fila["contenido"],
            "fuente": fila["fuente"],
            "validada": fila["estado"] == "VALIDADO",
        })
    return referencias


# ---------------------------------------------------------------------------
# COMPONENTE 4. MOTOR DE REFERENCIA
# ---------------------------------------------------------------------------

def consultar(pregunta: str, referencias: list[dict] | None = None) -> dict:
    """Elige la referencia validada con mas coincidencias y da su fuente.

    Estados: ENCONTRADA, SIN_REFERENCIA (borradores o sin cobertura) y
    SIN_DATOS (sin palabras utiles). Desempate por id ascendente.
    """

    if referencias is None:
        referencias = construir_base()

    palabras = normalizar(pregunta)
    if not palabras:
        return {"estado": "SIN_DATOS", "mensaje": MSJ_SIN_DATOS,
                "referencia": None}

    candidatos = []
    for referencia in referencias:
        if not referencia["validada"]:
            continue  # filtro de seguridad: un borrador jamas responde
        coincidencias = palabras.intersection(referencia["claves"])
        if coincidencias:
            candidatos.append((len(coincidencias), referencia["id"], referencia))

    if not candidatos:
        return {"estado": "SIN_REFERENCIA", "mensaje": MSJ_SIN_REFERENCIA,
                "referencia": None}

    candidatos.sort(key=lambda item: (-item[0], item[1]))
    puntuacion, _, mejor = candidatos[0]
    return {
        "estado": "ENCONTRADA",
        "mensaje": mejor["respuesta"],
        "referencia": {
            "id": mejor["id"],
            "titulo": mejor["titulo"],
            "fuente": mejor["fuente"],
            "coincidencias": puntuacion,
        },
    }


# ---------------------------------------------------------------------------
# COMPONENTE 5. GENERADOR DE RESPUESTAS
# ---------------------------------------------------------------------------

def generar_respuesta(resultado: dict) -> str:
    """Arma el texto final con la respuesta, el id y la fuente."""

    referencia = resultado["referencia"]
    if resultado["estado"] != "ENCONTRADA" or referencia is None:
        return resultado["mensaje"]
    return (
        f"{resultado['mensaje']}\n"
        f"Fuente: [{referencia['id']}] {referencia['titulo']} - "
        f"{referencia['fuente']} (coincidencias: {referencia['coincidencias']})"
    )


def pregunta_desde_clase(clase: str) -> str:
    """Convierte la clase detectada (semana 02) en una pregunta para el motor."""

    return " ".join(clase.replace("_", " ").split())


# ---------------------------------------------------------------------------
# ESCENARIOS DE DEMOSTRACION
# ---------------------------------------------------------------------------

def ejecutar_caso(ruta: Path | str | None = None) -> dict:
    """Ejecuta los cinco escenarios sobre la base (real o temporal)."""

    base = construir_base(ruta) if ruta is not None else construir_base()
    resultados = []
    for nombre, descripcion, consulta in ESCENARIOS:
        resultado = consultar(consulta, base)
        resultados.append({
            "nombre": nombre,
            "descripcion": descripcion,
            "consulta": consulta,
            "estado": resultado["estado"],
            "mensaje": resultado["mensaje"],
            "referencia": resultado["referencia"],
            "respuesta": generar_respuesta(resultado),
        })
    return {"componentes": COMPONENTES, "base": base, "escenarios": resultados}


def renderizar_caso(caso: dict) -> str:
    """Convierte los escenarios en texto legible para consola y reporte."""

    lineas = [
        "=" * 70,
        "ESCENARIOS: el motor responde con referencias validadas o se abstiene",
        "=" * 70,
        "",
        "Arquitectura (que hace cada componente):",
    ]
    for componente in caso["componentes"]:
        lineas.append(f"   - {componente['nombre']}: {componente['responsabilidad']}")

    lineas += ["", "Base de conocimiento (construida desde la semana 15):"]
    for referencia in caso["base"]:
        estado = "VALIDADA" if referencia["validada"] else "BORRADOR (no responde)"
        lineas.append(f"   - {referencia['id']} [{estado}] {referencia['titulo']}")

    for escenario in caso["escenarios"]:
        respuesta = escenario["respuesta"].replace("\n", "\n              ")
        lineas += [
            "",
            f"Caso {escenario['nombre']} ({escenario['descripcion']}):",
            f"   Consulta : {escenario['consulta'].strip() or '(vacia)'}",
            f"   Estado   : {escenario['estado']}",
            f"   Respuesta: {respuesta}",
        ]
    return "\n".join(lineas)


# ---------------------------------------------------------------------------
# COMPONENTE 6. CONTROL DE CALIDAD (pruebas unittest)
# ---------------------------------------------------------------------------

class TestMotorReferencia(unittest.TestCase):
    """Prueba la base, el normalizador, el motor y la trazabilidad."""

    def setUp(self) -> None:
        # Base temporal: los datos reales del proyecto no se tocan.
        self.temporal = TemporaryDirectory()
        self.ruta = Path(self.temporal.name) / "prueba.db"
        self.base = construir_base(self.ruta)

    def tearDown(self) -> None:
        self.temporal.cleanup()

    def test_base_construida_desde_semana15(self):
        """La base conserva los 5 articulos de la semana 15 y su estado."""

        self.assertEqual([r["id"] for r in self.base],
                         ["REF-001", "REF-002", "REF-003", "REF-004", "REF-005"])
        borradores = [r["id"] for r in self.base if not r["validada"]]
        self.assertEqual(borradores, ["REF-005"])  # el articulo 5 es BORRADOR

    def test_normalizacion_mayusculas_y_tildes(self):
        """Mayusculas, tildes y signos no deben impedir la coincidencia."""

        palabras = normalizar("MANCHAS en las hojas")
        self.assertEqual(palabras, {"manchas", "en", "las", "hojas"})
        self.assertIn("taxonomia", normalizar("TAXONOMÍA"))

    def test_consulta_con_referencia_validada(self):
        """Una consulta cubierta devuelve ENCONTRADA y la referencia correcta."""

        resultado = consultar("Cual es el tratamiento para las manchas?", self.base)
        self.assertEqual(resultado["estado"], "ENCONTRADA")
        self.assertEqual(resultado["referencia"]["id"], "REF-002")

    def test_ignora_referencia_no_validada(self):
        """El borrador coincide con la consulta, pero nunca responde."""

        resultado = consultar("Como es la calidad del dataset?", self.base)
        self.assertEqual(resultado["estado"], "SIN_REFERENCIA")
        self.assertIsNone(resultado["referencia"])

    def test_no_inventa_respuestas(self):
        """Una pregunta fuera del conocimiento se abstiene."""

        resultado = consultar("Cuanto cuesta el agua de riego?", self.base)
        self.assertEqual(resultado["estado"], "SIN_REFERENCIA")
        self.assertIsNone(resultado["referencia"])

    def test_consulta_vacia_pide_pregunta(self):
        """Sin palabras utiles el motor pide una consulta."""

        resultado = consultar("   ", self.base)
        self.assertEqual(resultado["estado"], "SIN_DATOS")

    def test_respuesta_con_fuente_identificable(self):
        """La respuesta proviene del registro y viaja con id y fuente."""

        resultado = consultar("Hay cura para el virus?", self.base)
        self.assertEqual(resultado["estado"], "ENCONTRADA")
        referencia = resultado["referencia"]
        registro = next(r for r in self.base if r["id"] == referencia["id"])
        self.assertEqual(resultado["mensaje"], registro["respuesta"])
        self.assertTrue(registro["validada"])
        self.assertTrue(referencia["id"] and referencia["fuente"])

    def test_pregunta_desde_clase_diagnostico(self):
        """La clase detectada en la web llega al motor y encuentra fuente."""

        pregunta = pregunta_desde_clase("Tomato___Septoria_leaf_spot")
        resultado = consultar(pregunta, self.base)
        self.assertEqual(resultado["estado"], "ENCONTRADA")
        self.assertEqual(resultado["referencia"]["id"], "REF-002")


def ejecutar_pruebas() -> tuple[str, bool]:
    """Ejecuta las pruebas unittest del modulo y captura su salida real."""

    suite = unittest.defaultTestLoader.loadTestsFromTestCase(TestMotorReferencia)
    flujo = io.StringIO()
    resultado = unittest.TextTestRunner(stream=flujo, verbosity=2).run(suite)
    return flujo.getvalue(), resultado.wasSuccessful()


# ---------------------------------------------------------------------------
# REPORTE Y CONSOLA
# ---------------------------------------------------------------------------

def generar_reporte(ruta: Path | None = None) -> Path:
    """Ejecuta el escenario y las pruebas, y escribe el reporte Markdown."""

    caso = ejecutar_caso()
    salida_pruebas, pruebas_ok = ejecutar_pruebas()

    destino = ruta or RUTA_REPORTE
    destino.parent.mkdir(parents=True, exist_ok=True)

    estado_pruebas = ("OK: las ocho pruebas pasaron." if pruebas_ok
                      else "FALLO: alguna prueba no paso.")

    filas_componentes = "\n".join(
        f"| {c['nombre']} | {c['responsabilidad']} | {c['relacion']} |"
        for c in caso["componentes"]
    )
    filas_base = "\n".join(
        f"| {r['id']} | {r['titulo']} | {', '.join(r['claves'])} "
        f"| {'si' if r['validada'] else 'NO (borrador)'} | {r['fuente']} |"
        for r in caso["base"]
    )
    filas_escenarios = "\n".join(
        f"| {e['nombre']} | {e['consulta'].strip() or '(vacia)'} "
        f"| {e['estado']} | {e['referencia']['id'] if e['referencia'] else '-'} |"
        for e in caso["escenarios"]
    )

    contenido = f"""# Semana 16 - Motor de referencia (arquitectura de sistemas inteligentes)

**Proyecto:** PlantAI - Deteccion de enfermedades en plantas con Inteligencia Artificial  
**Modulo:** `src/semana16_motor_referencia.py`  
**Reporte generado:** {date.today().isoformat()}  
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
{filas_componentes}

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
{filas_base}

## 3. Escenarios probados

| Caso | Consulta | Estado | Referencia |
|---|---|---|---|
{filas_escenarios}

El motor **no inventa respuestas**: el caso B coincide con un borrador y el
caso C esta fuera del conocimiento; en ambos el estado es `SIN_REFERENCIA`. La
puntuacion de coincidencias es un conteo de palabras en comun, no una
probabilidad ni un porcentaje de confianza.

## 4. Ejecucion de la demostracion

```text
{renderizar_caso(caso)}
```

## 5. Resultado de las pruebas unittest

```text
python -m unittest src.semana16_motor_referencia -v
```

Salida real capturada por el generador del reporte:

```text
{salida_pruebas.rstrip()}
```

Estado: **{estado_pruebas}**

## 6. Integracion con el proyecto

- La base de conocimiento es la de la **semana 15**: el motor solo agrega la
  busqueda y la recuperacion con trazabilidad (id + fuente).
- En la web (`index.html` + `server.py`), la pestana **Semana 16 - Motor de
  referencia** muestra la arquitectura, los escenarios y la base; al
  diagnosticar una imagen, la clase detectada (semana 02) se convierte en
  pregunta con `pregunta_desde_clase()` y el tab muestra la referencia
  validada que la soporta, o la abstencion si no hay evidencia.
"""
    destino.write_text(contenido, encoding="utf-8")
    return destino


def interfaz_consola() -> None:
    """COMPONENTE 1. Interfaz: lee preguntas por consola y responde con fuente."""

    print("Motor de referencia PlantAI (escribe 'salir' para terminar)")
    print("Preguntas de ejemplo: tratamiento para las manchas, cura para el")
    print("virus, calidad del dataset, agua de riego.")
    base = construir_base()
    while True:
        try:
            pregunta = input("\nTu pregunta: ").strip()
        except (EOFError, KeyboardInterrupt):
            break
        if pregunta.casefold() == "salir":
            break
        resultado = consultar(pregunta, base)
        print("Estado:", resultado["estado"])
        print(generar_respuesta(resultado))
    print("\nSesion terminada.")


def run() -> None:
    """Ejecuta la demostracion completa de la Semana 16."""

    print("=" * 70)
    print("SEMANA 16 - DISENO DE SISTEMAS INTELIGENTES: MOTOR DE REFERENCIA")
    print("=" * 70)
    print("  Proyecto: deteccion de enfermedades en plantas (PlantAI)")
    print("  Dominio: preguntas sobre el cuidado de las plantas, respondidas")
    print("           solo con referencias validadas (base de la semana 15)")

    caso = ejecutar_caso()
    print("\n" + renderizar_caso(caso))

    print("\n" + "=" * 70)
    print("Control de calidad (pruebas unittest):")
    salida, exitoso = ejecutar_pruebas()
    print(salida.rstrip())
    print("=" * 70)
    print("Semana 16 completada." + ("" if exitoso else " (HAY PRUEBAS FALLIDAS)"))
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

    if "--consola" in argumentos:
        interfaz_consola()
        return

    run()


if __name__ == "__main__":
    main()
