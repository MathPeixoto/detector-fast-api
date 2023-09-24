import asyncio
import unittest
from unittest.mock import patch, MagicMock

from botocore.exceptions import NoCredentialsError
from fastapi import UploadFile

from src.service.media import S3Service


class TestS3Service(unittest.TestCase):

    @patch('boto3.client')
    def setUp(self, mock_boto_client):
        self.mock_s3_client = MagicMock()
        mock_boto_client.return_value = self.mock_s3_client
        self.service = S3Service()

        self.loop = asyncio.get_event_loop()

    def test_upload_file_to_s3_success(self):
        mock_file = MagicMock(spec=UploadFile)
        self.mock_s3_client.upload_fileobj.return_value = None

        result = self.service.upload_file_to_s3(mock_file, 'folder', 'file.txt')

        self.assertTrue(result)

    def test_upload_file_to_s3_no_credentials(self):
        mock_file = MagicMock(spec=UploadFile)
        self.mock_s3_client.upload_fileobj.side_effect = NoCredentialsError

        result = self.service.upload_file_to_s3(mock_file, 'folder', 'file.txt')

        self.assertFalse(result)

    def test_upload_file_to_s3_exception(self):
        mock_file = MagicMock(spec=UploadFile)
        self.mock_s3_client.upload_fileobj.side_effect = Exception

        result = self.service.upload_file_to_s3(mock_file, 'folder', 'file.txt')

        self.assertFalse(result)

    @patch('builtins.open')
    @patch('os.remove')
    def test_upload_video_to_s3_success(self, mock_remove, mock_open):
        mock_file = MagicMock()
        mock_open.return_value.__enter__.return_value = mock_file
        self.mock_s3_client.upload_fileobj.return_value = None

        result = self.service.upload_video_to_s3('folder', 'file.mp4')

        self.assertTrue(result)
        mock_remove.assert_called_with('videos/file.mp4')

    def test_upload_video_to_s3_no_credentials(self):
        self.mock_s3_client.upload_fileobj.side_effect = NoCredentialsError

        result = self.service.upload_video_to_s3('folder', 'file.mp4')

        self.assertFalse(result)

    def test_upload_video_to_s3_exception(self):
        self.mock_s3_client.upload_fileobj.side_effect = Exception

        result = self.service.upload_video_to_s3('folder', 'file.mp4')

        self.assertFalse(result)

    # Test case for download_file_from_s3 with NoCredentialsError
    @patch('boto3.client')  # Replace 'your_module' with the actual module
    def test_download_file_from_s3_no_credential_error(self, mock_client):
        # Arrange
        mock_s3_client = mock_client.return_value
        mock_s3_client.generate_presigned_url.side_effect = NoCredentialsError
        s3_service = S3Service()

        # Act
        result = self.loop.run_until_complete(s3_service.download_file_from_s3("some_sub_folder", "some_file_name"))

        # Assert
        self.assertFalse(result)

    # Test case for download_file_from_s3 with general exception
    @patch('boto3.client')  # Replace 'your_module' with the actual module
    def test_download_file_from_s3_general_exception(self, mock_client):
        # Arrange
        mock_s3_client = mock_client.return_value
        mock_s3_client.generate_presigned_url.side_effect = Exception("Some error")
        s3_service = S3Service()

        # Act
        result = self.loop.run_until_complete(s3_service.download_file_from_s3("some_sub_folder", "some_file_name"))

        # Assert
        self.assertFalse(result)

    # Test case for view_files_from_s3 with NoCredentialsError
    @patch('boto3.client')  # Replace 'your_module' with the actual module
    def test_view_files_from_s3_no_credential_error(self, mock_client):
        # Arrange
        mock_s3_client = mock_client.return_value
        mock_s3_client.list_objects.side_effect = NoCredentialsError
        s3_service = S3Service()

        # Act
        result = self.loop.run_until_complete(s3_service.view_files_from_s3("some_sub_folder"))

        # Assert
        self.assertFalse(result)

    # Test case for view_files_from_s3 with general exception
    @patch('boto3.client')  # Replace 'your_module' with the actual module
    def test_view_files_from_s3_general_exception(self, mock_client):
        # Arrange
        mock_s3_client = mock_client.return_value
        mock_s3_client.list_objects.side_effect = Exception("Some error")
        s3_service = S3Service()

        # Act
        result = self.loop.run_until_complete(s3_service.view_files_from_s3("some_sub_folder"))

        # Assert
        self.assertFalse(result)
