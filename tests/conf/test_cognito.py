import json
import unittest
from unittest.mock import patch, MagicMock, Mock

import jwt
import pytest
from fastapi import HTTPException, status

from src.conf.cognito import CognitoAuth, get_current_user, is_admin


class TestCognitoAuth(unittest.TestCase):

    @patch('boto3.client')
    @patch('requests.get')
    def setUp(self, mock_requests_get, mock_boto_client):
        # Mock the boto3 client
        self.mock_cognito_client = MagicMock()
        mock_boto_client.return_value = self.mock_cognito_client

        # Mock the JWKS (JSON Web Key Set)
        mock_jwks = json.dumps({"keys": [{"kid": "someKid", "kty": "RSA"}]})
        mock_response = MagicMock()
        mock_response.text = mock_jwks
        mock_requests_get.return_value = mock_response

        # Initialize CognitoAuth instance
        self.cognito_auth = CognitoAuth()

    def test_get_unverified_header(self):
        with patch('jwt.get_unverified_header') as mock_jwt_header:
            mock_jwt_header.return_value = {"kid": "someKid"}
            header = self.cognito_auth.get_unverified_header("someToken")
            self.assertEqual(header, {"kid": "someKid"})

    def test_find_key(self):
        jwks = [{"kid": "someKid", "kty": "RSA"}, {"kid": "anotherKid", "kty": "RSA"}]
        key = self.cognito_auth.find_key("someKid", jwks)
        self.assertEqual(key, {"kid": "someKid", "kty": "RSA"})

    def test_extract_roles(self):
        decoded_token = {"cognito:groups": ["admin", "user"]}
        roles = self.cognito_auth.extract_roles(decoded_token)
        self.assertEqual(roles, ["admin", "user"])

    @patch.object(CognitoAuth, 'get_jwks', return_value=[{"kid": "someKid", "kty": "RSA"}])
    def test_get_jwks(self, mock_get_jwks):
        jwks = self.cognito_auth.get_jwks()
        self.assertEqual(jwks, [{"kid": "someKid", "kty": "RSA"}])

    def test_decode_jwt(self):
        with patch('jwt.decode') as mock_jwt_decode, \
                patch('jwt.get_unverified_header') as mock_get_unverified_header, \
                patch.object(self.cognito_auth, 'get_jwks') as mock_get_jwks, \
                patch.object(self.cognito_auth, 'find_key') as mock_find_key, \
                patch('jose.jwk.construct') as mock_jose_construct:
            # Create a mock object with a to_pem method
            mock_constructed_key = Mock()
            mock_constructed_key.to_pem.return_value = "some_pem_key"

            mock_jwt_decode.return_value = {"some": "payload"}
            mock_get_unverified_header.return_value = {"kid": "someKid"}
            mock_get_jwks.return_value = [{"kid": "someKid", "other": "data"}]
            mock_find_key.return_value = {"kid": "someKid", "kty": "RSA"}
            mock_jose_construct.return_value = mock_constructed_key

            decoded = self.cognito_auth.decode_jwt("someToken")

            self.assertEqual(decoded, {"some": "payload"})

    def test_get_secret_hash(self):
        # Dummy logic to mimic HMAC hashing and Base64 encoding
        with patch('hmac.new') as mock_hmac_new, patch('base64.b64encode') as mock_b64encode:
            mock_hmac_new.return_value.digest.return_value = b'somehash'
            mock_b64encode.return_value.decode.return_value = 'c29tZWhhc2g='
            secret_hash = self.cognito_auth.get_secret_hash('someUsername')
            self.assertEqual(secret_hash, 'c29tZWhhc2g=')

    def test_get_tokens(self):
        self.mock_cognito_client.initiate_auth.return_value = {'AuthenticationResult': {'IdToken': 'someToken'}}
        tokens = self.cognito_auth.get_tokens('username', 'password')
        self.assertEqual(tokens, {'AuthenticationResult': {'IdToken': 'someToken'}})

    @patch('requests.get')
    @patch('json.loads')  # Replace 'your_module' with the actual module where `json` is imported
    def test_get_jwks(self, mock_json_loads, mock_requests_get):
        # Mock the HTTP response from requests.get
        mock_response = Mock()
        mock_response.text = 'some_text'
        mock_requests_get.return_value = mock_response

        # Mock the JSON web keys returned by json.loads
        fake_jwks = [{"kid": "someKid", "kty": "RSA"}]
        mock_json_loads.return_value = {"keys": fake_jwks}

        # Instantiate your CognitoAuth class
        cognito_auth = CognitoAuth()  # Assume it takes no parameters, adjust accordingly
        cognito_auth.jwks_url = "http://example.com"  # Replace with actual jwks_url

        # Call the get_jwks method
        jwks = cognito_auth.get_jwks()

        # Assertions
        mock_requests_get.assert_called_once_with("http://example.com")
        mock_json_loads.assert_called_once_with('some_text')
        self.assertEqual(jwks, fake_jwks)

    @patch(
        'jwt.get_unverified_header')  # Replace 'your_module' with the actual module where `jwt` is imported
    def test_get_unverified_header_negative(self, mock_get_unverified_header):
        # Mock the jwt.get_unverified_header to throw a PyJWTError
        mock_get_unverified_header.side_effect = jwt.PyJWTError

        # Instantiate your CognitoAuth class
        cognito_auth = CognitoAuth()  # Assume it takes no parameters, adjust accordingly

        # Assertion: Make sure it raises the expected HTTPException
        with self.assertRaises(HTTPException) as context:
            cognito_auth.get_unverified_header("some_invalid_token")

        # Validate that the exception has a status code of 403
        self.assertEqual(context.exception.status_code, 403)
        self.assertEqual(context.exception.detail, "Invalid JWT token")


@pytest.mark.asyncio
async def test_get_current_user():
    fake_token = "fake_token"
    fake_decoded_token = {"cognito:username": "john", "some_other_field": "some_value"}
    fake_user = {"username": "john", "roles": ["user", "admin"]}

    with patch('src.conf.cognito.cognito_auth.decode_jwt', return_value=fake_decoded_token), \
            patch('src.conf.cognito.cognito_auth.extract_roles', return_value=["user", "admin"]):
        user = await get_current_user(token=fake_token)

    assert user == fake_user


@pytest.mark.asyncio
async def test_is_admin_success():
    fake_current_user = {"username": "john", "roles": ["user", "admin"]}

    user = await is_admin(current_user=fake_current_user)

    assert user == fake_current_user


@pytest.mark.asyncio
async def test_is_admin_failure():
    fake_current_user = {"username": "john", "roles": ["user"]}

    with pytest.raises(HTTPException) as excinfo:
        await is_admin(current_user=fake_current_user)

    assert excinfo.value.status_code == status.HTTP_403_FORBIDDEN
    assert str(excinfo.value.detail) == "Admin role required"
