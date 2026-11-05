# Project Eda: a chatbot robot built step by step

**What this is.** Eda is that robot. For now it is text in the Terminal, so no hardware is needed. It is built with  in one file, `eda.py`.

---

## 1. Reminders

**Where does its knowledge come from?**
It comes only from the text the model was trained on. Nothing is looked up unless tools are connected to it. A wrong answer can be given in a completely sure tone. This is called a *hallucination*.

**What does "4B" in `qwen3.5:4b` mean?**
The model is a big file of numbers that were learned during training, called *parameters*. "4B" means that about 4 billion of them are contained in it.

**What is a prompt?**
A prompt is everything that is sent to the model. The model is strongly affected by wording, so a better answer is given when a clear briefing is provided, as when a person who knows a lot but knows nothing about your situation is briefed. *Prompt engineering* means that this briefing is written carefully and tested.

**What are roles?**
A role is given to every message. `system` holds the instructions about who the model is and how it must behave (it is never seen by the visitor). `user` is what was said by the person. `assistant` is what was said earlier by the model.

**Does it remember converisation?**
No. Each call is started from nothing. A chatbot only *seems* to remember because the whole conversation is sent again by the program every time.

**What are temperature and seed?**
Temperature controls how adventurous the model is: 0 is the most predictable, 1 is more varied. A seed is a number by which the random choices are made repeatable.

**What is a chatbot robot?**
It is a pipeline: microphone, then speech-to-text (for example Whisper), then the LLM, then text-to-speech, then speaker. A *perception note* ("the visitor looks frustrated") can be added by a camera, and actions (nod, smile) can be added by motors. The language brain in the middle is formed by the LLM. In this project, typing is used instead of speaking, reading instead of listening, and the camera will be simulated with a `/face` command.
