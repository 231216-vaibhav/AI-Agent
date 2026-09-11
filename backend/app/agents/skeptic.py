"""Agent 4: Skeptic
Specialist in critical review and counter-investigation.
Its ONLY purpose is to challenge the leading theory, identify unsupported assumptions,
contradictions, alternative explanations, and missing evidence.
"""

import json
from typing import Dict, Any, List, Optional
from app.models import SkepticOutput, DetectiveOutput, EvidenceItemAnalysis, SuspectOutput
from app.services.openai_client import OpenAIService, openai_service

SYSTEM_PROMPT = """You are the Skeptic on the AI Mystery Detective Team.
Role: Critical counter-investigator / Devil's advocate.

YOUR ONLY PURPOSE:
Actively challenge and stress-test the leading theory identified by the Suspect agent.
You MUST NOT simply agree with the previous agents or validate their narrative.
You must aggressively identify flaws, alternate interpretations, and unproven leaps in logic.

REQUIRED RETURN SECTIONS:
1. unsupported_assumptions: Every assumption taken as fact without direct proof (e.g., assuming card possession equals physical person).
2. contradictions: Inconsistencies between evidence items, witness statements, or timing.
3. alternative_explanations: Viable alternative theories (e.g. card theft/framing, accomplice involvement, staged loss).
4. missing_evidence: Gaps in hard physical/digital evidence (e.g. folder contents unknown, video gap, fingerprinting).
5. questions_that_could_change_conclusion: High-impact investigative questions that could exonerate the leading suspect or implicate someone else.
"""


def run_skeptic_agent(
    case_data: Dict[str, Any],
    detective_report: DetectiveOutput,
    evidence_report: List[EvidenceItemAnalysis],
    suspect_report: SuspectOutput,
    service: Optional[OpenAIService] = None
) -> SkepticOutput:
    """Executes the Skeptic agent on the outputs from Detective, Evidence, and Suspect agents."""
    svc = service or openai_service
    input_payload = json.dumps({
        "case_data": {
            "title": case_data.get("title"),
            "incident": case_data.get("incident"),
            "evidence": case_data.get("evidence")
        },
        "detective_report": detective_report.model_dump(),
        "evidence_report": [e.model_dump() for e in evidence_report],
        "suspect_report": suspect_report.model_dump()
    }, indent=2)

    return svc.generate_structured(
        instructions=SYSTEM_PROMPT,
        input_data=f"Challenge the leading theory and identify weaknesses using the case and agent reports below:\n\n{input_payload}",
        response_model=SkepticOutput
    )
