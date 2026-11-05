"""
temperature_test.py — shows what temperature and seed do to a model's answers.

Run (from the project folder, with the project's own Python, which has `ollama`):
    .eda/bin/python temperature_test.py

Call chain:

    temperature_test.py -> llm.talk() -> llm.chat() -> Ollama -> qwen3.5:4b
                                |
              options {"temperature": ..., "seed": ...}

Background: the model writes an answer one token (word or word piece) at a
time. For each token it computes a probability for every possible next token,
then draws one at random.
  - temperature reshapes those probabilities before the draw
    (0 = always the most likely token; high = unlikely tokens get a real chance).
  - seed fixes the starting point of the random draws, so they repeat.
Further reading:
  https://poloclub.github.io/transformer-explainer/
  https://huggingface.co/blog/how-to-generate
"""
import llm

# The question is open-ended on purpose: many answers are good (Chess, Tag, Go...),
# so the effect of temperature is easy to see. A question with one right answer
# ("capital of France?") would look the same at every temperature.
QUESTION = "Suggest a game for a friendly robot. Answer with just the name and one short reason."

# Kept short so the 5 answers are easy to compare side by side.
SYSTEM = "You are a creative assistant. Answer in one short sentence."

TRIES = 5


def run(title, **settings):
    """Ask the same question TRIES times with the given settings and print the answers.

    `settings` are forwarded unchanged to llm.chat(), e.g. temperature=0.7, seed=42.
    """
    print(f"\n=== {title} ===")

    for i in range(TRIES):
        # Each call is independent: the model keeps no memory between them, so
        # any difference between the answers comes from the settings, not from history.
        # log=False keeps these test calls out of logs/calls.jsonl.
        answer = llm.talk(QUESTION, system=SYSTEM, log=False, **settings)

        # Truncated to one line per answer for readability.
        print(f"{i + 1}. {answer.strip()[:110]}")


# ---------------------------------------------------------------------------
# Experiments. "Real result" notes are from actual runs and will vary.
# ---------------------------------------------------------------------------

# 1. temperature 0: the most likely token is always chosen, so nothing is random.
#    Expected: 5 identical answers.
#    Real result: all 5 were "Chess, because it challenges logic without
#    requiring physical movement." Chess is simply the model's top choice.
run("temperature=0 (no seed)", temperature=0)

# 2. temperature 0.7, no seed: tokens are sampled from the probabilities and
#    every call starts from a new random state.
#    Expected: similar answers, different wording.
#
#    Why the answers diverge: every token is a new random draw, and each token
#    depends on the ones before it. The first draw already picks the game
#    ("Chess" / "Star" / "Go"), and that sends the rest of the sentence down a
#    different path:
#        "Chess" -> "; it relies on logic and strategy ..."
#        "Star"  -> " Trek: The Next Generation is perfect because ..."
#
#    Real result (one run): Chess, three different "Star Trek ..." games, and
#    "Go Go". "Star Trek" came up 3 of 5 times, each with a different ending.
#    Quality problem to notice: "Star Trek: The Role Playing Game" and a
#    "chibi-style platformer" are not games a robot would play, and the model
#    does not check that a game exists. Plausible-sounding is not the same as true.
run("temperature=0.7 (no seed)", temperature=0.7)

# 3. temperature 1.5: probabilities are flattened, so unlikely tokens get a much
#    bigger chance.
#    Expected: the most variety (new games, new sentence shapes) and more mistakes.
#    Variety is paid for with reliability.
run("temperature=1.5 (no seed)", temperature=1.5)

# 4. High temperature but a fixed seed: the random draws are identical on every
#    call, so the answer repeats even though the temperature is high.
#    Expected: 5 identical answers. Without a seed, temperature 1.0 would give
#    variety, so the repetition shows the seed removed the randomness.
run("temperature=1.0, seed=42 (fixed)", temperature=1.0, seed=42)

# 5. Same seed, temperature 0.7 instead of 1.0.
#    Expected: 5 identical answers, but different from test 4: the same random
#    draw lands on a different token when the probabilities change. A seed only
#    reproduces an answer if the prompt, model and temperature are also the same.
run("temperature=0.7, seed=42 (fixed)", temperature=0.7, seed=42)
