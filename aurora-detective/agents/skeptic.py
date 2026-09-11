# -*- coding: utf-8 -*-
"""Agent 4: SKEPTIC
Generic Counter-Investigator / Devil's Advocate.
Challenges the leading theory or explanation, exposes unsupported assumptions,
identifies contradictions, alternative explanations, and missing evidence to stress-test reasoning.
"""

import json
from typing import Dict, Any, List, Optional
from models import SkepticOutput, DetectiveOutput, EvidenceItemAnalysis, SuspectOutput
from gemini_client import GeminiService, gemini_service

SYSTEM_PROMPT = """You are the Skeptic on the AI Mystery Detective Team.
Role: Critical Counter-Investigator / Devil's Advocate.
Your mission is to critically challenge, deconstruct, and stress-test the leading theory or explanation across ANY case.

YOUR MISSION:
Actively challenge and stress-test the leading person of interest or hypothesis identified by the Suspect agent.
You MUST NOT simply agree or validate the prevailing narrative.
Expose weaknesses, cognitive leaps, and evidentiary gaps.

REQUIRED ANALYTICAL CATEGORIES:
1. unsupported_assumptions: Assumptions accepted without direct, unambiguous proof.
2. contradictions: Discrepancies between evidence items, movement logs, and statements.
3. alternative_explanations: Viable alternative hypotheses, third-party interventions, framing, or innocent explanations.
4. missing_evidence: Gaps in physical, digital, or testimonial evidence that prevent reaching a definitive conclusion.
5. questions_to_stress_test: Critical investigative questions that could alter the conclusion or exonerate the leading candidate.

RULES:
- Do NOT invent fictional evidence or timestamps.
- Ground all skeptical critiques in realistic investigative rigor and logical doubt.
"""


def run_skeptic_agent(
    case_data: Dict[str, Any],
    detective_report: DetectiveOutput,
    evidence_report: List[EvidenceItemAnalysis],
    suspect_report: SuspectOutput,
    service: Optional[GeminiService] = None
) -> SkepticOutput:
    """Executes the generic Skeptic agent to stress-test the leading theory."""
    svc = service or gemini_service
    input_payload = json.dumps({
        "case_data": {
            "case_name": case_data.get("case_name"),
            "critical_window": case_data.get("critical_opportunity_window"),
            "evidence": case_data.get("evidence")
        },
        "detective_report": detective_report.model_dump(),
        "evidence_report": [e.model_dump() for e in evidence_report],
        "suspect_report": suspect_report.model_dump()
    }, indent=2)

    return svc.generate_structured(
        system_instruction=SYSTEM_PROMPT,
        prompt=f"Challenge and stress-test the leading theory using the case and agent reports below:\n\n{input_payload}",
        response_model=SkepticOutput
    )
