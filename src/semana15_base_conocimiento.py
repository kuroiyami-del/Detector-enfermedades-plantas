
from __future__ import annotations

import io
import sqlite3
import sys
import unittest
from contextlib import contextmanager
from datetime import date
from pathlib import Path
from tempfile import TemporaryDirectory
from typing import Iterator


RAIZ = Path(__file__).resolve().parent.parent
RUTA_ESQUEMA = RAIZ / "sql" / "esquema.sql"
RUTA_DATOS = RAIZ / "sql" / "datos.sql"
RUTA_DB = RAIZ / "artifacts" / "conocimiento.db"
RUTA_REPORTE = RAIZ / "reports" / "reporte_semana15.md"

# Dominio donde vive el conocimiento que corresponde a cada categoria
# taxonomica de la semana 03. Permite responder con articulos validados
# a partir del diagnostico ya realizado.
DOMINIO_POR_CATEGORIA = {
    "Enfermedades fungicas": "Manejo fitosanitario",
    "Enfermedades bacterianas": "Manejo fitosanitario",
    "Enfermedades virales": "Manejo fitosanitario",
    "Plagas": "Manejo fitosanitario",
    "Plantas sanas": "Diagnostico foliar",
}

# Dominio que se consulta en el escenario de demostracion.
DOMINIO_CASO = "Manejo fitosanitario"

# Titulo del articulo que registra el escenario de demostracion.
TITULO_CASO = "Protocolo de manejo de mosaico en tomate"


# ---------------------------------------------------------------------------
# ACCESO A LA BASE DE DATOS
# ---------------------------------------------------------------------------

@contextmanager
def conectar(ruta: Path | str = RUTA_DB) -> Iterator[sqlite3.Connection]:
    """Abre una conexion SQLite con las claves foraneas activadas.

    Se usa como gestor de contexto: confirma al salir sin error, revierte
    ante un fallo y siempre cierra la conexion. `PRAGMA foreign_keys = ON`
    debe activarse en **cada** conexion; ponerlo solo en el `.sql` no
    garantiza que las demas lo respeten.
    """

    ruta = Path(ruta)
    ruta.parent.mkdir(parents=True, exist_ok=True)
    conexion = sqlite3.connect(ruta)
    conexion.row_factory = sqlite3.Row
    conexion.execute("PRAGMA foreign_keys = ON")
    try:
        yield conexion
        conexion.commit()
    except Exception:
        conexion.rollback()
        raise
    finally:
        conexion.close()


def inicializar(ruta: Path | str = RUTA_DB) -> None:
    """Crea las tablas y carga los datos de ejemplo.

    Es idempotente: `CREATE TABLE IF NOT EXISTS` e `INSERT OR IGNORE`
    permiten ejecutarla varias veces sin duplicar informacion.
    """

    with conectar(ruta) as conexion:
        conexion.executescript(RUTA_ESQUEMA.read_text(encoding="utf-8"))
        conexion.executescript(RUTA_DATOS.read_text(encoding="utf-8"))


# ---------------------------------------------------------------------------
# CONSULTA DEL CONOCIMIENTO PUBLICADO
# ---------------------------------------------------------------------------

def buscar_articulos(dominio: str, ruta: Path | str = RUTA_DB) -> list[dict]:
    """Devuelve los articulos **validados** de un dominio, con su contexto.

    - `JOIN` para lo obligatorio (dominio y experto responsable).
    - `LEFT JOIN` para lo opcional (aplicacion y herramienta): un articulo
      puede applies a un dominio completo sin提到的 una aplicacion concreta.
    - `estado = 'VALIDADO'` es la regla de publicacion: un borrador no se
      consulta como si estuviera aprobado.
    - El `?` evita concatenar la entrada del usuario dentro del SQL.
    """

    consulta = """
        SELECT a.id, a.titulo, a.contenido, d.nombre AS dominio,
               p.nombre AS responsable, p.cargo AS cargo,
               ap.nombre AS aplicacion,
               h.nombre AS herramienta, h.finalidad AS finalidad,
               a.fuente, a.fecha_revision
        FROM articulo a
        JOIN dominio d ON d.id = a.dominio_id
        JOIN experto p ON p.id = a.experto_id
        LEFT JOIN aplicacion ap ON ap.id = a.aplicacion_id
        LEFT JOIN herramienta h ON h.id = a.herramienta_id
        WHERE d.nombre = ? AND a.estado = 'VALIDADO'
        ORDER BY a.titulo
    """
    with conectar(ruta) as conexion:
        filas = conexion.execute(consulta, (dominio,)).fetchall()
        return [dict(fila) for fila in filas]


