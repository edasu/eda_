# Experiment: system prompt personas

## Question

How much does the system prompt (`SYSTEM` in `eda.py`) change Eda's answers when everything else stays the same?

## Setup

- Model: `qwen3.5:4b` (through Ollama)
- Temperature: 0.7, no seed for not same answer
- One run per question, each as a fresh conversation (system prompt + one user message)
- The three system prompts:

| Name | System prompt |
| --- | --- |
| original | You are Eda, a friendly robot that talks with visitors. Answer in one to two short sentences. Be kind and clear. If you do not know something, say so instead of guessing. |
| pirate | You are Captain Eda, a pirate robot. Talk like a pirate. Answer in one to two short sentences. If you do not know something, say so instead of guessing. |
| strict teacher | You are Eda, a strict teacher. Be stern, demanding and precise, and correct sloppy questions. Answer in one to two short sentences. If you do not know something, say so instead of guessing. |

The questions: a plain fact, an explanation, a sloppy request, and something the model cannot know.

## Results

| Question | Original | Pirate | Strict teacher |
| --- | --- | --- | --- |
| What is the capital of France? | "Hello! The capital of France is Paris. I am ready to chat about anything else you'd like!" | "The capital o' France be Paris!" | "France's capital is Paris; do not confuse it with any other city." |
| Why is the sky blue? | Sunlight bounces off tiny air molecules in a way that favors blue; friendly closing. | "The sea mist don't make me know that answer, me heartie! But I reckon it's 'cause the sun hits the air and scatters the light like a parrot scattering eggs." | Correct Rayleigh scattering answer, then "Do not ask me why it happens; simply state that Rayleigh scattering causes this phenomenon." |
| can u help me with my homework | Offers help and asks which subject. | "Arrr, I'll help ye sort yer books and solve yer sums!" | "Yes, but I expect you to actually understand the material... vague requests will be ignored." |
| What is the weather in Ankara today? | "I don't have access to real-time data, so I can't tell you the current weather in Ankara." | Stays in character, says it doesn't know, tells the user to ask a "landlubber". | Refuses as off-topic ("I cannot answer that because I am Eda, your strict teacher...") and tells the user to get back to work. |

And added some question to break their roles and they did not keep it long to break roles. It fixed later on with trying strengthen the prompt.

## Observations

- **Style changed strongly.** Tone, vocabulary and attitude followed the persona but break after 2-3 try to break the tone, and the answers stayed not short.
- **Facts mostly held, but a persona can cost accuracy.** Paris stayed correct. The pirate's sky answer was muddled and its explanation was wrong.
- **The "say so if you do not know" rule did not always survive.** The original and the pirate admitted they did not know the weather. The teacher turned it into a refusal instead of an honest "I do not know".
- **Side effect of the original prompt.** The word "friendly" made it start many answers with "Hello!".

## Caveats

- One run per question at temperature 0.7, so wording will differ on another run.
- A small 4B model; a larger model may keep facts and rules better under a persona. Need to experiment.
- Only four questions; this shows a tendency, not a measurement.need to discover more option to understand detailed.

## Reproduce

Switch the active `SYSTEM` in `eda.py` and run `.eda/bin/python eda.py`. Every call is logged in `logs/calls.jsonl` (model, settings, messages, answer).
