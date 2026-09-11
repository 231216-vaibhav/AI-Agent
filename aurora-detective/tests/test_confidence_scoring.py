"""Comprehensive test suite for Confidence Scoring Requirements in AI Mystery Detective Team.
Validates:
1. confidence_score accepts 0
2. confidence_score accepts 100
3. confidence_score rejects values below 0
4. confidence_score rejects values above 100
5. confidence level mapping works
6. Chief output contains confidence explanation
7. Chief output contains uncertainty
8. Evidence E removal produces a second investigation
9. Evidence E is actually absent from the modified evidence set
10. no hardcoded confidence score exists in the implementation
11. Gemini failures are handled safely
12. existing case-data tests continue passing
13. existing agent tests continue passing
14. existing orchestrator tests continue passing
"""

import re
import pytest
from pathlib import Path
from pydantic import ValidationError

from models import ChiefOutput, EvidenceCitation, InvestigationResult
from gemini_client import GeminiService, GeminiClientError
from orchestrator import Orchestrator
from agents.chief import run_chief_agent
from case_data import get_case_data
from tests.mock_gemini import (
    default_mock_gemini_handler,
    MOCK_DETECTIVE_OUTPUT,
    MOCK_EVIDENCE_ORIGINAL,
    MOCK_SUSPECT_OUTPUT,
    MOCK_SKEPTIC_OUTPUT
)
import app


@pytest.fixture
def mock_service():
    svc = GeminiService(api_key="mock-key", model="gemini-2.5-flash")
    svc.set_mock_handler(default_mock_gemini_handler)
    return svc


@pytest.fixture
def mock_orchestrator(mock_service):
    return Orchestrator(service=mock_service)


# ----------------------------------------------------
# 1 & 2. Boundary Values (0 and 100 accepted)
# ----------------------------------------------------

def test_confidence_score_accepts_0():
    chief = ChiefOutput(
        leading_person_of_interest="Arjun Vale",
        confidence_score=0,
        confidence_level="LOW",
        confidence_explanation="Zero confidence baseline under extreme ambiguity.",
        supporting_evidence=["None"],
        contradictory_evidence=["Strong alibis for all suspects"],
        unresolved_uncertainties=["No usable forensic traces"],
        alternative_theories=["Outside intrusion"],
        recommended_next_evidence=["Audit security perimeter"],
        human_review_required=True
    )
    assert chief.confidence_score == 0
    assert chief.confidence_level == "LOW"


def test_confidence_score_accepts_100():
    chief = ChiefOutput(
        leading_person_of_interest="Arjun Vale",
        confidence_score=100,
        confidence_level="VERY HIGH",
        confidence_explanation="Maximum evidence convergence.",
        supporting_evidence=["Evidence B", "Evidence E"],
        contradictory_evidence=["None"],
        unresolved_uncertainties=["None"],
        alternative_theories=["None"],
        recommended_next_evidence=["Proceed to formal inquiry"],
        human_review_required=True
    )
    assert chief.confidence_score == 100
    assert chief.confidence_level == "VERY HIGH"


# ----------------------------------------------------
# 3 & 4. Invalid Values (< 0 and > 100 rejected)
# ----------------------------------------------------

def test_confidence_score_rejects_values_below_0():
    for invalid_score in [-1, -15, -100]:
        with pytest.raises(ValidationError):
            ChiefOutput(
                leading_person_of_interest="Arjun Vale",
                confidence_score=invalid_score,
                confidence_level="LOW",
                confidence_explanation="Invalid negative score.",
                supporting_evidence=[],
                contradictory_evidence=[],
                unresolved_uncertainties=[],
                alternative_theories=[],
                recommended_next_evidence=[],
                human_review_required=True
            )


def test_confidence_score_rejects_values_above_100():
    for invalid_score in [101, 150, 200]:
        with pytest.raises(ValidationError):
            ChiefOutput(
                leading_person_of_interest="Arjun Vale",
                confidence_score=invalid_score,
                confidence_level="VERY HIGH",
                confidence_explanation="Invalid score above 100.",
                supporting_evidence=[],
                contradictory_evidence=[],
                unresolved_uncertainties=[],
                alternative_theories=[],
                recommended_next_evidence=[],
                human_review_required=True
            )


# ----------------------------------------------------
# 5. Confidence Level Mapping Works
# 0-39 = LOW, 40-69 = MEDIUM, 70-84 = HIGH, 85-100 = VERY HIGH
# ----------------------------------------------------

