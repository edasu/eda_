# Setup: get Eda running, step by step

This guide is written for macOS and the Terminal. Every step ends with a check, so you know it worked before you go on.

---

## 1. What you need

- Python 3.9 or newer
- Ollama (the program that runs the model on your computer)
- About 4 GB of free disk space for the model

## 2. Check Python

```
python3 --version
```

You should see `Python 3.9` or higher. If not, install it from <https://www.python.org/downloads/>.

## 3. Open the project folder

Go to the folder where you saved the project. Replace `/path/to/eda_` with your own folder path:

```
cd "/path/to/eda_"
```

Tip: in the Finder, drag the folder into the Terminal window to paste its path. Keep the quotes if the path contains spaces.

**Check:** `ls` shows `eda.py`, `llm.py` and `config.py`.

## 4. Create a virtual environment

A virtual environment keeps this project's packages separate from the rest of your computer.

```
python3 -m venv .venv
source .venv/bin/activate
```

**Check:** your prompt now starts with `(.venv)`or the venv name you gave.

Each time you open a new Terminal, run `source .venv/bin/activate` again.

## 5. Install the Python package

```
pip install ollama
```

**Check:** `pip show ollama` prints a version number.

## 6. Install and start Ollama

1. Download Ollama from <https://ollama.com/download> and install it.
2. Open the Ollama app (or run `ollama serve` in a separate Terminal window).

**Check:** `ollama --version` prints a version number.

## 7. Download the model

```
ollama pull qwen3.5:4b
```

This can take a few minutes. The model name must match `MODEL` in `config.py`.

**Check:** `ollama list` shows `qwen3.5:4b`.

## 8. Run Eda

```
python eda.py
```

Type a message and press Enter. Type `quit` to leave.

---

## Where things are

| File | What it does |
| ------ | -------------- |
| `eda.py` | The chat loop you talk to |
| `llm.py` | The helper that talks to the model and writes the log |
| `config.py` | Settings: model name, Ollama address, log file |
| `logs/calls.jsonl` | One line per model call (created automatically) |
