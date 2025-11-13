import os
from pydub import AudioSegment, effects
from scipy.io.wavfile import write
import librosa
import noisereduce as nr
import numpy as np

async def process_audio(recording_path: str) -> str:
    """
    Async audio normalization + noise reduction.
    """
    FS = 16000
    OUTPUT_DIR = "recordings"
    os.makedirs(OUTPUT_DIR, exist_ok=True)

    # Normalize
    audio = AudioSegment.from_wav(recording_path)
    normalized_audio = effects.normalize(audio)
    normalized_path = os.path.join(OUTPUT_DIR, "normalized.wav")
    normalized_audio.export(normalized_path, format="wav")

    # Noise Reduction
    y, sr = librosa.load(normalized_path, sr=FS)
    reduced_noise = nr.reduce_noise(y=y, sr=sr, prop_decrease=0.8)

    clean_path = os.path.join(OUTPUT_DIR, "final_clean.wav")
    write(clean_path, sr, (reduced_noise * 32767).astype(np.int16))

    return clean_path