def listar_articulos(ruta: Path | str = RUTA_DB) -> list[dict]:
    """Lista todos los articulos con su estado (vista de administracion).

    A diferencia de `buscar_articulos`, aqui si aparecen los borradores:
    sirve para revisar el ciclo de vida del contenido, no para consumirlo.
    """

    consulta = """
        SELECT a.id, a.titulo, d.nombre AS dominio, p.nombre AS responsable,
               a.fuente, a.fecha_revision, a.estado
        FROM articulo a
        JOIN dominio d ON d.id = a.dominio_id
        JOIN experto p ON p.id = a.experto_id
        ORDER BY d.nombre, a.titulo
    """
    with conectar(ruta) as conexion:
        filas = conexion.execute(consulta).fetchall()
        return [dict(fila) for fila in filas]


def listar_dominios(ruta: Path | str = RUTA_DB) -> list[dict]:
    """Resumen por dominio: cuantos articulos tiene y cuantos estan validados."""

    consulta = """
        SELECT d.nombre AS dominio,
               COUNT(a.id) AS articulos,
               SUM(CASE WHEN a.estado = 'VALIDADO' THEN 1 ELSE 0 END) AS validados
        FROM dominio d
        LEFT JOIN articulo a ON a.dominio_id = d.id
        GROUP BY d.id
        ORDER BY d.nombre
    """
    with conectar(ruta) as conexion:
        filas = conexion.execute(consulta).fetchall()
        return [dict(fila) for fila in filas]


def articulos_para_categoria(categoria: str,
                             ruta: Path | str = RUTA_DB) -> list[dict]:
    """Conocimiento validado que corresponde a una categoria de la semana 03.

    Es el puente con el resto del proyecto: dado el diagnostico (por ejemplo
    "Enfermedades fungicas"), devuelve los articulos publicados del dominio
    que documenta ese tipo de manejo.
    """

    dominio = DOMINIO_POR_CATEGORIA.get(categoria)
    if dominio is None:
        return []
    return buscar_articulos(dominio, ruta)


def resumen(ruta: Path | str = RUTA_DB) -> dict:
    """Cuentas generales del repositorio para la consola y el reporte."""

    with conectar(ruta) as conexion:
        dominio = conexion.execute("SELECT COUNT(*) FROM dominio").fetchone()[0]
        aplicacion = conexion.execute("SELECT COUNT(*) FROM aplicacion").fetchone()[0]
        experto = conexion.execute("SELECT COUNT(*) FROM experto").fetchone()[0]
        herramienta = conexion.execute("SELECT COUNT(*) FROM herramienta").fetchone()[0]
        total = conexion.execute("SELECT COUNT(*) FROM articulo").fetchone()[0]
        validados = conexion.execute(
            "SELECT COUNT(*) FROM articulo WHERE estado = 'VALIDADO'"
        ).fetchone()[0]
    return {
        "dominios": dominio,
        "aplicaciones": aplicacion,
        "expertos": experto,
        "herramientas": herramienta,
        "articulos": total,
        "validados": validados,
        "borradores": total - validados,
    }


# ---------------------------------------------------------------------------
# CICLO DE VIDA DEL ARTICULO: REGISTRO Y VALIDACION
# ---------------------------------------------------------------------------

def registrar_articulo(titulo: str, contenido: str, dominio_id: int,
                       experto_id: int, fuente: str,
                       aplicacion_id: int | None = None,
                       herramienta_id: int | None = None,
                       ruta: Path | str = RUTA_DB) -> int:
    """Registra un articulo nuevo y devuelve su id.

    El articulo **siempre** nace como BORRADOR: la publicacion es un paso
    posterior y explicito (`validar_articulo`). La fecha de revision la
    aporta el sistema. Titulo, contenido y fuente son obligatorios.
    """

    if not titulo.strip() or not contenido.strip() or not fuente.strip():
        raise ValueError("Titulo, contenido y fuente son obligatorios")

    with conectar(ruta) as conexion:
        cursor = conexion.execute(
            """INSERT INTO articulo
               (titulo, contenido, dominio_id, aplicacion_id, experto_id,
                herramienta_id, fuente, fecha_revision, estado)
               VALUES (?, ?, ?, ?, ?, ?, ?, ?, 'BORRADOR')""",
            (titulo, contenido, dominio_id, aplicacion_id, experto_id,
             herramienta_id, fuente, date.today().isoformat()),
        )
        return cursor.lastrowid


