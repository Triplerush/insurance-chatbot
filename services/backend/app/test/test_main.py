"""Tests for the backend /chat endpoint using the default MockAnswerFormatter."""

from pathlib import Path
import sys

THIS_FILE = Path(__file__).resolve()
for parent in THIS_FILE.parents:
    if (parent / "services").is_dir():
        if str(parent) not in sys.path:
            sys.path.append(str(parent))
        break

import pytest
from fastapi.testclient import TestClient

from services.backend.app.main import app


client = TestClient(app)


def test_health():
    resp = client.get("/health")
    assert resp.status_code == 200
    assert resp.json() == {"status": "ok"}


def test_root():
    resp = client.get("/")
    assert resp.status_code == 200
    body = resp.json()
    assert "docs_url" in body
    assert "/docs" in body["docs_url"]


def test_chat_get_landing():
    resp = client.get("/chat")
    assert resp.status_code == 200
    body = resp.json()
    assert "example_request" in body


def test_chat_mock_formatter():
    resp = client.post("/chat", json={
        "messages": [{"role": "user", "content": "¿Qué cubre la póliza?"}],
    })
    assert resp.status_code == 200
    body = resp.json()
    assert "answer" in body
    assert "(mock)" in body["answer"]
    assert body["usage"]["formatter"] == "mock"


def test_chat_empty_messages():
    resp = client.post("/chat", json={"messages": []})
    assert resp.status_code == 400
    assert "At least one message" in resp.json()["detail"]


def test_chat_last_message_not_user():
    resp = client.post("/chat", json={
        "messages": [
            {"role": "user", "content": "Hola"},
            {"role": "assistant", "content": "Hola, ¿en qué puedo ayudar?"},
        ],
    })
    assert resp.status_code == 400
    assert "user" in resp.json()["detail"].lower()


def test_chat_debug_mode():
    resp = client.post("/chat", json={
        "messages": [{"role": "user", "content": "¿Qué cubre?"}],
        "debug": True,
    })
    assert resp.status_code == 200
    body = resp.json()
    assert body["debug"] is not None
    assert "formatter" in body["debug"]
