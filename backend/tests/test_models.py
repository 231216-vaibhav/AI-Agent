"""Unit tests for Pydantic schema validation."""

import pytest
from pydantic import ValidationError
from app.models import (
    TimelineItem,
    DetectiveOutput,
    EvidenceItemAnalysis,
    EvidenceOutput,
    SuspectAnalysis,
    SuspectOutput,
    SkepticOutput,
    ChiefOutput,
    EvidenceCitation,
    InvestigateResponse,
    InvestigateModifiedResponse,
    InvestigationComparison,
    ComparisonMetric,
    HumanReviewInput,
    HumanReviewRecord
)


def test_timeline_item_validation():
    item = TimelineItem(
        time="8:23 PM",
        event="Card access to display case recorded",
        category="FACT",
        source="Electronic Lock Log"
    )
    assert item.category == "FACT"

    with pytest.raises(ValidationError):
        TimelineItem(
            time="8:23 PM",
            event="Invalid category test",
            category="GUESS",  # Invalid
            source="Electronic Lock Log"
        )


def test_detective_output_validation():
    data = {
        "timeline": [
            {
                "time": "8:20 PM - 8:24 PM",
                "event": "Power failure",
                "category": "FACT",
                "source": "Museum System"
            }
        ],
        "confirmed_facts": ["Electronic lock is battery-backed."],
        "important_time_window": "8:20 PM - 8:24 PM",
        "open_questions": ["Where was the card between 8:12 and 8:23 PM?"]
    }
    output = DetectiveOutput.model_validate(data)
    assert len(output.timeline) == 1
    assert output.important_time_window == "8:20 PM - 8:24 PM"


def test_evidence_item_analysis_validation():
    item = EvidenceItemAnalysis(
        id="B",
        observation="Arjun Vale's card opened display case at 8:23 PM.",
        classification="FACT",
        strength="STRONG",
        alternative_explanation="Card could have been taken from his jacket.",
        contradiction="Arjun claims card was inside his jacket in the archive."
    )
    assert item.id == "B"
    assert item.classification == "FACT"
    assert item.strength == "STRONG"


def test_suspect_output_validation():
    suspect_dict = {
        "suspect_comparison": {
            "Arjun Vale": {
                "name": "Arjun Vale",
                "motive": "Large private debt",
                "means": "Access to museum areas",
                "opportunity": "Present during blackout",
                "access": "Card opened display case at 8:23 PM",
                "alibi_support": "Uncorroborated claim of card staying in jacket",
                "evidence_against": ["Card used at 8:23 PM", "Folder carried at 8:25 PM"],
                "evidence_in_favor": ["No camera shows him in Grand Gallery directly"]
            }
        },
        "ranking": ["Arjun Vale", "Lena Ortiz", "Sofia Reed", "Theo Park"],
        "leading_person_of_interest": "Arjun Vale",
        "reasoning": "Direct card access to case at 8:23 PM and folder with matching fibers."
    }
    output = SuspectOutput.model_validate(suspect_dict)
    assert output.leading_person_of_interest == "Arjun Vale"
    assert len(output.ranking) == 4


def test_skeptic_output_validation():
    skeptic_data = {
        "unsupported_assumptions": ["Assuming Arjun was the one holding the card."],
        "contradictions": ["Arjun says card was in archive jacket vs case opened at 8:23 PM."],
        "alternative_explanations": ["Someone took the card from his jacket while he was distracted."],
        "missing_evidence": ["No visual record of folder contents."],
        "questions_that_could_change_conclusion": ["Are there fingerprints on the display case lock?"]
    }
    output = SkepticOutput.model_validate(skeptic_data)
    assert len(output.unsupported_assumptions) == 1
    assert len(output.missing_evidence) == 1


def test_chief_output_validation():
    chief_data = {
        "leading_person_of_interest": "Arjun Vale",
        "confidence": "MEDIUM",
        "reasoning": ["Card opened display case at 8:23 PM; folder carried at 8:25 PM."],
        "strongest_evidence": ["Evidence B: Card opened display case"],
        "weakest_evidence": ["Evidence F: Muddy shoeprint near case"],
        "contradictions": ["Arjun claims card stayed in jacket"],
        "alternative_explanation": ["Third-party framing or theft of card"],
        "uncertainty": ["Card usage does not prove Arjun personally opened case"],
        "missing_evidence": ["No camera footage inside folder"],
        "recommended_next_evidence": ["Fingerprint dusting on glass and lock"],
        "evidence_ids": ["B", "C", "D", "E"],
        "human_review_required": True,
        "evidence_citations": [
            {
                "claim": "Arjun is the leading person of interest.",
                "evidence_ids": ["B", "C", "D", "E"]
            }
        ]
    }
    output = ChiefOutput.model_validate(chief_data)
    assert output.leading_person_of_interest == "Arjun Vale"
    assert output.human_review_required is True
    assert output.evidence_citations[0].evidence_ids == ["B", "C", "D", "E"]


def test_human_review_models():
    review_in = HumanReviewInput(
        decision="REVISE",
        notes="Check archive hallway cameras between 8:12 and 8:25 PM.",
        next_evidence="Fingerprint analysis on display case lock"
    )
    assert review_in.decision == "REVISE"

    record = HumanReviewRecord(
        id="REV-12345678",
        decision=review_in.decision,
        notes=review_in.notes,
        next_evidence=review_in.next_evidence,
        timestamp="2026-09-11T12:00:00Z"
    )
    assert record.id.startswith("REV-")
