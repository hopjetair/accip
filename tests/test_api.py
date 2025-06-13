import pdb
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

    # Boarding Service Tests
    @patch('src.api.endpoints.boarding.get_boarding_pass_data', new_callable=MagicMock)
    def test_get_boarding_pass_success(self, mock_get_boarding_pass_data):
        logger.debug("Starting test_get_boarding_pass_success with booking_id B123")
        mock_get_boarding_pass_data.return_value = ("B5", "5B", "2025-06-08T09:30:00", "https://airline.com/boardingpass/B123.pdf")
        logger.debug(f"Mocked get_boarding_pass_data return value: {mock_get_boarding_pass_data.return_value}")

        logger.debug(f"secret value: {self.secretvalue}")
        response = self.client.get(
            "/api/v1/boarding-pass/B123",
            headers={"X-API-Key": self.secretvalue}
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

    @patch('src.api.endpoints.boarding.get_boarding_pass_data', new_callable=MagicMock)
    def test_get_boarding_pass_unauthorized(self, mock_get_boarding_pass_data):
        logger.debug("Starting test_get_boarding_pass_unauthorized with booking_id B123")
        response = self.client.get(
            "/api/v1/boarding-pass/B123",
            headers={"X-API-Key": "invalid-key"}
        )
        logger.debug(f"Response status: {response.status_code}, Response JSON: {response.json()}")

        self.assertEqual(response.status_code, 401)
        self.assertEqual(response.json(), {"detail": "Invalid or missing API Key"})

    @patch('src.api.endpoints.boarding.get_boarding_pass_data', new_callable=MagicMock)
    def test_print_boarding_pass_success(self, mock_get_boarding_pass_data):
        logger.debug("Starting test_print_boarding_pass_success with booking_id B123")
        mock_get_boarding_pass_data.return_value = ("B5", "5B", "2025-06-08T09:30:00", "https://airline.com/boardingpass/B123.pdf")
        response = self.client.get(
            "/api/v1/print-boarding-pass/B123",
            headers={"X-API-Key": self.secretvalue}
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

    @patch('src.api.endpoints.boarding.get_boarding_pass_data', new_callable=MagicMock)
    def test_print_boarding_pass_unauthorized(self, mock_get_boarding_pass_data):
        logger.debug("Starting test_print_boarding_pass_unauthorized with booking_id B123")
        response = self.client.get(
            "/api/v1/print-boarding-pass/B123",
            headers={"X-API-Key": "invalid-key"}
        )
        logger.debug(f"Response status: {response.status_code}, Response JSON: {response.json()}")

        self.assertEqual(response.status_code, 401)
        self.assertEqual(response.json(), {"detail": "Invalid or missing API Key"})

    @patch('src.api.endpoints.boarding.check_in_booking', new_callable=MagicMock)
    def test_check_in_success(self, mock_check_in_booking):
        logger.debug("Starting test_check_in_success with booking_id B123")
        mock_check_in_booking.return_value = {"updated": True, "gate": "B5", "seat": "5B", "boarding_time": "2025-06-08T09:30:00"}
        response = self.client.post(
            "/api/v1/check-in/B123",
            headers={"X-API-Key": self.secretvalue}
        )
        logger.debug(f"Response status: {response.status_code}, Response JSON: {response.json()}")

        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.json(), {
            "status": "success",
            "message": "Check-in successful",
            "boarding_pass": {"gate": "B5", "seat": "5B", "boarding_time": "2025-06-08T09:30:00"}
        })
        mock_check_in_booking.assert_called_once()

    @patch('src.api.endpoints.boarding.check_in_booking', new_callable=MagicMock)
    def test_check_in_unauthorized(self, mock_check_in_booking):
        logger.debug("Starting test_check_in_unauthorized with booking_id B123")
        response = self.client.post(
            "/api/v1/check-in/B123",
            headers={"X-API-Key": "invalid-key"}
        )
        logger.debug(f"Response status: {response.status_code}, Response JSON: {response.json()}")

        self.assertEqual(response.status_code, 401)
        self.assertEqual(response.json(), {"detail": "Invalid or missing API Key"})

    @patch('src.api.endpoints.boarding.choose_seat_data', new_callable=MagicMock)
    def test_choose_seat_success(self, mock_choose_seat_data):
        logger.debug("Starting test_choose_seat_success with booking_id B123")
        mock_choose_seat_data.return_value = {"flight_number": "FL123", "additional_fee": 10.0}
        response = self.client.post(
            "/api/v1/choose-seat/B123?seat_number=5B",
            headers={"X-API-Key": self.secretvalue}
        )
        logger.debug(f"Response status: {response.status_code}, Response JSON: {response.json()}")

        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.json(), {
            "status": "success",
            "seat": {"booking_id": "B123", "flight_number": "FL123", "seat_number": "5B", "additional_fee": 10.0}
        })
        mock_choose_seat_data.assert_called_once()

    @patch('src.api.endpoints.boarding.choose_seat_data', new_callable=MagicMock)
    def test_choose_seat_unauthorized(self, mock_choose_seat_data):
        logger.debug("Starting test_choose_seat_unauthorized with booking_id B123")
        response = self.client.post(
            "/api/v1/choose-seat/B123?seat_number=5B",
            headers={"X-API-Key": "invalid-key"}
        )
        logger.debug(f"Response status: {response.status_code}, Response JSON: {response.json()}")

        self.assertEqual(response.status_code, 401)
        self.assertEqual(response.json(), {"detail": "Invalid or missing API Key"})

    @patch('src.api.endpoints.boarding.change_seat_data', new_callable=MagicMock)
    def test_change_seat_success(self, mock_change_seat_data):
        logger.debug("Starting test_change_seat_success with booking_id B123")
        mock_change_seat_data.return_value = ("FL123", "5B", 20.0)
        response = self.client.post(
            "/api/v1/change-seat/B123?seat_number=5B",
            headers={"X-API-Key": self.secretvalue}
        )
        logger.debug(f"Response status: {response.status_code}, Response JSON: {response.json()}")

        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.json(), {
            "status": "success",
            "seat": {"flight_number": "FL123", "seat_number": "5B", "additional_fee": 20.0},
            "policy": "$20 fee for changes"
        })
        mock_change_seat_data.assert_called_once()

    @patch('src.api.endpoints.boarding.change_seat_data', new_callable=MagicMock)
    def test_change_seat_unauthorized(self, mock_change_seat_data):
        logger.debug("Starting test_change_seat_unauthorized with booking_id B123")
        response = self.client.post(
            "/api/v1/change-seat/B123?seat_number=5B",
            headers={"X-API-Key": "invalid-key"}
        )
        logger.debug(f"Response status: {response.status_code}, Response JSON: {response.json()}")

        self.assertEqual(response.status_code, 401)
        self.assertEqual(response.json(), {"detail": "Invalid or missing API Key"})

    # Flight Management Service Tests
    @patch('src.api.endpoints.flight_management.book_flight_data', new_callable=MagicMock)
    def test_book_flight_success(self, mock_book_flight_data):
        logger.debug("Starting test_book_flight_success with flight_number FL123")
        mock_book_flight_data.return_value = "B124"
        response = self.client.post(
            "/api/v1/book-flight/?flight_number=FL123&passenger_id=P124",
            headers={"X-API-Key": self.secretvalue}
        )
        logger.debug(f"Response status: {response.status_code}, Response JSON: {response.json()}")

        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.json(), {"status": "success", "booking_id": "B124"})
        mock_book_flight_data.assert_called_once()

    @patch('src.api.endpoints.flight_management.book_flight_data', new_callable=MagicMock)
    def test_book_flight_unauthorized(self, mock_book_flight_data):
        logger.debug("Starting test_book_flight_unauthorized with flight_number FL123")
        response = self.client.post(
            "/api/v1/book-flight/?flight_number=FL123&passenger_id=P124",
            headers={"X-API-Key": "invalid-key"}
        )
        logger.debug(f"Response status: {response.status_code}, Response JSON: {response.json()}")

        self.assertEqual(response.status_code, 401)
        self.assertEqual(response.json(), {"detail": "Invalid or missing API Key"})

    @patch('src.api.endpoints.flight_management.get_flight_offers_data', new_callable=MagicMock)
    def test_check_flight_offers_success(self, mock_get_flight_offers_data):
        logger.debug("Starting test_check_flight_offers_success")
        mock_get_flight_offers_data.return_value = [{"flight_number": "FL123", "price": 200.0}]
        response = self.client.get(
            "/api/v1/flight-offers/",
            headers={"X-API-Key": self.secretvalue}
        )
        logger.debug(f"Response status: {response.status_code}, Response JSON: {response.json()}")

        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.json(), {"status": "success", "offers": [{"flight_number": "FL123", "price": 200.0}]})
        mock_get_flight_offers_data.assert_called_once()

    @patch('src.api.endpoints.flight_management.get_flight_offers_data', new_callable=MagicMock)
    def test_check_flight_offers_unauthorized(self, mock_get_flight_offers_data):
        logger.debug("Starting test_check_flight_offers_unauthorized")
        response = self.client.get(
            "/api/v1/flight-offers/",
            headers={"X-API-Key": "invalid-key"}
        )
        logger.debug(f"Response status: {response.status_code}, Response JSON: {response.json()}")

        self.assertEqual(response.status_code, 401)
        self.assertEqual(response.json(), {"detail": "Invalid or missing API Key"})

    @patch('src.api.endpoints.flight_management.get_flight_prices_data', new_callable=MagicMock)
    def test_check_flight_prices_success(self, mock_get_flight_prices_data):
        logger.debug("Starting test_check_flight_prices_success with flight_number FL123")
        mock_get_flight_prices_data.return_value = (250.0, True)
        response = self.client.get(
            "/api/v1/flight-prices/FL123",
            headers={"X-API-Key": self.secretvalue}
        )
        logger.debug(f"Response status: {response.status_code}, Response JSON: {response.json()}")

        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.json(), {"status": "success", "prices": {"price": 250.0, "availability": True}})
        mock_get_flight_prices_data.assert_called_once()

    @patch('src.api.endpoints.flight_management.get_flight_prices_data', new_callable=MagicMock)
    def test_check_flight_prices_unauthorized(self, mock_get_flight_prices_data):
        logger.debug("Starting test_check_flight_prices_unauthorized with flight_number FL123")
        response = self.client.get(
            "/api/v1/flight-prices/FL123",
            headers={"X-API-Key": "invalid-key"}
        )
        logger.debug(f"Response status: {response.status_code}, Response JSON: {response.json()}")

        self.assertEqual(response.status_code, 401)
        self.assertEqual(response.json(), {"detail": "Invalid or missing API Key"})

    @patch('src.api.endpoints.flight_management.get_flight_reservation_data', new_callable=MagicMock)
    def test_check_flight_reservation_success(self, mock_get_flight_reservation_data):
        logger.debug("Starting test_check_flight_reservation_success with booking_id B123")
        mock_get_flight_reservation_data.return_value = ("P123", "FL123", "2025-06-03", "Confirmed", 300.0, "SYD", "MEL")
        response = self.client.get(
            "/api/v1/flight-reservation/B123",
            headers={"X-API-Key": self.secretvalue}
        )
        logger.debug(f"Response status: {response.status_code}, Response JSON: {response.json()}")

        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.json(), {
            "status": "success",
            "reservation": {
                "passenger_id": "P123",
                "flight_number": "FL123",
                "booking_date": "2025-06-03",
                "status": "Confirmed",
                "total_price": 300.0,
                "departure": "SYD",
                "destination": "MEL"
            }
        })
        mock_get_flight_reservation_data.assert_called_once()

    @patch('src.api.endpoints.flight_management.get_flight_reservation_data', new_callable=MagicMock)
    def test_check_flight_reservation_unauthorized(self, mock_get_flight_reservation_data):
        logger.debug("Starting test_check_flight_reservation_unauthorized with booking_id B123")
        response = self.client.get(
            "/api/v1/flight-reservation/B123",
            headers={"X-API-Key": "invalid-key"}
        )
        logger.debug(f"Response status: {response.status_code}, Response JSON: {response.json()}")

        self.assertEqual(response.status_code, 401)
        self.assertEqual(response.json(), {"detail": "Invalid or missing API Key"})

    @patch('src.api.endpoints.flight_management.get_flight_status_data', new_callable=MagicMock)
    def test_check_flight_status_success(self, mock_get_flight_status_data):
        logger.debug("Starting test_check_flight_status_success with flight_number FL123")
        mock_get_flight_status_data.return_value = ("SYD", "MEL", "On Time", "2025-06-08T09:00:00", "2025-06-08T12:00:00", "B5")
        response = self.client.get(
            "/api/v1/flight-status/FL123",
            headers={"X-API-Key": self.secretvalue}
        )
        logger.debug(f"Response status: {response.status_code}, Response JSON: {response.json()}")

        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.json(), {
            "status": "success",
            "flight_status": {
                "departure": "SYD",
                "destination": "MEL",
                "status": "On Time",
                "departure_time": "2025-06-08T09:00:00",
                "arrival_time": "2025-06-08T12:00:00",
                "gate": "B5"
            }
        })
        mock_get_flight_status_data.assert_called_once()

    @patch('src.api.endpoints.flight_management.get_flight_status_data', new_callable=MagicMock)
    def test_check_flight_status_unauthorized(self, mock_get_flight_status_data):
        logger.debug("Starting test_check_flight_status_unauthorized with flight_number FL123")
        response = self.client.get(
            "/api/v1/flight-status/FL123",
            headers={"X-API-Key": "invalid-key"}
        )
        logger.debug(f"Response status: {response.status_code}, Response JSON: {response.json()}")

        self.assertEqual(response.status_code, 401)
        self.assertEqual(response.json(), {"detail": "Invalid or missing API Key"})

    @patch('src.api.endpoints.flight_management.search_flights_data', new_callable=MagicMock)
    def test_search_flight_success(self, mock_search_flights_data):
        logger.debug("Starting test_search_flight_success with SYD to MEL on 2025-06-08")
        mock_search_flights_data.return_value = [{"flight_number": "FL123", "price": 250.0}]
        response = self.client.get(
            "/api/v1/search-flight/SYD/MEL/2025-06-08",
            headers={"X-API-Key": self.secretvalue}
        )
        logger.debug(f"Response status: {response.status_code}, Response JSON: {response.json()}")

        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.json(), {"status": "success", "flights": [{"flight_number": "FL123", "price": 250.0}]})
        mock_search_flights_data.assert_called_once()

    @patch('src.api.endpoints.flight_management.search_flights_data', new_callable=MagicMock)
    def test_search_flight_unauthorized(self, mock_search_flights_data):
        logger.debug("Starting test_search_flight_unauthorized with SYD to MEL on 2025-06-08")
        response = self.client.get(
            "/api/v1/search-flight/SYD/MEL/2025-06-08",
            headers={"X-API-Key": "invalid-key"}
        )
        logger.debug(f"Response status: {response.status_code}, Response JSON: {response.json()}")

        self.assertEqual(response.status_code, 401)
        self.assertEqual(response.json(), {"detail": "Invalid or missing API Key"})

    @patch('src.api.endpoints.flight_management.cancel_flight_data', new_callable=MagicMock)
    def test_cancel_flight_success(self, mock_cancel_flight_data):
        logger.debug("Starting test_cancel_flight_success with booking_id B123")
        mock_cancel_flight_data.return_value = True
        response = self.client.post(
            "/api/v1/cancel-flight/B123",
            headers={"X-API-Key": self.secretvalue}
        )
        logger.debug(f"Response status: {response.status_code}, Response JSON: {response.json()}")

        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.json(), {
            "status": "success",
            "booking_status": "Cancelled",
            "policy": "Free within 24 hours, $50 fee after"
        })
        mock_cancel_flight_data.assert_called_once()

    @patch('src.api.endpoints.flight_management.cancel_flight_data', new_callable=MagicMock)
    def test_cancel_flight_unauthorized(self, mock_cancel_flight_data):
        logger.debug("Starting test_cancel_flight_unauthorized with booking_id B123")
        response = self.client.post(
            "/api/v1/cancel-flight/B123",
            headers={"X-API-Key": "invalid-key"}
        )
        logger.debug(f"Response status: {response.status_code}, Response JSON: {response.json()}")

        self.assertEqual(response.status_code, 401)
        self.assertEqual(response.json(), {"detail": "Invalid or missing API Key"})

    @patch('src.api.endpoints.flight_management.change_flight_data', new_callable=MagicMock)
    def test_change_flight_success(self, mock_change_flight_data):
        logger.debug("Starting test_change_flight_success with booking_id B123")
        mock_change_flight_data.return_value = ("P123", "FL124", "2025-06-03", "Confirmed", 300.0)
        response = self.client.post(
            "/api/v1/change-flight/B123?new_flight_number=FL124",
            headers={"X-API-Key": self.secretvalue}
        )
        logger.debug(f"Response status: {response.status_code}, Response JSON: {response.json()}")

        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.json(), {
            "status": "success",
            "booking": {
                "passenger_id": "P123",
                "flight_number": "FL124",
                "booking_date": "2025-06-03",
                "status": "Confirmed",
                "total_price": 300.0
            },
            "policy": "Free within 24 hours, $75 fee after"
        })
        mock_change_flight_data.assert_called_once()

    @patch('src.api.endpoints.flight_management.change_flight_data', new_callable=MagicMock)
    def test_change_flight_unauthorized(self, mock_change_flight_data):
        logger.debug("Starting test_change_flight_unauthorized with booking_id B123")
        response = self.client.post(
            "/api/v1/change-flight/B123?new_flight_number=FL124",
            headers={"X-API-Key": "invalid-key"}
        )
        logger.debug(f"Response status: {response.status_code}, Response JSON: {response.json()}")

        self.assertEqual(response.status_code, 401)
        self.assertEqual(response.json(), {"detail": "Invalid or missing API Key"})

    @patch('src.api.endpoints.flight_management.purchase_flight_insurance_data', new_callable=MagicMock)
    def test_purchase_flight_insurance_success(self, mock_purchase_flight_insurance_data):
        logger.debug("Starting test_purchase_flight_insurance_success with booking_id B123")
        mock_purchase_flight_insurance_data.return_value = "INS123"
        response = self.client.post(
            "/api/v1/purchase-flight-insurance/B123",
            headers={"X-API-Key": self.secretvalue}
        )
        logger.debug(f"Response status: {response.status_code}, Response JSON: {response.json()}")

        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.json(), {
            "status": "success",
            "insurance_id": "INS123",
            "terms": "Covers cancellation up to $1,000"
        })
        mock_purchase_flight_insurance_data.assert_called_once()

    @patch('src.api.endpoints.flight_management.purchase_flight_insurance_data', new_callable=MagicMock)
    def test_purchase_flight_insurance_unauthorized(self, mock_purchase_flight_insurance_data):
        logger.debug("Starting test_purchase_flight_insurance_unauthorized with booking_id B123")
        response = self.client.post(
            "/api/v1/purchase-flight-insurance/B123",
            headers={"X-API-Key": "invalid-key"}
        )
        logger.debug(f"Response status: {response.status_code}, Response JSON: {response.json()}")

        self.assertEqual(response.status_code, 401)
        self.assertEqual(response.json(), {"detail": "Invalid or missing API Key"})

    @patch('src.api.endpoints.flight_management.get_refund_data', new_callable=MagicMock)
    def test_get_refund_success(self, mock_get_refund_data):
        logger.debug("Starting test_get_refund_success with booking_id B123")
        mock_get_refund_data.return_value = True
        response = self.client.post(
            "/api/v1/get-refund/B123",
            headers={"X-API-Key": self.secretvalue}
        )
        logger.debug(f"Response status: {response.status_code}, Response JSON: {response.json()}")

        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.json(), {
            "status": "success",
            "booking_status": "Refunded",
            "policy": "Processed in 5-7 days, 50% penalty for non-refundable"
        })
        mock_get_refund_data.assert_called_once()

    @patch('src.api.endpoints.flight_management.get_refund_data', new_callable=MagicMock)
    def test_get_refund_unauthorized(self, mock_get_refund_data):
        logger.debug("Starting test_get_refund_unauthorized with booking_id B123")
        response = self.client.post(
            "/api/v1/get-refund/B123",
            headers={"X-API-Key": "invalid-key"}
        )
        logger.debug(f"Response status: {response.status_code}, Response JSON: {response.json()}")

        self.assertEqual(response.status_code, 401)
        self.assertEqual(response.json(), {"detail": "Invalid or missing API Key"})

    @patch('src.api.endpoints.flight_management.get_arrival_time_data', new_callable=MagicMock)
    def test_check_arrival_time_success(self, mock_get_arrival_time_data):
        logger.debug("Starting test_check_arrival_time_success with flight_number FL123")
        mock_get_arrival_time_data.return_value = ("2025-06-08T12:00:00")
        response = self.client.get(
            "/api/v1/arrival-time/FL123",
            headers={"X-API-Key": self.secretvalue}
        )
        logger.debug(f"Response status: {response.status_code}, Response JSON: {response.json()}")
        
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.json(), {"status": "success", "arrival_time": "2025-06-08T12:00:00"})
        mock_get_arrival_time_data.assert_called_once()

    @patch('src.api.endpoints.flight_management.get_arrival_time_data', new_callable=MagicMock)
    def test_check_arrival_time_unauthorized(self, mock_get_arrival_time_data):
        logger.debug("Starting test_check_arrival_time_unauthorized with flight_number FL123")
        response = self.client.get(
            "/api/v1/arrival-time/FL123",
            headers={"X-API-Key": "invalid-key"}
        )
        logger.debug(f"Response status: {response.status_code}, Response JSON: {response.json()}")

        self.assertEqual(response.status_code, 401)
        self.assertEqual(response.json(), {"detail": "Invalid or missing API Key"})

    @patch('src.api.endpoints.flight_management.get_departure_time_data', new_callable=MagicMock)
    def test_check_departure_time_success(self, mock_get_departure_time_data):
        logger.debug("Starting test_check_departure_time_success with flight_number FL123")
        mock_get_departure_time_data.return_value = "2025-06-08T09:00:00"
        response = self.client.get(
            "/api/v1/departure-time/FL123",
            headers={"X-API-Key": self.secretvalue}
        )
        logger.debug(f"Response status: {response.status_code}, Response JSON: {response.json()}")

        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.json(), {"status": "success", "departure_time": "2025-06-08T09:00:00"})
        mock_get_departure_time_data.assert_called_once()

    @patch('src.api.endpoints.flight_management.get_departure_time_data', new_callable=MagicMock)
    def test_check_departure_time_unauthorized(self, mock_get_departure_time_data):
        logger.debug("Starting test_check_departure_time_unauthorized with flight_number FL123")
        response = self.client.get(
            "/api/v1/departure-time/FL123",
            headers={"X-API-Key": "invalid-key"}
        )
        logger.debug(f"Response status: {response.status_code}, Response JSON: {response.json()}")

        self.assertEqual(response.status_code, 401)
        self.assertEqual(response.json(), {"detail": "Invalid or missing API Key"})

    # Trip Management Service Tests
    @patch('src.api.endpoints.trip_management.get_trip_prices_data', new_callable=MagicMock)
    def test_check_trip_prices_success(self, mock_get_trip_prices_data):
        logger.debug("Starting test_check_trip_prices_success with trip_id T123")
        mock_get_trip_prices_data.return_value = (500.0,)
        response = self.client.get(
            "/api/v1/trip-prices/T123",
            headers={"X-API-Key": self.secretvalue}
        )
        logger.debug(f"Response status: {response.status_code}, Response JSON: {response.json()}")

        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.json(), {"status": "success", "trip_prices": {"total_price": 500.0}})
        mock_get_trip_prices_data.assert_called_once()

    @patch('src.api.endpoints.trip_management.get_trip_prices_data', new_callable=MagicMock)
    def test_check_trip_prices_unauthorized(self, mock_get_trip_prices_data):
        logger.debug("Starting test_check_trip_prices_unauthorized with trip_id T123")
        response = self.client.get(
            "/api/v1/trip-prices/T123",
            headers={"X-API-Key": "invalid-key"}
        )
        logger.debug(f"Response status: {response.status_code}, Response JSON: {response.json()}")

        self.assertEqual(response.status_code, 401)
        self.assertEqual(response.json(), {"detail": "Invalid or missing API Key"})

    @patch('src.api.endpoints.trip_management.book_trip_data', new_callable=MagicMock)
    def test_book_trip_success(self, mock_book_trip_data):
        logger.debug("Starting test_book_trip_success with passenger_id P124")
        mock_book_trip_data.return_value = "T124"
        response = self.client.post(
            "/api/v1/book-trip/?passenger_id=P124",
            headers={"X-API-Key": self.secretvalue}
        )
        logger.debug(f"Response status: {response.status_code}, Response JSON: {response.json()}")

        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.json(), {"status": "success", "trip_id": "T124"})
        mock_book_trip_data.assert_called_once()

    @patch('src.api.endpoints.trip_management.book_trip_data', new_callable=MagicMock)
    def test_book_trip_unauthorized(self, mock_book_trip_data):
        logger.debug("Starting test_book_trip_unauthorized with passenger_id P124")
        response = self.client.post(
            "/api/v1/book-trip/?passenger_id=P124",
            headers={"X-API-Key": "invalid-key"}
        )
        logger.debug(f"Response status: {response.status_code}, Response JSON: {response.json()}")

        self.assertEqual(response.status_code, 401)
        self.assertEqual(response.json(), {"detail": "Invalid or missing API Key"})

    @patch('src.api.endpoints.trip_management.get_trip_details_data', new_callable=MagicMock)
    def test_check_trip_details_success(self, mock_get_trip_details_data):
        logger.debug("Starting test_check_trip_details_success with trip_id T123")
        mock_get_trip_details_data.return_value = {"total_price": 500.0, "status": "Confirmed", "components": ["FL123", "FL124"]}
        response = self.client.get(
            "/api/v1/trip-details/T123",
            headers={"X-API-Key": self.secretvalue}
        )
        logger.debug(f"Response status: {response.status_code}, Response JSON: {response.json()}")

        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.json(), {
            "status": "success",
            "trip_details": {"total_price": 500.0, "status": "Confirmed", "components": ["FL123", "FL124"]}
        })
        mock_get_trip_details_data.assert_called_once()

    @patch('src.api.endpoints.trip_management.get_trip_details_data', new_callable=MagicMock)
    def test_check_trip_details_unauthorized(self, mock_get_trip_details_data):
        logger.debug("Starting test_check_trip_details_unauthorized with trip_id T123")
        response = self.client.get(
            "/api/v1/trip-details/T123",
            headers={"X-API-Key": "invalid-key"}
        )
        logger.debug(f"Response status: {response.status_code}, Response JSON: {response.json()}")

        self.assertEqual(response.status_code, 401)
        self.assertEqual(response.json(), {"detail": "Invalid or missing API Key"})

    @patch('src.api.endpoints.trip_management.get_trip_offers_data', new_callable=MagicMock)
    def test_check_trip_offers_success(self, mock_get_trip_offers_data):
        logger.debug("Starting test_check_trip_offers_success")
        mock_get_trip_offers_data.return_value = [{"trip_id": "T123", "price": 500.0}]
        response = self.client.get(
            "/api/v1/trip-offers/",
            headers={"X-API-Key": self.secretvalue}
        )
        logger.debug(f"Response status: {response.status_code}, Response JSON: {response.json()}")

        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.json(), {"status": "success", "offers": [{"trip_id": "T123", "price": 500.0}]})
        mock_get_trip_offers_data.assert_called_once()

    @patch('src.api.endpoints.trip_management.get_trip_offers_data', new_callable=MagicMock)
    def test_check_trip_offers_unauthorized(self, mock_get_trip_offers_data):
        logger.debug("Starting test_check_trip_offers_unauthorized")
        response = self.client.get(
            "/api/v1/trip-offers/",
            headers={"X-API-Key": "invalid-key"}
        )
        logger.debug(f"Response status: {response.status_code}, Response JSON: {response.json()}")

        self.assertEqual(response.status_code, 401)
        self.assertEqual(response.json(), {"detail": "Invalid or missing API Key"})

    @patch('src.api.endpoints.trip_management.get_trip_plan_data', new_callable=MagicMock)
    def test_check_trip_plan_success(self, mock_get_trip_plan_data):
        logger.debug("Starting test_check_trip_plan_success with trip_id T123")
        mock_get_trip_plan_data.return_value = {"flights": ["FL123", "FL124"], "hotels": ["H123"]}
        response = self.client.get(
            "/api/v1/trip-plan/T123",
            headers={"X-API-Key": self.secretvalue}
        )
        logger.debug(f"Response status: {response.status_code}, Response JSON: {response.json()}")

        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.json(), {"status": "success", "trip_plan": {"flights": ["FL123", "FL124"], "hotels": ["H123"]}})
        mock_get_trip_plan_data.assert_called_once()

    @patch('src.api.endpoints.trip_management.get_trip_plan_data', new_callable=MagicMock)
    def test_check_trip_plan_unauthorized(self, mock_get_trip_plan_data):
        logger.debug("Starting test_check_trip_plan_unauthorized with trip_id T123")
        response = self.client.get(
            "/api/v1/trip-plan/T123",
            headers={"X-API-Key": "invalid-key"}
        )
        logger.debug(f"Response status: {response.status_code}, Response JSON: {response.json()}")

        self.assertEqual(response.status_code, 401)
        self.assertEqual(response.json(), {"detail": "Invalid or missing API Key"})

    @patch('src.api.endpoints.trip_management.search_trips_data', new_callable=MagicMock)
    def test_search_trip_success(self, mock_search_trips_data):
        logger.debug("Starting test_search_trip_success with SYD to MEL on 2025-06-08")
        mock_search_trips_data.return_value = [{"trip_id": "T123", "price": 500.0}]
        response = self.client.get(
            "/api/v1/search-trip/SYD/MEL/2025-06-08",
            headers={"X-API-Key": self.secretvalue}
        )
        logger.debug(f"Response status: {response.status_code}, Response JSON: {response.json()}")

        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.json(), {"status": "success", "trips": [{"trip_id": "T123", "price": 500.0}]})
        mock_search_trips_data.assert_called_once()

    @patch('src.api.endpoints.trip_management.search_trips_data', new_callable=MagicMock)
    def test_search_trip_unauthorized(self, mock_search_trips_data):
        logger.debug("Starting test_search_trip_unauthorized with SYD to MEL on 2025-06-08")
        response = self.client.get(
            "/api/v1/search-trip/SYD/MEL/2025-06-08",
            headers={"X-API-Key": "invalid-key"}
        )
        logger.debug(f"Response status: {response.status_code}, Response JSON: {response.json()}")

        self.assertEqual(response.status_code, 401)
        self.assertEqual(response.json(), {"detail": "Invalid or missing API Key"})

    @patch('src.api.endpoints.trip_management.cancel_trip_data', new_callable=MagicMock)
    def test_cancel_trip_success(self, mock_cancel_trip_data):
        logger.debug("Starting test_cancel_trip_success with trip_id T123")
        mock_cancel_trip_data.return_value = True
        response = self.client.post(
            "/api/v1/cancel-trip/T123",
            headers={"X-API-Key": self.secretvalue}
        )
        logger.debug(f"Response status: {response.status_code}, Response JSON: {response.json()}")

        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.json(), {
            "status": "success",
            "trip_status": "Cancelled",
            "policy": "Free within 48 hours, $100 fee after"
        })
        mock_cancel_trip_data.assert_called_once()

    @patch('src.api.endpoints.trip_management.cancel_trip_data', new_callable=MagicMock)
    def test_cancel_trip_unauthorized(self, mock_cancel_trip_data):
        logger.debug("Starting test_cancel_trip_unauthorized with trip_id T123")
        response = self.client.post(
            "/api/v1/cancel-trip/T123",
            headers={"X-API-Key": "invalid-key"}
        )
        logger.debug(f"Response status: {response.status_code}, Response JSON: {response.json()}")

        self.assertEqual(response.status_code, 401)
        self.assertEqual(response.json(), {"detail": "Invalid or missing API Key"})

    @patch('src.api.endpoints.trip_management.change_trip_data', new_callable=MagicMock)
    def test_change_trip_success(self, mock_change_trip_data):
        logger.debug("Starting test_change_trip_success with trip_id T123")
        mock_change_trip_data.return_value = ("Flight", "FL124", 300.0)
        response = self.client.post(
            "/api/v1/change-trip/T123?new_flight_number=FL124",
            headers={"X-API-Key": self.secretvalue}
        )
        logger.debug(f"Response status: {response.status_code}, Response JSON: {response.json()}")

        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.json(), {
            "status": "success",
            "trip_component": {"component_type": "Flight", "flight_number": "FL124", "price": 300.0},
            "policy": "Free within 48 hours, $100 fee after"
        })
        mock_change_trip_data.assert_called_once()

    @patch('src.api.endpoints.trip_management.change_trip_data', new_callable=MagicMock)
    def test_change_trip_unauthorized(self, mock_change_trip_data):
        logger.debug("Starting test_change_trip_unauthorized with trip_id T123")
        response = self.client.post(
            "/api/v1/change-trip/T123?new_flight_number=FL124",
            headers={"X-API-Key": "invalid-key"}
        )
        logger.debug(f"Response status: {response.status_code}, Response JSON: {response.json()}")

        self.assertEqual(response.status_code, 401)
        self.assertEqual(response.json(), {"detail": "Invalid or missing API Key"})

    @patch('src.api.endpoints.trip_management.purchase_trip_insurance_data', new_callable=MagicMock)
    def test_purchase_trip_insurance_success(self, mock_purchase_trip_insurance_data):
        logger.debug("Starting test_purchase_trip_insurance_success with trip_id T123")
        mock_purchase_trip_insurance_data.return_value = "INS124"
        response = self.client.post(
            "/api/v1/purchase-trip-insurance/T123",
            headers={"X-API-Key": self.secretvalue}
        )
        logger.debug(f"Response status: {response.status_code}, Response JSON: {response.json()}")

        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.json(), {
            "status": "success",
            "insurance_id": "INS124",
            "terms": "Covers cancellation up to $2,000"
        })
        mock_purchase_trip_insurance_data.assert_called_once()

    @patch('src.api.endpoints.trip_management.purchase_trip_insurance_data', new_callable=MagicMock)
    def test_purchase_trip_insurance_unauthorized(self, mock_purchase_trip_insurance_data):
        logger.debug("Starting test_purchase_trip_insurance_unauthorized with trip_id T123")
        response = self.client.post(
            "/api/v1/purchase-trip-insurance/T123",
            headers={"X-API-Key": "invalid-key"}
        )
        logger.debug(f"Response status: {response.status_code}, Response JSON: {response.json()}")

        self.assertEqual(response.status_code, 401)
        self.assertEqual(response.json(), {"detail": "Invalid or missing API Key"})

if __name__ == "__main__":
    unittest.main()