def validar_articulo(articulo_id: int, ruta: Path | str = RUTA_DB) -> None:
    """Aprueba un articulo: cambia su estado a VALIDADO.

    Es una validacion **editorial**, no de identidad: no se comprueba quien
    aprueba. En produccion habria que anadir autenticacion, permisos y
    auditoria.
    """

    with conectar(ruta) as conexion:
        cursor = conexion.execute(
            "UPDATE articulo SET estado = 'VALIDADO' WHERE id = ?",
            (articulo_id,),
        )
        if cursor.rowcount == 0:
            raise ValueError("Articulo no encontrado")


# ---------------------------------------------------------------------------
# ESCENARIO DE DEMOSTRACION
# ---------------------------------------------------------------------------

def ejecutar_caso(ruta: Path | str | None = None) -> dict:
    """Demuestra el ciclo completo: catalogar, registrar, buscar y validar.

    Por defecto trabaja sobre una **base temporal**: la demostracion registra
    y valida un articulo de ejemplo, y asi el repositorio real
    (`artifacts/conocimiento.db`) no se modifica ni se ensucia al repetir la
    ejecucion. Si se pasa una `ruta`, el escenario corre sobre esa base.

    Devuelve un diccionario con los datos de cada paso para poder mostrarlos
    en consola y en el reporte sin repetir la ejecucion.
    """

    temporal = TemporaryDirectory()
    try:
        ruta_caso = Path(ruta) if ruta is not None else Path(temporal.name) / "caso.db"
        return _ejecutar_caso_en(ruta_caso)
    finally:
        temporal.cleanup()


def _ejecutar_caso_en(ruta: Path) -> dict:
    """Ejecuta el escenario sobre una base concreta."""

    inicializar(ruta)

    dominios = listar_dominios(ruta)
    antes = buscar_articulos(DOMINIO_CASO, ruta)

    # 1. Registrar un articulo nuevo (nace como BORRADOR).
    #    Se borra cualquier version previa del articulo de ejemplo para que el
    #    escenario pueda repetirse sin chocar con la unicidad del titulo.
    with conectar(ruta) as conexion:
        conexion.execute(
            "DELETE FROM articulo WHERE titulo = ? AND dominio_id = ?",
            (TITULO_CASO, 2),
        )
    nuevo_id = registrar_articulo(
        TITULO_CASO,
        "Retirar la planta infectada, controlar pulgones y mosca blanca y "
        "vigilar el cultivo durante 15 dias.",
        dominio_id=2,
        experto_id=1,
        fuente="Manual interno de manejo fitosanitario",
        aplicacion_id=2,
        herramienta_id=3,
        ruta=ruta,
    )

    # 2. Mientras es borrador no aparece en la busqueda habitual.
    durante = buscar_articulos(DOMINIO_CASO, ruta)

    # 3. El experto lo aprueba y recien ahi se publica.
    validar_articulo(nuevo_id, ruta)
    despues = buscar_articulos(DOMINIO_CASO, ruta)

    # 4. Errores controlados: integridad referencial y articulo inexistente.
    errores = []
    try:
        registrar_articulo(
            "Articulo con dominio inexistente", "Texto de prueba",
            dominio_id=99, experto_id=1, fuente="Prueba", ruta=ruta,
        )
    except sqlite3.IntegrityError as exc:
        errores.append(("dominio_id inexistente", f"sqlite3.IntegrityError: {exc}"))

    try:
        validar_articulo(9999, ruta)
    except ValueError as exc:
        errores.append(("articulo inexistente", f"ValueError: {exc}"))

    return {
        "dominios": dominios,
        "nuevo_id": nuevo_id,
        "antes": antes,
        "durante": durante,
        "despues": despues,
        "errores": errores,
        "todos": listar_articulos(ruta),
        "resumen": resumen(ruta),
    }


