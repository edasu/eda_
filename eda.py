"""
eda.py — Eda, a chatbot you talk to in the terminal.

Run:   .eda/bin/python eda.py
Quit:  type "quit" (or press Ctrl+C)

In-chat command:
    /face <emotion>   tell Eda what the visitor's face looks like (e.g. /face angry)
"""
import llm

# The system prompt defines who Eda is and how she answers. The visitor never
# sees it, but the model reads it first on every call.
# Persona comparison and results: docs/persona_experiment.md
PERSONAS = {
    "original": (
        "You are Eda, a friendly robot that talks with visitors. "
        "Answer in one to two short sentences. Be kind and clear. "
        "If you do not know something, say so instead of guessing."
    ),
    "pirate": (
        "You are Captain Eda, a pirate robot. Talk like a pirate. "
        "Answer in one to two short sentences. "
        "If you do not know something, say so instead of guessing."
    ),
    "teacher": (
        "You are Eda, a strict teacher. Be stern, demanding and precise, "
        "and correct sloppy questions. Answer in one to two short sentences. "
        "If you do not know something, say so instead of guessing."
    ),
}
SYSTEM = PERSONAS["pirate"]  # switch persona by changing this key


def main():
    # The model is stateless: it remembers nothing between calls. The "memory"
    # is this list, which is re-sent in full on every call.
    #
    # Each message has a role:
    #   system     instructions on who the model is and how to behave
    #   user       what the person said
    #   assistant  what the model said earlier
    #   tool       the result of a function the model asked us to run
    messages = [{"role": "system", "content": SYSTEM}]

    print("Eda: Hello! I am Eda the captain. how can I help you today? if you want to leave, type 'quit'.")
    print("     (Tip: '/face angry' tells Eda what the visitor's face looks like.)\n")

    # What the robot "sees". Held here until the next message, then prepended
    # to it. It is not sent as a second system message because some models
    # accept only one system message, at the very start.
    perception_note = None

    while True:
        try:
            user_text = input("You: ").strip()
        except (EOFError, KeyboardInterrupt):
            print("\nEda: Goodbye!")
            break

        if not user_text:
            print("Eda: I did not catch that. Please type something.\n")
            continue
        if user_text.lower() in ("quit", "exit"):
            print("Eda: Goodbye!")
            break

        messages.append({"role": "user", "content": user_text})

        # The full history goes to the model on every call.
        # temperature 0.7: some randomness in the wording (see temperature_test.py).
        response = llm.chat(messages, temperature=0.7)
        answer = response.message.content

        # Store the reply too, otherwise the model would not "remember" it next turn.
        messages.append({"role": "assistant", "content": answer})

        print(f"Eda: {answer}\n")


if __name__ == "__main__":
    main()
