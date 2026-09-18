from llama_cpp import Llama
from backend.utils.logger import logger
from backend.ai.model_manager import ModelManager
import time
from backend.ai.config import (
    N_CTX,
    N_THREADS,
    TEMPERATURE,
    MAX_TOKENS,
    VERBOSE,
)

from backend.ai.prompt import SYSTEM_PROMPT
from backend.ai.model_manager import ModelManager


class AIEngine:

    def get_available_models(self):

        return ModelManager.get_available_models()

    def __init__(self):

        print("=" * 60)
        print("EVE AI ENGINE")
        print("=" * 60)

        self.current_model = None
        self.llm = None

        self.change_model(
            "Qwen2.5-3B-Instruct-Q4_K_M.gguf"
        )

    def change_model(self, model_name):

        print("=" * 60)
        print("CHANGE EVE MODEL")
        print("=" * 60)

        model_path = ModelManager.get_model_path(
            model_name
        )

        print("Loading model:")
        print(model_path)

        # Hapus model lama dari memory
        self.llm = None

        self.llm = Llama(
            model_path=str(model_path),
            n_ctx=N_CTX,
            n_threads=N_THREADS,
            verbose=VERBOSE
        )

        self.current_model = model_name

        print(
            f"Model aktif: {model_name}"
        )

        logger.info(
            f"Model aktif: {model_name}"
        )

# class AIEngine:
#     def __init__(self):

#         print("=" * 60)
#         print("EVE AI ENGINE")
#         print("=" * 60)

#         model_path = ModelManager.get_model_path()

#         print("Loading model:")
#         print(model_path)

#         self.llm = Llama(
#             model_path=str(model_path),
#             n_ctx=N_CTX,
#             n_threads=N_THREADS,
#             verbose=VERBOSE
#         )

#         print("\nModel berhasil di-load.\n")

#         logger.info("Model berhasil dimuat.")


    def chat(self, message: str) -> str:

        logger.info(f"USER : {message}")

        start_time = time.time()

        response = self.llm.create_chat_completion(
            messages=[
                {
                    "role": "system",
                    "content": SYSTEM_PROMPT
                },
                {
                    "role": "user",
                    "content": message
                }
            ],
            temperature=TEMPERATURE,
            max_tokens=MAX_TOKENS
        )

        answer = response["choices"][0]["message"]["content"]

        elapsed = round(time.time() - start_time, 2)

        logger.info(f"EVE : {answer}")
        logger.info(f"Response Time : {elapsed} sec")

        return answer


    def chat_with_context(self, context: str, question: str) -> str:

        response = self.llm.create_chat_completion(
            messages=[
                {
                    "role": "system",
                    "content": """
    Kamu adalah EVE (Enterprise Virtual Expert), AI Assistant internal MMS Group Indonesia.

    Tugasmu adalah menjawab pertanyaan HANYA berdasarkan dokumen yang diberikan.

    ATURAN:

    1. Gunakan HANYA informasi pada CONTEXT.

    2. Jangan menggunakan pengetahuan umum.

    3. Jangan mengarang jawaban.

    4. Jika terdapat beberapa dokumen, prioritaskan dokumen yang paling relevan dengan pertanyaan.

    5. Bila konteks memuat beberapa bagian seperti:
    - Tujuan
    - Cakupan
    - Definisi
    - Kebijakan
    - Persyaratan
    - Prosedur
    - Ketentuan
    - Hak
    - Kewajiban

    maka rangkum seluruh informasi penting tersebut.

    6. Jangan hanya mengambil satu kalimat jika masih ada informasi yang berkaitan pada konteks.

    7. Jika informasi tidak ditemukan pada konteks, jawab persis:

    "Maaf, informasi tersebut tidak ditemukan pada dokumen yang tersedia."

    8. Jawablah menggunakan Bahasa Indonesia yang profesional.

    9. Jangan menyebutkan informasi yang tidak ada pada konteks.
    """
                },
                {
                    "role": "user",
                    "content": f"""
    CONTEXT

    {context}

    ====================================

    PERTANYAAN

    {question}

    ====================================

    Jawablah hanya berdasarkan CONTEXT di atas.
    """
                }
            ],
            temperature=0.2,
            max_tokens=512
        )

        return response["choices"][0]["message"]["content"]