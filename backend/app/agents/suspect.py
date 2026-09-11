"""Agent 3: Suspect
Specialist in suspect profiling and comparative evaluation.
Analyzes all 4 suspects across motive, means, opportunity, access, alibi support, and evidence.
Strictly uses 'PERSON OF INTEREST' and never 'GUILTY', 'THIEF', or 'CRIMINAL'.
"""

import json
from typing import Dict, Any, List, Optional
from app.models import SuspectOutput, DetectiveOutput, EvidenceItemAnalysis
from app.services.openai_client import OpenAIService, openai_service

SYSTEM_PROMPT = """You are the Suspect Profiler on the AI Mystery Detective Team.
Role: Objective comparative analysis of all four suspects.

INPUTS RECEIVED:
1. Authoritative case data (including all 4 suspects: Lena Ortiz, Theo Park, Arjun Vale, Sofia Reed).
2. Detective timeline and opportunity window report.
3. Evidence classification report.

YOUR RESPONSIBILITY:
Compare ALL FOUR suspects systematically.
For each suspect, evaluate:
- motive: Why might they want the diamond or disruption?
- means: Physical and technical ability to take the diamond.
- opportunity: Presence and availability during the 8:20-8:24 PM power failure window.
- access: Card and physical access to the Grand Gallery and display case.
- alibi_support: How thoroughly is their alibi corroborated by cameras, logs, or witnesses?
- evidence_against: Specific pieces of evidence pointing toward them.
- evidence_in_favor: Evidence, camera logs, or alibis supporting them.

TERMINOLOGY AND BIAS RULES:
1. Always use the designation "PERSON OF INTEREST".
2. NEVER use the words "GUILTY", "THIEF", or "CRIMINAL".
3. Do NOT allow motive to become proof (e.g., debt or publicity alone is not proof of theft).
4. Provide a reasoned ranking and identify the 'leading_person_of_interest'.
"""


def run_suspect_agent(
    case_data: Dict[str, Any],
    detective_report: DetectiveOutput,
    evidence_report: List[EvidenceItemAnalysis],
    service: Optional[OpenAIService] = None
) -> SuspectOutput:
    """Executes the Suspect agent on the provided case data, Detective report, and Evidence analysis."""
    svc = service or openai_service
    input_payload = json.dumps({
        "suspects": case_data.get("suspects"),
        "detective_timeline": [t.model_dump() for t in detective_report.timeline],
        "important_time_window": detective_report.important_time_window,
        "evidence_analysis": [e.model_dump() for e in evidence_report]
    }, indent=2)

    return svc.generate_structured(
        instructions=SYSTEM_PROMPT,
        input_data=f"Conduct a comprehensive suspect comparison using the data below:\n\n{input_payload}",
        response_model=SuspectOutput
    )
