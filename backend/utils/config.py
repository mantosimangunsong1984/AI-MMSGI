from pathlib import Path

# ==========================================================
# PROJECT
# ==========================================================

PROJECT_ROOT = Path(__file__).resolve().parents[2]

# ==========================================================
# STORAGE
# ==========================================================

STORAGE_DIR = PROJECT_ROOT / "storage"

MODEL_DIR = STORAGE_DIR / "models"

DOCUMENT_DIR = STORAGE_DIR / "documents"

EMBEDDING_DIR = STORAGE_DIR / "embeddings"

DATABASE_DIR = STORAGE_DIR / "database"

# ==========================================================
# LLM MODEL
# ==========================================================

MODEL_NAME = "Qwen2.5-3B-Instruct-Q4_K_M.gguf"

MODEL_PATH = MODEL_DIR / MODEL_NAME

# ==========================================================
# LLM SETTINGS
# ==========================================================

N_CTX = 4096

N_THREADS = 6

TEMPERATURE = 0.3

MAX_TOKENS = 512

# ==========================================================
# EMBEDDING MODEL
# ==========================================================

EMBEDDING_MODEL = "sentence-transformers/all-MiniLM-L6-v2"

EMBEDDING_DIMENSION = 384

# ==========================================================
# VECTOR DATABASE
# ==========================================================

VECTOR_INDEX = EMBEDDING_DIR / "maia.index"

VECTOR_METADATA = EMBEDDING_DIR / "metadata.pkl"

# ==========================================================
# CHUNK SETTINGS
# ==========================================================

CHUNK_SIZE = 800

CHUNK_OVERLAP = 200