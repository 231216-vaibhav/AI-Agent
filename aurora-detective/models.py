# -*- coding: utf-8 -*-
"""Pydantic schemas for Generic AI Multi-Agent Investigation System,
including Case Parsing, 5 Gemini Flash AI Agents, Pipeline Orchestration,
Dynamic Sensitivity Comparison, and Human Review.
"""

from typing import List, Dict, Literal, Optional, Any, Union
from pydantic import BaseModel, Field, field_validator, model_validator


# ----------------------------------------------------
# 0. GENERIC PARSED CASE MODELS
# ----------------------------------------------------

class ParsedTimelineItem(BaseModel):
    time: str = Field(default="UNKNOWN / NOT PROVIDED", description="Timestamp or interval")
    description: str = Field(..., description="Description of the event based strictly on facts")
    note: str = Field(default="", description="Significance, context, or observation source")


class ParsedSuspectItem(BaseModel):
    name: str = Field(..., description="Name or identifier of person/entity")
    background: str = Field(default="", description="Role, background, or context")
    motive: str = Field(default="UNKNOWN / NOT PROVIDED", description="Stated or apparent motive, or unknown")
    means: str = Field(default="UNKNOWN / NOT PROVIDED", description="Capability or means")
    opportunity: str = Field(default="UNKNOWN / NOT PROVIDED", description="Presence during critical timeframe")
    access: str = Field(default="UNKNOWN / NOT PROVIDED", description="Access credentials or physical access")
    alibi: str = Field(default="UNKNOWN / NOT PROVIDED", description="Stated alibi or whereabouts")
    movement: str = Field(default="", description="Known physical or digital movements")
    statement: str = Field(default="", description="Key statements made")


class ParsedEvidenceItem(BaseModel):
    id: str = Field(..., description="Evidence ID, e.g. 'E1', 'E2', 'A', 'B'")
    description: str = Field(..., description="Text description of the clue or observation")
    key_fact: str = Field(default="", description="Investigative nuance, limitation, or key fact")


class ParsedCase(BaseModel):
    case_name: str = Field(default="Investigation Inquiry", description="Case title or summary")
    location: str = Field(default="UNKNOWN / NOT PROVIDED", description="Incident location or scene")
    critical_opportunity_window: str = Field(
        default="UNKNOWN / NOT PROVIDED",
        description="Key timeframe or opportunity window"
    )
    incident_summary: str = Field(default="", description="Brief factual summary of the incident")
    timeline: List[ParsedTimelineItem] = Field(default_factory=list, description="Chronological timeline events")
    suspects: List[ParsedSuspectItem] = Field(default_factory=list, description="Persons, suspects, or entities involved")
    evidence: List[ParsedEvidenceItem] = Field(default_factory=list, description="Evidence items or clues")


# ----------------------------------------------------
# 1. DETECTIVE MODELS
# ----------------------------------------------------

class TimelineEvent(BaseModel):
    time: str = Field(..., description="Timestamp or interval, e.g., '8:20 PM - 8:24 PM' or 'UNKNOWN / NOT PROVIDED'")
    description: str = Field(..., description="Event description based on facts")
    category: Literal["FACT", "INFERENCE", "UNKNOWN"] = Field(
        ..., description="Classification separating confirmed facts, inferences, and unknown events"
    )
    source: str = Field(..., description="Information source or basis")


class DetectiveOutput(BaseModel):
    timeline: List[TimelineEvent] = Field(..., description="Chronological timeline of reconstructed events")
    confirmed_facts: List[str] = Field(..., description="Facts strictly confirmed by the case data")
    critical_opportunity_window: str = Field(..., description="Identified opportunity window or 'UNKNOWN / NOT PROVIDED'")
    unknowns: List[str] = Field(..., description="Unidentified gaps or unknown factors")
    open_questions: List[str] = Field(..., description="Investigative questions that require resolution")


# ----------------------------------------------------
# 2. EVIDENCE MODELS
# ----------------------------------------------------

class EvidenceItemAnalysis(BaseModel):
    id: str = Field(..., description="Evidence identifier (e.g. 'E1', 'E2', 'A', 'B', etc.)")
    description: str = Field(..., description="Text description of the evidence item")
    classification: Literal["FACT", "INFERENCE", "UNKNOWN"] = Field(
        ..., description="Classification: FACT, INFERENCE, or UNKNOWN"
    )
    strength: Literal["WEAK", "MODERATE", "STRONG"] = Field(
        ..., description="Investigative probative strength"
    )
    supports: str = Field(..., description="What this evidence item supports or points toward")
    alternative_explanation: str = Field(..., description="Viable alternative explanation or limitation for this item")


