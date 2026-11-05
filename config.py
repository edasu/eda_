"""config.py — the settings that llm.py reads."""
from pathlib import Path

MODEL = "qwen3.5:4b"                     # change this if you use another Ollama model
HOST = "http://localhost:11434"          # where Ollama is running
LOG_FILE = Path(__file__).parent / "logs" / "calls.jsonl"   # every call is logged here
