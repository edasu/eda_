"""
llm.py — one small helper that every step uses to talk to the model.

Why a helper?
  1. All steps call the model the same way, so if something changes (e.g. the model name, or the way we log calls), 
  we only have to change it here, not in every step.
  2. Every call is written to logs/calls.jsonl (model, settings, messages,
     answer, token counts, time). This is a research habit: later it can
     be used to reproduce the call, analyze the answers, or compare models.

The two functions will used by the steps are:
  ask(prompt, system=None, ...)  -> str        one question, one answer
  chat(messages, ...)            -> response   full control (history, JSON, tools)
"""
# --- Imports: ready-made tools (modules) that we use below ---
import datetime   # tool to get the current date and time (for the log)
import json       # tool to turn Python data into JSON text and back
import os         # tool to read environment variables (we use it for LLM_FAKE)
import re         # tool for regular expressions = pattern search/replace in text
import sys        # tool to reach Python itself (we use it to change error printing)
import time       # tool to measure how many seconds a call takes

import config    


class SetupError(RuntimeError):
    """Raised with a plain-English fix when Ollama or the model is missing."""

# FUNCTION that shows setup problems as one clear message instead of a long
# traceback. Any other kind of error is passed to Python's normal error printer.
# Input needed (Python gives these to it automatically when a program crashes):
#   exc_type = the class of the error (e.g. SetupError)
#   exc      = the error object itself (holds the message text)
#   tb       = the traceback (the list of steps that led to the crash)
#   _default = Python's original error printer (we keep it as a backup)
def _friendly_errors(exc_type, exc, tb, _default=sys.excepthook):
    # issubclass(A, B) asks: "is class A the same as, or a child class of, B?"
    if issubclass(exc_type, SetupError):
        print(f"\nSETUP PROBLEM: {exc}\n", file=sys.stderr)
    else:
        _default(exc_type, exc, tb)

# OVERRIDING (in the simple sense): sys.excepthook is the function Python calls
# when a program crashes.
sys.excepthook = _friendly_errors


# helper returns to client object build in _client.py
# FUNCTION that creates the connection to Ollama (the program that runs the model).
# Input needed: none. It reads HOST from config.py and LLM_FAKE from the system.
# Returns: a client OBJECT. it called its method .chat(...) later to talk to the model.
# LLM_FAKE=1 is only used to test the code without a real model.
def _client():
    if os.environ.get("LLM_FAKE") == "1":
        from tests.fake_ollama import FakeClient
        return FakeClient()
    import ollama # layzy import: only load it when we need it, so the program can start even if it's not installed.
    # ollama.Client is a class; ollama.Client(...) makes one object from it.
    return ollama.Client(host=config.HOST) 


# FUNCTION that removes the model's hidden "thinking" part.
# Some models put their thinking in <think>...</think>; the visitor should only
# Input needed: text = a string (the model's answer). None is also accepted.
# Returns: the cleaned string.
def _clean(text):
    # re.sub(pattern, replacement, text) = find the pattern and replace it.
    # `text or ""` means: if text is empty/None, use an empty string instead.
    # .strip() is a METHOD of every string: it removes spaces at both ends.
    return re.sub(r"<think>.*?</think>", "", text or "", flags=re.S).strip()


# FUNCTION that appends one line (one JSON object) to logs/calls.jsonl.
# Input needed: record = a dict (a Python dictionary) with the facts of one call.
# Returns: nothing; it only writes to the file.
def _log(record):
    # of it: make the logs/ folder if it does not exist yet.
    config.LOG_FILE.parent.mkdir(parents=True, exist_ok=True)
    with open(config.LOG_FILE, "a", encoding="utf-8") as f:
        f.write(json.dumps(record, ensure_ascii=False, default=str) + "\n")


