import face_recognition
import os
import sys


# encodes a list of faces of one person and returns a list of encodings of the person
def generate_encodings(person, faces):
    encodings = []
    for face in faces:
        image = face_recognition.load_image_file(face)
        encoding = face_recognition.face_encodings(image)[0]
        encodings.append(encoding)
    return encodings
        
# compares a list of encodings of a person to a face and returns true if the face matches the person
def compare_faces(known_faces, face):
    image = face_recognition.load_image_file(face)
    encoding = face_recognition.face_encodings(image)[0]
    results = face_recognition.compare_faces(known_faces, encoding)
    return results



# known_image = sys.argv[1]
# unknown_image = sys.argv[2]
# known_image = face_recognition.load_image_file(f"faces/{known_image}")
# unknown_image = face_recognition.load_image_file(f"faces/{unknown_image}")

# known_encoding = face_recognition.face_encodings(known_image)[0]
# print(known_encoding)
# unknown_encoding = face_recognition.face_encodings(unknown_image)[0]

# if len(unknown_encoding) > 0:
#     unknown_face_encoding = unknown_encoding[0]

# results = face_recognition.compare_faces([known_encoding], unknown_encoding)

# print(results)