import face_recognition
import os
import sys


# encodes a list of faces of people and returns a list of encodings of the person
def generate_encodings(path, people, faces):
    if len(people) != len(faces):
        print("Error: number of people and number of faces do not match")
        return
    encodings = {}
    for i in range(len(faces)):
        image = face_recognition.load_image_file(f"{path}/{faces[i]}")
        encoding = face_recognition.face_encodings(image)[0]
        encodings[people[i]] = encoding
    return encodings
        
# return first face that returns a match to known database
def compare_faces(encodings, face):
    image = face_recognition.load_image_file(f"{face}")
    encoding = face_recognition.face_encodings(image)
    if len(encoding) > 0:
        encoding = encoding[0]
    else:
        return None

    for known_face in encodings:
        results = face_recognition.compare_faces([encodings[known_face]], encoding)
        if results[0]:
            return known_face
    return None


# facelist = ['hello.jpg', 'testasian.jpeg', 'simu_liu.jpeg']
# peoplelist = ["anhphu", "asianman", "simu"]

# encodings = generate_encodings("encodings", peoplelist, facelist)
# print(compare_faces("encodings", encodings, "simu_liu.jpeg"))



def get_timeline(video_frames_dir, face_timeline):
    facelist = ['hello.jpg', 'testasian.jpeg', 'simu_liu.jpeg']
    peoplelist = ["anhphu", "asianman", "simu"]
    encodings = generate_encodings("faces", peoplelist, facelist)
    for i in face_timeline.keys():
        face = compare_faces(encodings, f"{video_frames_dir}/{i}.jpg")
        face_timeline[i] = face
    return face_timeline
"""
go through video at interval, run facial recognition for all faces, find highest match if above a threshlold
return a timeline in the form of:
{
0: "face",
1: "face",
2: "face",
...
}
"""
# print(get_timeline("img_input", {0: "face", 1: "face", 2: "face"}))