from unittest.mock import patch

from fastapi.testclient import TestClient

from app import app  # replace with your actual import
from conf.cognito import CognitoAuth
from conf.config import settings

client = TestClient(app)

import json
from fastapi.testclient import TestClient
import unittest

from app import app  # replace with your actual import

client = TestClient(app)


class TestAdminRoute(unittest.TestCase):

    def get_admin_admin_token(self):
        cognito = CognitoAuth()
        tokens = cognito.get_tokens(settings["EMAIL_TEST"], settings["PASSWORD_TEST"])
        authentication_result = tokens["AuthenticationResult"]
        return authentication_result["IdToken"]

    def test_admin_route(self):
        token = self.get_admin_admin_token()
        headers = {"Authorization": f"Bearer {token}"}

        response = client.get("/v1/admin/", headers=headers)

        self.assertEqual(response.status_code, 200)
        self.assertIn("This is a protected route for admins only", json.loads(response.text)["message"])

    @patch("src.controller.user.cognito_auth.get_tokens")  # Mocking the cognito_auth
    def test_token_endpoint(self, mock_get_tokens):
        mock_get_tokens.return_value = {"access_token": "some_access_token"}
        user_payload = {
            "username": "some_username",
            "password": "some_password"
        }
        response = client.post("/v1/token/", json=user_payload)
        assert response.status_code == 200
        assert "access_token" in json.loads(response.text)
