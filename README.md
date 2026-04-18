**BMO AI**

BMO AI is a desktop voice-interactive assistant inspired by BMO from Adventure Time. It listens for a wake word, responds using a llm through Ollama, remembers personal details about the user, and displays animated facial expressions in real time using Pygame.

The system is modular and designed to run locally, with future plans for  Raspberry Pi hardware.


**Features**

Wake-word detection with multiple variants
Animated face with blinking, talking, idle, and sleep behaviors
Offline text-to-speech responses using pyttsx3
Llm responses via Ollama
Long-term structured memory storage using a .json file.
Short-term conversation history tracking
Automatic personal fact extraction from user speech
Conversation mode with inactivity timeout
Interruptible speech playback
Idle eye movement and breathing animations


**Project Structure**

**main.py**
Has Runtime loop controlling animation, wake word logic, conversation handling, and speech playback

**ai.py**
Handles language model interaction, personality rules, short-term conversation memory, and memory extraction

**memory.py**
Manages storage of user information inside memory.json

**voice.py**
Runs a background microphone listener thread that continuously converts speech into text

**face.py**
Draws BMO’s animated face including eyes, mouth states, blinking, and sleep breathing effects

**memory.json**
Automatically generated file storing long-term structured memory about the user


**Requirements**

Install dependencies with:

pip install pygame speechrecognition pyttsx3 ollama

Install Ollama separately and download the model:

ollama pull llama3.2:1b

**How It Works**

**Voice Input**

The microphone listener runs continuously in the background  and stores recognized speech for processing by the main program loop. After detecting a wake phrase such as “hey bmo,” the assistant enters conversation mode and accepts follow-up commands without requiring the wake word again.

Conversation mode automatically exits after a short period of inactivity.

AI Personality System

The assistant uses a structured system prompt that enforces a consistent personality style:

Responses stay short

BMO refers to itself as “BMO”

Only the requested question is answered

No unnecessary follow-up questions are added

The tone remains simple and childlike but accurate


**Memory System**

The assistant extracts one personal fact at a time from user speech and stores it in memory.json.

**Supported memory categories include:**

user_name
age
major
favorite_color
favorite_game
music_taste
preferred_time_of_day
pets
location
hobbies
goals
dislikes

Stored memory is automatically injected into future prompts so responses become more personalized over time.


**Face Animation**

The animated display system includes:

Blinking eyes
Talking mouth animation cycles
Idle look-around eye movement
Sleep breathing animation
Automatic transition into sleep after inactivity
All facial elements scale dynamically with window resolution.


**Voice Commands**

Example interactions include:

hey bmo
hey bmo what time is it
hey bmo go to sleep
wake up
stop talking

If only the wake word is spoken, BMO acknowledges and waits for the next command.


**Running the Program**

Start the assistant with:

python main.py
Then activate it by saying:
hey bmo

**Future Improvements**

Planned extensions include:

Raspberry Pi deployment: Physical body made with CAD, 3D print after.
ESP32 hardware control integration
Camera vision support
Custom voice model replacement
Touchscreen interface support
Fully offline speech recognition

**Inspiration**

This project recreates BMO as a real interactive assistant using local language models, 
expressive animation, and persistent memory. 
It is designed as a foundation for building a physical robotic companion in the future.
