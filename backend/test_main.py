from fastapi.testclient import TestClient
from main import app

client = TestClient(app)

def test_health_check():
    response = client.get("/health")

    assert response.status_code == 200
    assert response.json()["status"] == "ok"

def test_wifi_question():
    response = client.post(
        "/api/chat",
        json={"message": "Is Wi-Fi available?", "history": []}
    )

    assert response.status_code == 200
    assert "Free Wi-Fi" in response.json()["reply"]

def test_availability_missing_dates():
    response = client.post(
        "/api/chat",
        json={"message": "Do you have rooms available?", "history": []}
    )

    assert response.status_code == 200
    assert "check-in and check-out dates" in response.json()["reply"]

def test_successful_room_availability():
    response = client.post(
        "/api/chat",
        json={
            "message": "I need a room from 2026-09-25 to 2026-09-27 for 2 adults",
            "history": []
        }
    )

    assert response.status_code == 200

    data = response.json()

    assert "Rooms are available" in data["reply"]
    assert data["rooms"] is not None
    assert len(data["rooms"]) > 0

def test_invalid_dates():
    response = client.post(
        "/api/chat",
        json={
            "message": "I need a room from 2026-09-27 to 2026-09-25 for 2 adults",
            "history": []
        }
    )

    assert response.status_code == 200
    assert "Check-out date must be after check-in date" in response.json()["reply"]

def test_pets_policy():
    response = client.post(
        "/api/chat",
        json={"message": "Do you allow pets?", "history": []}
    )

    assert response.status_code == 200
    assert "Pets are not allowed" in response.json()["reply"]

def test_availability_follow_up():
    response = client.post(
        "/api/chat",
        json={
            "message": "2 adults",
            "history": [
                {
                    "role": "user",
                    "content": "Do you have rooms available?"
                },
                {
                    "role": "assistant",
                    "content": "I'd be happy to check room availability. Please provide your check-in and check-out dates in YYYY-MM-DD format."
                },
                {
                    "role": "user",
                    "content": "2026-09-25 to 2026-09-27"
                }
            ]
        }
    )

    assert response.status_code == 200

    data = response.json()

    assert "Rooms are available" in data["reply"]
    assert data["rooms"] is not None
    assert len(data["rooms"]) > 0

def test_unknown_question_fallback():
    response = client.post(
        "/api/chat",
        json={
            "message": "Who is the president of France?",
            "history": []
        }
    )

    assert response.status_code == 200
    assert "I can help with information about our rooms" in response.json()["reply"]

def test_empty_message():
    response = client.post(
        "/api/chat",
        json={"message": "", "history": []}
    )

    assert response.status_code == 200
    assert "Please enter a question" in response.json()["reply"]