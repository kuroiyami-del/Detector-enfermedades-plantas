"""Pruebas de la Semana 15: organizacion de la base de conocimiento.

Las cinco pruebas viven en `src/semana15_base_conocimiento.py` para poder
ejecutarlas con:

    python -m unittest src.semana15_base_conocimiento -v

Este archivo las reexporta para que tambien funcionen con el formato del
material de la semana 15:

    python -m unittest discover -s tests -v

Las pruebas usan una base temporal: no alteran `artifacts/conocimiento.db`.
"""

import sys
from pathlib import Path

RAIZ = Path(__file__).resolve().parents[1]
if str(RAIZ) not in sys.path:
    sys.path.insert(0, str(RAIZ))

from src.semana15_base_conocimiento import (  # noqa: E402,F401
    TestBaseConocimiento,
)


if __name__ == "__main__":
    import unittest

    unittest.main()
