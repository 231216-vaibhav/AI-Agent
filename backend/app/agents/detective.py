"""Agent 1: Detective
Specialist in timeline and fact reconstruction.
Does NOT identify the thief. Strictly separates FACT, INFERENCE, and UNKNOWN.
"""

import json
from typing import Dict, Any, Optional
from app.models import DetectiveOutput
from app.services.openai_client import OpenAIService, openai_service

SYSTEM_PROMPT = """You are the Detective on the AI Mystery Detective Team.
Role: Timeline and fact reconstruction specialist.

IMPORTANT CONSTRAINTS:
1. Your job is NOT to identify the thief.
2. Reconstruct the chronological timeline with maximum accuracy.
3. Identify all confirmed facts strictly grounded in authoritative case data.
4. Identify the critical opportunity window for the theft.
5. Identify open investigative questions that require answers.
6. For every timeline event, explicitly separate its category into:
   - FACT: Documented physical or electronic record.
   - INFERENCE: Deductions derived from statements or circumstances.
   - UNKNOWN: Missing or unverified time periods or actions.
7. NEVER invent events, times, or evidence.
"""


def run_detective_agent(case_data: Dict[str, Any], service: Optional[OpenAIService] = None) -> DetectiveOutput:
    """Executes the Detective agent on the provided case data."""
    svc = service or openai_service
    input_payload = json.dumps({
        "case": case_data.get("title"),
        "location": case_data.get("location"),
        "incident": case_data.get("incident"),
        "suspects": case_data.get("suspects"),
        "evidence": case_data.get("evidence")
    }, indent=2)

    return svc.generate_structured(
        instructions=SYSTEM_PROMPT,
        input_data=f"Analyze the following authoritative case data and reconstruct the timeline:\n\n{input_payload}",
        response_model=DetectiveOutput
    )
