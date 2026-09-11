"""Unit and integration tests for the Investigation Orchestrator."""

import pytest
from app.orchestrator import InvestigationOrchestrator
from app.services.openai_client import OpenAIService
from tests.mock_helpers import mock_openai_handler


@pytest.fixture
def mock_orchestrator():
    svc = OpenAIService(api_key="mock-key", model="gpt-5")
    svc.set_mock_handler(mock_openai_handler)
    return InvestigationOrchestrator(service=svc)


def test_orchestrator_run_investigation(mock_orchestrator):
    response = mock_orchestrator.run_investigation()

    assert response.case_id == "001"
    assert response.status == "complete"

    # Verify all 5 agent sections exist
    assert response.detective is not None
    assert response.evidence is not None
    assert response.suspects is not None
    assert response.skeptic is not None
    assert response.chief is not None

    # Verify evidence items
    assert len(response.evidence) == 7

    # Verify Chief synthesis
    assert response.chief.leading_person_of_interest == "Arjun Vale"
    assert response.chief.human_review_required is True
    assert "B" in response.chief.evidence_ids


def test_orchestrator_run_modified_investigation(mock_orchestrator):
    mod_result = mock_orchestrator.run_modified_investigation()

    assert mod_result.original is not None
    assert mod_result.modified is not None
    assert mod_result.comparison is not None

    # Check evidence counts: Original has E, Modified does not
    orig_ids = [e.id for e in mod_result.original.evidence]
    mod_ids = [e.id for e in mod_result.modified.evidence]
    assert "E" in orig_ids
    assert "E" not in mod_ids

    # Check comparison metrics
    comp = mod_result.comparison
    assert comp.leading_person_of_interest.original == "Arjun Vale"
    assert comp.confidence.original == "MEDIUM"
    assert comp.confidence.modified == "LOW"
    assert comp.confidence.impact_analysis != ""
    assert comp.strongest_evidence.impact_analysis != ""
    assert comp.best_alternative.impact_analysis != ""
    assert comp.missing_evidence.impact_analysis != ""