# FUNCTION that sends a list of messages to the model and returns the full response.
# Input needed
def chat(messages, temperature=0.7, seed=None, schema=None, tools=None,
         think=False, model=None, log=True):
    """Send a list of messages to the model and return the full response.

    messages    list of {"role": "system"|"user"|"assistant"|"tool", "content": "..."}
    temperature 0 = most predictable, 1 = more varied
    seed        a number to make answers repeatable (with temperature 0)
    schema      a JSON schema (dict) if you want the answer as JSON
    tools       Python functions the model may ask to call (lesson 12)
    think       False = answer directly (simpler); True = let the model reason first
    """

    # Use the model from config.py unless the caller chose another one.
    model = model or config.MODEL

    # Build the settings that Ollama will receive.
    options = {"temperature": temperature}
    if seed is not None:
        options["seed"] = seed
    kwargs = {"model": model, "messages": messages, "options": options}
    if schema is not None:
        kwargs["format"] = schema   # forces the answer to match the JSON schema
    if tools is not None:
        kwargs["tools"] = tools

    client = _client()      # client is an OBJECT; it knows how to talk to Ollama
    # client = ollama.Client(host=config.HOST) 
    start = time.time()     # remember when we started
    try:
        try:
            # METHOD call: client.chat(...) is the actual call to the model.
            # **kwargs unpacks the dict into named inputs.
            response = client.chat(think=think, **kwargs)
        except Exception as e:
            # Models that can't "think" may reject the setting; try without it.
            if "think" in str(e).lower():
                response = client.chat(**kwargs)
            else:
                raise   # not a "think" problem: pass the error upward
    except Exception as e:
        # Turn technical errors into a short, helpful message (see _explain).
        raise SetupError(_explain(e, model)) from e
    seconds = round(time.time() - start, 2)

    # COMPOSITION in use: response.message is the object inside response, and
    # .content is the text inside that. We overwrite the text with the cleaned
    # version.
    response.message.content = _clean(response.message.content)

    if log:
        # If the model asked to call tools, note their names and arguments.
        calls = []
        for tc in (response.message.tool_calls or []):
            calls.append({"name": tc.function.name, "arguments": dict(tc.function.arguments)})
        # Save everything about this call so it can be reproduce it later.
        _log({
            "time": datetime.datetime.now().isoformat(timespec="seconds"),
            "model": model,
            "options": options,
            "json_schema": schema is not None,
            "messages": messages,
            "answer": response.message.content,
            "tool_calls": calls,
            "tokens_in": response.prompt_eval_count,    # size of what we sent
            "tokens_out": response.eval_count,          # size of the answer
            "seconds": seconds,
        })
    return response


# FUNCTION for one question and one answer.
# Input needed:
#   prompt   (required) the question as a string
#   system   optional string: who the model is and how to behave (default None)
#   **kwargs any extra settings, passed straight on to chat() (e.g. temperature=0)
# Returns: the answer as a plain string (not the whole response object).
def talk(prompt, system=None, **kwargs):
    """One question, one answer (a string). Optional system prompt."""
    messages = []
    if system:
        # The system message tells the model who it is and how to behave.
        # .append() is a METHOD of every list: it adds one item at the end.
        messages.append({"role": "system", "content": system})
    messages.append({"role": "user", "content": prompt})
    # Return only the text, not the whole response object.
    return chat(messages, **kwargs).message.content


# FUNCTION that asks for an answer as JSON and checks it.
# Input needed:
#   prompt   (required) the question as a string
#   schema   (required) a dict that describes the JSON you want, including a
#            "required" list of keys that must be present
#   system   optional system prompt string
#   retries  how many extra tries if the JSON is broken (default 2)
#   **kwargs extra settings passed on to chat()
# Returns: a Python dict. Raises ValueError if every try fails.
def talk_json(prompt, schema, system=None, retries=2, **kwargs):
    """Ask for an answer as JSON that matches `schema`. Returns a Python dict.

    Even with a schema, small models sometimes produce broken JSON, so
    check it and try again a couple of times.
    """
    messages = []
    if system:
        messages.append({"role": "system", "content": system})
    messages.append({"role": "user", "content": prompt + "\n\nReply only with JSON."})
    last_error = None
    for _ in range(retries + 1):   # first try + `retries` more tries
        text = chat(messages, schema=schema, **kwargs).message.content
        try:
            data = json.loads(text)   # is it valid JSON? (turns text into a dict)
            # Are all the keys the schema says are required present?
            missing = [k for k in schema.get("required", []) if k not in data]
            if not missing:
                return data
            last_error = f"missing keys: {missing}"
        except json.JSONDecodeError as e:
            last_error = f"not valid JSON: {e}"
    # All tries failed: stop with a clear error.
    raise ValueError(f"The model did not return usable JSON ({last_error}). Last answer: {text!r}")

