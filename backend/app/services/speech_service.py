import tempfile
from pathlib import Path
import os

os.environ["HF_HUB_DISABLE_SYMLINKS_WARNING"] = "1"

import sounddevice as sd
from scipy.io.wavfile import write
from faster_whisper import WhisperModel

SAMPLE_RATE = 16000
CHANNELS = 1

_model = None

def get_whisper_model():
    global _model

    if _model is None:
        _model = WhisperModel("base", device="cpu", compute_type="int8")

    return _model

def record_audio(duration_seconds: int = 5):
    print(f"Recording for {duration_seconds} seconds...")

    audio = sd.rec(
        int(duration_seconds * SAMPLE_RATE),
        samplerate=SAMPLE_RATE,
        channels=CHANNELS,
        dtype="int16"
    )

    sd.wait()

    temp_file = tempfile.NamedTemporaryFile(
        suffix=".wav",
        delete=False
    )

    temp_path = Path(temp_file.name)
    temp_file.close()

    write(temp_path, SAMPLE_RATE, audio)

    return temp_path

def transcribe_audio(file_path: Path):
    model = get_whisper_model()

    segments, _ = model.transcribe(
        str(file_path),
        beam_size=5
    )

    transcript_parts = []

    for segment in segments:
        transcript_parts.append(segment.text.strip())

    return " ".join(transcript_parts).strip()

def listen_and_transcribe(duration_seconds: int = 5):
    audio_path = record_audio(duration_seconds)

    try:
        transcript = transcribe_audio(audio_path)
        return transcript
    finally:
        try:
            audio_path.unlink(missing_ok=True)
        except Exception:
            pass

