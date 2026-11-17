"""Pruebas de la Semana 16: motor de referencia.

Las ocho pruebas viven en `src/semana16_motor_referencia.py` para poder
ejecutarlas con:

    python -m unittest src.semana16_motor_referencia -v

Este archivo las reexporta para que tambien funcionen con el formato del
material de referencia de la semana 16:

    python -m unittest discover -s tests -v

Las pruebas usan un repositorio temporal: no alteran `artifacts/conocimiento.db`.
"""

import sys
from pathlib import Path

RAIZ = Path(__file__).resolve().parents[1]
if str(RAIZ) not in sys.path:
    sys.path.insert(0, str(RAIZ))

from src.semana16_motor_referencia import (  # noqa: E402,F401
    TestMotorReferencia,
)


if __name__ == "__main__":
    import unittest

    unittest.main()
