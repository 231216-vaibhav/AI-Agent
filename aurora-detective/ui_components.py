# -*- coding: utf-8 -*-
"""UI Components and HTML/Markdown formatters for Generic AI Mystery Detective Team.
Supports dynamic case snapshots, dynamic timeline tables, dynamic evidence cards,
Chief synthesis hero cards, dynamic evidence sensitivity comparison, and human review logs.
"""

from typing import Dict, Any, List, Optional
from models import (
    InvestigationResult,
    ComparisonResult,
    HumanReviewRecord,
    ChiefOutput,
    EvidenceItemAnalysis,
    SuspectOutput,
    DetectiveOutput,
    SkepticOutput
)


def render_header_html() -> str:
    """Renders the compact command center header with system status indicator."""
    return """
<div class="cmd-header">
    <div class="cmd-header-left">
        <div class="cmd-title-row">
            <span class="cmd-badge">AI FORENSIC ENGINE</span>
            <h1 class="cmd-title">AI MYSTERY DETECTIVE TEAM</h1>
        </div>
        <div class="cmd-case-name">Generic Multi-Agent Investigation System</div>
        <div class="cmd-subtitle">5-Agent Evidence-Based Pipeline &bull; Gemini Flash &bull; Human-in-the-Loop &bull; Dynamic Input</div>
    </div>
    <div class="cmd-header-right">
        <div class="cmd-status-indicator">
            <span class="status-pulse-dot"></span>
            <span class="status-text">SYSTEM READY</span>
        </div>
        <div class="cmd-timestamp">AUTONOMOUS MULTI-AGENT REASONING</div>
    </div>
</div>
"""


def render_case_snapshot_html(case_data: Optional[Dict[str, Any]] = None) -> str:
    """Renders 5 equal-height, readable horizontal snapshot cards dynamically from case data."""
    if not case_data:
        return """
        <div class="snapshot-grid">
            <div class="snapshot-card">
                <div class="snapshot-label">CASE STATUS</div>
                <div class="snapshot-val">Awaiting Case Input</div>
                <div class="snapshot-sub">Enter text or load demo above</div>
            </div>
            <div class="snapshot-card">
                <div class="snapshot-label">LOCATION</div>
                <div class="snapshot-val">Pending</div>
                <div class="snapshot-sub">Scene not yet ingested</div>
            </div>
            <div class="snapshot-card">
                <div class="snapshot-label">PEOPLE / ENTITIES</div>
                <div class="snapshot-val">0 Ingested</div>
                <div class="snapshot-sub">Awaiting extraction</div>
            </div>
            <div class="snapshot-card">
                <div class="snapshot-label">EVIDENCE ITEMS</div>
                <div class="snapshot-val">0 Clues</div>
                <div class="snapshot-sub">Awaiting extraction</div>
            </div>
            <div class="snapshot-card highlight-card">
                <div class="snapshot-label">OPPORTUNITY WINDOW</div>
                <div class="snapshot-val" style="color: #f59e0b;">Pending</div>
                <div class="snapshot-sub">Timeframe to be parsed</div>
            </div>
        </div>
        """

    case_name = case_data.get("case_name", "Investigation Inquiry")
    location = case_data.get("location", "UNKNOWN / NOT PROVIDED")
    suspects_count = len(case_data.get("suspects", []))
    evidence_count = len(case_data.get("evidence", []))
    window = case_data.get("critical_opportunity_window", "UNKNOWN / NOT PROVIDED")

    return f"""
<div class="snapshot-grid">
    <div class="snapshot-card">
        <div class="snapshot-label">CASE</div>
        <div class="snapshot-val">{case_name[:40]}</div>
        <div class="snapshot-sub">Active Inquiry</div>
    </div>
    <div class="snapshot-card">
        <div class="snapshot-label">LOCATION</div>
        <div class="snapshot-val">{location[:35]}</div>
        <div class="snapshot-sub">Identified Scene</div>
    </div>
    <div class="snapshot-card">
        <div class="snapshot-label">PEOPLE / SUSPECTS</div>
        <div class="snapshot-val">{suspects_count} Identified</div>
        <div class="snapshot-sub">Persons of Interest / Witnesses</div>
    </div>
    <div class="snapshot-card">
        <div class="snapshot-label">EVIDENCE</div>
        <div class="snapshot-val">{evidence_count} Clues</div>
        <div class="snapshot-sub">Extracted Observations</div>
    </div>
    <div class="snapshot-card highlight-card">
        <div class="snapshot-label">OPPORTUNITY WINDOW</div>
        <div class="snapshot-val" style="color: #f59e0b;">{window[:35]}</div>
        <div class="snapshot-sub">Critical Timeframe</div>
    </div>
</div>
"""


