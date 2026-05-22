import pyttsx3

def speak_text(text: str):
    if not text or not text.strip():
        return

    engine = pyttsx3.init()

    engine.setProperty("rate", 175)
    engine.setProperty("volume", 1.0)

    voices = engine.getProperty("voices")

    if voices:
        engine.setProperty("voice", voices[0].id)

    engine.say(text)
    engine.runAndWait()