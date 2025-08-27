# /opt/script/modules/transcription.py

from faster_whisper import WhisperModel

print("🚀 Initialisiere Whisper-Modell …")
fw_model = WhisperModel("small", device="cuda", compute_type="float16")

def transkribiere_audio(wav_path: str) -> str:
    try:
        segments, _ = fw_model.transcribe(wav_path, beam_size=5, language="de")
        text = " ".join([segment.text.strip() for segment in segments]).strip()
        print(f"📝 Erkannter Text (Whisper): {repr(text)}")
        return text
    except Exception as e:
        print(f"❌ Fehler bei Transkription: {e}")
        return ""
