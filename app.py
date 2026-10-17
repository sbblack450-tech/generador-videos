import os
# ============================================================
# CONFIGURACIÓN PARA USAR EL DISCO D Y EVITAR ERRORES DE ESPACIO
# ============================================================
# Crear carpeta temporal en D: si no existe
TEMP_DIR = r"D:\temp_video"
os.makedirs(TEMP_DIR, exist_ok=True)
os.environ['TEMP'] = TEMP_DIR
os.environ['TMP'] = TEMP_DIR

# Forzar el uso del FFmpeg incluido con imageio-ffmpeg
os.environ['IMAGEIO_FFMPEG_EXE'] = 'ffmpeg'

# Configurar ImageMagick (ya lo tenías)
import moviepy.config as mpy_config
mpy_config.IMAGEMAGICK_BINARY = r"C:\Program Files\ImageMagick-7.1.2-Q16-HDRI\magick.exe"
mpy_config.FFMPEG_BINARY = r"C:\ffmpeg\bin\ffmpeg.exe"  # <--- AÑADE ESTA LÍNEA

# ============================================================
# IMPORTACIONES NORMALES
# ============================================================
import gradio as gr
from dotenv import load_dotenv
load_dotenv()
from openai import OpenAI
import edge_tts
import json
import asyncio
import whisper_timestamped as whisper
from utility.script_generator import generate_script
from utility.audio_generator import generate_audio
from utility.timed_captions_generator import generate_timed_captions
from utility.background_video_generator import generate_video_url
from utility.render_engine import get_output_media
from utility.video_search_query_generator import getVideoSearchQueriesTimed, merge_empty_intervals

async def generate_video(topic, progress=gr.Progress()):
    try:
        # Ensure audio directory exists
        os.makedirs("audio", exist_ok=True)
        
        SAMPLE_FILE_NAME = os.path.join("audio", "audio_tts.mp3")
        VIDEO_SERVER = "pixabay"
        
        progress(0.1, desc="Generating script...")
        response = generate_script(topic)
        
        progress(0.3, desc="Generating audio...")
        await generate_audio(response, SAMPLE_FILE_NAME)
        
        progress(0.5, desc="Generating captions...")
        timed_captions = generate_timed_captions(SAMPLE_FILE_NAME)
        
        progress(0.6, desc="Generating search terms...")
        search_terms = getVideoSearchQueriesTimed(response, timed_captions)
        
        if search_terms is not None:
            progress(0.7, desc="Fetching background videos...")
            background_video_urls = generate_video_url(search_terms, VIDEO_SERVER)
            background_video_urls = merge_empty_intervals(background_video_urls)
            
            if background_video_urls is not None:
                progress(0.9, desc="Rendering final video...")
                video = get_output_media(SAMPLE_FILE_NAME, timed_captions, background_video_urls, VIDEO_SERVER)
                return video, "Video generated successfully!"
            
        return None, "Failed to generate video. No suitable background videos found."
    
    except Exception as e:
        return None, f"Error: {str(e)}"

# Create Gradio interface
def create_interface():
    with gr.Blocks(theme=gr.themes.Soft()) as demo:
        gr.Markdown(
            """
            # AI Video Generator
            Generate engaging videos from any topic using AI
            """
        )
        
        with gr.Row():
            with gr.Column():
                topic_input = gr.Textbox(
                    label="Enter Your Topic",
                    placeholder="E.g., The history of artificial intelligence",
                    lines=2
                )
                generate_btn = gr.Button("Generate Video", variant="primary")
                
            with gr.Column():
                output_video = gr.Video(label="Generated Video")
                status_text = gr.Textbox(label="Status", interactive=False)
        
        generate_btn.click(
            fn=generate_video,
            inputs=[topic_input],
            outputs=[output_video, status_text]
        )
        
        gr.Markdown(
            """
            ### How it works:
            1. Enter a topic you want to create a video about
            2. Click 'Generate Video'
            3. Wait while the AI generates the script, audio, and matches appropriate visuals
            4. Download your finished video!
            """
        )
    
    return demo

if __name__ == "__main__":
    demo = create_interface()
    demo.launch(share=True)