import sys
from pathlib import Path
file = Path(__file__).resolve()
parent, root = file.parent, file.parents[1]
sys.path.append(str(root))
 
import unittest
import os
from fastapi.testclient import TestClient
from src.api.main import app
from src.api.auth import NoAuthProvider, BasicAuthProvider, CognitoAuthProvider, IamAuthProvider, LambdaAuthorizerProvider
from unittest.mock import patch

class TestAuthAPI(unittest.TestCase):
    def setUp(self):
        self.client = TestClient(app)
        self.original_auth_type = os.getenv("AUTH_TYPE")
        os.environ.pop("AUTH_TYPE", None)  # Clear AUTH_TYPE initially

    def tearDown(self):
        # Restore the original AUTH_TYPE
        if self.original_auth_type is not None:
            os.environ["AUTH_TYPE"] = self.original_auth_type
        else:
            os.environ.pop("AUTH_TYPE", None)

    def test_get_boarding_pass_no_auth(self):
        os.environ["AUTH_TYPE"] = "none"
        # Use the helper method to display and verify AUTH_TYPE
        auth_type_value = self.display_auth_type()
        response = self.client.get("/api/v1/boarding-pass/B000001")
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.json()["user"], "anonymous")

    def test_get_boarding_pass_basic_auth(self):
        os.environ["AUTH_TYPE"] = "basic"
        # Use the helper method to display and verify AUTH_TYPE
        auth_type_value = self.display_auth_type()
        response = self.client.get("/api/v1/boarding-pass/B000001", auth=("admin", "password123"))
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.json()["user"], "admin")

    def test_get_boarding_pass_cognito_auth(self):
        os.environ["AUTH_TYPE"] = "cognito"
        # Use the helper method to display and verify AUTH_TYPE
        auth_type_value = self.display_auth_type()

        # Mock a JWT token with a username
        mock_token = "mock_token"
        mock_decoded = {"username": "cognito_user"}
        with patch('jose.jwt.decode', return_value=mock_decoded):
            response = self.client.get("/api/v1/boarding-pass/B000001", headers={"Authorization": "Bearer mock_token"})
            self.assertEqual(response.status_code, 200)
            self.assertEqual(response.json()["user"], "cognito_user")

    def test_get_boarding_pass_iam_auth(self):
        os.environ["AUTH_TYPE"] = "iam"
        # Use the helper method to display and verify AUTH_TYPE
        auth_type_value = self.display_auth_type()
        response = self.client.get("/api/v1/boarding-pass/B000001", headers={"Authorization": "Bearer mock_token"})
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.json()["user"], "iam_user")

    def test_get_boarding_pass_lambda_auth(self):
        os.environ["AUTH_TYPE"] = "lambda"
        # Use the helper method to display and verify AUTH_TYPE
        auth_type_value = self.display_auth_type()
        response = self.client.get("/api/v1/boarding-pass/B000001", headers={"Authorization": "Bearer mock_token"})
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.json()["user"], "lambda_user")
        
    def display_auth_type(self):
        """Helper method to print and verify AUTH_TYPE"""
        auth_type_value = os.getenv("AUTH_TYPE")
        print(f"AUTH_TYPE is set to: {auth_type_value}")  # Prints to test output
        return auth_type_value        

if __name__ == "__main__":
    unittest.main()