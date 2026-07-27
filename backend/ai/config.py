from pathlib import Path

# ==================================================
# Project Path
# ==================================================

PROJECT_ROOT = Path(__file__).resolve().parents[2]

# ==================================================
# Storage
# ==================================================

STORAGE_DIR = PROJECT_ROOT / "storage"
MODEL_DIR = STORAGE_DIR / "models"
DOCUMENT_DIR = STORAGE_DIR / "documents"
EMBEDDING_DIR = STORAGE_DIR / "embeddings"
DATABASE_DIR = STORAGE_DIR / "database"

# ==================================================
# Model
# ==================================================

MODEL_NAME = "Qwen2.5-3B-Instruct-Q4_K_M.gguf"
MODEL_PATH = MODEL_DIR / MODEL_NAME

# ==================================================
# AI Settings
# ==================================================

N_CTX = 4096
N_THREADS = 6
TEMPERATURE = 0.3
MAX_TOKENS = 512

# Streaming (akan digunakan nanti)
STREAM = True

# GPU Layer
# 0 = CPU Only
N_GPU_LAYERS = 0

# Verbose Log
VERBOSE = False