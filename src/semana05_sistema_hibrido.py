import re
import unicodedata
from pathlib import Path

from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.linear_model import LogisticRegression
from sklearn.metrics.pairwise import cosine_similarity
from sklearn.pipeline import make_pipeline

ROOT = Path(__file__).resolve().parent.parent
KB_PATH = ROOT / "data" / "base_conocimiento.txt"

DEFAULT_DOCS = [
    "Enfermedades fungicas: manchas en las hojas, podredumbre, oxido, mildiu, moho.",
    "Enfermedades bacterianas: manchas acuosas, pudricion blanda, halo amarillo.",
    "Enfermedades virales: mosaico, amarillamiento, enrollamiento de hojas.",
    "Plagas: acaros, pulgones, orugas, mosca blanca, minadores en las hojas.",
    "Plantas sanas: sin sintomas visibles, hojas verdes, crecimiento normal.",
]


def load_documents() -> list:
    if not KB_PATH.exists():
        KB_PATH.parent.mkdir(parents=True, exist_ok=True)
        KB_PATH.write_text("\n".join(DEFAULT_DOCS), encoding="utf-8")
    lines = KB_PATH.read_text(encoding="utf-8").splitlines()
    return [line.strip() for line in lines if line.strip()]


def normalize(text: str) -> str:
    text = text.strip().lower()
    text = unicodedata.normalize("NFD", text)
    text = "".join(ch for ch in text if unicodedata.category(ch) != "Mn")
    text = re.sub(r"[^a-z0-9 ]+", " ", text)
    return re.sub(r"\s+", " ", text).strip()


def build_vectorizer(docs):
    vectorizer = TfidfVectorizer()
    doc_matrix = vectorizer.fit_transform([normalize(d) for d in docs])
    return vectorizer, doc_matrix


def build_classifier():
    train_x = [
        "manchas marrones en las hojas de tomate",
        "podredumbre y moho en los frutos",
        "oxido en las hojas de las plantas",
        "mildiu y manchas amarillas en las hojas",
        "pudricion y podredumbre en el cultivo",
        "patron de mosaico amarillo en las hojas",
        "mosaico y amarillamiento generalizado",
        "enrollamiento de las hojas del tomate",
        "hojas con deformaciones y enanismo",
        "insectos verdes en el enves de las hojas",
        "acaros y telaranas en las hojas",
        "orugas comiendo las hojas del cultivo",
        "mosca blanca en los cultivos",
        "minadores y huevos en las hojas",
        "hojas verdes sin manchas ni danos",
        "planta sana con buen crecimiento",
        "hojas sin sintomas y crecimiento normal",
        "mis plantas estan sanas y verdes",
        "la planta se ve sana sin sintomas visibles",
        "manchas negras en las hojas del tomate",
        "amarillamiento de hojas por exceso de riego",
    ]
    train_y = [
        "fungica",
        "fungica",
        "fungica",
        "fungica",
        "fungica",
        "viral",
        "viral",
        "viral",
        "viral",
        "plaga",
        "plaga",
        "plaga",
        "plaga",
        "plaga",
        "sana",
        "sana",
        "sana",
        "sana",
        "sana",
        "fungica",
        "viral",
    ]

    classifier = make_pipeline(
        TfidfVectorizer(),
        LogisticRegression(max_iter=1000, random_state=42),
    )
    classifier.fit(train_x, train_y)
    return classifier


DOCS = load_documents()
vectorizer, doc_matrix = build_vectorizer(DOCS)
classifier = build_classifier()

RULES = [
    ("Enfermedades virales", ("mosaico", "amarillamiento", "enrollamiento", "enanismo")),
    ("Plantas sanas", ("sanas", "sin manchas", "sin sintomas")),
    ("Enfermedades fungicas", ("mancha", "moho", "oxido", "mildiu", "podredumbre", "pudricion")),
    ("Plagas", ("insecto", "acaro", "pulgon", "oruga", "mosca blanca", "minador")),
]


def mejor_documento(area: str) -> str:
    for doc in DOCS:
        if normalize(doc).startswith(normalize(area)):
            return doc
    return DOCS[0]


def answer(query: str) -> dict:
    q = normalize(query)
    reglas = [nombre for nombre, palabras in RULES if any(p in q for p in palabras)]

    if reglas:
        evidencia = mejor_documento(reglas[0])
    else:
        sims = cosine_similarity(vectorizer.transform([q]), doc_matrix)[0]
        evidencia = DOCS[int(sims.argmax())]

    idx = DOCS.index(evidencia)
    similitud = float(cosine_similarity(vectorizer.transform([q]), doc_matrix)[0][idx])
    clase = str(classifier.predict([q])[0])

    return {
        "reglas": reglas,
        "evidencia": evidencia,
        "similitud": similitud,
        "clase": clase,
    }


def run():
    queries = [
        "Las hojas de mi tomate tienen manchas marrones y algo de moho.",
        "Veo insectos verdes pequenos en el enves de las hojas.",
        "Las hojas se estan poniendo amarillas y con patron de mosaico.",
        "Mis plantas tienen las hojas verdes y se ven sanas sin manchas.",
        "Hay oxido y podredumbre en las hojas y los frutos del cultivo.",
    ]

    print("=" * 60)
    print("SEMANA 05 - SISTEMA HIBRIDO")
    print("=" * 60)

    for i, q in enumerate(queries, start=1):
        result = answer(q)
        print(f"\nConsulta {i}: {q}")
        print(f"  Reglas activadas : {', '.join(result['reglas']) or 'ninguna'}")
        print(f"  Evidencia        : {result['evidencia']}")
        print(f"  Similitud        : {result['similitud']:.3f}")
        print(f"  Clasificacion    : {result['clase']}")

    print("\n" + "=" * 60)
    print(f"Consultas procesadas: {len(queries)}")
    print("=" * 60)


if __name__ == "__main__":
    run()