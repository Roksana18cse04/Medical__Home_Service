import os
from pydub import AudioSegment, effects
from scipy.io.wavfile import write
import librosa
import noisereduce as nr
import numpy as np
from app.core.config import UPLOAD_FOLDER
async def process_audio(recording_path: str) -> str:
    FS = 16000
    OUTPUT_DIR = UPLOAD_FOLDER
    os.makedirs(OUTPUT_DIR, exist_ok=True)

    # Use format-auto detection
    audio = AudioSegment.from_file(recording_path)
    normalized_audio = effects.normalize(audio)

    normalized_path = os.path.join(OUTPUT_DIR, "patient_normalized.wav")
    normalized_audio.export(normalized_path, format="wav")

    # Noise Reduction
    y, sr = librosa.load(normalized_path, sr=FS)
    reduced_noise = nr.reduce_noise(y=y, sr=sr, prop_decrease=0.8)

    clean_path = os.path.join(OUTPUT_DIR, "patient_final.wav")
    write(clean_path, sr, (reduced_noise * 32767).astype(np.int16))

    return clean_path  
