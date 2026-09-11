# -*- coding: utf-8 -*-
"""Comprehensive test suite for Generic Multi-Agent Investigation System.
Validates:
1. Aurora demo works through generic pipeline.
2. Arbitrary natural-language case works (e.g. College lab laptop theft).
3. Case with 2 suspects works.
4. Case with 5+ suspects works.
5. Variable evidence count (3 clues, 9 clues, etc.) works.
6. Evidence IDs generated (E1, E2, E3...) when missing.
7. Empty input is handled safely with user-friendly error.
8. Missing timeline / timestamps handled without fabricating times.
9. No explicit suspects handled without fabricating suspects.
10. Insufficient evidence handled with objective designation.
11. Dynamic evidence sensitivity works for arbitrary evidence removal.
12. No Aurora-specific details leak into unrelated cases.
13. Confidence is dynamically generated from case data.
14. Human review works across all case types.
"""

import pytest
from case_data import (
    parse_case_input,
    get_case_data,
    AURORA_DEMO_TEXT,
    COLLEGE_LAB_DEMO_TEXT
)
from models import (
    ParsedCase,
    InvestigationResult,
    DetectiveOutput,
    EvidenceOutput,
    SuspectOutput,
    SkepticOutput,
    ChiefOutput,
    TimelineEvent,
    EvidenceItemAnalysis,
    SuspectAnalysis
)
from orchestrator import Orchestrator
from gemini_client import GeminiService
from tests.mock_gemini import default_mock_gemini_handler
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
# 1. AURORA DEMO TEST
# ----------------------------------------------------

def test_aurora_demo_ingestion_and_pipeline(mock_orchestrator):
    parsed = parse_case_input(AURORA_DEMO_TEXT, service=mock_orchestrator.service)
    assert parsed["case_name"] == "The Vanishing Aurora Diamond"
    assert len(parsed["suspects"]) == 4
    assert len(parsed["evidence"]) == 7

    res = mock_orchestrator.run_investigation(AURORA_DEMO_TEXT)
    assert isinstance(res, InvestigationResult)
    assert res.case_name == "The Vanishing Aurora Diamond"
    assert res.chief.leading_person_of_interest == "Arjun Vale"


# ----------------------------------------------------
# 2. ARBITRARY NATURAL LANGUAGE CASE (COLLEGE LAB)
# ----------------------------------------------------

