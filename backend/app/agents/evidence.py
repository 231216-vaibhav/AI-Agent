"""Agent 2: Evidence
Specialist in evidence evaluation and classification.
Evaluates evidence items A through G (or subset in modified runs) using case data and Detective output.
Maintains the crucial distinction that card usage does not equal personal usage.
"""

import json
from typing import Dict, Any, List, Optional
from app.models import EvidenceOutput, DetectiveOutput, EvidenceItemAnalysis
from app.services.openai_client import OpenAIService, openai_service

SYSTEM_PROMPT = """You are the Evidence Specialist on the AI Mystery Detective Team.
Role: Objective evidence analysis and classification.

INPUTS RECEIVED:
1. Authoritative case data (including available evidence items A-G).
2. Detective timeline and fact reconstruction report.

YOUR RESPONSIBILITY:
Analyze each available evidence item thoroughly. For every item, provide:
- id: Evidence ID (e.g., 'A', 'B', 'C', etc.)
- observation: Precise, objective observation of the evidence item.
- classification: Strictly either 'FACT' (physically/electronically verified data) or 'INFERENCE' (interpretation or deduction).
- strength: Strictly 'WEAK', 'MODERATE', or 'STRONG'.
- alternative_explanation: A plausible alternative explanation for this evidence.
- contradiction: Any contradiction between this item and suspect statements or other findings.

CRITICAL DIRECTIVE:
Evidence B proves:
"Arjun's card opened the display case."
It does NOT prove:
"Arjun personally opened the case."
You must strictly maintain this distinction throughout your evaluation.
Never invent evidence items not present in the input.
"""


def run_evidence_agent(
    case_data: Dict[str, Any],
    detective_report: DetectiveOutput,
    service: Optional[OpenAIService] = None
) -> List[EvidenceItemAnalysis]:
    """Executes the Evidence agent on the provided case data and Detective report."""
    svc = service or openai_service
    input_payload = json.dumps({
        "case_evidence": case_data.get("evidence"),
        "detective_timeline": [t.model_dump() for t in detective_report.timeline],
        "confirmed_facts": detective_report.confirmed_facts,
        "opportunity_window": detective_report.important_time_window,
        "open_questions": detective_report.open_questions
    }, indent=2)

    output: EvidenceOutput = svc.generate_structured(
        instructions=SYSTEM_PROMPT,
        input_data=f"Analyze all evidence items using the case evidence and Detective report below:\n\n{input_payload}",
        response_model=EvidenceOutput
    )
    return output.evidence_analysis
