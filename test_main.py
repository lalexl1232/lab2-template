#!/usr/bin/env python3
"""
Integration tests for Car Rental System
Tests health endpoints and gateway API endpoints
"""
import pytest
import requests

BASE_URL = "http://localhost:8080"
CARS_SERVICE_URL = "http://localhost:8070"
RENTAL_SERVICE_URL = "http://localhost:8060"
PAYMENT_SERVICE_URL = "http://localhost:8050"

# Health check tests
def test_gateway_health():
    """Test Gateway service health endpoint"""
    response = requests.get(f"{BASE_URL}/manage/health")
    print(f"Gateway health: {response.status_code} - {response.json()}")
    assert response.status_code == 200
    assert response.json()["status"] == "ok"

def test_cars_service_health():
    """Test Cars service health endpoint"""
    response = requests.get(f"{CARS_SERVICE_URL}/manage/health")
    print(f"Cars service health: {response.status_code} - {response.json()}")
    assert response.status_code == 200
    assert response.json()["status"] == "ok"

def test_rental_service_health():
    """Test Rental service health endpoint"""
    response = requests.get(f"{RENTAL_SERVICE_URL}/manage/health")
    print(f"Rental service health: {response.status_code} - {response.json()}")
    assert response.status_code == 200
    assert response.json()["status"] == "ok"

def test_payment_service_health():
    """Test Payment service health endpoint"""
    response = requests.get(f"{PAYMENT_SERVICE_URL}/manage/health")
    print(f"Payment service health: {response.status_code} - {response.json()}")
    assert response.status_code == 200
    assert response.json()["status"] == "ok"

# Gateway API tests
def test_get_cars():
    """Test GET /api/v1/cars endpoint"""
    response = requests.get(f"{BASE_URL}/api/v1/cars?page=1&size=10&showAll=false")
    print(f"GET /api/v1/cars: {response.status_code}")
    assert response.status_code == 200
    data = response.json()
    assert "items" in data
    assert "page" in data
    assert "pageSize" in data
    assert "totalElements" in data

def test_get_user_rentals():
    """Test GET /api/v1/rental endpoint"""
    headers = {"X-User-Name": "Test Max"}
    response = requests.get(f"{BASE_URL}/api/v1/rental", headers=headers)
    print(f"GET /api/v1/rental: {response.status_code}")
    assert response.status_code == 200
    assert isinstance(response.json(), list)

def test_create_and_cancel_rental():
    """Test POST /api/v1/rental and DELETE /api/v1/rental/{rental_uid} endpoints"""
    headers = {"X-User-Name": "Test Max"}

    # Create rental
    rental_data = {
        "carUid": "109b42f3-198d-4c89-9276-a7520a7120ab",
        "dateFrom": "2021-10-08",
        "dateTo": "2021-10-11"
    }
    response = requests.post(f"{BASE_URL}/api/v1/rental", json=rental_data, headers=headers)
    print(f"POST /api/v1/rental: {response.status_code}")
    assert response.status_code == 200

    data = response.json()
    assert "rentalUid" in data
    assert "status" in data
    assert data["status"] == "IN_PROGRESS"

    rental_uid = data["rentalUid"]

    # Get specific rental
    response = requests.get(f"{BASE_URL}/api/v1/rental/{rental_uid}", headers=headers)
    print(f"GET /api/v1/rental/{rental_uid}: {response.status_code}")
    assert response.status_code == 200
    data = response.json()
    assert data["rentalUid"] == rental_uid

    # Cancel rental
    response = requests.delete(f"{BASE_URL}/api/v1/rental/{rental_uid}", headers=headers)
    print(f"DELETE /api/v1/rental/{rental_uid}: {response.status_code}")
    assert response.status_code == 204

def test_create_and_finish_rental():
    """Test POST /api/v1/rental/{rental_uid}/finish endpoint"""
    headers = {"X-User-Name": "Test Max"}

    # Create rental
    rental_data = {
        "carUid": "109b42f3-198d-4c89-9276-a7520a7120ab",
        "dateFrom": "2021-10-08",
        "dateTo": "2021-10-11"
    }
    response = requests.post(f"{BASE_URL}/api/v1/rental", json=rental_data, headers=headers)
    print(f"POST /api/v1/rental: {response.status_code}")
    assert response.status_code == 200

    rental_uid = response.json()["rentalUid"]

    # Finish rental
    response = requests.post(f"{BASE_URL}/api/v1/rental/{rental_uid}/finish", headers=headers)
    print(f"POST /api/v1/rental/{rental_uid}/finish: {response.status_code}")
    assert response.status_code == 204

    # Verify status changed
    response = requests.get(f"{BASE_URL}/api/v1/rental/{rental_uid}", headers=headers)
    assert response.status_code == 200
    data = response.json()
    assert data["status"] == "FINISHED"

if __name__ == "__main__":
    pytest.main([__file__, "-v"])