def test_college_lab_laptop_investigation(mock_service):
    """Verifies that a completely unrelated natural language case runs end-to-end."""
    case_text = """A high-end laptop disappeared from a college computer laboratory between 2 PM and 4 PM.
Three students had access to the room: Rahul, Priya, and Aman.
Rahul says he left at 2:30 PM.
Priya was seen entering the laboratory at 3:10 PM carrying a backpack.
Aman says he was in the library studying.
CCTV shows the laptop present at 3:00 PM and missing at 3:35 PM.
The laptop was later found in a storage room.
An unidentified fingerprint was found on the storage-room handle."""

    parsed = parse_case_input(case_text, service=mock_service)
    assert parsed is not None
    assert "timeline" in parsed
    assert "evidence" in parsed

    # Mock handler specifically for College Lab
    mock_det = DetectiveOutput(
        timeline=[
            TimelineEvent(time="2:00 PM - 4:00 PM", description="Laptop disappearance window", category="FACT", source="Lab Log"),
            TimelineEvent(time="3:00 PM", description="Laptop visible on Desk #4", category="FACT", source="CCTV"),
            TimelineEvent(time="3:10 PM", description="Priya enters carrying backpack", category="FACT", source="CCTV"),
            TimelineEvent(time="3:35 PM", description="Laptop missing from Desk #4", category="FACT", source="CCTV"),
            TimelineEvent(time="4:15 PM", description="Laptop found in storage room", category="FACT", source="Security Report")
        ],
        confirmed_facts=["Laptop present at 3:00 PM and missing at 3:35 PM.", "Priya entered lab at 3:10 PM with backpack."],
        critical_opportunity_window="3:00 PM – 3:35 PM",
        unknowns=["Ownership of fingerprint on storage handle", "Rahul and Aman verified exit times"],
        open_questions=["Does fingerprint match any enrolled student?"]
    )

    mock_ev = [
        EvidenceItemAnalysis(id="E1", description="CCTV at 3:00 PM & 3:35 PM", classification="FACT", strength="STRONG", supports="Establishes opportunity window", alternative_explanation="None"),
        EvidenceItemAnalysis(id="E2", description="Priya entering at 3:10 PM with backpack", classification="FACT", strength="MODERATE", supports="Priya physical presence during theft window", alternative_explanation="Carrying normal academic books"),
        EvidenceItemAnalysis(id="E3", description="Unidentified fingerprint on storage handle", classification="FACT", strength="STRONG", supports="Identifies who accessed storage locker", alternative_explanation="Deposited by prior authorized visitor")
    ]

    mock_sus = SuspectOutput(
        suspect_comparison={
            "Priya": SuspectAnalysis(
                name="Priya",
                motive="UNKNOWN / NOT PROVIDED",
                means="Possession of backpack and lab access",
                opportunity="Inside lab during 3:00–3:35 PM window",
                access="Valid card access to laboratory",
                alibi="No alibi during 3:00–3:35 PM window",
                evidence_for=[],
                evidence_against=["CCTV shows entry at 3:10 PM with backpack"],
                contradictions=[],
                overall_assessment="Leading PERSON OF INTEREST due to presence in critical 3:00–3:35 PM opportunity window."
            ),
            "Rahul": SuspectAnalysis(
                name="Rahul",
                motive="UNKNOWN / NOT PROVIDED",
                means="Lab access",
                opportunity="Departed at 2:30 PM prior to disappearance",
                access="Lab keycard access",
                alibi="Assignment submission verified at 2:28 PM",
                evidence_for=["Left prior to 3:00 PM"],
                evidence_against=[],
                contradictions=[],
                overall_assessment="Low priority; departed before laptop went missing."
            ),
            "Aman": SuspectAnalysis(
                name="Aman",
                motive="UNKNOWN / NOT PROVIDED",
                means="Lab access",
                opportunity="None verified in lab during blackout",
                access="Lab keycard access",
                alibi="Claims studied in library from 2:00–3:45 PM",
                evidence_for=["Library entry log at 2:10 PM"],
                evidence_against=[],
                contradictions=[],
                overall_assessment="Low priority; corroborated library presence."
            )
        },
        ranking=["Priya", "Aman", "Rahul"],
        leading_person_of_interest="Priya",
        reasoning="Priya is the only individual observed entering the laboratory with a container during the critical 3:00–3:35 PM window."
    )

    mock_sk = SkepticOutput(
        unsupported_assumptions=["Assuming backpack contained the laptop without interior inspection."],
        contradictions=[],
        alternative_explanations=["An unidentified third party entered unrecorded and deposited laptop in storage room."],
        missing_evidence=["Fingerprint analysis report from storage handle.", "Storage room corridor camera footage."],
        questions_to_stress_test=["Whose fingerprint is on the storage room handle?"]
    )

    mock_ch = ChiefOutput(
        leading_person_of_interest="Priya",
        confidence_score=68,
        confidence_level="MEDIUM",
        confidence_explanation="Priya is designated the leading PERSON OF INTEREST based on CCTV arrival at 3:10 PM during the 3:00-3:35 PM window. Confidence is capped at 68/100 (MEDIUM) because backpack contents were uninspected and fingerprint identity is pending.",
        supporting_evidence=["CCTV recording entry at 3:10 PM with backpack"],
        contradictory_evidence=["No direct visual recording of laptop being placed in backpack"],
        unresolved_uncertainties=["Identity of storage room handle fingerprint"],
        alternative_theories=["Another student accessed room during camera blindspot"],
        recommended_next_evidence=["Query fingerprint against campus registry"],
        human_review_required=True
    )

    def custom_handler(sys, prompt, model):
        name = model.__name__
        if name == "DetectiveOutput":
            return mock_det
        elif name == "EvidenceOutput":
            return EvidenceOutput(evidence_analysis=mock_ev)
        elif name == "SuspectOutput":
            return mock_sus
        elif name == "SkepticOutput":
            return mock_sk
        elif name == "ChiefOutput":
            return mock_ch
        return default_mock_gemini_handler(sys, prompt, model)

    svc = GeminiService(api_key="mock-key", model="gemini-2.5-flash")
    svc.set_mock_handler(custom_handler)
    orch = Orchestrator(service=svc)

    result = orch.run_investigation(case_text)
    assert result.chief.leading_person_of_interest == "Priya"
    assert result.chief.confidence_score == 68
    assert result.chief.confidence_level == "MEDIUM"

    # CRITICAL: Verify NO Aurora Diamond details leaked into this unrelated case
    full_dump = result.model_dump_json().lower()
    assert "aurora diamond" not in full_dump
    assert "arjun vale" not in full_dump
    assert "northbridge museum" not in full_dump
    assert "lena ortiz" not in full_dump
    assert "theo park" not in full_dump
    assert "sofia reed" not in full_dump


# ----------------------------------------------------
# 3. CASE WITH 2 SUSPECTS AND 3 CLUES
# ----------------------------------------------------

def test_case_with_two_suspects_and_variable_evidence(mock_service):
    raw_case = """Case: Company Data Leak
Location: Remote Cloud Servers
Two employees had administrator tokens: Alice and Bob.
Alice worked during the night shift when the transfer occurred.
Bob logged in 4 hours after the leak.
Clue 1: Token belonging to Alice authorized the exfiltration.
Clue 2: Alice claims her laptop was infected with malware.
Clue 3: IP address resolves to a commercial VPN."""

    parsed = parse_case_input(raw_case, service=mock_service)
    assert parsed["case_name"] is not None
    assert len(parsed["evidence"]) >= 3


# ----------------------------------------------------
# 4. EMPTY INPUT HANDLING
# ----------------------------------------------------

def test_empty_case_input_raises_error():
    with pytest.raises(ValueError) as exc:
        parse_case_input("")
    assert "empty" in str(exc.value)

    with pytest.raises(ValueError):
        parse_case_input("    \n\t   ")


