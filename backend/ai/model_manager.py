from pathlib import Path
from backend.ai.config import MODEL_DIR


class ModelManager:

    @staticmethod
    def get_model_path(model_name=None) -> Path:

        if model_name:
            model_path = MODEL_DIR / model_name
        else:
            model_path = MODEL_DIR / "Qwen2.5-3B-Instruct-Q4_K_M.gguf"

        if not model_path.exists():
            raise FileNotFoundError(
                f"Model tidak ditemukan:\n{model_path}"
            )

        return model_path

    @staticmethod
    def get_available_models():

        return [
            file.name
            for file in MODEL_DIR.glob("*.gguf")
        ]