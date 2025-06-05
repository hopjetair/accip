import unittest
import os
from fastapi.testclient import TestClient
from src.api.main_no_auth import app
from unittest.mock import patch, MagicMock

class TestNoAuthAPI(unittest.TestCase):
    def setUp(self):
        self.client = TestClient(app)
        # Mock database connection and cursor
        self.mock_conn = MagicMock()
        self.mock_cursor = MagicMock()
        self.mock_conn.cursor.return_value = self.mock_cursor
        patcher = patch('src.api.endpoints_no_auth.get_db_connection', return_value=self.mock_conn)
        self.addCleanup(patcher.stop)
        patcher.start()

    def test_get_boarding_pass_success(self):
        self.mock_cursor.fetchone.return_value = ("B5", "5B", "2025-06-08T09:30:00", "https://airline.com/boardingpass/B123.pdf")
        response = self.client.get("/api/v1/boarding-pass/B123")
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.json(), {
            "status": "success",
            "boarding_pass": {
                "gate": "B5", "seat": "5B", "boarding_time": "2025-06-08T09:30:00",
                "pdf_url": "https://airline.com/boardingpass/B123.pdf"
            }
        })

    def test_get_boarding_pass_not_found(self):
        self.mock_cursor.fetchone.return_value = None
        response = self.client.get("/api/v1/boarding-pass/B999")
        self.assertEqual(response.status_code, 404)
        self.assertEqual(response.json(), {"detail": "Boarding pass not found"})

    def test_print_boarding_pass_success(self):
        self.mock_cursor.fetchone.return_value = ("B5", "5B", "2025-06-08T09:30:00", "https://airline.com/boardingpass/B123.pdf")
        response = self.client.get("/api/v1/print-boarding-pass/B123")
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.json(), {
            "status": "success",
            "boarding_pass": {
                "gate": "B5", "seat": "5B", "boarding_time": "2025-06-08T09:30:00",
                "pdf_url": "https://airline.com/boardingpass/B123.pdf"
            }
        })

    def test_check_in_success(self):
        self.mock_cursor.rowcount = 1
        response = self.client.post("/api/v1/check-in/B123")
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.json(), {
            "status": "success",
            "message": "Check-in successful",
            "boarding_pass": {"gate": "B5", "seat": "5B", "boarding_time": "2025-06-08T09:30:00"}
        })

    def test_check_in_not_found(self):
        self.mock_cursor.rowcount = 0
        response = self.client.post("/api/v1/check-in/B999")
        self.assertEqual(response.status_code, 404)
        self.assertEqual(response.json(), {"detail": "Booking not found"})

    def test_book_flight_success(self):
        self.mock_cursor.fetchone.return_value = (300.00, 10)
        self.mock_cursor.rowcount = 1
        response = self.client.post("/api/v1/book-flight/?flight_number=FL123&passenger_id=P123")
        self.assertEqual(response.status_code, 200)
        self.assertIn("booking_id", response.json())

    def test_book_flight_not_available(self):
        self.mock_cursor.fetchone.return_value = (300.00, 0)
        response = self.client.post("/api/v1/book-flight/?flight_number=FL123&passenger_id=P123")
        self.assertEqual(response.status_code, 400)
        self.assertEqual(response.json(), {"detail": "Flight not available"})

    def test_get_flight_offers(self):
        self.mock_cursor.fetchall.return_value = [("Offer 1", 200.00, 10.00)]
        response = self.client.get("/api/v1/flight-offers/")
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.json(), {
            "status": "success",
            "offers": [{"description": "Offer 1", "price": 200.00, "discount": 10.00}]
        })

    def test_get_flight_prices_success(self):
        self.mock_cursor.fetchone.return_value = (300.00, 10)
        response = self.client.get("/api/v1/flight-prices/FL123")
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.json(), {
            "status": "success",
            "prices": {"price": 300.00, "availability": 10}
        })

    def test_get_flight_reservation_success(self):
        self.mock_cursor.fetchone.return_value = ("P123", "FL123", "2025-06-03", "Confirmed", 300.00, "SYD", "MEL")
        response = self.client.get("/api/v1/flight-reservation/B123")
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.json(), {
            "status": "success",
            "reservation": {
                "passenger_id": "P123", "flight_number": "FL123", "booking_date": "2025-06-03",
                "status": "Confirmed", "total_price": 300.00, "departure": "SYD", "destination": "MEL"
            }
        })

    def test_get_flight_status_success(self):
        self.mock_cursor.fetchone.return_value = ("SYD", "MEL", "On Time", "2025-06-08T10:00:00", "2025-06-08T12:00:00", "A1")
        response = self.client.get("/api/v1/flight-status/FL123")
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.json(), {
            "status": "success",
            "flight_status": {
                "departure": "SYD", "destination": "MEL", "status": "On Time",
                "departure_time": "2025-06-08T10:00:00", "arrival_time": "2025-06-08T12:00:00", "gate": "A1"
            }
        })

    def test_search_flight(self):
        self.mock_cursor.fetchall.return_value = [("FL123", "SYD", "MEL", "2025-06-08T10:00:00", 300.00, 10)]
        response = self.client.get("/api/v1/search-flight/SYD/MEL/2025-06-08")
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.json(), {
            "status": "success",
            "flights": [{
                "flight_number": "FL123", "departure": "SYD", "destination": "MEL",
                "departure_time": "2025-06-08T10:00:00", "price": 300.00, "availability": 10
            }]
        })

    def test_get_trip_prices_success(self):
        self.mock_cursor.fetchone.return_value = (750.00,)
        response = self.client.get("/api/v1/trip-prices/T123")
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.json(), {
            "status": "success",
            "trip_prices": {"total_price": 750.00}
        })

    def test_choose_seat(self):
        response = self.client.post("/api/v1/choose-seat/B123?seat_number=12A")
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.json(), {
            "status": "success",
            "seat": {"booking_id": "B123", "flight_number": "LH234", "seat_number": "12A", "additional_fee": 0.00}
        })

    def test_get_arrival_time_success(self):
        self.mock_cursor.fetchone.return_value = ("2025-06-08T12:00:00",)
        response = self.client.get("/api/v1/arrival-time/FL123")
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.json(), {
            "status": "success",
            "arrival_time": "2025-06-08T12:00:00"
        })

    def test_get_departure_time_success(self):
        self.mock_cursor.fetchone.return_value = ("2025-06-08T10:00:00",)
        response = self.client.get("/api/v1/departure-time/FL123")
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.json(), {
            "status": "success",
            "departure_time": "2025-06-08T10:00:00"
        })

    def test_book_trip(self):
        response = self.client.post("/api/v1/book-trip/?passenger_id=P123")
        self.assertEqual(response.status_code, 200)
        self.assertIn("trip_id", response.json())

    def test_get_trip_details_success(self):
        self.mock_cursor.fetchone.return_value = (750.00, "Confirmed")
        self.mock_cursor.fetchall.return_value = [("Flight", "SQ123", 600.00)]
        response = self.client.get("/api/v1/trip-details/T123")
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.json(), {
            "status": "success",
            "trip_details": {
                "total_price": 750.00, "status": "Confirmed",
                "components": [{"component_type": "Flight", "flight_number": "SQ123", "price": 600.00}]
            }
        })

    def test_get_trip_offers(self):
        self.mock_cursor.fetchall.return_value = [("Offer 1", 500.00, 20.00)]
        response = self.client.get("/api/v1/trip-offers/")
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.json(), {
            "status": "success",
            "offers": [{"description": "Offer 1", "price": 500.00, "discount": 20.00}]
        })

    def test_get_trip_plan_success(self):
        self.mock_cursor.fetchall.return_value = [("Flight", "SQ123", 600.00)]
        response = self.client.get("/api/v1/trip-plan/T123")
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.json(), {
            "status": "success",
            "trip_plan": [{"component_type": "Flight", "flight_number": "SQ123", "price": 600.00}]
        })

    def test_search_trip(self):
        self.mock_cursor.fetchall.return_value = [("T123", 750.00)]
        response = self.client.get("/api/v1/search-trip/SYD/MEL/2025-06-08")
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.json(), {
            "status": "success",
            "trips": [{"trip_id": "T123", "total_price": 750.00}]
        })

    def test_cancel_flight_success(self):
        self.mock_cursor.rowcount = 1
        response = self.client.post("/api/v1/cancel-flight/B123")
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.json(), {
            "status": "success",
            "booking_status": "Cancelled",
            "policy": "Free within 24 hours, $50 fee after"
        })

    def test_change_flight_success(self):
        self.mock_cursor.rowcount = 1
        self.mock_cursor.fetchone.return_value = ("P123", "FL456", "2025-06-03", "Confirmed", 350.00)
        response = self.client.post("/api/v1/change-flight/B123?new_flight_number=FL456")
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.json(), {
            "status": "success",
            "booking": {
                "passenger_id": "P123", "flight_number": "FL456", "booking_date": "2025-06-03",
                "status": "Confirmed", "total_price": 350.00
            },
            "policy": "Free within 24 hours, $75 fee after"
        })

    def test_purchase_flight_insurance(self):
        response = self.client.post("/api/v1/purchase-flight-insurance/B123")
        self.assertEqual(response.status_code, 200)
        self.assertIn("insurance_id", response.json())

    def test_get_refund_success(self):
        self.mock_cursor.rowcount = 1
        response = self.client.post("/api/v1/get-refund/B123")
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.json(), {
            "status": "success",
            "booking_status": "Refunded",
            "policy": "Processed in 5-7 days, 50% penalty for non-refundable"
        })

    def test_change_seat_success(self):
        self.mock_cursor.rowcount = 1
        self.mock_cursor.fetchone.return_value = ("FL123", "12B", 0.00)
        response = self.client.post("/api/v1/change-seat/B123?seat_number=12B")
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.json(), {
            "status": "success",
            "seat": {"flight_number": "FL123", "seat_number": "12B", "additional_fee": 0.00},
            "policy": "$20 fee for changes"
        })

    def test_cancel_trip_success(self):
        self.mock_cursor.rowcount = 1
        response = self.client.post("/api/v1/cancel-trip/T123")
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.json(), {
            "status": "success",
            "trip_status": "Cancelled",
            "policy": "Free within 48 hours, $100 fee after"
        })

    def test_change_trip_success(self):
        self.mock_cursor.rowcount = 1
        self.mock_cursor.fetchone.return_value = ("Flight", "FL456", 650.00)
        response = self.client.post("/api/v1/change-trip/T123?new_flight_number=FL456")
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.json(), {
            "status": "success",
            "trip_component": {"component_type": "Flight", "flight_number": "FL456", "price": 650.00},
            "policy": "Free within 48 hours, $100 fee after"
        })

    def test_purchase_trip_insurance(self):
        response = self.client.post("/api/v1/purchase-trip-insurance/T123")
        self.assertEqual(response.status_code, 200)
        self.assertIn("insurance_id", response.json())

if __name__ == "__main__":
    unittest.main()