# -*- coding: utf-8 -*-
"""Agent 2: EVIDENCE
Generic Evidence Specialist.
Analyzes any number of evidence items (e.g. 1, 3, 7, 12, etc.),
classifies each as FACT, INFERENCE, or UNKNOWN, evaluates probative strength,
identifies what each item supports, and outlines viable alternative explanations.
"""

import json
from typing import Dict, Any, List, Optional
from models import EvidenceOutput, DetectiveOutput, EvidenceItemAnalysis
from gemini_client import GeminiService, gemini_service

SYSTEM_PROMPT = """You are the Evidence Specialist on the AI Mystery Detective Team.
Role: Objective Evidence Analysis and Probative Classification.
Your mission is to rigorously evaluate all evidence items and clues provided in ANY case.

INPUTS:
1. Case evidence items (whether 1, 3, 7, 12, etc.).
2. Detective timeline and opportunity report.

RESPONSIBILITIES FOR EACH EVIDENCE ITEM:
- id: Evidence ID (e.g. 'E1', 'E2', 'A', 'B', etc.).
- description: Text description of the clue or observation.
- classification: Strictly FACT, INFERENCE, or UNKNOWN.
- strength: Strictly WEAK, MODERATE, or STRONG.
- supports: What investigative hypothesis, individual, or fact this item actually supports.
- alternative_explanation: Plausible alternative explanation or limitation for this item.

CRITICAL EVIDENCE & ETHICAL RULES:
1. Never equate electronic card/key usage or digital credential swipes with conclusive proof of personal physical presence unless corroborated by unbroken visual/biometric confirmation.
2. Never treat an unverified folder, bag, or container as proof of its contents without direct observation or verified recovery.
3. Treat visual fiber, toolmark, or preliminary matches as preliminary indicators rather than absolute scientific proof unless formal laboratory spectrometry is verified.
4. Do NOT manufacture evidence or assume facts not present in the case data.
"""


def run_evidence_agent(
    case_data: Dict[str, Any],
    detective_report: DetectiveOutput,
    service: Optional[GeminiService] = None
) -> List[EvidenceItemAnalysis]:
    """Executes the generic Evidence agent on available case evidence items."""
    svc = service or gemini_service
    evidence_items = case_data.get("evidence", [])
    
    # If no evidence items exist, generate an empty list
    if not evidence_items:
        return []

    input_payload = json.dumps({
        "case_name": case_data.get("case_name"),
        "case_evidence": evidence_items,
        "confirmed_facts": detective_report.confirmed_facts,
        "critical_window": detective_report.critical_opportunity_window,
        "timeline": [t.model_dump() for t in detective_report.timeline]
    }, indent=2)

    output: EvidenceOutput = svc.generate_structured(
        system_instruction=SYSTEM_PROMPT,
        prompt=f"Analyze all evidence items using the case data and Detective report:\n\n{input_payload}",
        response_model=EvidenceOutput
    )
    return output.evidence_analysis