class EvidenceOutput(BaseModel):
    evidence_analysis: List[EvidenceItemAnalysis] = Field(
        ..., description="Comprehensive analysis of each available evidence item"
    )


# ----------------------------------------------------
# 3. SUSPECT / ENTITY MODELS
# ----------------------------------------------------

class SuspectAnalysis(BaseModel):
    name: str = Field(..., description="Full name or identifier of suspect/entity")
    motive: str = Field(..., description="Motive assessment based on case facts or UNKNOWN")
    means: str = Field(..., description="Physical and operational capability")
    opportunity: str = Field(..., description="Presence during opportunity window or UNKNOWN")
    access: str = Field(..., description="Access to scene, credentials, or target")
    alibi: str = Field(..., description="Alibi statement and extent of independent corroboration")
    evidence_for: List[str] = Field(default_factory=list, description="Evidence points or alibis working in their favor")
    evidence_against: List[str] = Field(default_factory=list, description="Evidence points connecting them to the incident")
    contradictions: List[str] = Field(default_factory=list, description="Contradictions between statements, logs, or movements")
    overall_assessment: str = Field(..., description="Objective assessment (Never call anyone guilty)")


class SuspectOutput(BaseModel):
    suspect_analyses: List[SuspectAnalysis] = Field(
        default_factory=list,
        description="List of comparative analyses for each identified person, suspect, or entity"
    )
    ranking: List[str] = Field(default_factory=list, description="Ranked list of persons/entities in order of investigative priority")
    leading_person_of_interest: str = Field(
        ..., description="Leading PERSON OF INTEREST or LEADING EXPLANATION (or 'INSUFFICIENT EVIDENCE')"
    )
    reasoning: str = Field(..., description="Reasoning justifying the leading designation")

    @property
    def suspect_comparison(self) -> Dict[str, SuspectAnalysis]:
        return {s.name: s for s in self.suspect_analyses}

    @model_validator(mode="before")
    @classmethod
    def handle_comparison_input(cls, data: Any) -> Any:
        if isinstance(data, dict):
            if "suspect_analyses" not in data and "suspect_comparison" in data:
                comp = data["suspect_comparison"]
                analyses = []
                if isinstance(comp, dict):
                    for name, s_data in comp.items():
                        if isinstance(s_data, dict):
                            if "name" not in s_data:
                                s_data["name"] = name
                            analyses.append(s_data)
                        elif isinstance(s_data, SuspectAnalysis):
                            analyses.append(s_data)
                elif isinstance(comp, (list, tuple)):
                    analyses = list(comp)
                data["suspect_analyses"] = analyses
        return data


# ----------------------------------------------------
# 4. SKEPTIC MODELS
# ----------------------------------------------------

class SkepticOutput(BaseModel):
    unsupported_assumptions: List[str] = Field(
        ..., description="Assumptions accepted as fact without direct proof"
    )
    contradictions: List[str] = Field(
        ..., description="Key contradictions that challenge the leading theory"
    )
    alternative_explanations: List[str] = Field(
        ..., description="Viable alternative explanations and hypotheses"
    )
    missing_evidence: List[str] = Field(
        ..., description="Critical missing evidence gaps that prevent establishing certainty"
    )
    questions_to_stress_test: List[str] = Field(
        ..., description="Tough investigative questions that stress-test the reasoning"
    )


# ----------------------------------------------------
# 5. CHIEF MODELS
# ----------------------------------------------------

class EvidenceCitation(BaseModel):
    claim: str = Field(..., description="Key investigative claim or synthesis conclusion")
    evidence_ids: List[str] = Field(..., description="Evidence IDs directly supporting this claim (e.g. ['E1', 'E2'] or ['B', 'C'])")


