from huggingface_hub import hf_hub_download

MODEL_DIR = r"D:\AI-MMSGI\storage\models"

print("Mulai download model...")

model_path = hf_hub_download(
    repo_id="bartowski/Qwen2.5-3B-Instruct-GGUF",
    filename="Qwen2.5-3B-Instruct-Q4_K_M.gguf",
    local_dir=MODEL_DIR,
)

print("\nSelesai!")
print(model_path)