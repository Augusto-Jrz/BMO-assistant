import pygame
import sys
import face          # draws BMO's face (eyes + mouth animations)
import voice         # background microphone listener thread
import ai            # handles LLM conversation + personality + memory
import threading     # allows AI responses without freezing animation
import pyttsx3       # offline text-to-speech engine


# initialize pygame graphics system
pygame.init()


# window resolution
WIDTH, HEIGHT = 1200, 800

# create window surface
screen = pygame.display.set_mode((WIDTH, HEIGHT))

# window title
pygame.display.set_caption("BMO")


# BMO background color
GREEN = (127, 255, 212)

# controls animation frame timing (60 FPS)
clock = pygame.time.Clock()


# start microphone listener in background thread
voice.start_listening()


# current animation state
# possible: idle, sleep, open, open_small, mouth_half
state = "idle"


# blink animation progress (0=open, 1=closed)
anim = 0

# blink direction (1 = closing, -1 = opening)
blinkdirection = 0

# blink animation speed
speed = 0.12

# timestamp of last blink
last_blink_time = pygame.time.get_ticks()

# milliseconds between blinks
blink_interval = 5000


# main loop control flag
running = True

# used for timing mouth animation frames
frame_counter = 0


# talking animation cycle shapes
mouth_states = ["open", "open_small", "mouth_half"]

# current mouth animation index
mouth_index = 0

# True while BMO is speaking
talking = False

# used to interrupt speech early
cancelled = False


# idle eye movement direction (-1 left, 0 center, 1 right)
look_direction = 0

# timestamp of last eye movement
last_look = pygame.time.get_ticks()

# delay between eye movement steps
look_interval = 2000

# number of idle eye shifts performed
look_count = 0

# timestamp of last user interaction
last_active_time = pygame.time.get_ticks()

# current horizontal eye offset
eye_offset = 0

# target horizontal eye offset (smooth transition)
target_eye_offset = 0


# breathing animation variables (sleep mode only)
breath_amount = 0
breath_direction = 1
breath_speed = 0.65

# breathing limits
breath_min = int(WIDTH // -75)
breath_max = int(WIDTH * .125) // 4


# stores latest AI reply text
bmo_response = ''


# True after "hey bmo" but before actual command
waiting_for_command = False


# True while conversation mode is active (wake word no longer required)
active_conversation = False

# conversation auto-timeout duration (milliseconds)
CONVERSATION_TIMEOUT = 15000

# timestamp of last interaction during conversation
last_conversation_time = 0


# acceptable wake word variations
WAKE_WORDS = [
    "hey bmo",
    "hey beemo",
    "hey bimo",
    "hey be mo",
    "hey b mo",
    "hey bmoh",
    "hey vmo",
    "hey pmo",
    "hey nmo",
    "hey bno",
    "hey mo",
    "hey boo",
    "a bmo",
    "hey bm o",
]


# checks if input starts with a wake word
def is_wake_word(text):
    text = text.lower().strip()

    for w in WAKE_WORDS:
        if text.startswith(w):
            return True

    return False


# removes wake word from beginning of command
def strip_wake_word(text):
    text = text.lower().strip()

    for w in WAKE_WORDS:
        if text.startswith(w):
            return text[len(w):].strip()

    return text


# resets eyes back to center position
def reset_eyes():
    global look_direction, eye_offset, target_eye_offset

    look_direction = 0
    eye_offset = 0
    target_eye_offset = 0


# speaks text aloud using offline TTS
def speak(text):

    eng = pyttsx3.init()

    voices = eng.getProperty('voices')
    chosen = None

    # attempt to automatically choose a female voice if available
    for v in voices:
        name = v.name.lower()

        if any(w in name for w in [
            'zira', 'female', 'samantha',
            'karen', 'victoria', 'susan', 'hazel'
        ]):
            chosen = v.id
            break

    # fallback if preferred voices unavailable
    if chosen:
        eng.setProperty('voice', chosen)
    else:
        if len(voices) > 1:
            eng.setProperty('voice', voices[1].id)

    # speaking speed
    eng.setProperty('rate', 220)

    # volume level
    eng.setProperty('volume', 1.0)

    # speak text
    eng.say(text)
    eng.runAndWait()

    eng.stop()


# runs AI response in background thread
def run_ai(command):

    global bmo_response, talking, cancelled
    global state, look_count, last_conversation_time

    # reset idle behavior before responding
    state = "idle"
    look_count = 0

    # send command to LLM
    result = ai.ask_bmo(command)

    # exit if cancelled mid-response
    if cancelled:
        cancelled = False
        return

    # store response text
    bmo_response = result

    print(bmo_response)

    # enable talking animation
    talking = True

    reset_eyes()

    # speak response aloud
    speak(result)

    if not cancelled:
        talking = False

    # reset conversation timeout timer
    last_conversation_time = pygame.time.get_ticks()


# acknowledgement when user only says "hey bmo"
def acknowledge():

    global talking

    talking = True

    reset_eyes()

    ack = "Hmm?"

    print(f"BMO: {ack}")

    speak(ack)

    talking = False


# exits conversation mode and returns to idle listening behavior
def end_conversation():

    global active_conversation, waiting_for_command

    active_conversation = False
    waiting_for_command = False

    print("BMO: conversation ended")


# MAIN PROGRAM LOOP
while running:

    # lock animation to 60 FPS
    clock.tick(60)

    current_time = pygame.time.get_ticks()


    # detect window close event
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            running = False


    # BLINK SYSTEM

    # trigger blink after interval
    if current_time - last_blink_time > blink_interval and blinkdirection == 0:

        blinkdirection = 1
        last_blink_time = current_time


    # update blink animation progress
    anim += speed * blinkdirection

    if anim >= 1:
        anim = 1
        blinkdirection = -1

    if anim <= 0:
        anim = 0
        blinkdirection = 0


    # TALKING MOUTH ANIMATION

    frame_counter += 1

    if talking:

        last_active_time = current_time

        # cycle mouth shapes every 15 frames
        if frame_counter % 15 == 0:
            mouth_index = (mouth_index + 1) % len(mouth_states)

        mouth_state = mouth_states[mouth_index]

    else:
        mouth_state = "idle"


    # CONVERSATION TIMEOUT SYSTEM

    # if conversation active but no speech recently → exit conversation mode
    if active_conversation and not talking and not waiting_for_command:

        if current_time - last_conversation_time > CONVERSATION_TIMEOUT:

            end_conversation()

            print("BMO: conversation timed out")
