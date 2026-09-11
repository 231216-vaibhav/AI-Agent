"""API Integration tests for FastAPI endpoints using TestClient."""

import pytest
from fastapi.testclient import TestClient
from app.main import app, in_memory_reviews
from app.services.openai_client import openai_service, OpenAIClientError
from tests.mock_helpers import mock_openai_handler


@pytest.fixture(autouse=True)
def setup_mock_openai():
    """Ensure mock handler is configured during API tests and clear in-memory reviews."""
    in_memory_reviews.clear()
    openai_service.set_mock_handler(mock_openai_handler)
    yield
    openai_service.set_mock_handler(None)


@pytest.fixture
def client():
    return TestClient(app)


def test_health_endpoint(client):
    response = client.get("/health")
    assert response.status_code == 200
    data = response.json()
    assert data["status"] == "healthy"
    assert data["service"] == "AI Mystery Detective Backend"
    assert "model" in data


def test_case_endpoint(client):
    response = client.get("/case")
    assert response.status_code == 200
    data = response.json()
    assert data["case_id"] == "001"
    assert data["title"] == "The Vanishing Aurora Diamond"
    assert len(data["suspects"]) == 4
    assert len(data["evidence"]) == 7


def test_investigate_endpoint(client):
    response = client.post("/investigate")
    assert response.status_code == 200
    data = response.json()

    assert data["case_id"] == "001"
    assert data["status"] == "complete"
    assert "detective" in data
    assert "evidence" in data
    assert "suspects" in data
    assert "skeptic" in data
    assert "chief" in data

    # Verify Chief
    assert data["chief"]["leading_person_of_interest"] == "Arjun Vale"
    assert data["chief"]["human_review_required"] is True
    assert len(data["chief"]["evidence_ids"]) > 0


def test_investigate_modified_endpoint(client):
    response = client.post("/investigate/modified")
    assert response.status_code == 200
    data = response.json()

    assert "original" in data
    assert "modified" in data
    assert "comparison" in data

    # Check evidence sensitivity: modified run does not have E
    orig_evidence_ids = [e["id"] for e in data["original"]["evidence"]]
    mod_evidence_ids = [e["id"] for e in data["modified"]["evidence"]]
    assert "E" in orig_evidence_ids
    assert "E" not in mod_evidence_ids

    # Comparison metrics
    comp = data["comparison"]
    assert "leading_person_of_interest" in comp
    assert "confidence" in comp
    assert "strongest_evidence" in comp
    assert "best_alternative" in comp
    assert "missing_evidence" in comp


def test_human_review_lifecycle(client):
    # 1. Post a review with decision ACCEPT
    payload = {
        "decision": "ACCEPT",
        "notes": "Agree with Chief recommendation. Proceed with fiber spectrometry.",
        "next_evidence": ["Spectrometry test results", "Archive door badge audit"]
    }
    post_res = client.post("/human-review", json=payload)
    assert post_res.status_code == 200
    record = post_res.json()
    assert record["decision"] == "ACCEPT"
    assert record["id"].startswith("REV-")
    assert record["notes"] == payload["notes"]

    # 2. Retrieve reviews via GET
    get_res = client.get("/human-review")
    assert get_res.status_code == 200
    reviews = get_res.json()
    assert len(reviews) == 1
    assert reviews[0]["id"] == record["id"]

    # 3. Post another review with decision REVISE
    payload2 = {
        "decision": "REVISE",
        "notes": "Requesting clarification on Lena's bootprint.",
        "next_evidence": "Courtyard soil sample comparison"
    }
    post_res2 = client.post("/human-review", json=payload2)
    assert post_res2.status_code == 200
    assert post_res2.json()["decision"] == "REVISE"

    get_res2 = client.get("/human-review")
    assert len(get_res2.json()) == 2


def test_openai_failure_returns_502(client):
    def failing_handler(instructions, input_data, response_model):
        raise OpenAIClientError("Simulated OpenAI API outage")

    openai_service.set_mock_handler(failing_handler)

    response = client.post("/investigate")
    assert response.status_code == 502
    data = response.json()
    assert "error_type" in data
    assert data["error_type"] == "OpenAIClientError"
    assert "Simulated OpenAI API outage" in data["detail"]
