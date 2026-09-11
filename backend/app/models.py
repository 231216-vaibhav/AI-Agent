"""Pydantic models for structured outputs across all 5 GPT-5 investigation agents,
pipeline orchestration, and API endpoints.
"""

from typing import List, Dict, Optional, Literal, Union, Any
from pydantic import BaseModel, Field


# ----------------------------------------------------
# AGENT 1: DETECTIVE MODELS
# ----------------------------------------------------

class TimelineItem(BaseModel):
    time: str = Field(..., description="Timestamp or time interval of the event, e.g., '8:23 PM'")
    event: str = Field(..., description="Description of the event that occurred")
    category: Literal["FACT", "INFERENCE", "UNKNOWN"] = Field(
        ..., description="Classification separating confirmed facts, inferences, and unknown events"
    )
    source: str = Field(..., description="Source of information, e.g., 'Lock Log', 'Camera', 'Statement'")


class DetectiveOutput(BaseModel):
    timeline: List[TimelineItem] = Field(..., description="Reconstructed chronological timeline of events")
    confirmed_facts: List[str] = Field(..., description="Key facts strictly confirmed by authoritative case data")
    important_time_window: str = Field(..., description="Identified critical opportunity window for the theft")
    open_questions: List[str] = Field(..., description="Unresolved questions regarding timeline or actions")


# ----------------------------------------------------
# AGENT 2: EVIDENCE MODELS
# ----------------------------------------------------

class EvidenceItemAnalysis(BaseModel):
    id: str = Field(..., description="Evidence identifier (e.g., 'A', 'B', 'C', etc.)")
    observation: str = Field(..., description="Detailed factual observation of the evidence item")
    classification: Literal["FACT", "INFERENCE"] = Field(
        ..., description="Classification of the observation: strictly FACT or INFERENCE"
    )
    strength: Literal["WEAK", "MODERATE", "STRONG"] = Field(
        ..., description="Investigative strength of the evidence item"
    )
    alternative_explanation: str = Field(
        ..., description="Plausible alternative explanation for this piece of evidence"
    )
    contradiction: str = Field(
        ..., description="Any conflicts or contradictions this evidence poses with statements or other evidence"
    )


class EvidenceOutput(BaseModel):
    evidence_analysis: List[EvidenceItemAnalysis] = Field(
        ..., description="Rigorous analysis of each evidence item presented in the case"
    )


# ----------------------------------------------------
# AGENT 3: SUSPECT MODELS
# ----------------------------------------------------

class SuspectAnalysis(BaseModel):
    name: str = Field(..., description="Full name of suspect")
    motive: str = Field(..., description="Documented motive based on case background")
    means: str = Field(..., description="Physical capability and technical means to execute the theft")
    opportunity: str = Field(..., description="Presence and opportunity window during blackout")
    access: str = Field(..., description="Documented electronic and physical card/lock access")
    alibi_support: str = Field(..., description="Evaluation of alibi verification and witness support")
    evidence_against: List[str] = Field(..., description="Specific evidence points connecting them to the crime")
    evidence_in_favor: List[str] = Field(..., description="Evidence points or verified alibis working in their favor")


class SuspectOutput(BaseModel):
    suspect_comparison: Dict[str, SuspectAnalysis] = Field(
        ..., description="Detailed profile comparison for all four suspects"
    )
    ranking: List[str] = Field(..., description="Ranked list of suspect names by investigative focus")
    leading_person_of_interest: str = Field(
        ..., description="Name of leading person of interest (Must use 'PERSON OF INTEREST', never guilty/thief)"
    )
    reasoning: str = Field(..., description="Detailed objective reasoning justifying the leading person of interest")


# ----------------------------------------------------
# AGENT 4: SKEPTIC MODELS
# ----------------------------------------------------

class SkepticOutput(BaseModel):
    unsupported_assumptions: List[str] = Field(
        ..., description="Unverified assumptions embedded in the leading theory"
    )
    contradictions: List[str] = Field(
        ..., description="Key contradictions and inconsistencies that challenge the leading theory"
    )
    alternative_explanations: List[str] = Field(
        ..., description="Viable alternative hypotheses explaining the facts and evidence"
    )
    missing_evidence: List[str] = Field(
        ..., description="Crucial evidence gaps that prevent establishing guilt"
    )
    questions_that_could_change_conclusion: List[str] = Field(
        ..., description="Investigative questions whose answers could exonerate or implicate other parties"
    )


# ----------------------------------------------------
# AGENT 5: CHIEF MODELS
# ----------------------------------------------------

