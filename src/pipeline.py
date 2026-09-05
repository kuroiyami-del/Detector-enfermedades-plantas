from PIL import Image

from src.config import RAW_DIR
from src.data_loader import load_split
from src.semana02_entrenamiento import load_model, predict_single
from src.semana03_taxonomia import classify_class
from src.semana04_busqueda import TRATAMIENTOS, diagnose_recovery


def print_header(image_path):
    print("=" * 60)
    print("  PlantAI - Diagnostico de enfermedades en plantas")
    print(f"  Imagen: {image_path}")
    print("=" * 60)


def print_step(n, title):
    print(f"\nPASO {n}: {title}")
    print("-" * 60)


def show_plan(plan, total, expanded):
    if plan is None:
        print("  Meta inalcanzable: no hay cura para enfermedades virales.")
        print("  Plan disponible: solo contencion y manejo.")
        return

    print(f"  Costo total: {total}  |  Nodos expandidos: {expanded}")
    print()
    for i, (origen, accion, step, nxt) in enumerate(plan, start=1):
        print(f"  {i}. {accion:30s} +{step}")


def run():
    model, class_map = load_model()

    test_df = load_split("test.csv")
    idx = 0
    filepath = test_df.iloc[idx]["filepath"]
    image_path = str(RAW_DIR / filepath)
    class_real = test_df.iloc[idx]["class_name"]

    print_header(image_path)

    print_step(1, "Carga y preprocesamiento de imagen")
    img = Image.open(image_path)
    w, h = img.size
    print(f"  Tamano original: {w}x{h} RGB")
    print(f"  Preprocesada: 64x64 -> 12288 features")

    print_step(2, "Clasificacion (semana 02)")
    class_pred, confidence = predict_single(model, class_map, image_path)
    print(f"  Modelo: StandardScaler + LogisticRegression")
    print(f"  Clase detectada: {class_pred}")
    print(f"  Confianza: {confidence:.1%}")
    print(f"  Clase real: {class_real}")

    print_step(3, "Taxonomia (semana 03)")
    category = classify_class(class_pred)
    print(f"  Categoria: {category}")

    print_step(4, "Plan de recuperacion (semana 04)")
    plan, total, expanded, cat = diagnose_recovery(class_pred)

    if cat == "Plantas sanas":
        print("  La planta esta sana. No se requiere tratamiento.")
    else:
        grafo = TRATAMIENTOS.get(cat, TRATAMIENTOS["Sin clasificar"])
        print(f"\n  Grafo de tratamientos ({cat}):")
        for estado, acciones in grafo.items():
            for accion, nxt, step in acciones:
                print(f"    {estado:20s} --{accion:25s} (+{step})--> {nxt}")

        print(f"\n  Recorrido A*:")
        if plan:
            print(f"    inicio -> ", end="")
            for i, (origen, accion, step, nxt) in enumerate(plan):
                if i < len(plan) - 1:
                    print(f"{accion} (+{step}) -> ", end="")
                else:
                    print(f"{accion} (+{step}) -> {nxt}")
        show_plan(plan, total, expanded)

    print("\n" + "=" * 60)
    print("  Diagnostico completado")
    print("=" * 60)


if __name__ == "__main__":
    run()