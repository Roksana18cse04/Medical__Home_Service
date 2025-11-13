
import time
from faster_whisper import WhisperModel

# Load the medium model globally for reuse (more accurate but heavier)
model = WhisperModel("small", device="cuda", compute_type="float32")

def transcribe_audio(audio_path: str) -> str:
    start = time.time()
    
    # Convert to WAV if needed (make sure you have this function)
    
    # Transcribe audio using the medium model
    segments_generator, info = model.transcribe(audio_path)
    
    segments = list(segments_generator)
    
    print(f"Detected language: {info.language}")
    for segment in segments:
        print(f"[{segment.start:.2f} -> {segment.end:.2f}] {segment.text}")
    
    transcript = " ".join(segment.text for segment in segments)
    
    end = time.time()
    print(f"Transcription took {end - start:.2f} seconds")
    print(transcript)
    
    return transcript
