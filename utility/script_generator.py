import os
from dotenv import load_dotenv
load_dotenv()
from groq import Groq
import json

# Inicializamos el cliente (leerá la clave del archivo .env automáticamente)
client = Groq(api_key=os.environ.get("GROQ_API_KEY"))

# Definimos el nombre exacto del modelo que obtuvimos de tu lista
MODEL_NAME = "openai/gpt-oss-120b"

def generate_script(topic):
    prompt = (
        """You are a seasoned content writer for a YouTube Shorts channel, specializing in mystery, paranormal, and conspiracy theories. 
        Your shorts are concise, each lasting approximately 3 minutes (approximately 450-500 words). 
        They are incredibly engaging, mysterious, and original. When a user requests a specific topic, you will create it.

        Keep it brief, highly interesting, and unique. Use a suspenseful tone.

        Strictly output the script in a JSON format like below, and only provide a parsable JSON object with the key 'script'.

        # Output
        {"script": "Here is the script ..."}
        """
    )

    response = client.chat.completions.create(
            model=MODEL_NAME,
            messages=[
                {"role": "system", "content": prompt},
                {"role": "user", "content": topic}
            ]
        )
    content = response.choices[0].message.content
    try:
        # Basic cleanup of common JSON formatting issues
        content = content.strip()
        # Parse JSON directly
        response_dict = json.loads(content)
        script = response_dict["script"]
    except Exception as e:
        print(f"Error parsing script: {e}")
        print("Raw content:", content)
        script = "Failed to generate script. Please try again."

    return script