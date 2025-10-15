import pytest
from fastapi.testclient import TestClient
from src.app import app

client = TestClient(app)

def test_get_activities():
    response = client.get("/activities")
    assert response.status_code == 200
    data = response.json()
    assert isinstance(data, dict)
    assert all("description" in v for v in data.values())
    assert all("participants" in v for v in data.values())

def test_signup_and_unregister():
    activity = list(client.get("/activities").json().keys())[0]
    email = "testuser@example.com"
    # Sign up
    signup = client.post(f"/activities/{activity}/signup?email={email}")
    assert signup.status_code == 200
    # Check participant added
    participants = client.get("/activities").json()[activity]["participants"]
    assert email in participants
    # Unregister
    unregister = client.post(f"/activities/{activity}/unregister?email={email}")
    assert unregister.status_code == 200
    # Check participant removed
    participants = client.get("/activities").json()[activity]["participants"]
    assert email not in participants

def test_signup_twice():
    activity = list(client.get("/activities").json().keys())[0]
    email = "doubleuser@example.com"
    # First signup
    client.post(f"/activities/{activity}/signup?email={email}")
    # Second signup should fail
    response = client.post(f"/activities/{activity}/signup?email={email}")
    assert response.status_code == 400
    assert "signed up" in response.json()["detail"].lower()
    # Cleanup
    client.post(f"/activities/{activity}/unregister?email={email}")

def test_unregister_nonexistent():
    activity = list(client.get("/activities").json().keys())[0]
    email = "notfound@example.com"
    response = client.post(f"/activities/{activity}/unregister?email={email}")
    assert response.status_code == 400
    assert "not registered" in response.json()["detail"].lower()
