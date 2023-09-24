import json
import unittest

from fastapi.testclient import TestClient

from app import app
from conf.cognito import CognitoAuth
from conf.config import settings

client = TestClient(app)


class TestMediaRoutes(unittest.TestCase):

    def get_admin_token(self):
        cognito = CognitoAuth()
        tokens = cognito.get_tokens(settings["EMAIL_TEST"], settings["PASSWORD_TEST"])
        authentication_result = tokens["AuthenticationResult"]
        return authentication_result["IdToken"]

    def test_image_detection(self):
        token = self.get_admin_token()
        headers = {"Authorization": f"Bearer {token}"}

        with open("resources/test_image.jpg", "rb") as f:
            image_data = f.read()

        files = {"file": ("filename.jpg", image_data, "image/jpg")}

        response = client.post("/v1/detect/image", headers=headers, files=files)
        self.assertEqual(response.status_code, 200)
        self.assertIn("Processamento iniciado com sucesso", json.loads(response.text)["message"])

    def test_video_processing(self):
        # Similar to test_image_detection but for videos
        token = self.get_admin_token()
        headers = {"Authorization": f"Bearer {token}"}

        with open("resources/test_video.mp4", "rb") as f:
            video_data = f.read()

        files = {"file": ("filename.mp4", video_data, "video/mp4")}

        response = client.post("/v1/detect/video", headers=headers, files=files)
        self.assertEqual(response.status_code, 200)
        self.assertIn("Processamento iniciado com sucesso", json.loads(response.text)["message"])

    def test_download_file(self):
        token = self.get_admin_token()
        headers = {"Authorization": f"Bearer {token}"}

        # Assume "test_file.jpg" is a real file that exists on S3 for the user
        response = client.get(f"/v1/download/test_file.jpg", headers=headers)
        self.assertEqual(response.status_code, 200)

    def test_view_files(self):
        token = self.get_admin_token()
        headers = {"Authorization": f"Bearer {token}"}

        response = client.get("/v1/view/files", headers=headers)
        self.assertEqual(response.status_code, 200)
        self.assertIsInstance(json.loads(response.text), list)  # Assuming it returns a list of files
