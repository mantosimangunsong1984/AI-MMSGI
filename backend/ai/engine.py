from llama_cpp import Llama
from backend.utils.logger import logger
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
    def __init__(self):

        print("=" * 60)
        print("MAIA AI ENGINE")
        print("=" * 60)

        model_path = ModelManager.get_model_path()

        print("Loading model:")
        print(model_path)

        self.llm = Llama(
            model_path=str(model_path),
            n_ctx=N_CTX,
            n_threads=N_THREADS,
            verbose=VERBOSE
        )

        print("\nModel berhasil di-load.\n")

        logger.info("Model berhasil dimuat.")


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

        logger.info(f"MAIA : {answer}")
        logger.info(f"Response Time : {elapsed} sec")

        return answer


    def chat_with_context(self, context: str, question: str) -> str:

        response = self.llm.create_chat_completion(
            messages=[
                {
                    "role": "system",
                    "content": (
                        "Kamu adalah MAIA, AI Assistant internal MMS Group Indonesia.\n"
                        "Jawablah HANYA berdasarkan konteks yang diberikan.\n"
                        "Jika jawaban tidak ada pada konteks, katakan:\n"
                        "'Maaf, informasi tersebut tidak ditemukan pada dokumen yang tersedia.'\n"
                        "Jangan membuat informasi yang tidak terdapat pada konteks."
                    )
                },
                {
                    "role": "user",
                    "content": f"""
KONTEKS:

{context}

PERTANYAAN:

{question}
"""
                }
            ],
            temperature=0.2,
            max_tokens=512
        )

        return response["choices"][0]["message"]["content"]