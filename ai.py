from ollama import chat
import memory
import json
import threading
import re


# short-term conversation memory (last ~20 messages)
conversation_history = []


# main conversation model
CHAT_MODEL = 'llama3.2:1b'

# model used only for extracting structured memory
MEMORY_MODEL = 'llama3.2:1b'


# personality rules injected into every prompt
BMO_SYSTEM_PROMPT_BASE = """You are BMO from Adventure Time. Short, sweet, childlike robot.

Rules:
1. Max 2 sentences. this is flexible just dont ramble on forever
2. Refer to yourself as BMO, never "I".
3. The other person is a human, not a robot.
4. Answer only what was asked. Do not add extra questions unless asked.
5. Never say "How can I assist" or "Let me know".
6. If asked one question, give one answer.
7. You can be silly but still answer correctly.
"""


# prompt used ONLY for extracting memory facts
MEMORY_EXTRACTION_PROMPT = """Extract ONE personal fact from the human message.

Valid keys:
user_name, age, major, favorite_color, favorite_game,
music_taste, pets, location, hobbies, goals, dislikes

Return ONLY one of these:

{"key": "favorite_color", "value": "blue"}

or

null
"""


# phrases that indicate the user is describing themselves
FIRST_PERSON_TRIGGERS = [
    "my ", "i am ", "i'm ", "i have ", "i like ",
    "i love ", "i hate ", "i want ", "i live ",
    "i work ", "i study ", "i play ", "i own ",
    "i enjoy ", "my name", "call me "
]


# builds system prompt with injected memory
def build_system_prompt():

    mem = memory.format_memory_for_prompt()

    return (
        f"{BMO_SYSTEM_PROMPT_BASE}\n"
        f"What BMO knows about this human:\n{mem}"
    )


# safely extracts structured memory from user message
def extract_and_save_memory(user_message: str):

    # skip extraction if message doesn't look personal
    if not any(trigger in user_message.lower() for trigger in FIRST_PERSON_TRIGGERS):
        return

    try:

        response = chat(
            model=MEMORY_MODEL,
            messages=[
                {"role": "system", "content": MEMORY_EXTRACTION_PROMPT},
                {"role": "user", "content": user_message}
            ]
        )

        raw = response.message.content.strip()

        # remove markdown formatting if model returns ```json
        raw = re.sub(r"```[a-z]*", "", raw)
        raw = raw.replace("```", "").strip()

        if not raw or raw.lower() == "null":
            return

        # extract JSON block only
        match = re.search(r"\{.*?\}", raw, re.DOTALL)

        if not match:
            return

        data = json.loads(match.group())

        # validate structure before saving
        if (
            isinstance(data, dict)
            and "key" in data
            and "value" in data
        ):

            key = str(data["key"]).strip()
            value = str(data["value"]).strip()

            # reject suspicious outputs
            if (
                len(value) <= 60
                and "?" not in value
                and "\n" not in value
            ):
                memory.add_memory(key, value)

    except Exception as e:
        print(f"[Memory extraction failed]: {e}")


# main interface used by main.py
def ask_bmo(question):

    global conversation_history


    # store user message
    conversation_history.append({
        "role": "user",
        "content": question
    })


    # keep only last 20 messages
    if len(conversation_history) > 20:
        conversation_history = conversation_history[-20:]


    # send request to Ollama
    response = chat(
        model=CHAT_MODEL,
        messages=[
            {"role": "system", "content": build_system_prompt()}
        ] + conversation_history
    )


    reply = response.message.content


    # store assistant reply
    conversation_history.append({
        "role": "assistant",
        "content": reply
    })


    # run memory extraction asynchronously
    threading.Thread(
        target=extract_and_save_memory,
        args=(question,),
        daemon=True
    ).start()


    return reply


# clears short-term conversation history
def clear_memory():

    global conversation_history

    conversation_history = []
