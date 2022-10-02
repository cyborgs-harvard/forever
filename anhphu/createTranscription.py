import boto3
import os
import time
import pandas as pd
import json
from dotenv import load_dotenv
import math

def upload_video(video_file, bucket):
    base_path = "https://forever-videos.s3.us-east-1.amazonaws.com/"
    upload_path = "videos/" + video_file
    full_url = base_path + upload_path
    print("full url: ", full_url)

    session = boto3.Session(
        aws_access_key_id=os.getenv("AWS_ACCESS_KEY_ID"),
        aws_secret_access_key=os.getenv("AWS_SECRET_ACCESS_KEY"),
    )
    current_time = time.strftime("%H-%M-%S", time.localtime())
    s3 = session.resource('s3')
    s3.meta.client.upload_file(Filename=f'{video_file}_{current_time}', Bucket=bucket, Key=upload_path)



def get_transcript_words(full_transcript, i):
    transcript_words = []
    items = full_transcript["results"]["items"]
    for item in items:
        print("hello")
        if item["type"] == "pronunciation":
            start_time = float(item["start_time"])
            if start_time > i and start_time < i + 1:
                transcript_words.append(item["alternatives"][0]["content"])
        else:
            pass
    return transcript_words


def get_timeline(transcript_timeline):
    json_file = "asrOutput.json"
    with open(json_file) as json_file:
        transcript_json = json.load(json_file)
    for i in transcript_timeline.keys():
        transcript_words = get_transcript_words(transcript_json, i)
        transcript_timeline[i] = transcript_words
    return transcript_timeline

print(get_timeline({0: "face", 1: "face", 2: "face", 3: "face", 4: "face", 5: "face", 6: "face", 7: "face", 8: "face", 9: "face", 10: "face", 11: "face", 12: "face", 13: "face", 14: "face", 15: "face"}))


def transcribe_file(job_name, file_uri, transcribe_client):
    transcribe_client.start_transcription_job(
        TranscriptionJobName=job_name,
        Media={'MediaFileUri': file_uri},
        MediaFormat='mp4',
        LanguageCode='en-US'
    )

    max_tries = 60
    while max_tries > 0:
        max_tries -= 1
        job = transcribe_client.get_transcription_job(TranscriptionJobName=job_name)
        job_status = job['TranscriptionJob']['TranscriptionJobStatus']
        if job_status in ['COMPLETED', 'FAILED']:
            print(f"Job {job_name} is {job_status}.")
            if job_status == 'COMPLETED':
                print(
                    f"Download the transcript from\n"
                    f"\t{job['TranscriptionJob']['Transcript']['TranscriptFileUri']}.")
                    
                return job['TranscriptionJob']['Transcript']['TranscriptFileUri']
            break
        else:
            print(f"Waiting for {job_name}. Current status is {job_status}.")
        time.sleep(10)
video_file = "testVideo.mp4"

transcribe_client = boto3.client('transcribe', aws_access_key_id=os.getenv("AWS_ACCESS_KEY_ID"), aws_secret_access_key=os.getenv("AWS_SECRET_ACCESS_KEY"), region_name = "us-east-1")
file_uri = f's3://forever-videos/{video_file}'
# get current time for an id of a file
current_time = time.strftime("%H-%M-%S", time.localtime())


# transcribe_file(f'{video_file}_{current_time}', file_uri, transcribe_client)




# returns the full transcription of the video
def get_full_transcription(json_file):
    # read json file
    with open(json_file) as json_file:
        data = json.load(json_file)
    # get the transcript
    transcript = data['results']['transcripts'][0]['transcript']
    return transcript



# # create a function that takes in asrOutput.json, and a string query and returns a list of timestamps
# def query_transcribed_file(json_file, query):
    
#     # read json file
#     with open(json_file) as json_file:
#         data = json.load(json_file)
#     # get the transcript
#     transcript = data['results']['transcripts'][0]['transcript']

#     # check if query in transcript
#     if query in transcript.lower():
#         # get the items
#         items = data['results']['items']
#         # create a list of timestamps
#         timestamps = []

#         word_list = transcript.split(' ')
#         first_word = word_list[0]

#         print(first_word)

#         print("length itmes", len(items))
#         print("words: ", len(word_list))
#         count = 0
#         for i in range (0, len (transcript)):   
#             #Checks whether given character is a punctuation mark  
#             if transcript[i] in ('!', "," ,";", ".","?"):  
#                 count = count + 1;  
#         print("Punctuation marks:", count)
#         print("TOTAL WORDS: ", len(word_list) + count)


#         for i, item in enumerate(items):
#             print(items[i]['alternatives'][0]['content'])
#             if item['type'] == 'pronunciation':
#                 if item['alternatives'][0]['content'] == first_word:
#                     timestamps.append(item['start_time'])
#         return timestamps

# print(query_transcribed_file('asrOutput.json', 'thank you when'))

# "thank you for doing this for me"

# "thank you for"



# create a function that takes in asrOutput.json, and returns a list of start times and end times based on the time difference between period punctuation marks and the next word with a threshold of 30 seconds.
def get_timestamps_convos(json_file):
    # list of dicts
    timestamps = []
    time_threshold = 1

    # read json file
    with open(json_file) as json_file:
        data = json.load(json_file)
    # get the transcript
    transcript = data['results']['transcripts'][0]['transcript']
    items = data['results']['items']
    first_word_start_time = items[0]['start_time']
    print(first_word_start_time)
    last_word_end_time = items[-2]['end_time']
    print(items[-2]['alternatives'][0]['content'])
    items_length = len(items)

    # for every word
    for i in range(items_length):
        # if the word is a punctuation mark
        if items[i]['type'] == 'punctuation':


            punctuation = items[i]['alternatives'][0]['content']
            possible_puncs = ['.', ',', '?', '!']
            # if the punctuation mark is in the possible punctuation marks
            if punctuation in possible_puncs:
                # get the time the sentence ended and the next start time
                sentence_end = items[i-1]['end_time']
                # if not at end of time list
                if i < items_length - 1:
                    new_sentence_start = items[i+1]['start_time']
                    # if the time difference is greater than 30 seconds
                    time_separation = float(new_sentence_start) - float(sentence_end)
                    print(time_separation)
                    if time_separation > time_threshold:
                        # add the start and end times to the list; if first convo, add the first word start time
                        if len(timestamps) == 0:
                            timestamps.append({'start_time': first_word_start_time, 'end_time': sentence_end})
                        else: 
                            timestamps.append({'start_time': new_sentence_start, 'end_time': sentence_end})
                    # add the last word end time
                else:
                    print('last word')
                    timestamps.append({'start_time': new_sentence_start, 'end_time': last_word_end_time})
    return timestamps

# LOG: still getting four different time separations even tho there should be 3

# print(get_timestamps_convos('asrOutputShort.json'))