def render_agent_pipeline_html(step_completed: int = 0) -> str:
    """Renders the horizontal 5-agent pipeline with clear stages and readiness."""
    agents = [
        ("01 DETECTIVE", "Timeline & Facts"),
        ("02 EVIDENCE", "Clue Analysis"),
        ("03 SUSPECT", "People & Explanations"),
        ("04 SKEPTIC", "Challenge"),
        ("05 CHIEF", "Synthesis")
    ]
    cards = []
    for i, (name, duty) in enumerate(agents, start=1):
        is_done = step_completed >= i
        status_label = "✓ Completed" if is_done else "✓ Ready"
        status_class = "status-done" if is_done else "status-ready"
        card_class = "pipeline-card done" if is_done else "pipeline-card"

        cards.append(f"""
        <div class="{card_class}">
            <div class="pipeline-num-title">{name}</div>
            <div class="pipeline-duty">{duty}</div>
            <div class="pipeline-status {status_class}">● {status_label}</div>
        </div>
        """)

    return f"""
<div class="pipeline-bar">
    {'<div class="pipeline-arrow">&rarr;</div>'.join(cards)}
</div>
"""


def format_timeline_markdown(case_data: Optional[Dict[str, Any]] = None) -> str:
    """Formats the timeline table dynamically from the parsed case events."""
    if not case_data or not case_data.get("timeline"):
        return """
        <div class="table-container">
            <div style="padding: 20px; color: #94a3b8; text-align: center;">
                No timeline events parsed yet. Load a case or enter text and click <strong>RUN INVESTIGATION</strong>.
            </div>
        </div>
        """

    rows = []
    opp_window = (case_data.get("critical_opportunity_window") or "").lower()

    for ev in case_data["timeline"]:
        t_str = ev.get("time", "UNKNOWN / NOT PROVIDED")
        desc = ev.get("description", "")
        note = ev.get("note", "")

        is_opp = any(token in t_str.lower() or token in desc.lower() for token in ["blackout", "power failure", "opportunity", "missing", "window"])
        row_class = "row-highlight-opportunity" if is_opp else ""
        badge_html = f'<span class="badge-opportunity">{t_str}</span>' if is_opp else f'<strong>{t_str}</strong>'

        rows.append(f"""
        <tr class="{row_class}">
            <td style="width: 160px;">{badge_html}</td>
            <td><strong>{desc}</strong></td>
            <td>{note or 'Recorded observation.'}</td>
        </tr>
        """)

    return f"""
<div class="table-container">
<table class="cmd-table">
    <thead>
        <tr>
            <th style="width: 160px;">TIME</th>
            <th>EVENT DESCRIPTION</th>
            <th>FORENSIC SIGNIFICANCE / SOURCE</th>
        </tr>
    </thead>
    <tbody>
        {''.join(rows)}
    </tbody>
</table>
</div>
"""