@pytest.mark.parametrize("score,expected_level", [
    (0, "LOW"),
    (20, "LOW"),
    (39, "LOW"),
    (40, "MEDIUM"),
    (55, "MEDIUM"),
    (69, "MEDIUM"),
    (70, "HIGH"),
    (78, "HIGH"),
    (84, "HIGH"),
    (85, "VERY HIGH"),
    (92, "VERY HIGH"),
    (100, "VERY HIGH")
])
def test_confidence_level_mapping_valid(score, expected_level):
    chief = ChiefOutput(
        leading_person_of_interest="Arjun Vale",
        confidence_score=score,
        confidence_level=expected_level,
        confidence_explanation=f"Valid calibration at score {score}.",
        supporting_evidence=["Evidence B"],
        contradictory_evidence=["Evidence C"],
        unresolved_uncertainties=["Card use != presence"],
        alternative_theories=["Card lifted from jacket"],
        recommended_next_evidence=["Spectrometry"],
        human_review_required=True
    )
    assert chief.confidence_score == score
    assert chief.confidence_level == expected_level


def test_confidence_level_mapping_rejects_mismatch():
    # Score 78 should be HIGH, not LOW
    with pytest.raises(ValidationError) as exc:
        ChiefOutput(
            leading_person_of_interest="Arjun Vale",
            confidence_score=78,
            confidence_level="LOW",
            confidence_explanation="Mismatched level.",
            supporting_evidence=[],
            contradictory_evidence=[],
            unresolved_uncertainties=[],
            alternative_theories=[],
            recommended_next_evidence=[],
            human_review_required=True
        )
    assert "confidence_level" in str(exc.value)

    # Score 25 should be LOW, not HIGH
    with pytest.raises(ValidationError):
        ChiefOutput(
            leading_person_of_interest="Arjun Vale",
            confidence_score=25,
            confidence_level="HIGH",
            confidence_explanation="Mismatched level.",
            supporting_evidence=[],
            contradictory_evidence=[],
            unresolved_uncertainties=[],
            alternative_theories=[],
            recommended_next_evidence=[],
            human_review_required=True
        )

    # Score 55 should be MEDIUM, not VERY HIGH
    with pytest.raises(ValidationError):
        ChiefOutput(
            leading_person_of_interest="Arjun Vale",
            confidence_score=55,
            confidence_level="VERY HIGH",
            confidence_explanation="Mismatched level.",
            supporting_evidence=[],
            contradictory_evidence=[],
            unresolved_uncertainties=[],
            alternative_theories=[],
            recommended_next_evidence=[],
            human_review_required=True
        )


# ----------------------------------------------------
# 6 & 7. Chief Output Contains Explanation and Uncertainty
# ----------------------------------------------------

def test_chief_output_contains_confidence_explanation(mock_service):
    case = get_case_data()
    output = run_chief_agent(
        case,
        MOCK_DETECTIVE_OUTPUT,
        MOCK_EVIDENCE_ORIGINAL,
        MOCK_SUSPECT_OUTPUT,
        MOCK_SKEPTIC_OUTPUT,
        service=mock_service
    )
    assert isinstance(output.confidence_explanation, str)
    assert len(output.confidence_explanation.strip()) > 20


def test_chief_output_contains_uncertainty(mock_service):
    case = get_case_data()
    output = run_chief_agent(
        case,
        MOCK_DETECTIVE_OUTPUT,
        MOCK_EVIDENCE_ORIGINAL,
        MOCK_SUSPECT_OUTPUT,
        MOCK_SKEPTIC_OUTPUT,
        service=mock_service
    )
    assert isinstance(output.unresolved_uncertainties, list)
    assert len(output.unresolved_uncertainties) >= 1
    joined = " ".join(output.unresolved_uncertainties).lower()
    assert any(term in joined for term in ["card", "spectrometry", "camera", "folder", "presence"])


# ----------------------------------------------------
# 8 & 9. Evidence E Removal Produces Second Run with E Absent
# ----------------------------------------------------

def test_evidence_e_removal_produces_second_investigation(mock_orchestrator):
    orig, mod, comp = mock_orchestrator.run_sensitivity_experiment()

    assert isinstance(orig, InvestigationResult)
    assert isinstance(mod, InvestigationResult)
    assert orig is not mod
    assert orig.chief is not mod.chief


