"""Basic tests for the Flask app. Run with:  pytest -q"""

from app import create_app


def client():
    return create_app().test_client()


def test_home_page_loads():
    res = client().get("/")
    assert res.status_code == 200
    assert b"Medical Chatbot" in res.data


def test_health():
    res = client().get("/health")
    assert res.get_json() == {"status": "ok"}


def test_chat_known_topic():
    res = client().post("/api/chat", json={"message": "What is a fever?"})
    assert res.status_code == 200
    data = res.get_json()
    assert "temperature" in data["answer"]
    assert data["sources"] == []


def test_chat_empty_message_rejected():
    res = client().post("/api/chat", json={"message": "   "})
    assert res.status_code == 400


def test_chat_too_long_rejected():
    res = client().post("/api/chat", json={"message": "a" * 1001})
    assert res.status_code == 400

def test_chat_headache():
    res = client().post("/api/chat", json={"message": "I have a headache"})
    assert "dehydration" in res.get_json()["answer"]