def format_evidence_repository_markdown(
    case_data: Optional[Dict[str, Any]] = None,
    analyzed_evidence: Optional[List[EvidenceItemAnalysis]] = None
) -> str:
    """Formats Evidence as compact structured cards with expandable forensic breakdown."""
    if not case_data or not case_data.get("evidence"):
        return """
        <div class="evidence-grid">
            <div style="grid-column: 1 / -1; padding: 20px; color: #94a3b8; text-align: center; background: #111827; border-radius: 8px;">
                No evidence items parsed yet. Run an investigation to analyze clues.
            </div>
        </div>
        """

    analyzed_map = {e.id: e for e in analyzed_evidence} if analyzed_evidence else {}
    cards_html = []

    for item in case_data["evidence"]:
        eid = str(item.get("id", "E"))
        desc = item.get("description", "")
        key_fact = item.get("key_fact", "Extracted clue observation.")

        analysis = analyzed_map.get(eid)
        strength = analysis.strength if analysis else "MODERATE"
        classification = analysis.classification if analysis else "FACT"
        supports = analysis.supports if analysis else "Under evaluation by Evidence Agent."
        alt_exp = analysis.alternative_explanation if analysis else "Alternative explanations subject to investigation."

        cards_html.append(f"""
<div class="evidence-card">
    <div class="evidence-header">
        <span class="evidence-id-badge">{eid}</span>
        <span class="evidence-title">{desc[:60]}</span>
        <span class="evidence-strength-badge">{strength}</span>
    </div>
    <div class="evidence-obs">{desc}</div>
    <details class="evidence-details">
        <summary class="evidence-summary-btn">View Forensic Breakdown &bull; Classification: {classification}</summary>
        <div class="evidence-breakdown">
            <div><strong>Key Fact / Nuance:</strong> {key_fact}</div>
            <div><strong>Supported Hypothesis:</strong> {supports}</div>
            <div><strong>Alternative Explanation:</strong> {alt_exp}</div>
        </div>
    </details>
</div>
""")

    return f"""<div class="evidence-grid">{''.join(cards_html)}</div>"""


def format_suspect_profiles_markdown(case_data: Optional[Dict[str, Any]] = None) -> str:
    """Formats suspect / entity background cards dynamically from case data."""
    if not case_data or not case_data.get("suspects"):
        return """
        <div style="padding: 20px; color: #94a3b8; text-align: center; background: #111827; border-radius: 8px;">
            No explicit suspects or entities provided in case text.
        </div>
        """

    cards = []
    for s in case_data["suspects"]:
        name = s.get("name", "Unknown Person")
        bg = s.get("background", "")
        motive = s.get("motive", "UNKNOWN / NOT PROVIDED")
        opp = s.get("opportunity", "UNKNOWN / NOT PROVIDED")
        access = s.get("access", "UNKNOWN / NOT PROVIDED")
        alibi = s.get("alibi", "UNKNOWN / NOT PROVIDED")
        movement = s.get("movement", "")

        cards.append(f"""
<div class="suspect-profile-card">
    <div class="suspect-card-header">
        <div class="suspect-name">👤 {name}</div>
        <div class="suspect-badge">{bg or 'Entity of Interest'}</div>
    </div>
    <div class="suspect-grid-inner">
        <div><strong>Motive:</strong> {motive}</div>
        <div><strong>Opportunity:</strong> {opp}</div>
        <div><strong>Means & Access:</strong> {access}</div>
        <div><strong>Alibi Statement:</strong> {alibi}</div>
        {f'<div style="grid-column: 1 / -1;"><strong>Movement:</strong> {movement}</div>' if movement else ''}
    </div>
</div>
""")
    return f"""<div class="suspect-profiles-container">{''.join(cards)}</div>"""


