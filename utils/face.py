import face_recognition
import os
import sys


# encodes a list of faces of people and returns a list of encodings of the person
def generate_encodings(people, faces):
    if len(people) != len(faces):
        print("Error: number of people and number of faces do not match")
        return
    encodings = []
    for i in range(len(faces)):
        image = face_recognition.load_image_file(faces[i])
        encoding = face_recognition.face_encodings(image)[0]
        encodings.append({people[i], encoding})
    return encodings
        
# compares a list of encodings of a person to a face and returns true if the face matches the person
# TODO return first face that returns a match
def compare_faces(encodings, face):
    image = face_recognition.load_image_file(face)
    encoding = face_recognition.face_encodings(image)[0]
    for known_face in encodings:
        results = face_recognition.compare_faces(known_face, encoding)
    return results


def generate_encodings_test(path, people, faces):
    if len(people) != len(faces):
        print("Error: number of people and number of faces do not match")
        return
    encodings = []
    # for every different person
    for i in range(len(people)):
        # for every face of that person
        for j in range(len(faces[i])):
            image = face_recognition.load_image_file(path + faces[i][j])
            encoding = face_recognition.face_encodings(image)[0]
            encodings.append({people[i], encoding})
    return encodings

facelist = [['unknown.jpg', 'hello.jpg'], ['simu_liu.jpeg', 'testasian.jpeg']]
peoplelist = ["anhphu", "simu"]

print(generate_encodings_test("encodings/", peoplelist, facelist))


# known_image = sys.argv[1]
# unknown_image = sys.argv[2]
# known_image = face_recognition.load_image_file(f"{known_image}")
# unknown_image = face_recognition.load_image_file(f"{unknown_image}")

# known_encoding = face_recognition.face_encodings(known_image)[0]
# print(known_encoding)
# unknown_encoding = face_recognition.face_encodings(unknown_image)[0]

# if len(unknown_encoding) > 0:
#     unknown_face_encoding = unknown_encoding[0]

# results = face_recognition.compare_faces([known_encoding], unknown_encoding)

# print(results)


def get_timeline(video_frames_dir, face_timeline):
    for i in face_timeline.keys():
        face = compare_faces(f"{video_frames_dir}/{i}.png")
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
