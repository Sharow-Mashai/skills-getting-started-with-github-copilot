import pytest
from fastapi.testclient import TestClient

import src.app as app_module


@pytest.fixture
def client(monkeypatch):
    test_activities = {
        "Test Activity": {
            "description": "A test activity",
            "schedule": "Fridays",
            "max_participants": 3,
            "participants": ["existing@mergington.edu"],
        }
    }
    monkeypatch.setattr(app_module, "activities", test_activities)

    with TestClient(app_module.app) as test_client:
        yield test_client


def test_get_activities_returns_activity_data(client):
    response = client.get("/activities")

    assert response.status_code == 200
    assert response.json()["Test Activity"]["participants"] == [
        "existing@mergington.edu"
    ]


def test_signup_adds_participant(client):
    response = client.post(
        "/activities/Test Activity/signup",
        params={"email": "new@mergington.edu"},
    )

    assert response.status_code == 200
    assert response.json() == {
        "message": "Signed up new@mergington.edu for Test Activity"
    }
    assert (
        "new@mergington.edu"
        in app_module.activities["Test Activity"]["participants"]
    )


def test_signup_rejects_duplicate_participant(client):
    response = client.post(
        "/activities/Test Activity/signup",
        params={"email": "existing@mergington.edu"},
    )

    assert response.status_code == 400
    assert response.json()["detail"] == "Student already signed up for this activity"
    assert app_module.activities["Test Activity"]["participants"] == [
        "existing@mergington.edu"
    ]


def test_signup_rejects_unknown_activity(client):
    response = client.post(
        "/activities/Unknown/signup",
        params={"email": "new@mergington.edu"},
    )

    assert response.status_code == 404
    assert response.json()["detail"] == "Activity not found"


def test_unregister_removes_participant(client):
    response = client.delete(
        "/activities/Test Activity/participants",
        params={"email": "existing@mergington.edu"},
    )

    assert response.status_code == 200
    assert response.json() == {
        "message": "Unregistered existing@mergington.edu from Test Activity"
    }
    assert app_module.activities["Test Activity"]["participants"] == []


def test_unregister_rejects_unknown_activity(client):
    response = client.delete(
        "/activities/Unknown/participants",
        params={"email": "existing@mergington.edu"},
    )

    assert response.status_code == 404
    assert response.json()["detail"] == "Activity not found"


def test_unregister_rejects_unregistered_participant(client):
    response = client.delete(
        "/activities/Test Activity/participants",
        params={"email": "missing@mergington.edu"},
    )

    assert response.status_code == 404
    assert response.json()["detail"] == "Student is not registered for this activity"
