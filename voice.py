import speech_recognition as sr
import threading


# create recognizer object used for speech-to-text
recognizer = sr.Recognizer()


# shared variable read by main.py
# stores the most recent spoken command
last_command = None


def listen_loop():
    """
    Runs continuously in a background thread.
    Listens to microphone input and converts speech to text.
    Updates last_command whenever speech is recognized.
    """

    global last_command

    # open system microphone as input source
    with sr.Microphone() as source:

        # calibrate microphone to ignore background noise
        recognizer.adjust_for_ambient_noise(source, duration=1)

        # allow slightly longer pauses during speech
        recognizer.pause_threshold = 1.2

        # amount of silence allowed before speech considered finished
        recognizer.non_speaking_duration = 0.8

        while True:
            try:
                # listen until speaker stops naturally
                audio = recognizer.listen(source)

                # convert speech audio to lowercase text
                text = recognizer.recognize_google(audio).lower()

                # store command for main.py to process
                last_command = text

                print("Heard:", text)

            except sr.UnknownValueError:
                # speech detected but not understood
                pass

            except sr.RequestError:
                # internet/API unavailable
                pass

            except sr.WaitTimeoutError:
                # timeout waiting for speech (safe to ignore)
                pass


def start_listening():
    """
    Starts microphone listener in background daemon thread.
    Called once from main.py at startup.
    """

    thread = threading.Thread(
        target=listen_loop,
        daemon=True
    )

    thread.start()
