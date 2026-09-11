"""Unit tests for the 5 specialized investigative agents."""

import pytest
from app.case_data import get_authoritative_case
from app.services.openai_client import OpenAIService
from app.agents.detective import run_detective_agent
from app.agents.evidence import run_evidence_agent
from app.agents.suspect import run_suspect_agent
from app.agents.skeptic import run_skeptic_agent
from app.agents.chief import run_chief_agent
from tests.mock_helpers import (
    mock_openai_handler,
    MOCK_DETECTIVE_OUTPUT,
    MOCK_EVIDENCE_ANALYSIS_ORIGINAL,
    MOCK_SUSPECT_OUTPUT,
    MOCK_SKEPTIC_OUTPUT,
    MOCK_CHIEF_OUTPUT_ORIGINAL
)


@pytest.fixture
def mock_service():
    svc = OpenAIService(api_key="mock-key", model="gpt-5")
    svc.set_mock_handler(mock_openai_handler)
    return svc


def test_detective_agent_execution(mock_service):
    case = get_authoritative_case()
    output = run_detective_agent(case, service=mock_service)

    assert len(output.timeline) > 0
    assert output.important_time_window != ""
    assert len(output.confirmed_facts) > 0
    assert len(output.open_questions) > 0

    # Ensure categories are strictly partitioned
    for t in output.timeline:
        assert t.category in ["FACT", "INFERENCE", "UNKNOWN"]
        assert t.time != ""
        assert t.event != ""


def test_evidence_agent_execution(mock_service):
    case = get_authoritative_case()
    output = run_evidence_agent(case, MOCK_DETECTIVE_OUTPUT, service=mock_service)

    assert len(output) == 7
    ids = [item.id for item in output]
    assert ids == ["A", "B", "C", "D", "E", "F", "G"]

    # Check Evidence B nuance: card opened case, not personal presence
    item_b = next(item for item in output if item.id == "B")
    assert item_b.classification == "FACT"
    assert "Arjun Vale's card opened" in item_b.observation
    assert "personally" not in item_b.observation.lower() or "card" in item_b.observation.lower()


def test_suspect_agent_execution(mock_service):
    case = get_authoritative_case()
    output = run_suspect_agent(
        case,
        MOCK_DETECTIVE_OUTPUT,
        MOCK_EVIDENCE_ANALYSIS_ORIGINAL,
        service=mock_service
    )

    # Must compare all 4 suspects
    assert len(output.suspect_comparison) == 4
    assert "Arjun Vale" in output.suspect_comparison
    assert "Lena Ortiz" in output.suspect_comparison
    assert "Theo Park" in output.suspect_comparison
    assert "Sofia Reed" in output.suspect_comparison

    # Strict terminology check: PERSON OF INTEREST, never GUILTY, THIEF, CRIMINAL
    assert output.leading_person_of_interest == "Arjun Vale"
    combined_text = (
        output.reasoning + " " +
        " ".join(s.motive for s in output.suspect_comparison.values())
    ).lower()
    assert "guilty" not in combined_text
    assert "thief" not in combined_text
    assert "criminal" not in combined_text


def test_skeptic_agent_execution(mock_service):
    case = get_authoritative_case()
    output = run_skeptic_agent(
        case,
        MOCK_DETECTIVE_OUTPUT,
        MOCK_EVIDENCE_ANALYSIS_ORIGINAL,
        MOCK_SUSPECT_OUTPUT,
        service=mock_service
    )

    assert len(output.unsupported_assumptions) > 0
    assert len(output.contradictions) > 0
    assert len(output.alternative_explanations) > 0
    assert len(output.missing_evidence) > 0
    assert len(output.questions_that_could_change_conclusion) > 0

    # Actively challenges Arjun theory
    assert any("card" in a.lower() for a in output.unsupported_assumptions)


def test_chief_agent_execution(mock_service):
    case = get_authoritative_case()
    output = run_chief_agent(
        case,
        MOCK_DETECTIVE_OUTPUT,
        MOCK_EVIDENCE_ANALYSIS_ORIGINAL,
        MOCK_SUSPECT_OUTPUT,
        MOCK_SKEPTIC_OUTPUT,
        service=mock_service
    )

    assert output.leading_person_of_interest == "Arjun Vale"
    assert output.confidence in ["LOW", "MEDIUM", "HIGH"]
    assert output.human_review_required is True
    assert len(output.evidence_ids) > 0
    assert len(output.evidence_citations) > 0

    # Ensure evidence citation maps claim to valid evidence IDs
    for citation in output.evidence_citations:
        assert citation.claim != ""
        assert len(citation.evidence_ids) > 0
        for eid in citation.evidence_ids:
            assert eid in ["A", "B", "C", "D", "E", "F", "G"]
