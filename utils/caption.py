import os
import requests
import json
import gradio as gr

def caption_photo(photo_path):
    
    photo_url = gr.processing_utils.encode_url_or_file_to_base64(photo_path)
    r = requests.post(url='https://hf.space/embed/akhaliq/CLIP_prefix_captioning/+/api/predict/', json={"data": [photo_url,"conceptual-captions"]})
    r.json()
    result = json.loads(r.text)['data'][0]
    return result

def get_timeline(video_frames_dir, caption_timeline):
    for i in caption_timeline.keys():
        caption = caption_photo(f"{video_frames_dir}/{i}.png")
        caption_timeline[i] = caption
    return caption_timeline