class EvidenceCitation(BaseModel):
    claim: str = Field(..., description="Key investigative claim or finding")
    evidence_ids: List[str] = Field(..., description="Directly relevant evidence IDs (e.g., ['B', 'C', 'D', 'E'])")


class ChiefOutput(BaseModel):
    leading_person_of_interest: str = Field(
        ..., description="Designated leading person of interest (e.g., 'Arjun Vale')"
    )
    confidence: Literal["LOW", "MEDIUM", "HIGH"] = Field(
        ..., description="Overall investigative confidence level"
    )
    reasoning: List[str] = Field(
        ..., description="Synthesized reasoning synthesizing all agents' findings"
    )
    strongest_evidence: List[str] = Field(
        ..., description="Most compelling evidence points supporting the investigation"
    )
    weakest_evidence: List[str] = Field(
        ..., description="Evidence items that are circumstantial, vulnerable, or require validation"
    )
    contradictions: List[str] = Field(
        ..., description="Reconciled or identified contradictions in suspect statements vs logs"
    )
    alternative_explanation: List[str] = Field(
        ..., description="Alternative explanations acknowledged by leadership"
    )
    uncertainty: List[str] = Field(
        ..., description="Areas of remaining uncertainty"
    )
    missing_evidence: List[str] = Field(
        ..., description="Critical investigative gaps (e.g. folder contents, scientific fiber confirmation)"
    )
    recommended_next_evidence: List[str] = Field(
        ..., description="Actionable next forensic or investigative steps recommended"
    )
    evidence_ids: List[str] = Field(
        ..., description="List of all primary evidence IDs cited in the synthesis"
    )
    human_review_required: bool = Field(
        True, description="Human review flag indicating supervisor sign-off is needed"
    )
    evidence_citations: List[EvidenceCitation] = Field(
        default_factory=list,
        description="Structured citations linking specific claims directly to evidence IDs"
    )


# ----------------------------------------------------
# PIPELINE & API RESPONSE MODELS
# ----------------------------------------------------

class InvestigateResponse(BaseModel):
    case_id: str = Field("001", description="Case identifier")
    status: str = Field("complete", description="Investigation status")
    detective: DetectiveOutput = Field(..., description="Reconstructed facts and timeline from Detective agent")
    evidence: List[EvidenceItemAnalysis] = Field(..., description="Analysis of evidence items from Evidence agent")
    suspects: SuspectOutput = Field(..., description="Comparison of all suspects from Suspect agent")
    skeptic: SkepticOutput = Field(..., description="Critical counter-analysis from Skeptic agent")
    chief: ChiefOutput = Field(..., description="Final leadership synthesis from Chief agent")


class ComparisonMetric(BaseModel):
    original: Any = Field(..., description="Value in original investigation (with full Evidence A-G)")
    modified: Any = Field(..., description="Value in modified investigation (without Evidence E)")
    impact_analysis: str = Field(..., description="Analytical explanation of the impact caused by removing Evidence E")


class InvestigationComparison(BaseModel):
    leading_person_of_interest: ComparisonMetric = Field(..., description="Comparison of leading suspect")
    confidence: ComparisonMetric = Field(..., description="Comparison of confidence levels")
    strongest_evidence: ComparisonMetric = Field(..., description="Comparison of strongest evidence")
    best_alternative: ComparisonMetric = Field(..., description="Comparison of best alternative theory")
    missing_evidence: ComparisonMetric = Field(..., description="Comparison of missing evidence gaps")


class InvestigateModifiedResponse(BaseModel):
    original: InvestigateResponse = Field(..., description="Full original investigation result")
    modified: InvestigateResponse = Field(..., description="Modified investigation result without Evidence E")
    comparison: InvestigationComparison = Field(..., description="Direct sensitivity comparison of both runs")


# ----------------------------------------------------
# HUMAN REVIEW MODELS
# ----------------------------------------------------

class HumanReviewInput(BaseModel):
    decision: Literal["ACCEPT", "REVISE", "REJECT"] = Field(
        ..., description="Human investigator review decision"
    )
    notes: str = Field(..., description="Investigator notes and rationale")
    next_evidence: Union[str, List[str]] = Field(
        ..., description="Follow-up forensic or testimonial evidence requested"
    )


class HumanReviewRecord(BaseModel):
    id: str = Field(..., description="Unique review identifier")
    decision: Literal["ACCEPT", "REVISE", "REJECT"] = Field(..., description="Human review decision")
    notes: str = Field(..., description="Investigator notes")
    next_evidence: Union[str, List[str]] = Field(..., description="Requested next evidence")
    timestamp: str = Field(..., description="Submission ISO timestamp")
