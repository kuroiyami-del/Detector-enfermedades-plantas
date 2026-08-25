from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent

DATA_DIR = ROOT / "data"
RAW_DIR = DATA_DIR / "raw" / "PlantVillage-Dataset" / "raw" / "color"
PROCESSED_DIR = DATA_DIR / "processed"

RANDOM_STATE = 42
IMG_SIZE = 64
