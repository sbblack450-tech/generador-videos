import os 
import requests
from utility.utils import log_response, LOG_TYPE_PEXEL

PIXABAY_API_KEY = os.environ.get('PIXABAY_API_KEY')

def search_videos(query_string, orientation_landscape=True):
    url = "https://pixabay.com/api/videos/"
    params = {
        "key": PIXABAY_API_KEY,
        "q": query_string,
        "orientation": "horizontal" if orientation_landscape else "vertical",
        "per_page": 15
    }

    response = requests.get(url, params=params)
    json_data = response.json()
    log_response(LOG_TYPE_PEXEL, query_string, json_data)
   
    return json_data


def getBestVideo(query_string, orientation_landscape=True, used_vids=[]):
    vids = search_videos(query_string, orientation_landscape)
    
    if 'hits' not in vids:
        print("No hits in Pixabay response:", vids)
        videos = []
    else:
        videos = vids['hits']

    video_urls = []
    for video in videos:
        if 'videos' not in video: 
            continue
            
        v_data = video['videos']
        v_info = v_data.get('large')
        if not v_info:
            v_info = v_data.get('medium')
        if not v_info: 
            continue

        width = v_info.get('width', 0)
        height = v_info.get('height', 0)
        url = v_info.get('url')
        duration = video.get('duration', 0)

        if not url: 
            continue
        
        # Filtrar por orientación y resolución (MÁXIMO 1920x1080 para evitar errores de memoria)
        if orientation_landscape:
            if 1280 <= width <= 1920 and 720 <= height <= 1080:
                video_urls.append((url, duration))
        else:
            if 720 <= width <= 1080 and 1280 <= height <= 1920:
                video_urls.append((url, duration))

    sorted_videos = sorted(video_urls, key=lambda x: abs(15 - x[1]))

    for video_url, _ in sorted_videos:
        clean_url = video_url.split('?')[0]
        if clean_url not in used_vids:
            return video_url

    # FALLBACK: Si no encontramos nada, probamos términos genéricos
    print(f"NO LINKS found for query '{query_string}'. Probando fallback...")
    fallback_terms = ["mystery", "dark", "fog", "night", "forest", "old book"]
    for term in fallback_terms:
        print(f"Fallback: buscando '{term}'...")
        fallback_data = search_videos(term, orientation_landscape)
        if 'hits' not in fallback_data:
            continue
        for video in fallback_data['hits']:
            if 'videos' not in video:
                continue
            v_data = video['videos']
            v_info = v_data.get('large') or v_data.get('medium')
            if not v_info:
                continue
            width = v_info.get('width', 0)
            height = v_info.get('height', 0)
            url = v_info.get('url')
            if not url:
                continue
            
            # APLICAMOS EL MISMO LÍMITE DE RESOLUCIÓN EN EL FALLBACK
            if orientation_landscape:
                if 1280 <= width <= 1920 and 720 <= height <= 1080:
                    clean_url = url.split('?')[0]
                    if clean_url not in used_vids:
                        print(f"Fallback exitoso con '{term}'")
                        return url
            else:
                if 720 <= width <= 1080 and 1280 <= height <= 1920:
                    clean_url = url.split('?')[0]
                    if clean_url not in used_vids:
                        print(f"Fallback exitoso con '{term}'")
                        return url

    return None


def generate_video_url(timed_video_searches, video_server):
        timed_video_urls = []
        
        if video_server == "pexel":
            used_links = []
            for (t1, t2), search_terms in timed_video_searches:
                url = ""
                for query in search_terms:
                    url = getBestVideo(query, orientation_landscape=True, used_vids=used_links)
                    if url:
                        used_links.append(url.split('.hd')[0])
                        break
                timed_video_urls.append([[t1, t2], url])
                
        elif video_server == "pixabay":
            used_links = []
            for (t1, t2), search_terms in timed_video_searches:
                url = ""
                for query in search_terms:
                    url = getBestVideo(query, orientation_landscape=True, used_vids=used_links)
                    if url:
                        used_links.append(url.split('?')[0])
                        break
                timed_video_urls.append([[t1, t2], url])
                
        elif video_server == "stable_diffusion":
            timed_video_urls = get_images_for_video(timed_video_searches)

        return timed_video_urls