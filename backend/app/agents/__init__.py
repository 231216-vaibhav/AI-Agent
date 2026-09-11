from app.agents.detective import run_detective_agent
from app.agents.evidence import run_evidence_agent
from app.agents.suspect import run_suspect_agent
from app.agents.skeptic import run_skeptic_agent
from app.agents.chief import run_chief_agent

__all__ = [
    "run_detective_agent",
    "run_evidence_agent",
    "run_suspect_agent",
    "run_skeptic_agent",
    "run_chief_agent"
]