def format_chief_results(chief: ChiefOutput) -> str:
    """Renders the primary CHIEF SYNTHESIS focal card with high visual clarity."""
    level_css = chief.confidence_level.replace(" ", "-")
    conf_class = f"conf-{level_css}"
    score = chief.confidence_score

    # Determine meter bar fill color
    if score <= 39:
        meter_color = "#ef4444"
    elif score <= 69:
        meter_color = "#f59e0b"
    elif score <= 84:
        meter_color = "#22c55e"
    else:
        meter_color = "#10b981"

    tier_low = "active-tier" if chief.confidence_level == "LOW" else ""
    tier_med = "active-tier" if chief.confidence_level == "MEDIUM" else ""
    tier_high = "active-tier" if chief.confidence_level == "HIGH" else ""
    tier_vhigh = "active-tier" if chief.confidence_level == "VERY HIGH" else ""

    citations_html = ""
    if chief.evidence_citations:
        c_lines = []
        for c in chief.evidence_citations:
            eids = ", ".join(f"<strong>{eid}</strong>" for eid in c.evidence_ids)
            c_lines.append(f"<li><em>\"{c.claim}\"</em> &mdash; [Cites: {eids}]</li>")
        citations_html = f"""
        <div class="citations-box">
            <div class="box-subtitle">STRUCTURED EVIDENCE CITATIONS</div>
            <ul class="citations-list">{''.join(c_lines)}</ul>
        </div>
        """

    supporting_items = "".join(f"<li>{s}</li>" for s in chief.supporting_evidence) or "<li>None recorded</li>"
    contradictory_items = "".join(f"<li>{c}</li>" for c in chief.contradictory_evidence) or "<li>None recorded</li>"
    uncertainty_items = "".join(f"<li>{u}</li>" for u in chief.unresolved_uncertainties) or "<li>None recorded</li>"
    alternative_items = "".join(f"<li>{a}</li>" for a in chief.alternative_theories) or "<li>None recorded</li>"
    next_evidence_items = "".join(f"<li>{n}</li>" for n in chief.recommended_next_evidence) or "<li>None recorded</li>"

    why_conclusion = chief.why_this_conclusion or chief.confidence_explanation
    opp_window = chief.opportunity_window or "Opportunity window cannot be precisely established from the supplied information."
    important_unc = chief.important_uncertainty or (chief.unresolved_uncertainties[0] if chief.unresolved_uncertainties else "Not established from the provided evidence.")
    final_conc = chief.final_conclusion or f"{chief.leading_person_of_interest} is currently designated based on opportunity and available evidence, but remaining uncertainties require further verification."

    return f"""
<div class="chief-main-card">
    <div class="chief-badge-bar">
        <span class="chief-kicker">CHIEF SYNTHESIS &bull; EXECUTIVE FORENSIC INVESTIGATION REPORT</span>
        <span class="chief-agent-tag">AGENT 05 &bull; CHIEF</span>
    </div>

    <!-- 1. LEADING PERSON OF INTEREST & 2. CONFIDENCE -->
    <div class="chief-hero-grid">
        <div class="chief-poi-col">
            <div class="hero-label">1. LEADING PERSON OF INTEREST / EXPLANATION</div>
            <div class="hero-poi-badge">{chief.leading_person_of_interest}</div>
            <div class="hero-forensic-sub">Designated based on evidentiary weight &bull; Not a legal judgment of guilt</div>
        </div>

        <div class="chief-score-col">
            <div class="hero-label">2. SYNTHESIS CONFIDENCE</div>
            <div class="hero-score-val">{score} <span class="score-denom">/ 100</span></div>
            <div class="confidence-badge {conf_class}">{chief.confidence_level} CONFIDENCE</div>
        </div>
    </div>

    <!-- Visual Confidence Indicator Gauge -->
    <div class="meter-box">
        <div class="meter-header-row">
            <span class="meter-title">Visual Confidence Gauge</span>
            <span class="meter-val-text">{score} / 100 ({chief.confidence_level})</span>
        </div>
        <div class="meter-track">
            <div class="meter-fill" style="width: {score}%; background: {meter_color};"></div>
            <div class="meter-divider" style="left: 40%;" title="40% Threshold"></div>
            <div class="meter-divider" style="left: 70%;" title="70% Threshold"></div>
            <div class="meter-divider" style="left: 85%;" title="85% Threshold"></div>
        </div>
        <div class="meter-labels">
            <span class="meter-tier-label {tier_low}" style="width: 40%; text-align: left;">0–39 LOW</span>
            <span class="meter-tier-label {tier_med}" style="width: 30%; text-align: left; padding-left: 6px;">40–69 MEDIUM</span>
            <span class="meter-tier-label {tier_high}" style="width: 15%; text-align: left; padding-left: 6px;">70–84 HIGH</span>
            <span class="meter-tier-label {tier_vhigh}" style="width: 15%; text-align: right;">85–100 VERY HIGH</span>
        </div>
    </div>

    <!-- 3. WHY THIS CONCLUSION? -->
    <div class="why-confidence-box">
        <div class="box-subtitle">3. WHY THIS CONCLUSION?</div>
        <div class="why-confidence-text">{why_conclusion}</div>
    </div>

    <!-- 8. OPPORTUNITY / CRITICAL WINDOW -->
    <div class="citations-box" style="border-left-color: #f59e0b; margin-bottom: 14px;">
        <div class="box-subtitle" style="color: #f59e0b;">8. OPPORTUNITY / CRITICAL WINDOW</div>
        <div style="font-size: 0.95rem; font-weight: 700; color: #ffffff; margin-top: 4px;">{opp_window}</div>
    </div>

    {citations_html}

    <!-- 4. SUPPORTING EVIDENCE vs 5. CONTRADICTORY / LIMITING EVIDENCE -->
    <div class="evidence-balance-grid">
        <div class="balance-card supporting-card">
            <div class="balance-header">
                <span class="balance-icon">✓</span>
                <span class="balance-title">4. SUPPORTING EVIDENCE</span>
            </div>
            <ul class="balance-list">{supporting_items}</ul>
        </div>

        <div class="balance-card limiting-card">
            <div class="balance-header">
                <span class="balance-icon">⚠</span>
                <span class="balance-title">5. CONTRADICTORY / LIMITING EVIDENCE</span>
            </div>
            <ul class="balance-list">{contradictory_items}</ul>
        </div>
    </div>

    <!-- 6. ALTERNATIVE EXPLANATIONS, 7. IMPORTANT UNCERTAINTY, 9. NEXT EVIDENCE NEEDED -->
    <div class="trio-grid">
        <div class="trio-card">
            <div class="trio-title">6. ALTERNATIVE EXPLANATIONS</div>
            <ul class="trio-list">{alternative_items}</ul>
        </div>
        <div class="trio-card">
            <div class="trio-title">7. IMPORTANT UNCERTAINTY</div>
            <div style="font-size: 0.85rem; color: #cbd5e1; margin-bottom: 6px; line-height: 1.4;">{important_unc}</div>
            <ul class="trio-list">{uncertainty_items}</ul>
        </div>
        <div class="trio-card">
            <div class="trio-title">9. NEXT EVIDENCE NEEDED</div>
            <ul class="trio-list">{next_evidence_items}</ul>
        </div>
    </div>

    <!-- 10. FINAL CONCLUSION -->
    <div class="why-confidence-box" style="border-left-color: #10b981; background: rgba(16, 185, 129, 0.08); margin-top: 14px;">
        <div class="box-subtitle" style="color: #10b981;">10. FINAL CONCLUSION</div>
        <div class="why-confidence-text" style="font-weight: 600;">{final_conc}</div>
    </div>

    <!-- Legal Disclaimer and Human Review Required Banner -->
    <div class="disclaimer-banner">
        <strong>⚖️ Investigative Disclaimer:</strong> Confidence reflects the strength of the available evidence relative to competing explanations. It is not a probability of guilt and does not establish legal culpability.
    </div>

    <div class="review-notice">
        ⚠️ HUMAN REVIEW: REQUIRED — Senior Investigator sign-off is mandated before proceeding with formal forensic or prosecutorial actions.
    </div>
</div>
"""


