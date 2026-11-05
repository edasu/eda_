"""
temperature_test.py — shows what temperature and seed do.

Run it from the project folder with the project's own Python:
    .eda/bin/python temperature_test.py
(ath specific The system python3 does not have the `ollama` package; .eda does.)

HOW THIS FILE WORKS, in one picture:

    temperature_test.py  --calls-->  llm.talk()  --calls-->  llm.chat()
                                                              |
                                  sends options {"temperature":..., "seed":...}
                                                              v
                                           Ollama (running on your computer)
                                                              |
                                                  qwen3.5:4b generates text
                                                              v
    prints the 5 answers  <-------------- the text comes back up the same chain
"""

import llm

# The SAME question is asked every time.
# The question is open ("suggest a game"), so there are MANY good answers
# (Chess, Tag, Go, a video game, ...). That is what makes the effect of
# temperature easy to see. A question with ONE right answer, like "What is the
# capital of France?", would look the same at every temperature.
QUESTION = "Suggest a game for a friendly robot. Answer with just the name and one short reason."

# The system prompt: who the model is and how it must answer.
# It is kept short ("one short sentence") so the 5 answers are easy to compare.
SYSTEM = "You are a creative assistant. Answer in one short sentence."


def run(title, **settings):
    """Ask the same question 5 times with the given settings and print the answers.

    title      a text that is printed as a heading
    **settings the two stars COLLECT every named input that is given
               (temperature=0.7, seed=42, ...) into one dict, for example
               {"temperature": 1.0, "seed": 42}. Nothing is fixed in advance,
               so this function works for any setting that llm.chat() knows.
    """

    print(f"\n=== {title} ===")

    for i in range(5):
        # llm.talk sends ONE question and returns ONLY the answer text.
        #   QUESTION        what the "user" says
        #   system=SYSTEM   who the model is (added as the "system" message)
        #   log=False       do NOT write these test calls into logs/calls.jsonl,
        #                   so the real conversation log stays clean
        #   **settings      the two stars here do the opposite of above: they
        #                   UNPACK the dict back into named inputs, so
        #                   temperature=0.7 arrives in llm.chat() as if it was
        #                   typed there directly.
        # the model remembers nothing,
        # so the 5 answers are 5 independent tries.
        answer = llm.talk(QUESTION, system=SYSTEM, log=False, **settings)

        # i starts at 0, so i + 1 is used to count 1..5 for a human reader.
        # .strip() removes spaces and new lines at the start and end.
        # [:110] keeps only the first 110 characters, so each answer stays on one line.
        print(f"{i + 1}. {answer.strip()[:110]}")


# ---------------------------------------------------------------------------
# The experiments
# ---------------------------------------------------------------------------

# 1. temperature 0: the most likely next token is ALWAYS chosen, so nothing is
#    random any more.
#    Expected: 5 identical answers.
#    Real result: all 5 were
#        "Chess, because it challenges logic without requiring physical movement."
#    "Chess" is simply the model's single most likely game for a robot.
run("temperature=0 (no seed)", temperature=0)

# 2. temperature 0.7: the next token is SAMPLED from the probabilities
#    (for example "Chess" 40%, "Star" 30%, "Go" 10%). No seed is given, so a new
#    random start is used for every call.
#    Expected: similar answers, but different wording.
#
#    HOW the answers become different:
#      An answer is written one token (word or word piece) at a time, and EVERY
#      token is a new random draw. The FIRST draw already decides the game:
#          "Chess"  /  "Star"  /  "Go" ...
#      Every later token depends on the tokens before it, so one different draw
#      sends the sentence down another path:
#          "Chess"  -> "; it relies on logic and strategy ..."
#          "Star"   -> " Trek: The Next Generation is perfect because ..."
#      A small difference at the start grows into a different sentence.
#         read:https://poloclub.github.io/transformer-explainer/
#
#    WHAT is different (real answers from one run at temperature 0.7):
#      - the game:    Chess / Star Trek: The Role Playing Game /
#                     Star Trek: The Next Generation / Star Trek: The Board Game /
#                     Go Go
#      - the reason:  "relies on logic and strategy, which robots excel at"
#                     "simulate human social interaction"
#                     "classic platforming with a humorous, chibi-style aesthetic"
#      - the format:  "Chess; it relies ..."  versus  "Go Go: It's perfect because ..."
#    "Star Trek" appears 3 times out of 5, but with a different
#    ending each time. Once the first tokens are chosen, a "family" of answers
#    follows. Also notice a quality problem: "Star Trek: The Role Playing Game"
#    and "Go Go ... chibi-style platforming" are not really games a robot would
#    play, and the model does not check whether a game even exists. read: https://huggingface.co/blog/how-to-generate
run("temperature=0.7 (no seed)", temperature=0.7)

# 3. temperature 1.5: the probabilities are flattened, so unlikely tokens get a
#    much bigger chance.
#    Expected: the most variety (new games, new sentence shapes).
#    High temperature gives creativity AND more
#    mistakes: the price of variety is reliability.
run("temperature=1.5 (no seed)", temperature=1.5)

# 4. a HIGH temperature but a FIXED seed: the random choices are the same in
#    every call, so the answer repeats even though the temperature is high.
#    Expected: 5 identical answers.
#    At temperature 1.0 with NO seed we would have expected variety, so the
#    repetition shows that the seed, and not the temperature, removed the randomness.
run("temperature=1.0, seed=42 (fixed)", temperature=1.0, seed=42)

# 5. the same fixed seed 42, but temperature 0.7 instead of 1.0.
#    Expected: again 5 identical answers, but a DIFFERENT answer than in test 4.
#    So the same dice roll can land on a different token. A seed is only
#    repeatable when the temperature (and the prompt and the model) are also the same.
run("temperature=0.7, seed=42 (fixed)", temperature=0.7, seed=42)
