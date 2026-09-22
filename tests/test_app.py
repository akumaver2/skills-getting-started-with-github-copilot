import pytest
from fastapi.testclient import TestClient

from app import app, activities


@pytest.fixture(autouse=True)
def reset_activities():
    original = {
        name: {
            "description": details["description"],
            "schedule": details["schedule"],
            "max_participants": details["max_participants"],
            "participants": list(details["participants"]),
        }
        for name, details in activities.items()
    }

    activities.clear()
    activities.update(original)
    yield
    activities.clear()
    activities.update(original)


client = TestClient(app)


def test_get_activities_returns_all_activity_data():
    response = client.get("/activities")

    assert response.status_code == 200
    data = response.json()
    assert "Chess Club" in data
    assert data["Chess Club"]["participants"] == ["michael@mergington.edu", "daniel@mergington.edu"]


def test_signup_adds_new_participant():
    email = "newstudent@mergington.edu"

    response = client.post("/activities/Chess Club/signup?email=" + email)

    assert response.status_code == 200
    assert response.json()["message"] == f"Signed up {email} for Chess Club"
    assert email in activities["Chess Club"]["participants"]


def test_signup_rejects_duplicate_participant():
    email = "michael@mergington.edu"

    response = client.post("/activities/Chess Club/signup?email=" + email)

    assert response.status_code == 400
    assert response.json()["detail"] == "Student already signed up for this activity"


def test_signup_rejects_unknown_activity():
    response = client.post("/activities/Unknown Activity/signup?email=test@example.com")

    assert response.status_code == 404
    assert response.json()["detail"] == "Activity not found"


def test_unregister_removes_participant():
    email = "michael@mergington.edu"

    response = client.delete(f"/activities/Chess Club/participants/{email}")

    assert response.status_code == 200
    assert response.json()["message"] == f"Removed {email} from Chess Club"
    assert email not in activities["Chess Club"]["participants"]


def test_unregister_missing_participant_returns_404():
    email = "missing@mergington.edu"

    response = client.delete(f"/activities/Chess Club/participants/{email}")

    assert response.status_code == 404
    assert response.json()["detail"] == "Student is not signed up for this activity"