def format_detective_results(det: DetectiveOutput) -> str:
    """Formats Detective Agent detailed report."""
    md = ["### 🕵️ Agent 1: Detective — Timeline & Fact Reconstruction\n"]
    md.append(f"**Critical Opportunity Window:** `{det.critical_opportunity_window}`\n")
    md.append("#### Reconstructed Chronological Timeline:")
    for t in det.timeline:
        badge = f"`{t.category}`"
        md.append(f"- **{t.time}** [{badge}] {t.description} *(Source: {t.source})*")
    md.append("\n#### Confirmed Facts:")
    for f in det.confirmed_facts:
        md.append(f"- ✓ {f}")
    md.append("\n#### Unknowns & Evidentiary Gaps:")
    for u in det.unknowns:
        md.append(f"- ? {u}")
    md.append("\n#### Open Investigative Questions:")
    for q in det.open_questions:
        md.append(f"- ❓ {q}")
    return "\n".join(md)


def format_evidence_results(evidence_list: List[EvidenceItemAnalysis]) -> str:
    """Formats Evidence Agent detailed report."""
    if not evidence_list:
        return "*No evidence items provided in this case.*"
    md = ["### 🔬 Agent 2: Evidence Specialist — Evaluation & Strength Assessment\n"]
    md.append("| ID | Description | Classification | Strength | Supported Hypothesis | Alternative Explanation |")
    md.append("|---|---|---|---|---|---|")
    for ev in evidence_list:
        md.append(f"| **{ev.id}** | {ev.description} | `{ev.classification}` | **{ev.strength}** | {ev.supports} | {ev.alternative_explanation} |")
    md.append("\n> **Core Evidentiary Principle:** Electronic credential access does not automatically prove personal physical presence unless corroborated by independent visual/biometric confirmation.")
    return "\n".join(md)