def renderizar_caso(caso: dict) -> str:
    """Convierte el escenario en texto legible para consola y reporte."""

    lineas = [
        "=" * 70,
        f"ESCENARIO A: ciclo de vida del conocimiento en {DOMINIO_CASO}",
        "=" * 70,
        "",
        "1) Organizacion por dominio (dominio -> aplicacion -> experto -> herramienta):",
    ]
    for dominio in caso["dominios"]:
        lineas.append(
            f"   - {dominio['dominio']}: {dominio['validados']} validado(s) "
            f"de {dominio['articulos']} articulo(s)"
        )

    lineas += [
        "",
        f"2) Articulos validados del dominio {DOMINIO_CASO} (consulta inicial):",
    ]
    for articulo in caso["antes"]:
        lineas.append(
            f"   - {articulo['titulo']} | responsable: {articulo['responsable']} "
            f"| aplicacion: {articulo['aplicacion']} | fuente: {articulo['fuente']}"
        )

    lineas += [
        "",
        f"3) Se registra el articulo {caso['nuevo_id']} "
        "(nace como BORRADOR, no se publica).",
        f"   Articulos validados visibles: {len(caso['durante'])} "
        "(el borrador sigue oculto)",
        "",
        "4) El experto lo valida y ahora si aparece en la busqueda:",
    ]
    for articulo in caso["despues"]:
        lineas.append(
            f"   - {articulo['titulo']} | responsable: {articulo['responsable']} "
            f"| aplicacion: {articulo['aplicacion']} | fuente: {articulo['fuente']}"
        )

    lineas += ["", "5) Errores controlados (integridad y validacion):"]
    for situacion, mensaje in caso["errores"]:
        lineas.append(f"   - {situacion}: {mensaje}")

    cuentas = caso["resumen"]
    lineas += [
        "",
        "6) Contenido del repositorio:",
        f"   - {cuentas['dominios']} dominios, {cuentas['aplicaciones']} aplicaciones, "
        f"{cuentas['expertos']} expertos, {cuentas['herramientas']} herramientas",
        f"   - {cuentas['articulos']} articulos: {cuentas['validados']} validados "
        f"y {cuentas['borradores']} en borrador",
    ]
    return "\n".join(lineas)


# ---------------------------------------------------------------------------
# PRUEBAS AUTOMATIZADAS
# ---------------------------------------------------------------------------

class TestBaseConocimiento(unittest.TestCase):
    """Verifica busqueda, registro, publicacion y manejo de errores.

    Cada prueba usa una base temporal: los datos reales del proyecto no se
    tocan.
    """

    def setUp(self) -> None:
        self.temporal = TemporaryDirectory()
        self.ruta = Path(self.temporal.name) / "prueba.db"
        inicializar(self.ruta)

    def tearDown(self) -> None:
        self.temporal.cleanup()

    def test_solo_articulos_validados(self) -> None:
        """El validado se ve; el borrador sigue oculto."""

        self.assertEqual(len(buscar_articulos("Diagnostico foliar", self.ruta)), 2)
        self.assertEqual(len(buscar_articulos("Calidad de datos", self.ruta)), 0)

    def test_ciclo_registro_validacion(self) -> None:
        """Un articulo nuevo nace como borrador y solo aparece tras validarlo."""

        articulo_id = registrar_articulo(
            "Guia de captura de evidencia", "Registrar el panel de la semana 09",
            1, 2, "Manual interno", aplicacion_id=1, herramienta_id=2,
            ruta=self.ruta,
        )
        self.assertEqual(len(buscar_articulos("Diagnostico foliar", self.ruta)), 2)

        validar_articulo(articulo_id, self.ruta)
        self.assertEqual(len(buscar_articulos("Diagnostico foliar", self.ruta)), 3)

    def test_dato_obligatorio(self) -> None:
        """No se registra un articulo sin titulo, contenido o fuente."""

        with self.assertRaises(ValueError):
            registrar_articulo("", "Contenido", 1, 1, "Fuente", ruta=self.ruta)

    def test_referencia_inexistente(self) -> None:
        """Un dominio_id inexistente rompe la integridad referencial."""

        with self.assertRaises(sqlite3.IntegrityError):
            registrar_articulo(
                "Articulo externo", "Texto", 99, 1, "Fuente", ruta=self.ruta
            )

    def test_id_no_existente(self) -> None:
        """Validar un id que no existe informa el error."""

        with self.assertRaises(ValueError):
            validar_articulo(9999, self.ruta)


def ejecutar_pruebas() -> tuple[str, bool]:
    """Ejecuta las pruebas unittest del modulo y captura su salida real."""

    suite = unittest.defaultTestLoader.loadTestsFromTestCase(TestBaseConocimiento)
    flujo = io.StringIO()
    resultado = unittest.TextTestRunner(stream=flujo, verbosity=2).run(suite)
    return flujo.getvalue(), resultado.wasSuccessful()


