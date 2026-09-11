"""Unit tests for the Orchestrator and sensitivity experiment in aurora-detective."""

import pytest
from orchestrator import Orchestrator
from gemini_client import GeminiService
from tests.mock_gemini import default_mock_gemini_handler


@pytest.fixture
def mock_orchestrator():
    svc = GeminiService(api_key="mock-key", model="gemini-2.5-flash")
    svc.set_mock_handler(default_mock_gemini_handler)
    return Orchestrator(service=svc)


def test_full_pipeline_run(mock_orchestrator):
    result = mock_orchestrator.run_investigation()

    assert result.case_name == "The Vanishing Aurora Diamond"
    assert result.detective is not None
    assert result.evidence is not None
    assert result.suspects is not None
    assert result.skeptic is not None
    assert result.chief is not None

    # Check Chief
    assert result.chief.leading_person_of_interest == "Arjun Vale"
    assert result.chief.human_review_required is True
    assert "B" in [eid for c in result.chief.evidence_citations for eid in c.evidence_ids]


def test_sensitivity_experiment(mock_orchestrator):
    orig, mod, comp = mock_orchestrator.run_sensitivity_experiment()

    # Original has 7 items including E
    orig_e_ids = [e.id for e in orig.evidence]
    assert "E" in orig_e_ids

    # Modified has 6 items excluding E
    mod_e_ids = [e.id for e in mod.evidence]
    assert "E" not in mod_e_ids
    assert len(mod_e_ids) == 6

    # Verify comparison
    assert comp.original_score == 78
    assert comp.modified_score == 52
    assert comp.score_change == -26
    assert "HIGH" in comp.original_confidence
    assert "MEDIUM" in comp.modified_confidence
    assert comp.poi_comparison != ""
    assert comp.confidence_comparison != ""
    assert comp.strongest_evidence_comparison != ""
    assert comp.reasoning_changes != ""


def test_human_review_recording(mock_orchestrator):
    rec = mock_orchestrator.record_human_review(
        decision="ACCEPT",
        notes="Approve recommendation for fiber spectrometry analysis.",
        next_evidence="Spectrometry laboratory analysis report"
    )

    assert rec.id.startswith("REV-")
    assert rec.decision == "ACCEPT"
    assert len(mock_orchestrator.get_human_reviews()) == 1
