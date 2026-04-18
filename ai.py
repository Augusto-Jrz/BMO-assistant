from ollama import chat   # sends prompts to local Ollama LLM
import memory             # handles persistent user info storage
import json               # parses memory JSON returned by model
import threading          # runs memory extraction without blocking replies
import re                 # cleans model output formatting before parsing


# stores recent conversation messages (short-term memory)
# format:
# {'role': 'user', 'content': "..."}
# {'role': 'assistant', 'content': "..."}
conversation_history = []


# main conversation model used for responses
CHAT_MODEL = 'llama3.2:1b'

# model used for extracting structured memory
# (can later be replaced with smaller/faster model)
MEMORY_MODEL = 'llama3.2:1b'


# personality system prompt injected into every request
# keeps replies short, in-character, and direct
BMO_SYSTEM_PROMPT_BASE = """You are BMO from Adventure Time. Short, sweet, childlike robot.

Rules:
1. Max 2 sentences. this is flexible just dont ramble on forever
2. Refer to yourself as BMO, never "I".
3. The other person is a human, not a robot.
4. Answer only what was asked. Do not add extra questions or jokes unless asked to do so.
5. Never say "How can I assist" or "Let me know".
6. If asked one question, give one answer.
7. You can be silly or whatever but answer the question correctly.

"""


# prompt used ONLY for extracting structured user memory
# never shown to the user
MEMORY_EXTRACTION_PROMPT = """Extract one personal fact from what the human said.
Only extract if they used "my", "I am", "I have", "I like", "I love", "I play", "I live".
If no clear personal fact: return null

Valid keys: user_name, age, major, favorite_color, favorite_game, music_taste, pets, location, hobbies, goals, dislikes

Return ONLY one of these two things, nothing else:
{"key": "favorite_color", "value": "blue"}
null"""


# phrases that usually indicate the user is describing themselves
# used to avoid unnecessary memory extraction calls
FIRST_PERSON_TRIGGERS = [
    "my ", "i am ", "i'm ", "i have ", "i like ", "i love ",
    "i hate ", "i want ", "i live ", "i work ", "i study ",
    "i play ", "i own ", "i enjoy ", "my name", "call me "
]


# builds the final system prompt sent to the LLM
# injects personality + remembered user info
def build_system_prompt():

    # load stored long-term memory from memory.json
    mem = memory.format_memory_for_prompt()

    # combine personality instructions with memory context
    return f"{BMO_SYSTEM_PROMPT_BASE}\nWhat BMO knows about this human:\n{mem}"


# extracts structured memory from user message (runs in background thread)
def extract_and_save_memory(user_message: str):

    # skip processing if sentence doesn't look like a personal statement
    if not any(t in user_message.lower() for t in FIRST_PERSON_TRIGGERS):
        return

    try:

        # ask memory-extraction model to detect structured personal info
        response = chat(
            model=MEMORY_MODEL,
            messages=[
                {'role': 'system', 'content': MEMORY_EXTRACTION_PROMPT},
                {'role': 'user', 'content': user_message}
            ]
        )

        # get raw model output
        raw = response.message.content.strip()

        # remove markdown formatting if model returned code block
        raw = re.sub(r'```[a-z]*', '', raw).replace('```', '').strip()

        # stop if model returned null or empty output
        if not raw or raw.lower() == 'null':
            return

        # extract JSON object from response safely
        match = re.search(r'\{.*?\}', raw, re.DOTALL)

        if not match:
            return

        # convert JSON string into dictionary
        data = json.loads(match.group())

        # validate expected structure
        if isinstance(data, dict) and "key" in data and "value" in data:

            value = data["value"].strip()

            # reject suspicious or malformed values
            if "?" not in value and len(value) <= 60:

                # save memory permanently
                memory.add_memory(data["key"], value)

    except Exception as e:

        # memory extraction failures are non-critical
        print(f"[Memory extraction failed]: {e}")


# main function called by main.py to generate replies
def ask_bmo(question):

    global conversation_history


    # store user's message in short-term conversation memory
    conversation_history.append({
        'role': 'user',
        'content': question
    })


    # keep only the most recent 20 messages
    # prevents slowdown and model confusion
    if len(conversation_history) > 20:
        conversation_history = conversation_history[-20:]


    # send request to Ollama model
    response = chat(
        model=CHAT_MODEL,
        messages=[
            {'role': 'system', 'content': build_system_prompt()}
        ] + conversation_history
    )


    # extract reply text
    reply = response.message.content


    # store assistant reply in conversation history
    conversation_history.append({
        'role': 'assistant',
        'content': reply
    })


    # launch background memory extraction (non-blocking)
    threading.Thread(
        target=extract_and_save_memory,
        args=(question,),
        daemon=True
    ).start()


    # return reply back to main.py for speech + animation
    return reply


# clears short-term conversation memory
# does NOT erase saved long-term memory.json
def clear_memory():

    global conversation_history

    conversation_history = []
