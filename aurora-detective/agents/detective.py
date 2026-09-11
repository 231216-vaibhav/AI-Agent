# -*- coding: utf-8 -*-
"""Agent 1: DETECTIVE
Generic Timeline and Fact Reconstruction Specialist.
Reconstructs the timeline, identifies confirmed facts, determines the critical opportunity window,
identifies unknowns, and generates open investigative questions.
NEVER accuses a suspect.
"""

import json
from typing import Dict, Any, Optional
from models import DetectiveOutput
from gemini_client import GeminiService, gemini_service

SYSTEM_PROMPT = """You are the Detective Agent on the AI Mystery Detective Team.
Role: Timeline and Fact Reconstruction Specialist.
Your mission is to objectively reconstruct the facts and chronological sequence of ANY supplied case.

PRIMARY INSTRUCTIONS:
1. Reconstruct the case timeline chronologically with utmost precision based ONLY on the provided case data.
2. Identify all strictly confirmed facts based exclusively on authorized records, logs, and observations.
3. Identify the critical opportunity window or timeframe when the incident occurred. If timestamps are absent, state 'UNKNOWN / NOT PROVIDED'.
4. Identify unknowns and gaps where critical information is missing.
5. Identify key open investigative questions that require forensic resolution.

CRITICAL ETHICAL & EVIDENTIARY RULES:
- NEVER accuse a suspect or declare who is responsible.
- Categorize every timeline event strictly as FACT, INFERENCE, or UNKNOWN.
- NEVER invent timestamps, CCTV footage, witnesses, physical evidence, locations, statements, or events.
- If information is missing, explicitly designate it as 'UNKNOWN / NOT PROVIDED'.
"""


def run_detective_agent(case_data: Dict[str, Any], service: Optional[GeminiService] = None) -> DetectiveOutput:
    """Executes the generic Detective agent on case data."""
    svc = service or gemini_service
    input_payload = json.dumps({
        "case_name": case_data.get("case_name"),
        "location": case_data.get("location"),
        "incident_summary": case_data.get("incident_summary", ""),
        "timeline_events": case_data.get("timeline"),
        "suspects_or_people": case_data.get("suspects"),
        "evidence_clues": case_data.get("evidence")
    }, indent=2)

    return svc.generate_structured(
        system_instruction=SYSTEM_PROMPT,
        prompt=f"Reconstruct the timeline and facts from the case data below:\n\n{input_payload}",
        response_model=DetectiveOutput
    )
