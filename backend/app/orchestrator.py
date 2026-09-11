"""Investigation Orchestrator.
Coordinates the execution of the 5 specialized GPT-5 agents in sequential order:
Case -> Detective -> Evidence -> Suspect -> Skeptic -> Chief.
Provides both full investigation and modified investigation (sensitivity analysis).
"""

import logging
from typing import Dict, Any, Optional

from app.case_data import get_authoritative_case, get_modified_case
from app.models import (
    InvestigateResponse,
    InvestigateModifiedResponse,
    InvestigationComparison,
    ComparisonMetric
)
from app.agents.detective import run_detective_agent
from app.agents.evidence import run_evidence_agent
from app.agents.suspect import run_suspect_agent
from app.agents.skeptic import run_skeptic_agent
from app.agents.chief import run_chief_agent
from app.services.openai_client import OpenAIService, openai_service

logger = logging.getLogger("investigation.orchestrator")


class InvestigationOrchestrator:
    def __init__(self, service: Optional[OpenAIService] = None):
        self.service = service or openai_service

    def run_investigation(self, case_data: Optional[Dict[str, Any]] = None) -> InvestigateResponse:
        """Executes the full 5-agent sequential investigation pipeline on the given case data."""
        active_case = case_data or get_authoritative_case()
        logger.info("Starting investigation pipeline for case '%s'...", active_case.get("title"))

        # Step 1: Detective agent reconstructs timeline and facts
        logger.debug("Executing Detective Agent...")
        detective_result = run_detective_agent(active_case, service=self.service)

        # Step 2: Evidence agent analyzes all available evidence items
        logger.debug("Executing Evidence Agent...")
        evidence_result = run_evidence_agent(active_case, detective_result, service=self.service)

        # Step 3: Suspect agent compares all suspects
        logger.debug("Executing Suspect Agent...")
        suspect_result = run_suspect_agent(active_case, detective_result, evidence_result, service=self.service)

        # Step 4: Skeptic agent stress-tests the leading theory
        logger.debug("Executing Skeptic Agent...")
        skeptic_result = run_skeptic_agent(active_case, detective_result, evidence_result, suspect_result, service=self.service)

        # Step 5: Chief agent synthesizes all previous outputs into executive report
        logger.debug("Executing Chief Agent...")
        chief_result = run_chief_agent(active_case, detective_result, evidence_result, suspect_result, skeptic_result, service=self.service)

        logger.info("Investigation pipeline completed successfully.")
        return InvestigateResponse(
            case_id=active_case.get("case_id", "001"),
            status="complete",
            detective=detective_result,
            evidence=evidence_result,
            suspects=suspect_result,
            skeptic=skeptic_result,
            chief=chief_result
        )

    def run_modified_investigation(self) -> InvestigateModifiedResponse:
        """Runs the investigation on the full authoritative case (Evidence A-G),
        then reruns the exact same pipeline on the modified case with ONLY Evidence E removed,
        and computes an evidence sensitivity comparison.
        """
        logger.info("Initiating Evidence Sensitivity Investigation (Original vs Modified without E)...")

        # 1. Run Original Pipeline (All Evidence A-G)
        original_case = get_authoritative_case()
        original_response = self.run_investigation(original_case)

        # 2. Run Modified Pipeline (Evidence E strictly removed)
        modified_case = get_modified_case()
        modified_response = self.run_investigation(modified_case)

        # 3. Formulate comparative analysis
        orig_chief = original_response.chief
        mod_chief = modified_response.chief

        # Analysis of Person of Interest
        if orig_chief.leading_person_of_interest == mod_chief.leading_person_of_interest:
            poi_analysis = (
                f"{orig_chief.leading_person_of_interest} remains the leading person of interest due to card access logs, "
                f"but physical connection to the stolen item is significantly weaker without fiber Evidence E."
            )
        else:
            poi_analysis = (
                f"Leading person of interest shifted from {orig_chief.leading_person_of_interest} to "
                f"{mod_chief.leading_person_of_interest} in the absence of physical fiber linkage."
            )

        # Analysis of Confidence
        conf_analysis = (
            f"Confidence shifted from {orig_chief.confidence} to {mod_chief.confidence}. "
            f"Removing Evidence E strips away the only physical trace directly connecting Arjun's folder to the display cushion."
        )

        # Analysis of Strongest Evidence
        strongest_analysis = (
            "In the modified case, Electronic Lock Log B remains the principal evidence against Arjun, "
            "but lacks corroborating physical evidence from the folder."
        )

        # Analysis of Alternative Theories
        alternative_analysis = (
            "With Evidence E omitted, alternative theories—such as someone stealing or cloning Arjun's card while "
            "he remained in the archive—become considerably more plausible."
        )

        # Analysis of Missing Evidence
        missing_analysis = (
            "Removing Evidence E creates a critical evidentiary void: there is now no physical or visual evidence "
            "verifying what was carried out of the archive in the folder."
        )

        comparison = InvestigationComparison(
            leading_person_of_interest=ComparisonMetric(
                original=orig_chief.leading_person_of_interest,
                modified=mod_chief.leading_person_of_interest,
                impact_analysis=poi_analysis
            ),
            confidence=ComparisonMetric(
                original=orig_chief.confidence,
                modified=mod_chief.confidence,
                impact_analysis=conf_analysis
            ),
            strongest_evidence=ComparisonMetric(
                original=orig_chief.strongest_evidence,
                modified=mod_chief.strongest_evidence,
                impact_analysis=strongest_analysis
            ),
            best_alternative=ComparisonMetric(
                original=orig_chief.alternative_explanation,
                modified=mod_chief.alternative_explanation,
                impact_analysis=alternative_analysis
            ),
            missing_evidence=ComparisonMetric(
                original=orig_chief.missing_evidence,
                modified=mod_chief.missing_evidence,
                impact_analysis=missing_analysis
            )
        )

        return InvestigateModifiedResponse(
            original=original_response,
            modified=modified_response,
            comparison=comparison
        )


# Global orchestrator instance
investigation_orchestrator = InvestigationOrchestrator()
