# TODO: Add tests for rate limiter

from fastapi.testclient import TestClient
from main import app
from time import time

client = TestClient(app)

def test_post_observation():
    current_time = round(time())
    new_observation = {
        "external_id": 12345,
        "provider": "INaturalist",
        "observed_on": current_time,
        "posted_on": current_time,
        "description": "Test observation",
        "latitude": 48.8566,
        "longitude": 2.3522,
        "observer": "test_user",
        "place": "Paris",
        "photos": []
    }
    response = client.post("/observation", json=new_observation)
    assert response.status_code == 200
    assert isinstance(response.json(), int)
    
def test_post_multiple_observations():
    current_time = round(time())
    new_observations = [
        {
            "external_id": 12346,
            "provider": "INaturalist",
            "observed_on": current_time,
            "posted_on": current_time,
            "description": "Test observation 1",
            "latitude": 48.8566,
            "longitude": 2.3522,
            "observer": "test_user",
            "place": "Paris",
            "photos": []
        },
        {
            "external_id": 12347,
            "provider": "INaturalist",
            "observed_on": current_time,
            "posted_on": current_time,
            "description": "Test observation 2",
            "latitude": 48.8566,
            "longitude": 2.3522,
            "observer": "test_user",
            "place": "Paris",
            "photos": []
        }
    ]
    response = client.post("/observations", json=new_observations)
    assert response.status_code == 200
    assert isinstance(response.json(), list)
    assert all(isinstance(id, int) for id in response.json())

def test_read_observations():
    response = client.get("/observations")
    assert response.status_code == 200
    assert isinstance(response.json(), list)

def test_read_observation():
    response = client.get("/observation/1")
    assert response.status_code == 200
    assert isinstance(response.json()["id"], int)

def test_read_nonexistent_observation():
    response = client.get("/observation/99999")
    assert response.status_code == 404

def test_update_observation():
    current_time = round(time())
    updated_observation = {
        "external_id": 12348,
        "provider": "INaturalist",
        "observed_on": current_time,
        "posted_on": current_time,
        "description": "Updated observation",
        "latitude": 48.8566,
        "longitude": 2.3522,
        "observer": "updated_user",
        "place": "Paris",
        "photos": []
    }
    response = client.put("/observations/1", json=updated_observation)
    assert response.status_code == 200
    assert isinstance(response.json(), int)

def test_update_nonexistent_observation():
    current_time = round(time())
    updated_observation = {
        "external_id": 12349,
        "provider": "INaturalist",
        "observed_on": current_time,
        "posted_on": current_time,
        "description": "Updated observation",
        "latitude": 48.8566,
        "longitude": 2.3522,
        "observer": "updated_user",
        "place": "Paris",
        "photos": []
    }
    response = client.put("/observations/99999", json=updated_observation)
    assert response.status_code == 404

def test_delete_observation():
    response = client.delete("/observations/3")
    assert response.status_code == 200
    assert isinstance(response.json(), int)

def test_delete_nonexistent_observation():
    response = client.delete("/observations/99999")
    assert response.status_code == 404