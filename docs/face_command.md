# The `/face` input: how Eda "sees" emotion

## What it does

`/face <emotion>` tells Eda what the visitor's face looks like, for example `/face angry`. It is a stand-in for a real camera and emotion classifier: the user types the emotion by hand.

## How it works (`eda.py`)

1. The input is handled in Python and never reaches the model.
2. The emotion word is lowercased and stored as a text note:
   `[Perception: the visitor's face looks angry.]`
   There is no list of allowed emotions, so any word works (`/face banana` too).
3. Eda prints a fixed line, `(I see that you look angry.)`. It is hardcoded in Python and the model does not write it.
4. On the next message, the note is put in front of the user's text, and the note variable is cleared:

   ```
   [Perception: the visitor's face looks angry.]
   Why is the sky blue?
   ```

5. This combined text is one `user` message sent to the model with the full history. The note stays in the history, so the model still sees it on later turns. The note itself is only added once, for one message.

The note is not sent as a second `system` message because some models accept only one system message, at the very start.

## Who decides how Eda reacts?

The model does. There is no `if emotion == "angry"` logic in the code. The model reads the note as part of the user's message and adjusts its reply (tone, empathy, wording) using what it learned in training. The persona in the system prompt (original, pirate, teacher) also shapes the reaction, so an angry visitor gets a different reply from each persona.

## Does Eda learn from emotions?

No. The model's weights are fixed and it is stateless. It only "remembers" because `messages` is re-sent on every call. Nothing in a chat changes the model.

## How the model learned tone, empathy and wording

The model learned these in three training stages. Chatting with Eda teaches it nothing.

1. **Pre-training.** The model reads a huge amount of human text and learns to predict the next word. That text is full of patterns:
   - Tone: angry messages are often short and blunt, polite ones have "please" and "thank you", pirate speech has "arr" and "ye".
   - Empathy: "I'm so upset" is usually followed by "I'm sorry to hear that", not a joke or a fact. Learning this makes the prediction more accurate. Nobody told the model that empathy is good.
   - Wording: it learns which phrases go with which situations, such as "I understand how frustrating this must be" for a complaint.
2. **Instruction tuning.** The model is trained on examples of good assistant conversations (a request followed by a good answer), so it learns to answer in a clear, polite, patient tone.
3. **Preference training (RLHF or similar).** Humans or other models compare answers and rate which is better. Warm replies to a stressed user are preferred over cold or rude ones, and the weights are adjusted toward them.

At runtime none of this is learned again. The persona and the perception note are only context. The model finds matching patterns from training and combines them. For example, a pirate persona with an angry visitor works because it has seen pirate text and angry-visitor text separately, not that exact combination.

Everything here is learned imitation of patterns in text. The model has no experience of being angry or comforted. It reproduces what comforting text looks like.

## How emotion works inside an LLM

- There is no dedicated "emotion weight" and no emotion module. Knowledge about emotion is spread across billions of weights.
- During training the model learned from human text that angry, sad or happy people write and are answered in certain ways. To predict the next word well, it built internal representations of emotion concepts.
- Interoperability research (probing, representation engineering, sparse autoencoder features) finds directions in the model's activation space that respond to emotional content, stated or implied. Steering along such a direction changes the tone of the output, so these directions are causally involved.

- The word "angry" in the note activates these learned representations, which change which next words are likely. That is why a text note is enough.
- This does not mean the model feels the emotion. It represents emotion as a concept to produce fitting text. There is no evidence of experience.
- The model does not see faces. A real camera model, trained on images, would have to turn the face into text first, the same way `/face` does by hand.

## Limits and ideas

- **The note is a hint, not a command.** The model decides how to react by itself, and it may ignore the perception note. To check how much the note matters, send the same message with and without `/face` and compare the replies. --In a test, the two replies were not very different. The reply with the note was more apologetic and used softer tone, more conversational words. The reply without the note was more encouraging.
- **You can make the note matter more.** Add a rule to the persona, e.g. "If a perception note says the visitor looks upset, respond with empathy first."
- **You can automate the note.** Instead of typing `/face`, let a real emotion classifier (for example one that reads the camera image) write the same `[Perception: ...]` note. The model's side stays unchanged.
