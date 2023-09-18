import os

import boto3
from botocore.exceptions import NoCredentialsError
from fastapi import UploadFile

from src.conf.config import settings


class S3Service:
    def __init__(self):
        self.s3_client = boto3.client(
            's3',
            aws_access_key_id=settings["ACCESS_KEY"],
            aws_secret_access_key=settings["SECRET_KEY"])
        self.bucket_name = 'fast-detector-bucket'

    async def upload_file_to_s3(self, file: UploadFile, sub_folder: str, file_name: str):
        try:
            self.s3_client.upload_fileobj(file, self.bucket_name, f"{sub_folder}/{file_name}")
            return True
        except NoCredentialsError:
            return False
        except Exception as e:
            print(e)
            return False

    async def upload_video_to_s3(self, sub_folder: str, file_name: str):
        try:
            # Step 1: Read the video file from the local disk
            video_path = "videos/" + file_name
            with open(video_path, 'rb') as file:
                # Step 2: Upload the file to S3
                self.s3_client.upload_fileobj(file, self.bucket_name, f"{sub_folder}/{file_name}")

            # Step 3: Delete the local file (if needed)
            os.remove(video_path)

            return True
        except NoCredentialsError:
            return False
        except Exception as e:
            print(e)
            return False
