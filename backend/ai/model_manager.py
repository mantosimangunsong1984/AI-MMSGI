from pathlib import Path
from backend.ai.config import MODEL_PATH


class ModelManager:

    @staticmethod
    def get_model_path() -> Path:

        if not MODEL_PATH.exists():
            raise FileNotFoundError(
                f"Model tidak ditemukan:\n{MODEL_PATH}"
            )

        return MODEL_PATH