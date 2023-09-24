import unittest
from unittest.mock import patch, MagicMock

import pytest
from botocore.exceptions import NoCredentialsError
from fastapi import UploadFile

from src.service.media import S3Service


class TestS3Service(unittest.TestCase):

    @patch('boto3.client')
    def setUp(self, mock_boto_client):
        self.mock_s3_client = MagicMock()
        mock_boto_client.return_value = self.mock_s3_client
        self.service = S3Service()

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

    @patch('builtins.open')
    @patch('os.remove')
    def test_upload_video_to_s3_success(self, mock_remove, mock_open):
        mock_file = MagicMock()
        mock_open.return_value.__enter__.return_value = mock_file
        self.mock_s3_client.upload_fileobj.return_value = None

        result = self.service.upload_video_to_s3('folder', 'file.mp4')

        self.assertTrue(result)
        mock_remove.assert_called_with('videos/file.mp4')

    @pytest.mark.asyncio
    async def test_download_file_from_s3_success(self):
        self.mock_s3_client.generate_presigned_url.return_value = 'https://some_url_here'

        result = await self.service.download_file_from_s3('folder', 'file.txt')

        self.assertEqual(result, 'https://some_url_here')

    @patch('boto3.client')
    @pytest.mark.asyncio
    async def test_view_files_from_s3_success(self, mock_boto_client):
        self.mock_s3_client.list_objects.return_value = {
            'Contents': [
                {'Key': 'folder/file1.txt'},
                {'Key': 'folder/file2.txt'},
            ]
        }

        result = await self.service.view_files_from_s3('folder')

        self.assertEqual(result, ['file1.txt', 'file2.txt'])


if __name__ == '__main__':
    unittest.main()
