from gtts import gTTS
import os

async def generate_audio(text, output_file):
    """
    Genera un archivo de audio a partir de un texto usando gTTS (Google TTS).
    """
    try:
        print(f"Generando audio con gTTS para: {text[:80]}...")
        # gTTS guarda directamente en formato MP3
        tts = gTTS(text=text, lang='en', slow=False)
        tts.save(output_file)
        print(f"Audio guardado en: {output_file}")
        return True
    except Exception as e:
        print(f"Error generating audio with gTTS: {e}")
        return False