class ChiefOutput(BaseModel):
    leading_person_of_interest: str = Field(
        ..., description="Designated leading PERSON OF INTEREST or LEADING EXPLANATION (Use 'Leading Person of Interest' or 'Leading Explanation'; if none, 'Insufficient evidence to identify a leading person of interest.')"
    )
    confidence_score: int = Field(
        ..., description="Numeric confidence score from 0 to 100 evaluating evidence strength relative to alternatives"
    )
    confidence_level: str = Field(
        ..., description="Confidence level: LOW (0-39), MEDIUM (40-69), HIGH (70-84), VERY HIGH (85-100)"
    )
    why_this_conclusion: str = Field(
        default="",
        description="Concise explanation of why the leading person/explanation currently ranks highest using concrete case facts"
    )
    confidence_explanation: str = Field(
        default="",
        description="Transparent explanation of how the confidence score was derived across evidence dimensions"
    )
    supporting_evidence: List[str] = Field(
        ..., description="Key evidence items supporting the designated person of interest / explanation, formatted as: '[EVIDENCE ID] — short explanation'"
    )
    contradictory_evidence: List[str] = Field(
        ..., description="MANDATORY: Evidence that contradicts, limits, or fails to prove the conclusion (e.g. no direct proof, incomplete coverage, other access)"
    )
    alternative_theories: List[str] = Field(
        ..., description="Viable alternative hypotheses or competing explanations supported by supplied facts (or 'No additional alternative explanation is supported by the provided evidence.')"
    )
    important_uncertainty: str = Field(
        default="Not established from the provided evidence.",
        description="Explicit identification of the biggest unresolved question and established facts vs unknowns"
    )
    unresolved_uncertainties: List[str] = Field(
        default_factory=list,
        description="Explicit list of unresolved case uncertainties"
    )
    opportunity_window: str = Field(
        default="Opportunity window cannot be precisely established from the supplied information.",
        description="Narrowest defensible opportunity window distinguishing last confirmed present and first missing"
    )
    recommended_next_evidence: List[str] = Field(
        ..., description="Practical next evidence/tests needed to resolve uncertainties and distinguish competing explanations"
    )
    final_conclusion: str = Field(
        default="",
        description="Concise evidence-based final conclusion summarizing the investigative assessment without overstating certainty"
    )
    evidence_citations: List[EvidenceCitation] = Field(
        default_factory=list,
        description="Structured citations linking specific claims directly to evidence IDs"
    )
    human_review_required: bool = Field(
        True, description="Flag explicitly requiring human supervisor review"
    )

    @field_validator("confidence_score")
    @classmethod
    def validate_score_range(cls, v: int) -> int:
        if isinstance(v, bool) or not isinstance(v, int):
            try:
                v = int(v)
            except Exception:
                raise ValueError(f"confidence_score must be an integer, got {v}")
        if v < 0 or v > 100:
            raise ValueError(f"confidence_score must be between 0 and 100, got {v}")
        return v

    @model_validator(mode="before")
    @classmethod
    def handle_legacy_fields(cls, data: Any) -> Any:
        if isinstance(data, dict):
            if "confidence_score" not in data and "confidence" in data:
                level = str(data["confidence"]).strip().upper()
                if level == "LOW":
                    data["confidence_score"] = 25
                elif level == "MEDIUM":
                    data["confidence_score"] = 55
                elif level == "VERY HIGH":
                    data["confidence_score"] = 90
                else:
                    data["confidence_score"] = 78
                data["confidence_level"] = level
            elif "confidence_level" not in data and "confidence" in data:
                data["confidence_level"] = str(data["confidence"]).strip().upper()

            if "confidence_explanation" not in data and "reasoning" in data:
                reasoning = data["reasoning"]
                data["confidence_explanation"] = " ".join(reasoning) if isinstance(reasoning, list) else str(reasoning)

            if not data.get("why_this_conclusion") and data.get("confidence_explanation"):
                data["why_this_conclusion"] = data["confidence_explanation"]
            elif not data.get("confidence_explanation") and data.get("why_this_conclusion"):
                data["confidence_explanation"] = data["why_this_conclusion"]

            if "supporting_evidence" not in data and "strongest_evidence" in data:
                data["supporting_evidence"] = data["strongest_evidence"]

            if "contradictory_evidence" not in data:
                contra = []
                if "weakest_uncertain_evidence" in data and isinstance(data["weakest_uncertain_evidence"], list):
                    contra.extend(data["weakest_uncertain_evidence"])
                if "contradictions" in data and isinstance(data["contradictions"], list):
                    contra.extend(data["contradictions"])
                data["contradictory_evidence"] = contra or ["None recorded"]

            if "unresolved_uncertainties" not in data:
                if "missing_evidence" in data and isinstance(data["missing_evidence"], list):
                    data["unresolved_uncertainties"] = data["missing_evidence"]
                else:
                    data["unresolved_uncertainties"] = ["Key identity or physical confirmation remains pending."]

            if not data.get("important_uncertainty"):
                if data.get("unresolved_uncertainties") and len(data["unresolved_uncertainties"]) > 0:
                    data["important_uncertainty"] = data["unresolved_uncertainties"][0]
                else:
                    data["important_uncertainty"] = "Not established from the provided evidence."

            if "alternative_theories" not in data:
                if "alternative_explanations" in data and isinstance(data["alternative_explanations"], list):
                    data["alternative_theories"] = data["alternative_explanations"]
                else:
                    data["alternative_theories"] = ["Alternative explanation by unverified third party."]

            if "recommended_next_evidence" not in data:
                if "missing_evidence" in data and isinstance(data["missing_evidence"], list):
                    data["recommended_next_evidence"] = data["missing_evidence"]
                else:
                    data["recommended_next_evidence"] = ["Collect additional forensic corroboration."]

            if not data.get("final_conclusion"):
                poi = data.get("leading_person_of_interest", "The leading explanation")
                data["final_conclusion"] = f"{poi} is designated based on currently available evidence and opportunity, but remaining uncertainties require further verification."
        return data

    @model_validator(mode="after")
    def validate_confidence_level_match(self) -> "ChiefOutput":
        score = self.confidence_score
        expected_level: str
        if 0 <= score <= 39:
            expected_level = "LOW"
        elif 40 <= score <= 69:
            expected_level = "MEDIUM"
        elif 70 <= score <= 84:
            expected_level = "HIGH"
        else:  # 85 <= score <= 100
            expected_level = "VERY HIGH"

        clean_level = self.confidence_level.strip().upper()
        if clean_level != expected_level:
            raise ValueError(
                f"confidence_level '{self.confidence_level}' does not correspond to score {score} (expected '{expected_level}')"
            )
        self.confidence_level = expected_level
        return self

    @property
    def confidence(self) -> str:
        return self.confidence_level

    @property
    def strongest_evidence(self) -> List[str]:
        return self.supporting_evidence

    @property
    def weakest_uncertain_evidence(self) -> List[str]:
        return self.contradictory_evidence

    @property
    def contradictions(self) -> List[str]:
        return self.contradictory_evidence

    @property
    def alternative_explanations(self) -> List[str]:
        return self.alternative_theories

    @property
    def missing_evidence(self) -> List[str]:
        return self.recommended_next_evidence

    @property
    def reasoning(self) -> List[str]:
        return [self.confidence_explanation]


