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

    def upload_video_to_s3(self, sub_folder: str, file_name: str):
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

    async def download_file_from_s3(self, sub_folder: str, file_name: str):
        try:
            url = self.s3_client.generate_presigned_url(
                'get_object',
                Params={
                    'Bucket': self.bucket_name,
                    'Key': f"{sub_folder}/{file_name}"
                },
                ExpiresIn=3600  # URL expires in 1 hour
            )
            return url
        except NoCredentialsError:
            return False
        except Exception as e:
            print(e)
            return False

    async def view_files_from_s3(self, sub_folder: str):
        try:
            response = self.s3_client.list_objects(Bucket=self.bucket_name, Prefix=sub_folder)

            # Check if the 'Contents' key exists in the response
            if 'Contents' in response:
                # Extract only the 'Key' field for each file
                files = [content['Key'].replace(f"{sub_folder}/", "", 1) for content in response['Contents']]
            else:
                files = []

            return files
        except NoCredentialsError:
            return False
        except Exception as e:
            print(e)
            return False


