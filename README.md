# Project Eda: a chatbot robot built step by step

Eda is a friendly chatbot robot. For now it is text in the Terminal, so no hardware is needed. It is built with Python and a language model (`qwen3.5:4b`) that runs on your own computer through [Ollama](https://ollama.com). The aim of the project is to **learn how LLMs work by playing with them**.

## Contents

1. [Quick start](#1-quick-start)
2. [Project files](#2-project-files)
3. [How the pieces talk to each other](#3-how-the-pieces-talk-to-each-other)
4. [Concepts and reminders](#4-concepts-and-reminders)
5. [Experiment: temperature and seed](#5-experiment-temperature-and-seed)
6. [Troubleshooting](#6-troubleshooting)
7. [Ideas to play with next](#7-ideas-to-play-with-next)

---

## 1. Quick start

**You need:** Python 3.9 or newer, Ollama installed and running, and about 4 GB of free disk space for the model. The full step-by-step guide is in [docs/setup.md](docs/setup.md).

```bash
source .eda/bin/activate     # use the project's own Python (virtual environment)
ollama pull qwen3.5:4b       # download the model once
python eda.py                # talk to Eda; type "quit" to leave
python temperature_test.py   # see what temperature and seed do
```

If you do not activate the environment, call Python directly: `.eda/bin/python eda.py`. The system `python3` does not have the `ollama` package.

---

## 2. Project files

| File / folder | What it does |
| --- | --- |
| `eda.py` | The chatbot loop: reads what you type, sends the whole history to the model, prints the answer. |
| `llm.py` | The helper that talks to Ollama: `chat()` (full control), `talk()` (one question, one answer) and `talk_json()` (answer as JSON). |
| `config.py` | Settings: which model (`MODEL`), where Ollama runs (`HOST`), where calls are logged (`LOG_FILE`). |
| `temperature_test.py` | Experiment: asks the same question 5 times with different temperature and seed settings. |
| `docs/setup.md` | Step-by-step setup guide for macOS. |
| `logs/calls.jsonl` | A record of every model call. Not committed, because chats can be private. |
| `.eda/` | The virtual environment: a private Python with the packages of this project (for example `ollama`). |

---

## 3. How the pieces talk to each other

```text
You type  -->  eda.py  -->  llm.py  -->  Ollama  -->  qwen3.5:4b
                 ^                                         |
                 +---------------- the answer -------------+
```

Ollama runs as a small server on your computer, at `http://localhost:11434`. The Python package `ollama` (used in `llm.py`) sends requests to that server, and the server runs the model. The same server can be called without Python, through its REST API.

**Read more:** [Ollama API introduction](https://docs.ollama.com/api/introduction). It describes the endpoints (for example `/api/chat`), the message format and the options such as `temperature` and `seed` that `llm.py` sends.

---

## 4. Concepts and reminders

**Where does its knowledge come from?**
It comes only from the text the model was trained on. Nothing is looked up unless tools are connected to it. A wrong answer can be given in a completely sure tone. This is called a *hallucination*.

**Does the model think?**
Not like a person. It repeats one step: it predicts the next *token* (a word or a piece of a word) from all the text so far. This is enough to look like reasoning, but it can also give invented facts. Some models can write out reasoning steps first (`think=True` in `llm.chat()`), which often helps with harder questions but is slower.

**What does "4B" in `qwen3.5:4b` mean?**
The model is a big file of numbers that were learned during training, called *parameters*. "4B" means that about 4 billion of them are contained in it. Change the model in `config.py`.

**What is a prompt?**
A prompt is everything that is sent to the model. The model is strongly affected by wording, so a better answer is given when a clear briefing is provided, as when a person who knows a lot but knows nothing about your situation is briefed. *Prompt engineering* means that this briefing is written carefully and tested.

**What are roles?**
A role is given to every message:

- `system` holds the instructions about who the model is and how it must behave (it is never seen by the visitor).
- `user` is what was said by the person.
- `assistant` is what was said earlier by the model.
- `tool` is the result of a function that was called on request of the model.

**Does it remember the conversation?**
No. Each call is started from nothing. A chatbot only *seems* to remember because the whole conversation is sent again by the program every time (the `messages` list in `eda.py`). When the history gets longer than the model's *context window*, the oldest parts no longer fit.

## 5. Experiment: temperature and seed

The model writes an answer one token at a time. For each token it calculates a probability for every possible next token, then makes a random draw.

- **Temperature** changes the probabilities before the draw. Low values make the most likely token dominate (0 = always the top token, so the same answer every time). High values flatten the probabilities, so unlikely tokens get a real chance: more variety, but also more mistakes and invented answers.
- **Seed** is the starting number of the random draws. With the same seed, the same draws are made, so the answer is repeatable even at a high temperature. It only repeats if the prompt, the model *and* the temperature are also the same.

Use a seed while you develop or compare prompts, so a different answer comes from your change and not from luck. Do not use a seed in the real chatbot, or Eda will answer the same conversation identically every time.

Result of `temperature_test.py` with the question "Suggest a game for a friendly robot" (5 tries each):

| Setting | What happened |
| --- | --- |
| temperature 0 | 5 identical answers ("Chess, because ...") |
| temperature 0.7 | Chess and several "Star Trek ..." games, each with different wording |
| temperature 1.5 | 5 different ideas, some of them invented ("Bolt & Button") |
| temperature 1.0, seed 42 | 5 identical answers ("Tag ...") |
| temperature 0.7, seed 42 | 5 identical answers ("Star Trek: Voyager ..."), different from the line above |

Your own run will differ for the settings without a seed. The comments inside `temperature_test.py` explain every line.

---
