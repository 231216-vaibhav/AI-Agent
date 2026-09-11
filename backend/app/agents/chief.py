"""Agent 5: Chief
Senior investigative leader and synthesizer.
Synthesizes findings from Detective, Evidence, Suspect, and Skeptic.
Designates the leading person of interest with evidence-grounded nuance and explicit citations.
"""

import json
from typing import Dict, Any, List, Optional
from app.models import (
    ChiefOutput,
    DetectiveOutput,
    EvidenceItemAnalysis,
    SuspectOutput,
    SkepticOutput
)
from app.services.openai_client import OpenAIService, openai_service

SYSTEM_PROMPT = """You are the Chief of the AI Mystery Detective Team.
Role: Senior lead investigator synthesizing the complete investigation.

INPUTS RECEIVED:
1. Authoritative case data.
2. Detective timeline and opportunity report.
3. Evidence analysis report.
4. Suspect comparative report.
5. Skeptic critique and stress-test report.

SYNTHESIS GUIDELINES:
1. The intended evidence-grounded conclusion is:
   Arjun Vale is the leading person of interest (or primary suspect under scrutiny).
   HOWEVER, do NOT state that he is definitely guilty or convicted.
2. You must recognize the incriminating facts:
   - Arjun's card opened the display case at 8:23 PM during the blackout.
   - His statement (card in jacket in archive) conflicts with the access record.
   - He was observed leaving the archive carrying a flat folder at 8:25 PM.
   - Blue velvet fibers matching the cushion were found inside the folder (if Evidence E is present).
3. You must equally recognize the critical investigative uncertainties highlighted by the Skeptic:
   - Card usage proves the card was used, not that Arjun personally swiped it.
   - The camera does not reveal the contents of the catalogue folder.
   - Fiber evidence requires comparative scientific spectrometry/analysis before conclusive proof.
4. EVIDENCE CITATIONS:
   Every important conclusion must reference relevant evidence IDs (e.g., A, B, C, D, E, F, G).
   Include structured evidence_citations mapping claims to valid evidence IDs.
   Do not cite irrelevant evidence.
5. human_review_required must be true.
"""


def run_chief_agent(
    case_data: Dict[str, Any],
    detective_report: DetectiveOutput,
    evidence_report: List[EvidenceItemAnalysis],
    suspect_report: SuspectOutput,
    skeptic_report: SkepticOutput,
    service: Optional[OpenAIService] = None
) -> ChiefOutput:
    """Executes the Chief agent to synthesize all previous agent reports into a final assessment."""
    svc = service or openai_service
    input_payload = json.dumps({
        "case_data": {
            "title": case_data.get("title"),
            "incident": case_data.get("incident"),
            "evidence": case_data.get("evidence")
        },
        "detective_report": detective_report.model_dump(),
        "evidence_report": [e.model_dump() for e in evidence_report],
        "suspect_report": suspect_report.model_dump(),
        "skeptic_report": skeptic_report.model_dump()
    }, indent=2)

    return svc.generate_structured(
        instructions=SYSTEM_PROMPT,
        input_data=f"Synthesize the complete case and deliver the executive investigation report:\n\n{input_payload}",
        response_model=ChiefOutput
    )