# ---------------------------------------------------------------------------
# REPORTE Y CONSOLA
# ---------------------------------------------------------------------------

def _tabla_casos(caso: dict) -> str:
    """Tabla Markdown de los articulos validados del escenario."""

    lineas = [
        "| Titulo | Responsable | Aplicacion | Herramienta | Fuente | Fecha |",
        "|---|---|---|---|---|---|",
    ]
    for articulo in caso["despues"]:
        lineas.append(
            f"| {articulo['titulo']} | {articulo['responsable']} "
            f"| {articulo['aplicacion']} | {articulo['herramienta']} "
            f"| {articulo['fuente']} | {articulo['fecha_revision']} |"
        )
    return "\n".join(lineas)


def generar_reporte(ruta: Path | None = None) -> Path:
    """Ejecuta el escenario y las pruebas, y escribe el reporte Markdown."""

    caso = ejecutar_caso()
    salida_pruebas, pruebas_ok = ejecutar_pruebas()

    destino = ruta or RUTA_REPORTE
    destino.parent.mkdir(parents=True, exist_ok=True)

    estado_pruebas = "OK: las cinco pruebas pasaron." if pruebas_ok else (
        "FALLO: alguna prueba no paso."
    )

    contenido = f"""# Semana 15 - Ingenieria del conocimiento: base de conocimiento

**Proyecto:** PlantAI - Deteccion de enfermedades en plantas con Inteligencia Artificial  
**Modulo:** `src/semana15_base_conocimiento.py`  
**Reporte generado:** {date.today().isoformat()}  
**Comandos:** `python src/semana15_base_conocimiento.py` | `--reporte` | `--pruebas`  
**Tema:** organizacion de bases de conocimiento: dominios, aplicaciones,
recursos humanos, herramientas y articulos validados.


{renderizar_caso(caso)}
```

La tabla de los articulos publicados al final del escenario:

{_tabla_casos(caso)}

Los pasos son: **capturar** (registrar), **contextualizar** (dominio,
aplicacion, fuente y experto), **validar** (el experto aprueba) y **recuperar**
(la consulta devuelve solo lo publicado).

## 6. Resultado de las pruebas unittest

Desde la raiz del proyecto:

```text
python -m unittest src.semana15_base_conocimiento -v
python -m unittest discover -s tests -v
```

Salida real capturada por el generador del reporte:

```text
{salida_pruebas.rstrip()}
```

Estado: **{estado_pruebas}**

Las cinco pruebas cubren: solo se muestran los validados, el ciclo
registro->validacion, los datos obligatorios, la integridad referencial y el
articulo inexistente. La suite usa una base temporal, asi que no altera los
datos del repositorio.

El puente con el diagnostico ya implementado es la funcion
`articulos_para_categoria(categoria)`: dada la categoria de la semana 03
("Enfermedades fungicas", "Plantas sanas"...) devuelve los articulos
**validados** del dominio que documenta ese manejo. El modulo solo usa la
biblioteca estandar, por lo que puede probarse aislado y conectarse despues a
`src/pipeline.py` o a `server.py`.
"""
    destino.write_text(contenido, encoding="utf-8")
    return destino


def run() -> None:
    """Ejecuta la demostracion completa de la Semana 15."""

    print("=" * 70)
    print("SEMANA 15 - INGENIERIA DEL CONOCIMIENTO: BASE DE CONOCIMIENTO")
    print("=" * 70)
    print("  Proyecto: deteccion de enfermedades en plantas (PlantAI)")
    print("  Dominio: organizacion del conocimiento (dominios, aplicaciones,")
    print("           expertos, herramientas y articulos validados)")
    print("  Almacenamiento: SQLite en artifacts/conocimiento.db")

    # Se crea (o completa) el repositorio real con el esquema y los datos.
    inicializar(RUTA_DB)

    # El escenario se ejecuta sobre una base temporal para no modificarlo.
    caso = ejecutar_caso()
    print("\n" + renderizar_caso(caso))
    print(f"\nRepositorio: {RUTA_DB.relative_to(RAIZ)}")
    print("Contenido del repositorio real (vista de administracion):")
    for articulo in listar_articulos(RUTA_DB):
        print(f"   - [{articulo['estado']}] {articulo['titulo']} "
              f"| {articulo['dominio']} | {articulo['responsable']}")

    print("\n" + "=" * 70)
    print("Semana 15 completada.")
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
