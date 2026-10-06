import pytest
from fastapi.testclient import TestClient

import src.app as app_module


ACTIVITY_NAME = "Robotics Club"
EXISTING_EMAIL = "student@mergington.edu"


@pytest.fixture
def client(monkeypatch):
    activities = {
        ACTIVITY_NAME: {
            "description": "Build and program robots",
            "schedule": "Fridays, 3:00 PM - 4:00 PM",
            "max_participants": 5,
            "participants": [EXISTING_EMAIL],
        }
    }
    monkeypatch.setattr(app_module, "activities", activities)
    return TestClient(app_module.app)


def test_get_activities_returns_activity_details(client):
    # Arrange
    expected_activity = {
        "description": "Build and program robots",
        "schedule": "Fridays, 3:00 PM - 4:00 PM",
        "max_participants": 5,
        "participants": [EXISTING_EMAIL],
    }

    # Act
    response = client.get("/activities")

    # Assert
    assert response.status_code == 200
    assert response.json() == {ACTIVITY_NAME: expected_activity}


def test_signup_adds_participant(client):
    # Arrange
    new_email = "new.student@mergington.edu"

    # Act
    response = client.post(
        f"/activities/{ACTIVITY_NAME}/signup",
        params={"email": new_email},
    )

    # Assert
    assert response.status_code == 200
    assert response.json() == {
        "message": f"Signed up {new_email} for {ACTIVITY_NAME}"
    }
    participants = client.get("/activities").json()[ACTIVITY_NAME]["participants"]
    assert participants == [EXISTING_EMAIL, new_email]


def test_signup_returns_404_for_unknown_activity(client):
    # Arrange
    unknown_activity = "Unknown Club"

    # Act
    response = client.post(
        f"/activities/{unknown_activity}/signup",
        params={"email": "new.student@mergington.edu"},
    )

    # Assert
    assert response.status_code == 404
    assert response.json() == {"detail": "Activity not found"}


def test_signup_returns_400_for_duplicate_participant(client):
    # Arrange
    email = EXISTING_EMAIL

    # Act
    response = client.post(
        f"/activities/{ACTIVITY_NAME}/signup",
        params={"email": email},
    )

    # Assert
    assert response.status_code == 400
    assert response.json() == {
        "detail": "Student is already signed up for this activity"
    }


def test_remove_participant_unregisters_student(client):
    # Arrange
    email = EXISTING_EMAIL

    # Act
    response = client.delete(
        f"/activities/{ACTIVITY_NAME}/signup",
        params={"email": email},
    )

    # Assert
    assert response.status_code == 200
    assert response.json() == {
        "message": f"Removed {EXISTING_EMAIL} from {ACTIVITY_NAME}"
    }
    participants = client.get("/activities").json()[ACTIVITY_NAME]["participants"]
    assert participants == []


def test_remove_participant_returns_404_for_unknown_activity(client):
    # Arrange
    unknown_activity = "Unknown Club"

    # Act
    response = client.delete(
        f"/activities/{unknown_activity}/signup",
        params={"email": EXISTING_EMAIL},
    )

    # Assert
    assert response.status_code == 404
    assert response.json() == {"detail": "Activity not found"}


def test_remove_participant_returns_404_if_not_signed_up(client):
    # Arrange
    missing_email = "missing.student@mergington.edu"

    # Act
    response = client.delete(
        f"/activities/{ACTIVITY_NAME}/signup",
        params={"email": missing_email},
    )

    # Assert
    assert response.status_code == 404
    assert response.json() == {
        "detail": "Student is not signed up for this activity"
    }