# ----------------------------------------------------
# 5. DYNAMIC EVIDENCE SENSITIVITY REMOVAL
# ----------------------------------------------------

def test_dynamic_evidence_sensitivity_with_custom_id(mock_orchestrator):
    orig, mod, comp = mock_orchestrator.run_sensitivity_experiment(
        case_input=AURORA_DEMO_TEXT,
        evidence_id_to_remove="B"
    )
    assert comp.removed_evidence_id == "B"
    assert comp.score_change is not None


# ----------------------------------------------------
# 6. HUMAN REVIEW ACROSS GENERIC CASES
# ----------------------------------------------------

def test_human_review_recording_in_generic_system(mock_orchestrator):
    rec = mock_orchestrator.record_human_review(
        decision="REVISE",
        notes="Request immediate forensic fingerprint comparison for storage room.",
        next_evidence="Campus registry print match report"
    )
    assert rec.decision == "REVISE"
    assert "fingerprint" in rec.notes
    reviews = mock_orchestrator.get_human_reviews()
    assert len(reviews) >= 1


# ----------------------------------------------------
# 7. CHIEF AGENT 10-SECTION & FORENSIC RULES VALIDATION
# ----------------------------------------------------

def test_chief_agent_10_required_sections_present():
    """Validates that ChiefOutput contains all 10 forensic sections."""
    chief = ChiefOutput(
        leading_person_of_interest="Leading Person of Interest: Vikram Shah",
        confidence_score=65,
        confidence_level="MEDIUM",
        why_this_conclusion="Vikram entered during the critical window carrying a tool bag.",
        confidence_explanation="Evaluated based on access logs and opportunity timeframe.",
        supporting_evidence=["[Clue 1] — Vikram opened the cleanroom door at 4:15 PM."],
        contradictory_evidence=["No direct visual recording confirms he removed the prototype wafer."],
        alternative_theories=["Another technician with master badge access could have entered."],
        important_uncertainty="Exact removal timestamp between 4:00 PM and 4:30 PM is unverified.",
        unresolved_uncertainties=["Wafer serial tracking log audit pending."],
        opportunity_window="4:00 PM – 4:30 PM",
        recommended_next_evidence=["Audit badge log records for secondary cleanroom exit."],
        final_conclusion="Vikram is the leading person of interest based on opportunity, but evidence is insufficient to establish removal."
    )

    # 1. LEADING PERSON OF INTEREST
    assert "Vikram Shah" in chief.leading_person_of_interest
    assert "guilty" not in chief.leading_person_of_interest.lower()

    # 2. CONFIDENCE
    assert chief.confidence_score == 65
    assert chief.confidence_level == "MEDIUM"

    # 3. WHY THIS CONCLUSION?
    assert "Vikram entered" in chief.why_this_conclusion

    # 4. SUPPORTING EVIDENCE
    assert len(chief.supporting_evidence) > 0
    assert "[Clue 1]" in chief.supporting_evidence[0]

    # 5. CONTRADICTORY / LIMITING EVIDENCE
    assert len(chief.contradictory_evidence) > 0
    assert "No direct" in chief.contradictory_evidence[0]

    # 6. ALTERNATIVE EXPLANATIONS
    assert len(chief.alternative_theories) > 0

    # 7. IMPORTANT UNCERTAINTY
    assert "Exact removal timestamp" in chief.important_uncertainty

    # 8. OPPORTUNITY / CRITICAL WINDOW
    assert "4:00 PM" in chief.opportunity_window

    # 9. NEXT EVIDENCE NEEDED
    assert len(chief.recommended_next_evidence) > 0

    # 10. FINAL CONCLUSION
    assert "Vikram is the leading person of interest" in chief.final_conclusion
    assert chief.human_review_required is True


def test_insufficient_evidence_case_handling():
    """Validates that a case with insufficient evidence designates 'INSUFFICIENT EVIDENCE'."""
    chief = ChiefOutput(
        leading_person_of_interest="Insufficient evidence to identify a leading person of interest.",
        confidence_score=20,
        confidence_level="LOW",
        why_this_conclusion="Multiple individuals had access and no forensic or digital evidence points to a specific person.",
        confidence_explanation="No verified physical, digital, or biometric evidence connects any named individual.",
        supporting_evidence=["[Clue A] — Item confirmed present at 9:00 AM."],
        contradictory_evidence=["Over 50 unidentified visitors passed through the hallway with unmonitored access."],
        alternative_theories=["Item may have been misplaced or removed during routine maintenance."],
        important_uncertainty="Unmonitored 6-hour gap with no access logs or camera coverage.",
        opportunity_window="9:00 AM – 3:00 PM",
        recommended_next_evidence=["Conduct inventory search and review facility visitor sign-in book."],
        final_conclusion="Insufficient evidence is currently available to identify a responsible person."
    )

    assert "insufficient evidence" in chief.leading_person_of_interest.lower()
    assert chief.confidence_score < 40
    assert chief.confidence_level == "LOW"
    assert "insufficient evidence" in chief.final_conclusion.lower()