def format_suspect_results(suspects: SuspectOutput, chief: Optional[ChiefOutput] = None) -> str:
    """Formats Suspect Profiler detailed report."""
    md = ["### 📋 Agent 3: Suspect Profiler — Comparative Evaluation\n"]
    md.append(f"**Designated Leading PERSON OF INTEREST / EXPLANATION:** `{suspects.leading_person_of_interest}`\n")
    if suspects.ranking:
        md.append(f"**Ranking:** {' > '.join(suspects.ranking)}\n")
    md.append(f"**Reasoning:** {suspects.reasoning}\n\n")

    comp = suspects.suspect_comparison
    items = comp.items() if hasattr(comp, "items") else (comp.items() if isinstance(comp, dict) else [])

    for name, s in items:
        md.append(f"#### 👤 {name}")
        md.append(f"- **Motive:** {s.motive}")
        md.append(f"- **Means & Opportunity:** {s.means} | *Opportunity:* {s.opportunity}")
        md.append(f"- **Access:** {s.access}")
        md.append(f"- **Alibi Support:** {s.alibi}")
        md.append(f"- **Evidence Against:** {', '.join(s.evidence_against) if s.evidence_against else 'None recorded'}")
        md.append(f"- **Evidence In Favor:** {', '.join(s.evidence_for) if s.evidence_for else 'None recorded'}")
        if s.contradictions:
            md.append(f"- **Contradictions:** {', '.join(s.contradictions)}")
        md.append(f"- **Assessment:** *{s.overall_assessment}*\n")
    return "\n".join(md)


def format_skeptic_results(sk: SkepticOutput) -> str:
    """Formats Skeptic Agent detailed report."""
    md = ["### 🧐 Agent 4: Skeptic — Counter-Investigation & Stress-Testing\n"]
    md.append("#### ⚠️ Unsupported Assumptions:")
    for a in sk.unsupported_assumptions:
        md.append(f"- {a}")
    md.append("\n#### ⚡ Key Contradictions:")
    for c in sk.contradictions:
        md.append(f"- {c}")
    md.append("\n#### 🔄 Viable Alternative Explanations:")
    for alt in sk.alternative_explanations:
        md.append(f"- {alt}")
    md.append("\n#### 🔍 Missing Critical Evidence:")
    for m in sk.missing_evidence:
        md.append(f"- {m}")
    md.append("\n#### ❓ Questions to Stress-Test the Theory:")
    for q in sk.questions_to_stress_test:
        md.append(f"- {q}")
    return "\n".join(md)


