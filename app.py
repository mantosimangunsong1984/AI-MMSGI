from backend.ai.engine import AIEngine

print("=" * 60)
print("MMSGI AI ASSISTANT")
print("=" * 60)

ai = AIEngine()

while True:
    question = input("\nAnda : ")

    if question.lower() in ["exit", "quit", "keluar"]:
        break

    answer = ai.chat(question)

    print("\nMAIA :")
    print(answer)