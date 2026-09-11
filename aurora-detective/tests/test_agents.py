"""Unit tests for the five specialized Gemini investigation agents."""

import pytest
from case_data import get_case_data
from gemini_client import GeminiService
from agents.detective import run_detective_agent
from agents.evidence import run_evidence_agent
from agents.suspect import run_suspect_agent
from agents.skeptic import run_skeptic_agent
from agents.chief import run_chief_agent
from tests.mock_gemini import (
    default_mock_gemini_handler,
    MOCK_DETECTIVE_OUTPUT,
    MOCK_EVIDENCE_ORIGINAL,
    MOCK_SUSPECT_OUTPUT,
    MOCK_SKEPTIC_OUTPUT
)


@pytest.fixture
def mock_service():
    svc = GeminiService(api_key="mock-key", model="gemini-2.5-flash")
    svc.set_mock_handler(default_mock_gemini_handler)
    return svc


def test_detective_agent(mock_service):
    case = get_case_data()
    output = run_detective_agent(case, service=mock_service)

    assert len(output.timeline) > 0
    assert output.critical_opportunity_window == "8:20 PM – 8:24 PM (Power Failure)"
    assert len(output.confirmed_facts) > 0
    assert len(output.unknowns) > 0
    assert len(output.open_questions) > 0


def test_evidence_agent(mock_service):
    case = get_case_data()
    output = run_evidence_agent(case, MOCK_DETECTIVE_OUTPUT, service=mock_service)

    assert len(output) == 7
    ids = [e.id for e in output]
    assert ids == ["A", "B", "C", "D", "E", "F", "G"]

    # Check Evidence B nuance: card opened case, not personal presence
    item_b = next(e for e in output if e.id == "B")
    assert item_b.classification == "FACT"
    assert "Arjun Vale's card opened" in item_b.description


def test_suspect_agent(mock_service):
    case = get_case_data()
    output = run_suspect_agent(
        case,
        MOCK_DETECTIVE_OUTPUT,
        MOCK_EVIDENCE_ORIGINAL,
        service=mock_service
    )

    assert len(output.suspect_comparison) == 4
    assert "Arjun Vale" in output.suspect_comparison
    assert "Lena Ortiz" in output.suspect_comparison
    assert "Theo Park" in output.suspect_comparison
    assert "Sofia Reed" in output.suspect_comparison

    # Strict terminology check: PERSON OF INTEREST, never GUILTY
    assert output.leading_person_of_interest == "Arjun Vale"
    text = (
        output.reasoning + " " +
        " ".join(s.overall_assessment for s in output.suspect_comparison.values())
    ).lower()
    assert "guilty" not in text


def test_skeptic_agent(mock_service):
    case = get_case_data()
    output = run_skeptic_agent(
        case,
        MOCK_DETECTIVE_OUTPUT,
        MOCK_EVIDENCE_ORIGINAL,
        MOCK_SUSPECT_OUTPUT,
        service=mock_service
    )

    assert len(output.unsupported_assumptions) > 0
    assert len(output.contradictions) > 0
    assert len(output.alternative_explanations) > 0
    assert len(output.missing_evidence) > 0


def test_chief_agent(mock_service):
    case = get_case_data()
    output = run_chief_agent(
        case,
        MOCK_DETECTIVE_OUTPUT,
        MOCK_EVIDENCE_ORIGINAL,
        MOCK_SUSPECT_OUTPUT,
        MOCK_SKEPTIC_OUTPUT,
        service=mock_service
    )

    assert output.leading_person_of_interest == "Arjun Vale"
    assert output.confidence in ["LOW", "MEDIUM", "HIGH", "VERY HIGH"]
    assert 0 <= output.confidence_score <= 100
    assert output.confidence_level in ["LOW", "MEDIUM", "HIGH", "VERY HIGH"]
    assert len(output.confidence_explanation) > 0
    assert len(output.supporting_evidence) > 0
    assert len(output.unresolved_uncertainties) > 0
    assert output.human_review_required is True
    assert len(output.evidence_citations) > 0

    for citation in output.evidence_citations:
        assert citation.claim != ""
        assert len(citation.evidence_ids) > 0