def format_sensitivity_html(orig: InvestigationResult, mod: InvestigationResult, comp: ComparisonResult) -> str:
    """Renders the Dynamic Evidence Sensitivity Experiment cards and explanation cleanly."""
    orig_score = orig.chief.confidence_score
    orig_level = orig.chief.confidence_level
    orig_poi = orig.chief.leading_person_of_interest

    mod_score = mod.chief.confidence_score
    mod_level = mod.chief.confidence_level
    mod_poi = mod.chief.leading_person_of_interest

    score_diff = mod_score - orig_score
    diff_sign = "+" if score_diff > 0 else ""
    diff_color = "#ef4444" if score_diff < 0 else "#22c55e" if score_diff > 0 else "#94a3b8"

    orig_strong = "<br>".join(f"• {s}" for s in comp.original_strongest) or "None recorded"
    mod_strong = "<br>".join(f"• {s}" for s in comp.modified_strongest) or "None recorded"

    removed_id = comp.removed_evidence_id or "Selected Item"
    removed_desc = comp.removed_evidence_desc or ""

    return f"""
<div class="sensitivity-shell">
    <div class="sensitivity-header-box">
        <div class="sensitivity-tag">EVIDENCE SENSITIVITY TEST</div>
        <h2 class="sensitivity-main-title">Impact of Removing Evidence {removed_id}</h2>
        <div class="sensitivity-sub">{removed_desc[:90]}</div>
    </div>

    <div class="sensitivity-cards-row">
        <div class="sens-card sens-orig">
            <div class="sens-card-label">ORIGINAL INVESTIGATION (Full Evidence)</div>
            <div class="sens-card-poi">{orig_poi}</div>
            <div class="sens-card-score">{orig_score} <span class="score-denom">/ 100</span></div>
            <div class="sens-badge sens-badge-orig">{orig_level} CONFIDENCE</div>
        </div>

        <div class="sens-diff-pill">
            <div class="diff-label">CONFIDENCE SHIFT</div>
            <div class="diff-val" style="color: {diff_color};">{diff_sign}{score_diff} POINTS</div>
            <div class="diff-sub">({orig_score} &rarr; {mod_score})</div>
        </div>

        <div class="sens-card sens-mod">
            <div class="sens-card-label">WITHOUT EVIDENCE {removed_id}</div>
            <div class="sens-card-poi">{mod_poi}</div>
            <div class="sens-card-score">{mod_score} <span class="score-denom">/ 100</span></div>
            <div class="sens-badge sens-badge-mod">{mod_level} CONFIDENCE</div>
        </div>
    </div>

    <div class="what-changed-box">
        <div class="box-subtitle">WHAT CHANGED & WHY?</div>
        <div class="what-changed-text">{comp.confidence_comparison}</div>
        <div class="what-changed-sub"><strong>Reasoning Shift:</strong> {comp.reasoning_changes}</div>
    </div>

    <details class="sensitivity-details-accordion">
        <summary class="sens-summary-btn">▼ VIEW DETAILED SENSITIVITY COMPARISON TABLE</summary>
        <div class="sens-table-wrapper">
            <table class="cmd-table">
                <thead>
                    <tr>
                        <th style="width: 180px;">DIMENSION</th>
                        <th style="width: 220px;">ORIGINAL RUN</th>
                        <th style="width: 220px;">WITHOUT EVIDENCE {removed_id}</th>
                        <th>FORENSIC INTERPRETATION</th>
                    </tr>
                </thead>
                <tbody>
                    <tr>
                        <td><strong>Person of Interest / Explanation</strong></td>
                        <td><span style="color:#f59e0b; font-weight:700;">{comp.original_poi}</span></td>
                        <td><span style="color:#f59e0b; font-weight:700;">{comp.modified_poi}</span></td>
                        <td>{comp.poi_comparison}</td>
                    </tr>
                    <tr>
                        <td><strong>Confidence Score</strong></td>
                        <td><strong>{orig_score} / 100 ({orig_level})</strong></td>
                        <td><strong>{mod_score} / 100 ({mod_level})</strong></td>
                        <td>{comp.confidence_comparison}</td>
                    </tr>
                    <tr>
                        <td><strong>Supporting Evidence</strong></td>
                        <td>{orig_strong}</td>
                        <td>{mod_strong}</td>
                        <td>{comp.strongest_evidence_comparison}</td>
                    </tr>
                </tbody>
            </table>
        </div>
    </details>
</div>
"""


def format_human_reviews_table_html(reviews: List[HumanReviewRecord]) -> str:
    """Formats human reviews in an HTML table with fixed readable column widths."""
    if not reviews:
        return """
        <div class="empty-reviews-box">
            <div style="color: #94a3b8; font-size: 0.95rem;">No supervisor reviews recorded in this session.</div>
            <div style="color: #64748b; font-size: 0.82rem; margin-top: 4px;">Submit an evaluation using the review form on the left.</div>
        </div>
        """

    rows = []
    for r in reversed(reviews):
        badge_class = f"badge-dec-{r.decision.lower()}"
        rows.append(f"""
        <tr>
            <td class="col-id"><code>{r.id}</code></td>
            <td class="col-decision"><span class="badge-decision {badge_class}">{r.decision}</span></td>
            <td class="col-notes">{r.notes}</td>
            <td class="col-evidence">{r.next_evidence or '&mdash;'}</td>
            <td class="col-time">{r.timestamp}</td>
        </tr>
        """)

    return f"""
<div class="table-container review-history-table">
<table class="cmd-table">
    <thead>
        <tr>
            <th style="width: 90px;">ID</th>
            <th style="width: 110px;">DECISION</th>
            <th>SUPERVISOR NOTES</th>
            <th style="width: 220px;">REQUESTED EVIDENCE</th>
            <th style="width: 160px;">TIMESTAMP</th>
        </tr>
    </thead>
    <tbody>
        {''.join(rows)}
    </tbody>
</table>
</div>
"""
