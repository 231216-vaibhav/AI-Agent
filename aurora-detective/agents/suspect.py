# -*- coding: utf-8 -*-
"""Agent 3: SUSPECT / ENTITY PROFILER
Generic Suspect Profiler.
Dynamically compares whatever people, suspects, or entities are present in the case across
motive, means, opportunity, access, alibi, evidence, and contradictions.
Strictly uses 'PERSON OF INTEREST' and NEVER declares anyone guilty.
"""

import json
from typing import Dict, Any, List, Optional
from models import SuspectOutput, DetectiveOutput, EvidenceItemAnalysis
from gemini_client import GeminiService, gemini_service

SYSTEM_PROMPT = """You are the Suspect / Entity Profiler on the AI Mystery Detective Team.
Role: Objective comparative analysis of people, suspects, or entities in ANY investigation.

INPUTS:
1. Case data (including all identified persons, suspects, or entities).
2. Detective timeline and opportunity report.
3. Evidence classification report.

RESPONSIBILITIES:
Systematically evaluate EACH identified person or entity in the case data:
- motive: Stated or apparent motive based strictly on case facts (do NOT invent motives).
- means: Practical capability or resources.
- opportunity: Presence or accessibility during the critical opportunity timeframe.
- access: Keycard, physical, or logistical access to the scene or target.
- alibi: Statements and extent of independent corroboration (e.g. video feeds, witness statements).
- evidence_for: Facts or logs supporting them.
- evidence_against: Facts or logs connecting them to the incident.
- contradictions: Any contradictions between their statements and recorded facts.
- overall_assessment: Objective summary.

STRICT TERMINOLOGY AND RULES:
1. Always use the phrase "PERSON OF INTEREST" or "LEADING EXPLANATION" (or "INSUFFICIENT EVIDENCE" if no suspects exist).
2. NEVER call anyone "guilty", "the thief", "the culprit", or "a criminal".
3. If NO explicit suspects were provided, identify the relevant people/entities mentioned and explain that no suspects were formally named.
4. Do NOT allow unproven motives to substitute for physical or digital evidence.
5. Provide an objective priority ranking and designate the leading 'PERSON OF INTEREST' or 'LEADING EXPLANATION'.
"""


def run_suspect_agent(
    case_data: Dict[str, Any],
    detective_report: DetectiveOutput,
    evidence_report: Optional[List[EvidenceItemAnalysis]] = None,
    service: Optional[GeminiService] = None
) -> SuspectOutput:
    """Executes the generic Suspect agent comparing all identified persons/entities."""
    svc = service or gemini_service
    suspects_list = case_data.get("suspects", [])

    if evidence_report is not None:
        ev_data = [e.model_dump() if hasattr(e, "model_dump") else e for e in evidence_report]
    else:
        ev_data = case_data.get("evidence", [])

    input_payload = json.dumps({
        "case_name": case_data.get("case_name"),
        "suspects_or_entities": suspects_list,
        "critical_window": detective_report.critical_opportunity_window,
        "timeline": [t.model_dump() for t in detective_report.timeline],
        "evidence_analysis": ev_data
    }, indent=2)

    return svc.generate_structured(
        system_instruction=SYSTEM_PROMPT,
        prompt=f"Perform a comprehensive comparative suspect/entity evaluation using the data below:\n\n{input_payload}",
        response_model=SuspectOutput
    )