# ----------------------------------------------------
# PIPELINE & EXPERIMENT RESULTS
# ----------------------------------------------------

class InvestigationResult(BaseModel):
    case_name: str = Field(..., description="Name of the case")
    detective: DetectiveOutput = Field(..., description="Agent 1: Detective report")
    evidence: List[EvidenceItemAnalysis] = Field(..., description="Agent 2: Evidence analysis")
    suspects: SuspectOutput = Field(..., description="Agent 3: Suspect comparison")
    skeptic: SkepticOutput = Field(..., description="Agent 4: Skeptic critique")
    chief: ChiefOutput = Field(..., description="Agent 5: Chief synthesis")
    parsed_case: Optional[Dict[str, Any]] = Field(default=None, description="Original parsed case data")


class ComparisonResult(BaseModel):
    removed_evidence_id: str = Field(default="", description="ID of the evidence item removed")
    removed_evidence_desc: str = Field(default="", description="Description of removed evidence")

    original_poi: str
    modified_poi: str
    poi_comparison: str

    original_score: int = 0
    modified_score: int = 0
    score_change: int = 0

    original_confidence: str
    modified_confidence: str
    confidence_comparison: str

    original_strongest: List[str] = Field(default_factory=list)
    modified_strongest: List[str] = Field(default_factory=list)
    strongest_evidence_comparison: str

    reasoning_changes: str


# ----------------------------------------------------
# HUMAN REVIEW
# ----------------------------------------------------

class HumanReviewRecord(BaseModel):
    id: str
    decision: Literal["ACCEPT", "REVISE", "REJECT"]
    notes: str
    next_evidence: str
    timestamp: str
