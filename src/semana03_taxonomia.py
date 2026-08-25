from dataclasses import dataclass

from src.config import PROCESSED_DIR
from src.data_loader import load_class_map, load_split


@dataclass(frozen=True)
class DiseaseCategory:
    name: str
    keywords: tuple[str, ...]


DISEASE_CATEGORIES = [
    DiseaseCategory("Plantas sanas", (
        "healthy",
    )),

    DiseaseCategory("Plagas", (
        "Spider_mites", "mites",
    )),

    DiseaseCategory("Enfermedades bacterianas", (
        "Bacterial",
    )),

    DiseaseCategory("Enfermedades virales", (
        "Virus", "mosaic", "greening", "Haunglongbing",
    )),

    DiseaseCategory("Enfermedades fungicas", (
        "Rust", "Rot", "Scab", "Blight", "Mildew", "Mold",
        "Spot", "Esca", "Leaf_scorch", "Measles",
    )),
]


def classify_class(class_name: str) -> str:
    lower_name = class_name.lower()
    for category in DISEASE_CATEGORIES:
        for keyword in category.keywords:
            if keyword.lower() in lower_name:
                return category.name
    return "Sin clasificar"


def run():
    print("=" * 70)
    print("SEMANA 03 - CLASIFICACION DEL DATASET POR TIPO DE ENFERMEDAD")
    print("=" * 70)

    class_map = load_class_map()
    train_df = load_split("train.csv")
    test_df = load_split("test.csv")

    train_counts = train_df["class_name"].value_counts().to_dict()
    test_counts = test_df["class_name"].value_counts().to_dict()

    stats = {cat.name: {"clases": 0, "train": 0, "test": 0} for cat in DISEASE_CATEGORIES}
    stats["Sin clasificar"] = {"clases": 0, "train": 0, "test": 0}

    print("\nClasificacion de cada clase:")
    print("-" * 70)

    for class_name in sorted(class_map.keys()):
        category = classify_class(class_name)
        stats[category]["clases"] += 1
        stats[category]["train"] += train_counts.get(class_name, 0)
        stats[category]["test"] += test_counts.get(class_name, 0)

        cultivo = class_name.split("___")[0]
        enfermedad = class_name.split("___")[1] if "___" in class_name else class_name
        print(f"  {class_name:60s} -> {category}")

    print("\n" + "=" * 70)
    print("RESUMEN POR CATEGORIA")
    print("=" * 70)
    print(f"\n  {'Categoria':35s} {'Clases':>7s} {'Train':>8s} {'Test':>7s} {'Total':>8s}")
    print("  " + "-" * 65)

    total_clases = 0
    total_train = 0
    total_test = 0

    for category in DISEASE_CATEGORIES:
        s = stats[category.name]
        total_cat = s["train"] + s["test"]
        print(f"  {category.name:35s} {s['clases']:7d} {s['train']:8d} {s['test']:7d} {total_cat:8d}")
        total_clases += s["clases"]
        total_train += s["train"]
        total_test += s["test"]

    s = stats["Sin clasificar"]
    if s["clases"] > 0:
        total_cat = s["train"] + s["test"]
        print(f"  {'Sin clasificar':35s} {s['clases']:7d} {s['train']:8d} {s['test']:7d} {total_cat:8d}")
        total_clases += s["clases"]
        total_train += s["train"]
        total_test += s["test"]

    total_total = total_train + total_test
    print("  " + "-" * 65)
    print(f"  {'TOTAL':35s} {total_clases:7d} {total_train:8d} {total_test:7d} {total_total:8d}")

    print("\n" + "=" * 70)
    print("Semana 03 completada.")
    print("=" * 70)
