# server called by: 1) ar glasses to record and 2) frontend to do live queries

from flask import Flask, send_file, request
import flask
from flask_cors import CORS

from utils import caption, face, tags, transcript,  s3
from collections import defaultdict
# from datetime import datetime
from moviepy.editor import VideoFileClip
import math
import ast
import os
import base64
import requests

app = Flask(__name__)
CORS(app)

UPLOAD_FOLDER = '/uploads'
ALLOWED_EXTENSIONS = set(['txt', 'pdf', 'png', 'jpg', 'jpeg', 'gif'])
app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER

"""
UPLOAD PHOTO
"""
@app.route('/upload-photo', methods=["POST"])
def upload_photo():
    
    print("\nupload endpoint hit.")

    data = request.get_json()
    print("got file")
    imageUrl = data["imageUrl"] 
    name = data["name"]
    # print("imageUrl: ", imageUrl, "name: ", name)
    upload_path = f"photos/{name}.jpg"
    file_source = f"uploads/{upload_path}"
    with open(file_source, "wb") as fh:
        imgdata = base64.b64decode(imageUrl)
        fh.write(imgdata)
    
    # save file to s3
#     current_time = time.strftime("%H-%M-%S", time.localtime())
    # upload_path=f"uploads/{datatype}/{filename}"
    # print(f"Uploading {filename} to {upload_path}...")
    s3.upload_file(file_source=file_source, upload_path=upload_path, bucket="forever-videos")
    s3_url = "https://forever-videos.s3.us-east-1.amazonaws.com/" + upload_path
  
    return f"Uploaded at: {s3_url}, local path at: {file_source}" 


def get_tag_clips(tag_timeline, tags):
    """
    [{"start": time, "end": time}, {"start": time, "end": time}, ...]
    """
    tag_clips_status = {tag: False for tag in tags}
    tag_clips = defaultdict()
    for i in tag_timeline.keys():
        for tag in tags:
            if tag in tag_timeline[i] and tag_clips_status[tag] == False:
                tag_clips[face].append({"start": i, "end": None})
                tag_clips_status[face] = True
            elif tag not in tag_timeline[i] and tag_clips_status[face] == True:
                tag_clips[face][-1]["end"] = i
                tag_clips_status[face] = False 
                
    return tag_clips

def get_face_clips(face_timeline, faces):
    """
    {face: [{"start": time, "end": time}, {"start": time, "end": time}, ...], ...}
    """
    face_clips = {face: [] for face in faces}
    last_face = None
    last_face_start = 0
    for i in face_timeline.keys():

        current_face = face_timeline[i]
        if current_face != last_face:
            face_clips[last_face].append({"start": last_face_start, "end": i-1})
            last_face_start = i
            
        last_face = current_face
    del face_clips[None]
    return face_clips

"""
LIVE SEARCH
{
query: "query",
caption_timeline: caption_timeline,
transcript_timeline: transcript_timeline,
}
"""
@app.route('/search', methods=["POST"])
def search():
    
    print("\nsearch endpoint hit.")
    data = request.get_json()
    query = data["query"]
    caption_timeline = data["caption_timeline"]
    transcript_timeline = data["transcript_timeline"]
    
    query_timeline = tags.get_timeline(caption_timeline, tags_timeline=caption_timeline) # things assumed continuous unless interval > 5 frames

    query_clips = get_tag_clips(query_timeline, query)
    
    response = {
        "query_clips": query_clips
    }

    return response

"""
BATCH PROCESS
batch process videos at the end of a recording session for static labels
{
video_path: "video_path",
faces: ["person_url", "person_url", "person_url"],
tags: ["tag", "tag", "tag"] (demo: conversations, objects)
}
"""
@app.route('/batch-process', methods=["POST"])
def batch_process():
    
    print("\nbatch-process endpoint hit.")
    data = request.get_json()
    faces = ast.literal_eval(data["faces"]) # list of faces
    base_url = "https://forever-videos.s3.us-east-1.amazonaws.com/"
    faces_dict  = {face : base_url + "photos/" + face for face in faces}
    for face in faces_dict:

        img_data = requests.get(faces_dict[face]).content
        with open(f'faces/{face}.jpg', 'wb') as handler:
            handler.write(img_data)

    tag = ast.literal_eval(data["tags"]) # list of tags
    video_path = data["video_path"]
    
    # process into frames: https://superuser.com/questions/135117/how-to-extract-one-frame-of-a-video-every-n-seconds-to-an-image
    interval = 4 # every four seconds
    rate = 1/interval
    os.system(f"ffmpeg -i {video_path} -r {rate} video_frames_dir/%d.png")
    video_frames_dir = "video_frames_dir"
    
    """
    get timelines
    for faces, in the form:
    {
    0: "face",
    1: "face",
    2: "face",
    ...
    }
    for caption and transcript, in the form:
    {
    0: "caption / transcript",
    1: "caption / transcript",
    2: "caption / transcript",
    ...
    }
    """

    clip = VideoFileClip(video_path)
    starter_dict = {i : None for i in range(math.floor(clip.duration))}
        
    face_timeline = face.get_timeline(video_frames_dir=video_frames_dir, face_timeline=starter_dict)
    print("face_timeline: ", face_timeline)
    caption_timeline = caption.get_timeline(video_frames_dir=video_frames_dir,face_timeline=starter_dict)
    print("caption_timeline: ", caption_timeline)
    transcript_timeline = transcript.get_timeline(video_path=video_path, transcript_timeline=starter_dict)
    print("transcript_timeline: ", transcript_timeline)

    # for dev purposes:
    transcript_timeline = starter_dict
                           
    tag_timeline = tags.get_timeline(caption_timeline=caption_timeline, transcript_timeline=transcript_timeline, tags_timeline=starter_dict) 
    print("tag_timeline: ", tag_timeline)

    face_clips = get_face_clips(face_timeline, faces)
    tag_clips = get_tag_clips(tag_timeline, tags)
    
    """
    get conversation clips
    [{"start": time, "end": time}, {"start": time, "end": time}, ...]
    """
    
    # search_and_store_tags(caption_timeline, transcript_timeline)
    response = {
        # to save with video data
        "caption_timeline": caption_timeline,
        "transcript_timeline": transcript_timeline,
        "face_clips": face_clips,
        "tag_clips": tag_clips
    }
    
    return response

# RUN SERVER
if __name__ == '__main__':
    print("*** Forever Server ***")
    app.run(host='0.0.0.0', port=3000, threaded=True)
   