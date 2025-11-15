from app.utils.audio_transcribe import transcribe_audio
from app.services.Seperate_pateint_context import extract_patient_context_from_transcript
from app.utils.ProcessAudio import process_audio
import warnings
warnings.filterwarnings("ignore", category=FutureWarning)
import os

async def get_patient_context_from_audio(audio_path: str) -> dict:
    clean_path = await process_audio(audio_path)

    transcript = transcribe_audio(clean_path)

    # Now safe to delete
    if os.path.exists(clean_path):
        os.remove(clean_path)

    return extract_patient_context_from_transcript(transcript)



#Example :
if __name__ == "__main__":
    path ="videoplayback.weba"
    l = get_patient_context_from_audio(path)
    print(l)