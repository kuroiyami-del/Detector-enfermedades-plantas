import sys

from src import (
    pipeline,
    semana02_entrenamiento,
    semana03_taxonomia,
    semana04_busqueda,
    semana05_sistema_hibrido,
)


def main():
    if len(sys.argv) > 1:
        pipeline.run()
    else:
        semana02_entrenamiento.run()
        print()
        semana03_taxonomia.run()
        print()
        semana04_busqueda.run()
        print()
        semana05_sistema_hibrido.run()


if __name__ == "__main__":
    main()