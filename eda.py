"""
eda.py — Eda, a simple chatbot that is talked to in the Terminal.

The program is started with:   python eda.py
It is stopped by typing:       quit  (or by pressing Ctrl+C)
"""
import llm

# The system prompt: it is defined here who Eda is and how she must behave.
# It is never seen by the visitor.
SYSTEM = (
    "You are Eda, a friendly robot that talks with visitors. "
    "Answer in one to two short sentences. Be kind and clear. "
    "If you do not know something, say so instead of guessing."
)


def main():
    # Nothing is remembered by the model between calls, so the whole
    # conversation is kept in this list and is sent again every time.
    messages = [{"role": "system", "content": SYSTEM}]

    print("Eda: Hello! I am Eda. how can I help you today? if you want to leave, type 'quit'.\n")

    while True:
        try:
            user_text = input("You: ").strip()
        except (EOFError, KeyboardInterrupt):
            print("\nEda: Goodbye!")
            break

        if not user_text:
            # A message is shown to the user, then the question is asked again.
            print("Eda: I did not catch that. Please type something.\n")
            continue
        if user_text.lower() in ("quit", "exit"):
            print("Eda: Goodbye!")
            break

        # 1. What was visitor is added to the history.
        #    Four roles can be given to a message:
        #      "system"    = the instructions about who the model is and how it must behave
        #      "user"      = what was said by the person
        #      "assistant" = what was said earlier by the model
        #      "tool"      = the result of a tool (function) that was called on request of the model
        messages.append({"role": "user", "content": user_text})

        # 2. The whole history is sent to the model.
        response = llm.chat(messages, temperature=0.7)
        answer = response.message.content

        # 3. Eda's answer is added to the history, so that it can be "remembered" in the next turn.
        messages.append({"role": "assistant", "content": answer})

        print(f"Eda: {answer}\n")


if __name__ == "__main__":
    main()
