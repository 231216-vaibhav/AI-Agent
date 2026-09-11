# -*- coding: utf-8 -*-
"""Investigation Orchestrator.
Sequentially executes the 5 Gemini Flash AI Agents on ANY supplied case:
Case Parsing -> Detective -> Evidence -> Suspect -> Skeptic -> Chief.
Also handles Dynamic Evidence Sensitivity Testing and In-Memory Human Reviews.
"""

import uuid
import logging
import concurrent.futures
from datetime import datetime, timezone
from typing import Dict, Any, Optional, List, Tuple, Union
from copy import deepcopy

from case_data import parse_case_input, get_case_data
from models import (
    InvestigationResult,
    ComparisonResult,
    HumanReviewRecord
)
from agents.detective import run_detective_agent
from agents.evidence import run_evidence_agent
from agents.suspect import run_suspect_agent
from agents.skeptic import run_skeptic_agent
from agents.chief import run_chief_agent
from gemini_client import GeminiService, gemini_service

logger = logging.getLogger("aurora.orchestrator")


class Orchestrator:
    def __init__(self, service: Optional[GeminiService] = None):
        self.service = service or gemini_service
        self.human_reviews: List[HumanReviewRecord] = []

    def run_investigation(
        self,
        case_input: Optional[Union[Dict[str, Any], str]] = None,
        progress_callback: Optional[Any] = None
    ) -> InvestigationResult:
        """Executes the full 5-agent sequential investigation pipeline on any case."""
        # 0. Ingest and parse case data
        if progress_callback:
            progress_callback(0.05, desc="Parsing and structuring investigation case data...")

        if case_input is None:
            active_case = get_case_data()
        else:
            active_case = parse_case_input(case_input, service=self.service)

        case_name = active_case.get("case_name", "Investigation Inquiry")
        logger.info("Starting Generic AI Investigation pipeline for: %s", case_name)

        # 1. Detective Agent
        if progress_callback:
            progress_callback(0.2, desc="Agent 1: Detective reconstructing timeline & facts...")
        detective_out = run_detective_agent(active_case, service=self.service)

        # 2 & 3. Evidence & Suspect Agents (Concurrent execution for speed)
        if progress_callback:
            progress_callback(0.45, desc="Agents 2 & 3: Evidence & Suspect analyzing concurrently...")
        with concurrent.futures.ThreadPoolExecutor(max_workers=2) as executor:
            ev_future = executor.submit(run_evidence_agent, active_case, detective_out, self.service)
            sus_future = executor.submit(run_suspect_agent, active_case, detective_out, None, self.service)
            evidence_out = ev_future.result()
            suspect_out = sus_future.result()

        # 4. Skeptic Agent
        if progress_callback:
            progress_callback(0.8, desc="Agent 4: Skeptic stress-testing the leading theory...")
        skeptic_out = run_skeptic_agent(active_case, detective_out, evidence_out, suspect_out, service=self.service)

        # 5. Chief Agent
        if progress_callback:
            progress_callback(0.95, desc="Agent 5: Chief synthesizing complete investigation...")
        chief_out = run_chief_agent(active_case, detective_out, evidence_out, suspect_out, skeptic_out, service=self.service)

        if progress_callback:
            progress_callback(1.0, desc="Investigation Complete!")

        return InvestigationResult(
            case_name=case_name,
            detective=detective_out,
            evidence=evidence_out,
            suspects=suspect_out,
            skeptic=skeptic_out,
            chief=chief_out,
            parsed_case=active_case
        )

    def run_sensitivity_experiment(
        self,
        case_input: Optional[Union[Dict[str, Any], str]] = None,
        evidence_id_to_remove: Optional[str] = None,
        original_result: Optional[InvestigationResult] = None,
        progress_callback: Optional[Any] = None
    ) -> Tuple[InvestigationResult, InvestigationResult, ComparisonResult]:
        """Runs dynamic evidence sensitivity testing by comparing the baseline case
        against a fresh rerun omitting a specific selected evidence item.
        """
        logger.info("Starting Dynamic Evidence Sensitivity Test...")

        # 1. Ensure original run exists
        if original_result is None:
            if progress_callback:
                progress_callback(0.1, desc="Running Baseline Investigation...")
            original_result = self.run_investigation(case_input, progress_callback=None)

        orig_case = original_result.parsed_case or parse_case_input(case_input, service=self.service)

        # 2. Determine which evidence item to remove
        avail_evidence = orig_case.get("evidence", [])
        avail_ids = [e["id"] for e in avail_evidence]

        target_id = evidence_id_to_remove
        if not target_id or target_id not in avail_ids:
            # Pick first available or 'E' if present
            if "E" in avail_ids:
                target_id = "E"
            elif avail_ids:
                target_id = avail_ids[0]
            else:
                target_id = "NONE"

        removed_desc = "Specified evidence item"
        for ev in avail_evidence:
            if ev["id"] == target_id:
                removed_desc = ev.get("description", "")
                break

        # 3. Create modified case omitting strictly the target evidence item
        modified_case = deepcopy(orig_case)
        modified_case["evidence"] = [e for e in modified_case.get("evidence", []) if e["id"] != target_id]

        if progress_callback:
            progress_callback(0.5, desc=f"Rerunning 5-Agent Pipeline WITHOUT Evidence {target_id}...")
        modified_result = self.run_investigation(modified_case, progress_callback=None)

        # 4. Perform dynamic sensitivity comparison
        orig_chief = original_result.chief
        mod_chief = modified_result.chief

        orig_score = orig_chief.confidence_score
        mod_score = mod_chief.confidence_score
        score_change = mod_score - orig_score

        orig_conf_str = f"{orig_score} / 100 ({orig_chief.confidence_level})"
        mod_conf_str = f"{mod_score} / 100 ({mod_chief.confidence_level})"

        # Dynamic POI Comparison
        if orig_chief.leading_person_of_interest == mod_chief.leading_person_of_interest:
            poi_comp = (
                f"Both analyses designate {orig_chief.leading_person_of_interest} as the leading PERSON OF INTEREST / explanation. "
                f"However, with Evidence {target_id} omitted, the corroborating evidentiary weight is shifted."
            )
        else:
            poi_comp = (
                f"Designation shifted from {orig_chief.leading_person_of_interest} to "
                f"{mod_chief.leading_person_of_interest} when Evidence {target_id} was removed."
            )

        # Dynamic Confidence Comparison
        if score_change < 0:
            conf_comp = (
                f"Confidence decreased by {abs(score_change)} points (from {orig_score}/100 [{orig_chief.confidence_level}] "
                f"to {mod_score}/100 [{mod_chief.confidence_level}]). Removing Evidence {target_id} ({removed_desc[:60]}...) "
                f"weakens the evidentiary nexus and elevates the plausibility of competing alternative explanations."
            )
        elif score_change == 0:
            conf_comp = (
                f"Confidence remained unchanged at {orig_score}/100 ({orig_chief.confidence_level}). "
                f"Even without Evidence {target_id}, the remaining evidence was assessed as maintaining equivalent relative priority."
            )
        else:
            conf_comp = (
                f"Confidence shifted from {orig_score}/100 ({orig_chief.confidence_level}) "
                f"to {mod_score}/100 ({mod_chief.confidence_level}) (+{score_change} points)."
            )

        strongest_comp = (
            f"Original baseline incorporates Evidence {target_id}. In the modified run, "
            f"the synthesis must rely strictly on the remaining {len(modified_case['evidence'])} evidence items."
        )

        reasoning_comp = (
            f"Omitting Evidence {target_id} tests evidentiary sensitivity: without this clue, "
            f"gaps highlighted by the Skeptic become more prominent and require additional corroboration."
        )

        comparison = ComparisonResult(
            removed_evidence_id=str(target_id),
            removed_evidence_desc=removed_desc,
            original_poi=orig_chief.leading_person_of_interest,
            modified_poi=mod_chief.leading_person_of_interest,
            poi_comparison=poi_comp,
            original_score=orig_score,
            modified_score=mod_score,
            score_change=score_change,
            original_confidence=orig_conf_str,
            modified_confidence=mod_conf_str,
            confidence_comparison=conf_comp,
            original_strongest=orig_chief.supporting_evidence,
            modified_strongest=mod_chief.supporting_evidence,
            strongest_evidence_comparison=strongest_comp,
            reasoning_changes=reasoning_comp
        )

        if progress_callback:
            progress_callback(1.0, desc="Sensitivity Analysis Complete!")

        return original_result, modified_result, comparison

    def record_human_review(self, decision: str, notes: str, next_evidence: str) -> HumanReviewRecord:
        """Stores a human supervisor review in memory."""
        record = HumanReviewRecord(
            id=f"REV-{uuid.uuid4().hex[:8].upper()}",
            decision=decision,  # type: ignore
            notes=notes.strip(),
            next_evidence=next_evidence.strip(),
            timestamp=datetime.now(timezone.utc).strftime("%Y-%m-%d %H:%M:%S UTC")
        )
        self.human_reviews.append(record)
        logger.info("Recorded human review %s: Decision=%s", record.id, record.decision)
        return record

    def get_human_reviews(self) -> List[HumanReviewRecord]:
        """Returns the list of in-memory human review records."""
        return list(self.human_reviews)


# Global orchestrator instance
orchestrator = Orchestrator()
