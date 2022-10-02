import boto3
import os
from dotenv import load_dotenv
import time

load_dotenv()

def upload_file(file_source, upload_path, bucket):
    base_path = "https://forever-videos.s3.us-east-1.amazonaws.com/"
    full_url = base_path + upload_path
    session = boto3.Session(
        aws_access_key_id=os.getenv("AWS_ACCESS_KEY_ID"),
        aws_secret_access_key=os.getenv("AWS_SECRET_ACCESS_KEY"),
    )
#     current_time = time.strftime("%H-%M-%S", time.localtime())
    s3 = session.resource('s3')
    s3.meta.client.upload_file(Filename=file_source, Bucket=bucket, Key=upload_path)