def test_evidence_e_is_absent_from_modified_evidence_set(mock_orchestrator):
    orig, mod, comp = mock_orchestrator.run_sensitivity_experiment()

    orig_ids = [e.id for e in orig.evidence]
    mod_ids = [e.id for e in mod.evidence]

    assert "E" in orig_ids
    assert "E" not in mod_ids
    assert len(mod_ids) == len(orig_ids) - 1


# ----------------------------------------------------
# 10. No Hardcoded Confidence Score in Implementation
# ----------------------------------------------------

def test_no_hardcoded_confidence_score_in_implementation():
    """Scans production source code to guarantee that confidence scores are not
    hardcoded as fixed constants or direct assignments in agents, orchestrator, or app.
    """
    root_dir = Path(__file__).resolve().parent.parent
    files_to_check = [
        root_dir / "agents" / "chief.py",
        root_dir / "orchestrator.py",
        root_dir / "gemini_client.py",
        root_dir / "app.py"
    ]

    hardcoded_pattern = re.compile(r"^\s*confidence_score\s*=\s*\d+", re.MULTILINE)

    for file_path in files_to_check:
        assert file_path.exists(), f"Expected file {file_path} to exist"
        content = file_path.read_text(encoding="utf-8")
        matches = hardcoded_pattern.findall(content)
        assert len(matches) == 0, (
            f"Found forbidden hardcoded confidence score in {file_path.name}: {matches}"
        )


# ----------------------------------------------------
# 11. Gemini Failures Handled Safely
# ----------------------------------------------------

def test_gemini_failures_handled_safely():
    """Verifies that GeminiService catches network or generation errors,
    retries once, and raises GeminiClientError without crashing.
    """
    svc = GeminiService(api_key="mock-key", model="gemini-2.5-flash")

    def failing_handler(system_instruction, prompt, response_model):
        raise RuntimeError("Simulated connection timeout to Gemini API")

    svc.set_mock_handler(failing_handler)

    with pytest.raises(GeminiClientError) as exc_info:
        svc.generate_structured("sys", "prompt", ChiefOutput)

    assert "failed after 2 attempts" in str(exc_info.value) or "Simulated connection timeout" in str(exc_info.value)


def test_app_graceful_error_handling_on_failure():
    """Verifies that app's on_run_investigation catches failures and returns
    user-friendly error messaging instead of crashing the UI.
    """
    svc = GeminiService(api_key="mock-key", model="gemini-2.5-flash")

    def failing_handler(system_instruction, prompt, response_model):
        raise RuntimeError("API quota exhausted")

    svc.set_mock_handler(failing_handler)
    test_orch = Orchestrator(service=svc)

    orig_orch = app.orchestrator
    app.orchestrator = test_orch
    try:
        outputs = app.on_run_investigation()
        error_msg = outputs[7]  # error_box output
        assert "Investigation Error" in error_msg
        assert "API quota exhausted" in error_msg
    finally:
        app.orchestrator = orig_orch


# ----------------------------------------------------
# 12. Terminology and Legal Disclaimer Verification
# ----------------------------------------------------

def test_person_of_interest_terminology_enforced(mock_service):
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
    full_text = (
        output.confidence_explanation + " " +
        " ".join(output.supporting_evidence) + " " +
        " ".join(output.alternative_theories)
    ).lower()
    assert "guilty" not in full_text
    assert "culprit" not in full_text
    assert "proven thief" not in full_text


def test_ui_contains_disclaimer_and_visual_indicator():
    sample_chief = ChiefOutput(
        leading_person_of_interest="Arjun Vale",
        confidence_score=78,
        confidence_level="HIGH",
        confidence_explanation="Strong card access and folder fiber traces support Arjun.",
        supporting_evidence=["Evidence B", "Evidence E"],
        contradictory_evidence=["Evidence C"],
        unresolved_uncertainties=["Card swipe does not establish physical presence"],
        alternative_theories=["Card stolen from jacket"],
        recommended_next_evidence=["Spectrometry lab test"],
        human_review_required=True
    )
    html = app.format_chief_results(sample_chief)

    # Required disclaimer
    assert "Confidence reflects the strength of the available evidence" in html
    assert "not a probability of guilt and does not establish legal culpability" in html

    # Visual gauge and score prominence
    assert "78" in html
    assert "/ 100" in html
    assert "HIGH" in html
    assert "Visual Confidence Gauge" in html
    assert "meter-track" in html
    assert "meter-fill" in html
    assert "0–39 LOW" in html
    assert "40–69 MEDIUM" in html
    assert "70–84 HIGH" in html
    assert "85–100 VERY HIGH" in html
    assert "HUMAN REVIEW: REQUIRED" in html
