import json
import os


# file where long-term memory is stored
MEMORY_FILE = "memory.json"


# only these keys are allowed to be saved
# prevents the AI from inventing random categories
ALLOWED_MEMORY_KEYS = {
    "user_name",
    "age",
    "major",
    "favorite_color",
    "favorite_game",
    "music_taste",
    "preferred_time_of_day",
    "pets",
    "location",
    "hobbies",
    "goals",
    "dislikes"
}


# values that should never be saved
# prevents hallucinated or useless memory entries
INVALID_VALUES = {
    "",
    "null",
    "none",
    "unknown",
    "helpful",
    "bmo"
}


# alternate key spellings mapped to valid schema keys
KEY_ALIASES = {
    "name": "user_name",
    "users_name": "user_name",
    "user's_name": "user_name",
    "username": "user_name",
    "favourite_color": "favorite_color",
    "favorite_colour": "favorite_color",
}


# loads memory.json safely
def load_memory():

    # if file doesn't exist yet, return empty memory
    if not os.path.exists(MEMORY_FILE):
        return {}

    try:
        with open(MEMORY_FILE, "r") as f:
            data = json.load(f)

            # ensure file actually contains dictionary
            if isinstance(data, dict):
                return data
            else:
                return {}

    # catches corrupted JSON file errors
    except Exception:
        return {}



# saves dictionary to memory.json
def save_memory(memory: dict):

    try:
        with open(MEMORY_FILE, "w") as f:
            json.dump(memory, f, indent=2)

    except Exception as e:
        print(f"[Memory save failed]: {e}")



# adds or updates stored memory entry
def add_memory(key: str, value: str):

    # normalize key formatting
    key = key.strip().lower().replace(" ", "_")

    # normalize value formatting
    value = value.strip()

    # apply alias corrections
    key = KEY_ALIASES.get(key, key)


    # reject invalid keys
    if not key or key not in ALLOWED_MEMORY_KEYS:
        print(f"[Memory ignored] invalid key: {key}")
        return


    # reject invalid values
    if value.lower() in INVALID_VALUES:
        print(f"[Memory ignored] invalid value: {value}")
        return


    memory = load_memory()


    # avoid rewriting identical values
    if memory.get(key) == value:
        return


    # save new memory
    memory[key] = value
    save_memory(memory)

    print(f"[Memory saved] {key}: {value}")



# removes stored memory entry
def forget(key: str):

    memory = load_memory()

    key = key.strip().lower().replace(" ", "_")

    if key in memory:

        del memory[key]

        save_memory(memory)

        print(f"[Memory removed] {key}")



# formats memory for insertion into AI system prompt
def format_memory_for_prompt() -> str:

    memory = load_memory()

    # fallback text if nothing stored yet
    if not memory:
        return "BMO does not know anything about this person yet."

    # convert dictionary into readable lines
    lines = [
        f"{k.replace('_', ' ')}: {v}"
        for k, v in memory.items()
    ]

    return "\n".join(lines)
