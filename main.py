import sys

from src import (
    pipeline,
    semana02_entrenamiento,
    semana03_taxonomia,
    semana04_busqueda,
    semana05_sistema_hibrido,
    semana07_representaciones,
)


def main():
    if len(sys.argv) > 1 and sys.argv[1] == "--semanas":
        semana02_entrenamiento.run()
        print()
        semana03_taxonomia.run()
        print()
        semana04_busqueda.run()
        print()
        semana05_sistema_hibrido.run()
        print()
        semana07_representaciones.run()
        return

    pipeline.main()


if __name__ == "__main__":
    main()