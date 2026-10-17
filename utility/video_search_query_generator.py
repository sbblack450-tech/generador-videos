import os
from dotenv import load_dotenv
load_dotenv()
from groq import Groq
import json

client = Groq(api_key=os.environ.get("GROQ_API_KEY"))
MODEL_NAME = "openai/gpt-oss-120b"

def getVideoSearchQueriesTimed(script, timed_captions):
    # Extraer el texto completo del guion
    full_text = script
    
    prompt = f"""You are a video editor. Given the following script, generate short, simple 1-2 word English search terms for finding background videos on stock video sites. 

IMPORTANT RULES:
- Use ONLY simple English words like: mystery, dark, fog, forest, night, city, fire, ruins, church, candle, moon, storm, rain, ocean, mountain, cave, tunnel, library, book, old, abandoned, ghost, shadow, secret, symbol, map, sky, stars
- NEVER use long phrases or sentences
- Each term must be 1-2 words maximum
- Output ONLY a JSON with key "queries" containing a list of 3 to 5 terms

Script: {full_text[:500]}

Output: {{"queries": ["dark forest", "old book", "fog", "mystery", "night sky"]}}"""

    try:
        response = client.chat.completions.create(
            model=MODEL_NAME,
            messages=[{"role": "user", "content": prompt}]
        )
        content = response.choices[0].message.content.strip()
        # Limpiar posibles bloques de código
        if "```" in content:
            content = content.split("```")[1]
            if content.startswith("json"):
                content = content[4:]
        data = json.loads(content)
        queries = data.get("queries", ["mystery", "dark", "fog"])
    except Exception as e:
        print(f"Error generando queries: {e}")
        queries = ["mystery", "dark", "fog", "night", "forest"]

    # Asignar las mismas queries a todos los intervalos de tiempo
    timed_queries = []
    for interval in timed_captions:
        timed_queries.append((interval[0], queries))
    
    return timed_queries


def merge_empty_intervals(timed_video_urls):
    # Rellenar URLs vacías con la anterior disponible
    if not timed_video_urls:
        return timed_video_urls
    
    last_url = None
    for item in timed_video_urls:
        if item[1]:
            last_url = item[1]
        else:
            item[1] = last_url
    
    return timed_video_urls