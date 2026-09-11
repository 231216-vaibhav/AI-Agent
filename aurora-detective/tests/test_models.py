"""Unit tests for Pydantic models in aurora-detective."""

import pytest
from pydantic import ValidationError
from models import (
    TimelineEvent,
    DetectiveOutput,
    EvidenceItemAnalysis,
    EvidenceOutput,
    SuspectAnalysis,
    SuspectOutput,
    SkepticOutput,
    ChiefOutput,
    EvidenceCitation,
    HumanReviewRecord
)


def test_timeline_event_model():
    ev = TimelineEvent(
        time="8:20 PM - 8:24 PM",
        description="Power failure in Grand Gallery.",
        category="FACT",
        source="Power Monitor"
    )
    assert ev.category == "FACT"

    with pytest.raises(ValidationError):
        TimelineEvent(
            time="8:20 PM",
            description="Invalid category",
            category="INVALID",  # Not FACT/INFERENCE/UNKNOWN
            source="Source"
        )


def test_evidence_item_analysis_model():
    item = EvidenceItemAnalysis(
        id="B",
        description="Arjun Vale's card opened the display case at 8:23 PM.",
        classification="FACT",
        strength="STRONG",
        supports="Display case unlock during blackout.",
        alternative_explanation="Card was taken or cloned."
    )
    assert item.id == "B"
    assert item.classification == "FACT"
    assert item.strength == "STRONG"


def test_suspect_output_model():
    data = {
        "suspect_comparison": {
            "Arjun Vale": {
                "name": "Arjun Vale",
                "motive": "Private debt",
                "means": "Access to museum",
                "opportunity": "Present during blackout",
                "access": "Card used at 8:23 PM",
                "alibi": "Uncorroborated jacket claim",
                "evidence_for": ["No gallery footage"],
                "evidence_against": ["Evidence B: card access"],
                "contradictions": ["Card swipe contradicts jacket statement"],
                "overall_assessment": "Leading PERSON OF INTEREST"
            }
        },
        "ranking": ["Arjun Vale", "Lena Ortiz", "Sofia Reed", "Theo Park"],
        "leading_person_of_interest": "Arjun Vale",
        "reasoning": "Direct card log and timing."
    }
    output = SuspectOutput.model_validate(data)
    assert output.leading_person_of_interest == "Arjun Vale"
    assert len(output.ranking) == 4


def test_chief_output_model():
    data = {
        "leading_person_of_interest": "Arjun Vale",
        "confidence": "MEDIUM",
        "reasoning": ["Card opened case at 8:23 PM."],
        "strongest_evidence": ["Evidence B: Card access log"],
        "weakest_uncertain_evidence": ["Evidence F: Muddy print"],
        "contradictions": ["Arjun statement vs lock record"],
        "alternative_explanations": ["Card theft from archive jacket"],
        "missing_evidence": ["Grand Gallery camera footage"],
        "evidence_citations": [
            {
                "claim": "Arjun Vale is the leading PERSON OF INTEREST.",
                "evidence_ids": ["B", "C", "D", "E"]
            }
        ],
        "human_review_required": True
    }
    output = ChiefOutput.model_validate(data)
    assert output.leading_person_of_interest == "Arjun Vale"
    assert output.human_review_required is True
    assert output.evidence_citations[0].evidence_ids == ["B", "C", "D", "E"]
    assert output.confidence_score == 55
    assert output.confidence_level == "MEDIUM"


def test_chief_output_numeric_score_and_levels():
    # Valid high score
    chief = ChiefOutput(
        leading_person_of_interest="Arjun Vale",
        confidence_score=78,
        confidence_level="HIGH",
        confidence_explanation="Score based on card access and velvet fiber match.",
        supporting_evidence=["Evidence B", "Evidence E"],
        contradictory_evidence=["Evidence C"],
        unresolved_uncertainties=["Card use != personal use"],
        alternative_theories=["Card lifted from jacket"],
        recommended_next_evidence=["Spectrometry lab analysis"],
        human_review_required=True
    )
    assert chief.confidence_score == 78
    assert chief.confidence_level == "HIGH"
    assert chief.confidence == "HIGH"
    assert len(chief.supporting_evidence) == 2
    assert len(chief.unresolved_uncertainties) == 1

    # Score accepts 0 (LOW)
    low_chief = ChiefOutput(
        leading_person_of_interest="Arjun Vale",
        confidence_score=0,
        confidence_level="LOW",
        confidence_explanation="Zero confidence baseline.",
        supporting_evidence=["None"],
        contradictory_evidence=["All alibis solid"],
        unresolved_uncertainties=["No usable evidence"],
        alternative_theories=["Unknown actor"],
        recommended_next_evidence=["Collect baseline forensics"],
        human_review_required=True
    )
    assert low_chief.confidence_score == 0
    assert low_chief.confidence_level == "LOW"

    # Score accepts 100 (VERY HIGH)
    high_chief = ChiefOutput(
        leading_person_of_interest="Arjun Vale",
        confidence_score=100,
        confidence_level="VERY HIGH",
        confidence_explanation="Hypothetical maximum evidentiary convergence.",
        supporting_evidence=["Evidence B", "Evidence E", "Evidence D"],
        contradictory_evidence=["None"],
        unresolved_uncertainties=["None"],
        alternative_theories=["None"],
        recommended_next_evidence=["Final review"],
        human_review_required=True
    )
    assert high_chief.confidence_score == 100
    assert high_chief.confidence_level == "VERY HIGH"

    # Score rejects < 0
    with pytest.raises(ValidationError):
        ChiefOutput(
            leading_person_of_interest="Arjun Vale",
            confidence_score=-1,
            confidence_level="LOW",
            confidence_explanation="Invalid negative score.",
            supporting_evidence=[],
            contradictory_evidence=[],
            unresolved_uncertainties=[],
            alternative_theories=[],
            recommended_next_evidence=[],
            human_review_required=True
        )

    # Score rejects > 100
    with pytest.raises(ValidationError):
        ChiefOutput(
            leading_person_of_interest="Arjun Vale",
            confidence_score=101,
            confidence_level="VERY HIGH",
            confidence_explanation="Invalid > 100 score.",
            supporting_evidence=[],
            contradictory_evidence=[],
            unresolved_uncertainties=[],
            alternative_theories=[],
            recommended_next_evidence=[],
            human_review_required=True
        )

    # Mismatched level (score=78 requires HIGH, not LOW)
    with pytest.raises(ValidationError):
        ChiefOutput(
            leading_person_of_interest="Arjun Vale",
            confidence_score=78,
            confidence_level="LOW",
            confidence_explanation="Mismatched score and level.",
            supporting_evidence=[],
            contradictory_evidence=[],
            unresolved_uncertainties=[],
            alternative_theories=[],
            recommended_next_evidence=[],
            human_review_required=True
        )
