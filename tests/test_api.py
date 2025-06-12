import unittest
import os
import logging
from fastapi.testclient import TestClient
from src.api.main import app
from unittest.mock import patch, MagicMock

from src.utils.secretload import get_secret
from config import api_key_secret_name


get_secret(api_key_secret_name)

# Set up logging
logging.basicConfig(level=logging.DEBUG)
logger = logging.getLogger(__name__)

class TestAuthAPI(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.secretvalue = os.getenv(api_key_secret_name)      
        
    def setUp(self):
        self.client = TestClient(app)
        logger.debug("Test client initialized")

    @patch('src.api.endpoints.get_boarding_pass_data', new_callable=MagicMock)
    def test_get_boarding_pass_success(self, mock_get_boarding_pass_data):
        logger.debug("Starting test_get_boarding_pass_success with booking_id B123")
        mock_get_boarding_pass_data.return_value = ("B5", "5B", "2025-06-08T09:30:00", "https://airline.com/boardingpass/B123.pdf")
        logger.debug(f"Mocked get_boarding_pass_data return value: {mock_get_boarding_pass_data.return_value}")

        logger.debug(f"secret value: {self.secretvalue}")
        # Include API key in the request header
        response = self.client.get(
            "/api/v1/boarding-pass/B123",
            headers={"X-API-Key":  self.secretvalue}
        )
        logger.debug(f"Response status: {response.status_code}, Response JSON: {response.json()}")

        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.json(), {
            "status": "success",
            "boarding_pass": {
                "gate": "B5",
                "seat": "5B",
                "boarding_time": "2025-06-08T09:30:00",
                "pdf_url": "https://airline.com/boardingpass/B123.pdf"
            }
        })
        mock_get_boarding_pass_data.assert_called_once()

    @patch('src.api.endpoints.get_boarding_pass_data', new_callable=MagicMock)
    def test_get_boarding_pass_unauthorized(self, mock_get_boarding_pass_data):
        logger.debug("Starting test_get_boarding_pass_unauthorized with booking_id B123")
        mock_get_boarding_pass_data.return_value = ("B5", "5B", "2025-06-08T09:30:00", "https://airline.com/boardingpass/B123.pdf")

        # Test with an invalid API key
        response = self.client.get(
            "/api/v1/boarding-pass/B123",
            headers={"X-API-Key": "invalid-key"}
        )
        logger.debug(f"Response status: {response.status_code}, Response JSON: {response.json()}")

        self.assertEqual(response.status_code, 401)
        self.assertEqual(response.json(), {"detail": "Invalid or missing API Key"})

if __name__ == "__main__":
    unittest.main()