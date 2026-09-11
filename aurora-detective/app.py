# -*- coding: utf-8 -*-
"""Gradio User Interface for AI Mystery Detective Team: Generic Multi-Agent Investigation System.
Powered by Google Gemini Flash API, Pydantic structured outputs, and python-dotenv.
Runs standalone with 'python app.py'.
"""

import os
import sys

# Ensure UTF-8 output on Windows consoles
if sys.platform == "win32":
    try:
        sys.stdout.reconfigure(encoding="utf-8")
        sys.stderr.reconfigure(encoding="utf-8")
    except Exception:
        pass

import json
import gradio as gr
from typing import Dict, Any, List, Optional, Tuple

from case_data import (
    get_case_data,
    get_modified_case_data,
    AURORA_DEMO_TEXT,
    COLLEGE_LAB_DEMO_TEXT
)
from models import (
    InvestigationResult,
    ComparisonResult,
    HumanReviewRecord,
    ChiefOutput
)
from orchestrator import orchestrator
from gemini_client import gemini_service, GeminiClientError
from ui_components import (
    render_header_html,
    render_case_snapshot_html,
    render_agent_pipeline_html,
    format_timeline_markdown,
    format_evidence_repository_markdown,
    format_suspect_profiles_markdown,
    format_chief_results,
    format_detective_results,
    format_evidence_results,
    format_suspect_results,
    format_skeptic_results,
    format_sensitivity_html,
    format_human_reviews_table_html
)

# State cache for current investigation result
current_investigation: Optional[InvestigationResult] = None

# Custom CSS for Modern AI Investigation Command Center Theme
CUSTOM_CSS = """
:root {
    --bg-main: #090d16;
    --bg-card: #111827;
    --bg-card-alt: #162238;
    --bg-highlight: #1e293b;
    --border-subtle: rgba(255, 255, 255, 0.08);
    --border-card: #1e2e4a;
    --accent-amber: #f59e0b;
    --accent-gold: #fca311;
    --accent-cyan: #38bdf8;
    --status-green: #10b981;
    --status-red: #ef4444;
    --text-primary: #f8fafc;
    --text-secondary: #94a3b8;
    --text-muted: #64748b;
}

body, .gradio-container {
    background-color: var(--bg-main) !important;
    color: var(--text-primary) !important;
    font-family: 'Inter', 'Segoe UI', system-ui, -apple-system, sans-serif !important;
    width: 98% !important;
    max-width: 1680px !important;
    margin: 0 auto !important;
    padding: 8px 14px !important;
}

.gradio-container > .main,
.gradio-container > .wrap,
.gradio-container-6-27-0 {
    width: 100% !important;
    max-width: 100% !important;
    padding: 0 !important;
}

.gradio-container .prose * {
    color: var(--text-primary);
}

/* Header */
.cmd-header {
    background: linear-gradient(135deg, #0b1329 0%, #111d3d 60%, #192a54 100%);
    border: 1px solid var(--border-card);
    border-radius: 12px;
    padding: 16px 22px;
    margin-bottom: 14px;
    display: flex;
    justify-content: space-between;
    align-items: center;
    flex-wrap: wrap;
    gap: 12px;
    box-shadow: 0 4px 20px rgba(0, 0, 0, 0.4);
}

.cmd-title-row {
    display: flex;
    align-items: center;
    gap: 10px;
}

.cmd-badge {
    background: rgba(245, 158, 11, 0.15);
    color: var(--accent-amber);
    border: 1px solid rgba(245, 158, 11, 0.4);
    font-size: 0.72rem;
    font-weight: 800;
    letter-spacing: 1px;
    padding: 3px 8px;
    border-radius: 6px;
    text-transform: uppercase;
}

.cmd-title {
    margin: 0;
    font-size: 1.4rem;
    font-weight: 800;
    color: #ffffff;
    letter-spacing: 0.5px;
}

.cmd-case-name {
    font-size: 1.1rem;
    font-weight: 700;
    color: var(--accent-amber);
    margin-top: 2px;
}

.cmd-subtitle {
    font-size: 0.83rem;
    color: var(--text-secondary);
    margin-top: 2px;
}

.cmd-header-right {
    text-align: right;
}

.cmd-status-indicator {
    display: inline-flex;
    align-items: center;
    gap: 8px;
    background: rgba(16, 185, 129, 0.12);
    border: 1px solid rgba(16, 185, 129, 0.35);
    padding: 6px 14px;
    border-radius: 20px;
}

.status-pulse-dot {
    width: 8px;
    height: 8px;
    background: var(--status-green);
    border-radius: 50%;
    box-shadow: 0 0 8px var(--status-green);
}

.status-text {
    font-size: 0.78rem;
    font-weight: 800;
    letter-spacing: 0.8px;
    color: var(--status-green);
}

.cmd-timestamp {
    font-size: 0.72rem;
    font-weight: 600;
    color: var(--text-muted);
    margin-top: 4px;
    letter-spacing: 0.6px;
}

/* Case Input Box Section */
.case-input-container {
    background: var(--bg-card);
    border: 1px solid var(--border-card);
    border-radius: 12px;
    padding: 16px 20px;
    margin-bottom: 16px;
}

.input-section-header {
    display: flex;
    justify-content: space-between;
    align-items: center;
    margin-bottom: 10px;
    flex-wrap: wrap;
    gap: 10px;
}

.input-section-title {
    font-size: 1.05rem;
    font-weight: 800;
    color: #ffffff;
    letter-spacing: 0.5px;
}

/* Primary Action Button */
button.btn-primary-investigate {
    background: linear-gradient(135deg, #f59e0b 0%, #d97706 100%) !important;
    color: #000000 !important;
    font-size: 1.05rem !important;
    font-weight: 800 !important;
    letter-spacing: 0.5px !important;
    border: none !important;
    border-radius: 10px !important;
    padding: 12px 24px !important;
    box-shadow: 0 4px 16px rgba(245, 158, 11, 0.3) !important;
    cursor: pointer !important;
    transition: all 0.2s ease !important;
}

button.btn-primary-investigate:hover {
    background: linear-gradient(135deg, #fbbf24 0%, #f59e0b 100%) !important;
    box-shadow: 0 6px 22px rgba(245, 158, 11, 0.45) !important;
    transform: translateY(-1px) !important;
}

/* Secondary Outlined Action Button */
button.btn-secondary-action {
    background: rgba(17, 24, 39, 0.8) !important;
    color: var(--accent-cyan) !important;
    font-size: 0.9rem !important;
    font-weight: 700 !important;
    letter-spacing: 0.3px !important;
    border: 1.5px solid var(--border-card) !important;
    border-radius: 8px !important;
    padding: 10px 16px !important;
    cursor: pointer !important;
    transition: all 0.2s ease !important;
}

button.btn-secondary-action:hover {
    background: rgba(56, 189, 248, 0.12) !important;
    border-color: var(--accent-cyan) !important;
    color: #ffffff !important;
}

/* Snapshot Cards */
.snapshot-grid {
    display: grid;
    grid-template-columns: repeat(auto-fit, minmax(200px, 1fr));
    gap: 12px;
    margin-bottom: 16px;
}

.snapshot-card {
    background: var(--bg-card);
    border: 1px solid var(--border-card);
    border-radius: 10px;
    padding: 12px 16px;
    display: flex;
    flex-direction: column;
    justify-content: center;
    transition: transform 0.15s ease, border-color 0.15s ease;
}

.snapshot-label {
    font-size: 0.7rem;
    font-weight: 800;
    text-transform: uppercase;
    color: var(--text-secondary);
    letter-spacing: 1px;
}

.snapshot-val {
    font-size: 1.05rem;
    font-weight: 700;
    color: #ffffff;
    margin: 4px 0 2px 0;
}

.snapshot-sub {
    font-size: 0.74rem;
    color: var(--text-muted);
}

.highlight-card {
    border-left: 3px solid var(--accent-amber) !important;
}

/* Pipeline Bar */
.pipeline-bar {
    display: flex;
    align-items: center;
    justify-content: space-between;
    gap: 8px;
    background: var(--bg-card);
    border: 1px solid var(--border-card);
    border-radius: 10px;
    padding: 10px 14px;
    margin-bottom: 16px;
    overflow-x: auto;
}

.pipeline-card {
    flex: 1;
    min-width: 140px;
    background: rgba(15, 23, 42, 0.6);
    border: 1px solid rgba(255, 255, 255, 0.05);
    border-radius: 8px;
    padding: 8px 12px;
    text-align: center;
}

.pipeline-card.done {
    background: rgba(16, 185, 129, 0.08);
    border-color: rgba(16, 185, 129, 0.4);
}

.pipeline-num-title {
    font-size: 0.8rem;
    font-weight: 800;
    color: #ffffff;
    letter-spacing: 0.5px;
}

.pipeline-duty {
    font-size: 0.72rem;
    color: var(--text-secondary);
    margin: 2px 0;
}

.pipeline-status {
    font-size: 0.7rem;
    font-weight: 700;
}

.status-ready { color: var(--accent-cyan); }
.status-done { color: var(--status-green); }

.pipeline-arrow {
    color: var(--text-muted);
    font-weight: 700;
    font-size: 1rem;
    user-select: none;
}

/* Tables */
.table-container {
    overflow-x: auto;
    border-radius: 8px;
    border: 1px solid var(--border-card);
    background: var(--bg-card);
    margin: 10px 0;
}

table.cmd-table {
    width: 100%;
    border-collapse: collapse;
    font-size: 0.88rem;
    text-align: left;
}

table.cmd-table th {
    background: #0f172a;
    color: var(--text-secondary);
    font-size: 0.74rem;
    font-weight: 800;
    text-transform: uppercase;
    letter-spacing: 0.8px;
    padding: 10px 14px;
    border-bottom: 1px solid var(--border-card);
}

table.cmd-table td {
    padding: 10px 14px;
    border-bottom: 1px solid rgba(255, 255, 255, 0.04);
    color: var(--text-primary);
    line-height: 1.45;
}

.row-highlight-opportunity {
    background: rgba(245, 158, 11, 0.08) !important;
    border-left: 3px solid var(--accent-amber);
}

.badge-opportunity {
    background: var(--accent-amber);
    color: #000000;
    font-weight: 800;
    padding: 2px 7px;
    border-radius: 4px;
    font-size: 0.76rem;
}

/* Evidence Cards */
.evidence-grid {
    display: grid;
    grid-template-columns: repeat(auto-fit, minmax(280px, 1fr));
    gap: 12px;
    margin: 10px 0;
    align-items: start;
}

.evidence-card {
    background: var(--bg-card);
    border: 1px solid var(--border-card);
    border-radius: 10px;
    padding: 14px 16px;
    display: flex;
    flex-direction: column;
}

.evidence-header {
    display: flex;
    align-items: center;
    gap: 8px;
    margin-bottom: 8px;
}

.evidence-id-badge {
    background: rgba(245, 158, 11, 0.15);
    color: var(--accent-amber);
    border: 1px solid rgba(245, 158, 11, 0.4);
    font-weight: 800;
    font-size: 0.78rem;
    padding: 2px 6px;
    border-radius: 4px;
}

.evidence-title {
    font-weight: 700;
    font-size: 0.9rem;
    color: #ffffff;
    flex: 1;
}

.evidence-strength-badge {
    font-size: 0.68rem;
    font-weight: 700;
    background: rgba(255, 255, 255, 0.08);
    color: var(--text-secondary);
    padding: 2px 6px;
    border-radius: 4px;
    text-transform: uppercase;
}

.evidence-obs {
    font-size: 0.84rem;
    color: #cbd5e1;
    line-height: 1.45;
    margin-bottom: 8px;
    flex: 1;
}

.evidence-details {
    margin-top: auto;
    border-top: 1px solid rgba(255, 255, 255, 0.06);
    padding-top: 8px;
}

.evidence-summary-btn {
    font-size: 0.74rem;
    font-weight: 700;
    color: var(--accent-cyan);
    cursor: pointer;
    user-select: none;
}

.evidence-breakdown {
    font-size: 0.8rem;
    color: var(--text-secondary);
    line-height: 1.45;
    margin-top: 8px;
    display: flex;
    flex-direction: column;
    gap: 4px;
    background: rgba(15, 23, 42, 0.6);
    padding: 8px 10px;
    border-radius: 6px;
}

/* Suspect Cards */
.suspect-profiles-container {
    display: grid;
    grid-template-columns: repeat(auto-fit, minmax(280px, 1fr));
    gap: 12px;
    margin: 10px 0;
    align-items: start;
}

.suspect-profile-card {
    background: var(--bg-card);
    border: 1px solid var(--border-card);
    border-radius: 10px;
    padding: 14px 16px;
}

.suspect-card-header {
    display: flex;
    justify-content: space-between;
    align-items: center;
    border-bottom: 1px solid rgba(255, 255, 255, 0.06);
    padding-bottom: 8px;
    margin-bottom: 10px;
}

.suspect-name {
    font-size: 1.05rem;
    font-weight: 700;
    color: #ffffff;
}

.suspect-badge {
    font-size: 0.72rem;
    color: var(--accent-amber);
    background: rgba(245, 158, 11, 0.1);
    padding: 2px 8px;
    border-radius: 4px;
}

.suspect-grid-inner {
    display: grid;
    grid-template-columns: 1fr;
    gap: 6px;
    font-size: 0.82rem;
    color: #cbd5e1;
    line-height: 1.4;
}

/* Chief Main Hero Card */
.chief-main-card {
    background: linear-gradient(145deg, #111a2e 0%, #162238 60%, #111a2e 100%);
    border: 2px solid var(--accent-amber);
    border-radius: 14px;
    padding: 22px 26px;
    margin: 16px 0;
    box-shadow: 0 8px 30px rgba(0, 0, 0, 0.5), 0 0 15px rgba(245, 158, 11, 0.12);
}

.chief-badge-bar {
    display: flex;
    justify-content: space-between;
    align-items: center;
    margin-bottom: 14px;
    border-bottom: 1px solid rgba(245, 158, 11, 0.2);
    padding-bottom: 8px;
}

.chief-kicker {
    font-size: 0.78rem;
    font-weight: 800;
    color: var(--accent-amber);
    letter-spacing: 1.2px;
    text-transform: uppercase;
}

.chief-agent-tag {
    font-size: 0.72rem;
    font-weight: 700;
    color: var(--text-secondary);
    background: rgba(255, 255, 255, 0.06);
    padding: 2px 8px;
    border-radius: 4px;
}

.chief-hero-grid {
    display: grid;
    grid-template-columns: 1fr auto;
    gap: 20px;
    align-items: center;
    margin-bottom: 16px;
}

.hero-label {
    font-size: 0.74rem;
    font-weight: 800;
    color: var(--text-secondary);
    letter-spacing: 1px;
    text-transform: uppercase;
    margin-bottom: 4px;
}

.hero-poi-badge {
    display: inline-block;
    background: linear-gradient(135deg, #f59e0b 0%, #d97706 100%);
    color: #000000;
    font-size: 1.45rem;
    font-weight: 900;
    padding: 6px 18px;
    border-radius: 8px;
    letter-spacing: 0.5px;
    box-shadow: 0 4px 12px rgba(245, 158, 11, 0.3);
}

.hero-forensic-sub {
    font-size: 0.78rem;
    color: var(--text-muted);
    margin-top: 6px;
}

.chief-score-col {
    text-align: right;
}

.hero-score-val {
    font-size: 2.6rem;
    font-weight: 900;
    color: #ffffff;
    line-height: 1;
}

.score-denom {
    font-size: 1.2rem;
    font-weight: 600;
    color: var(--text-secondary);
}

.confidence-badge {
    display: inline-block;
    padding: 4px 12px;
    border-radius: 20px;
    font-size: 0.8rem;
    font-weight: 800;
    letter-spacing: 0.5px;
    text-transform: uppercase;
    margin-top: 4px;
}

.conf-HIGH { background: var(--status-green); color: #000000; }
.conf-VERY-HIGH, .conf-VERY_HIGH { background: #10b981; color: #ffffff; }
.conf-MEDIUM { background: var(--accent-amber); color: #000000; }
.conf-LOW { background: var(--status-red); color: #ffffff; }

.meter-box {
    background: #0d1527;
    border: 1px solid var(--border-card);
    border-radius: 8px;
    padding: 12px 16px;
    margin: 14px 0;
}

.meter-header-row {
    display: flex;
    justify-content: space-between;
    align-items: center;
}

.meter-title {
    font-size: 0.78rem;
    font-weight: 800;
    text-transform: uppercase;
    color: var(--text-secondary);
    letter-spacing: 0.6px;
}

.meter-val-text {
    font-size: 0.85rem;
    font-weight: 800;
    color: var(--accent-amber);
}

.meter-track {
    height: 14px;
    background: #1e293b;
    border-radius: 7px;
    position: relative;
    overflow: hidden;
    margin: 8px 0 6px 0;
}

.meter-fill {
    height: 100%;
    border-radius: 7px;
    transition: width 0.4s ease;
    position: relative;
    z-index: 1;
}

.meter-divider {
    position: absolute;
    top: 0;
    bottom: 0;
    width: 2px;
    background: rgba(255, 255, 255, 0.28);
    z-index: 2;
    transform: translateX(-50%);
}

.meter-labels {
    display: flex;
    width: 100%;
    font-size: 0.72rem;
    font-weight: 700;
    color: var(--text-muted);
}

.meter-tier-label {
    box-sizing: border-box;
}

.meter-labels span.active-tier {
    color: var(--accent-amber);
    font-weight: 800;
}

.why-confidence-box {
    background: rgba(15, 23, 42, 0.7);
    border-left: 3px solid var(--accent-amber);
    border-radius: 6px;
    padding: 12px 16px;
    margin: 14px 0;
}

.box-subtitle {
    font-size: 0.75rem;
    font-weight: 800;
    text-transform: uppercase;
    color: var(--accent-amber);
    letter-spacing: 0.8px;
    margin-bottom: 4px;
}

.why-confidence-text {
    font-size: 0.9rem;
    color: #f1f5f9;
    line-height: 1.5;
}

.citations-box {
    background: rgba(15, 23, 42, 0.5);
    border-left: 3px solid var(--accent-cyan);
    border-radius: 6px;
    padding: 10px 16px;
    margin: 12px 0;
}

.citations-list {
    margin: 4px 0 0 0;
    padding-left: 18px;
    font-size: 0.85rem;
    color: #e2e8f0;
    line-height: 1.45;
}

.evidence-balance-grid {
    display: grid;
    grid-template-columns: repeat(auto-fit, minmax(280px, 1fr));
    gap: 14px;
    margin: 14px 0;
}

.balance-card {
    background: #0d1527;
    border-radius: 8px;
    padding: 14px 16px;
}

.supporting-card { border-left: 3px solid var(--status-green); }
.limiting-card { border-left: 3px solid var(--accent-amber); }

.balance-header {
    display: flex;
    align-items: center;
    gap: 6px;
    margin-bottom: 8px;
}

.balance-icon { font-weight: 900; font-size: 0.85rem; }
.supporting-card .balance-icon, .supporting-card .balance-title { color: var(--status-green); }
.limiting-card .balance-icon, .limiting-card .balance-title { color: var(--accent-amber); }

.balance-title {
    font-size: 0.78rem;
    font-weight: 800;
    letter-spacing: 0.8px;
    text-transform: uppercase;
}

.balance-list {
    margin: 0;
    padding-left: 18px;
    font-size: 0.85rem;
    color: #e2e8f0;
    line-height: 1.45;
}

.balance-list li { margin-bottom: 4px; }

.trio-grid {
    display: grid;
    grid-template-columns: repeat(auto-fit, minmax(240px, 1fr));
    gap: 12px;
    margin: 14px 0;
}

.trio-card {
    background: #0d1527;
    border: 1px solid var(--border-card);
    border-radius: 8px;
    padding: 12px 14px;
}

.trio-title {
    font-size: 0.75rem;
    font-weight: 800;
    color: var(--text-secondary);
    text-transform: uppercase;
    letter-spacing: 0.8px;
    margin-bottom: 6px;
    border-bottom: 1px solid rgba(255, 255, 255, 0.05);
    padding-bottom: 4px;
}

.trio-list {
    margin: 0;
    padding-left: 16px;
    font-size: 0.82rem;
    color: #cbd5e1;
    line-height: 1.4;
}

.trio-list li { margin-bottom: 3px; }

.disclaimer-banner {
    background: rgba(56, 189, 248, 0.06);
    border-left: 3px solid var(--accent-cyan);
    padding: 10px 14px;
    border-radius: 6px;
    color: #e2e8f0;
    font-size: 0.83rem;
    line-height: 1.45;
    margin: 12px 0 8px 0;
}

.review-notice {
    background: rgba(239, 68, 68, 0.1);
    border-left: 3px solid var(--status-red);
    padding: 10px 14px;
    border-radius: 6px;
    color: #fca5a5;
    font-weight: 700;
    font-size: 0.85rem;
    margin-top: 8px;
}

/* Sensitivity Section */
.sensitivity-shell {
    background: var(--bg-card);
    border: 1px solid var(--border-card);
    border-radius: 12px;
    padding: 20px 24px;
    margin: 16px 0;
}

.sensitivity-header-box {
    margin-bottom: 16px;
    border-bottom: 1px solid var(--border-card);
    padding-bottom: 10px;
}

.sensitivity-tag {
    font-size: 0.75rem;
    font-weight: 800;
    color: var(--accent-cyan);
    letter-spacing: 1px;
    text-transform: uppercase;
}

.sensitivity-main-title {
    font-size: 1.25rem;
    font-weight: 800;
    color: #ffffff;
    margin: 2px 0 4px 0;
}

.sensitivity-sub {
    font-size: 0.82rem;
    color: var(--text-secondary);
}

.sensitivity-cards-row {
    display: flex;
    align-items: center;
    gap: 14px;
    margin-bottom: 16px;
    flex-wrap: wrap;
}

.sens-card {
    flex: 1;
    min-width: 240px;
    background: #0d1527;
    border-radius: 10px;
    padding: 16px 18px;
}

.sens-orig { border-left: 4px solid var(--status-green); }
.sens-mod { border-left: 4px solid var(--accent-amber); }

.sens-card-label {
    font-size: 0.72rem;
    font-weight: 800;
    text-transform: uppercase;
    color: var(--text-secondary);
    letter-spacing: 0.8px;
}

.sens-card-poi {
    font-size: 1.15rem;
    font-weight: 800;
    color: #ffffff;
    margin: 4px 0;
}

.sens-card-score {
    font-size: 1.8rem;
    font-weight: 900;
    color: #ffffff;
    line-height: 1;
    margin-bottom: 6px;
}

.sens-badge {
    display: inline-block;
    font-size: 0.75rem;
    font-weight: 800;
    padding: 2px 10px;
    border-radius: 12px;
}

.sens-badge-orig { background: var(--status-green); color: #000000; }
.sens-badge-mod { background: var(--accent-amber); color: #000000; }

.sens-diff-pill {
    background: rgba(15, 23, 42, 0.8);
    border: 1px solid var(--border-card);
    border-radius: 10px;
    padding: 12px 18px;
    text-align: center;
    min-width: 140px;
}

.diff-label {
    font-size: 0.7rem;
    font-weight: 800;
    color: var(--text-muted);
    text-transform: uppercase;
    letter-spacing: 0.8px;
}

.diff-val {
    font-size: 1.3rem;
    font-weight: 900;
    margin: 2px 0;
}

.diff-sub {
    font-size: 0.75rem;
    color: var(--text-secondary);
}

.what-changed-box {
    background: rgba(15, 23, 42, 0.7);
    border-left: 3px solid var(--accent-cyan);
    border-radius: 6px;
    padding: 14px 16px;
    margin-bottom: 14px;
}

.what-changed-text {
    font-size: 0.88rem;
    color: #f1f5f9;
    line-height: 1.5;
    margin-top: 4px;
}

.what-changed-sub {
    font-size: 0.83rem;
    color: var(--text-secondary);
    margin-top: 8px;
    line-height: 1.45;
}

.sensitivity-details-accordion {
    border-top: 1px solid var(--border-card);
    padding-top: 10px;
}

.sens-summary-btn {
    font-size: 0.82rem;
    font-weight: 800;
    color: var(--accent-cyan);
    cursor: pointer;
    user-select: none;
}

.sens-table-wrapper { margin-top: 10px; }

/* Review Station */
.review-console-header {
    border-bottom: 1px solid var(--border-card);
    padding-bottom: 8px;
    margin-bottom: 14px;
}

.review-console-title {
    font-size: 1.15rem;
    font-weight: 800;
    color: #ffffff;
    margin: 0;
}

.review-console-sub {
    font-size: 0.82rem;
    color: var(--text-secondary);
    margin-top: 2px;
}

.badge-decision {
    display: inline-block;
    padding: 3px 8px;
    border-radius: 4px;
    font-weight: 800;
    font-size: 0.78rem;
    letter-spacing: 0.5px;
    text-transform: uppercase;
    white-space: nowrap !important;
}

.badge-dec-accept {
    background: rgba(16, 185, 129, 0.2);
    color: #34d399;
    border: 1px solid rgba(16, 185, 129, 0.5);
}

.badge-dec-revise {
    background: rgba(245, 158, 11, 0.2);
    color: #fbbf24;
    border: 1px solid rgba(245, 158, 11, 0.5);
}

.badge-dec-reject {
    background: rgba(239, 68, 68, 0.2);
    color: #f87171;
    border: 1px solid rgba(239, 68, 68, 0.5);
}

.review-history-table td.col-decision {
    min-width: 100px !important;
    white-space: nowrap !important;
}

.empty-reviews-box {
    background: #0d1527;
    border: 1px dashed var(--border-card);
    border-radius: 8px;
    padding: 24px;
    text-align: center;
}
"""


# ----------------------------------------------------
# GRADIO EVENT HANDLERS
# ----------------------------------------------------

def on_run_investigation(case_text: Optional[str] = None, progress=gr.Progress()):
    global current_investigation
    try:
        # If no input provided, default to Aurora demo data for backward compatibility
        input_data = case_text if (case_text and case_text.strip()) else get_case_data()

        res = orchestrator.run_investigation(case_input=input_data, progress_callback=progress)
        current_investigation = res
        parsed_case = res.parsed_case or get_case_data()

        pipeline_html = render_agent_pipeline_html(5)
        snapshot_html = render_case_snapshot_html(parsed_case)
        timeline_html = format_timeline_markdown(parsed_case)
        evidence_html = format_evidence_repository_markdown(parsed_case, res.evidence)
        suspect_html = format_suspect_profiles_markdown(parsed_case)

        det_md = format_detective_results(res.detective)
        ev_md = format_evidence_results(res.evidence)
        sus_md = format_suspect_results(res.suspects, res.chief)
        sk_md = format_skeptic_results(res.skeptic)
        chief_html = format_chief_results(res.chief)

        # Build dropdown options for evidence sensitivity removal
        evidence_choices = []
        for ev in parsed_case.get("evidence", []):
            eid = str(ev.get("id", "E"))
            desc = str(ev.get("description", ""))[:45]
            evidence_choices.append((f"Evidence {eid}: {desc}", eid))

        first_choice_val = evidence_choices[0][1] if evidence_choices else None
        dropdown_update = gr.update(choices=evidence_choices, value=first_choice_val)

        return (
            pipeline_html,
            det_md,
            ev_md,
            sus_md,
            sk_md,
            chief_html,
            gr.update(visible=True),  # 6: results_container
            "",                       # 7: error_box
            snapshot_html,            # 8: snapshot_display
            timeline_html,            # 9: timeline_display
            evidence_html,            # 10: evidence_display
            suspect_html,             # 11: suspect_display
            dropdown_update           # 12: evidence_dropdown
        )
    except Exception as exc:
        err_msg = f"❌ **Investigation Error:** {str(exc)}"
        return (
            render_agent_pipeline_html(0),
            "", "", "", "", "",
            gr.update(visible=False), # 6: results_container
            err_msg,                  # 7: error_box
            render_case_snapshot_html(None),
            format_timeline_markdown(None),
            format_evidence_repository_markdown(None),
            format_suspect_profiles_markdown(None),
            gr.update(choices=[])
        )


def on_run_sensitivity_experiment(
    case_text: Optional[str] = None,
    selected_evidence_id: Optional[str] = None,
    progress=gr.Progress()
):
    global current_investigation
    try:
        input_data = case_text if (case_text and case_text.strip()) else get_case_data()

        orig, mod, comp = orchestrator.run_sensitivity_experiment(
            case_input=input_data,
            evidence_id_to_remove=selected_evidence_id,
            original_result=current_investigation,
            progress_callback=progress
        )
        current_investigation = orig
        comp_html = format_sensitivity_html(orig, mod, comp)
        return comp_html, gr.update(visible=True), ""
    except Exception as exc:
        err_msg = f"❌ **Sensitivity Test Error:** {str(exc)}"
        return "", gr.update(visible=False), err_msg


def on_load_aurora_demo():
    return AURORA_DEMO_TEXT


def on_load_college_demo():
    return COLLEGE_LAB_DEMO_TEXT


def on_submit_human_review(decision: str, notes: str, next_evidence: str):
    if not notes or not notes.strip():
        return format_human_reviews_table_html(orchestrator.get_human_reviews()), "⚠️ Please provide supervisor notes."
    if not decision:
        return format_human_reviews_table_html(orchestrator.get_human_reviews()), "⚠️ Please select a decision (ACCEPT, REVISE, REJECT)."

    orchestrator.record_human_review(decision, notes, next_evidence)
    return format_human_reviews_table_html(orchestrator.get_human_reviews()), f"✓ Recorded review with decision '{decision}'."


# ----------------------------------------------------
# BUILD GRADIO BLOCKS APP
# ----------------------------------------------------

def build_app():
    with gr.Blocks(title="AI Mystery Detective Team — Generic Investigation System") as demo:
        # 1. Header
        gr.HTML(render_header_html())

        # 2. Case Input Section (Free-form Natural Language Input)
        with gr.Column(elem_classes=["case-input-container"]):
            with gr.Row(elem_classes=["input-section-header"]):
                gr.Markdown("### 📝 NEW INVESTIGATION: Enter Case Scenario")
                with gr.Row():
                    load_aurora_btn = gr.Button("📂 LOAD AURORA DEMO", variant="secondary", elem_classes=["btn-secondary-action"], size="sm")
                    load_college_btn = gr.Button("💻 LOAD COLLEGE LAB DEMO", variant="secondary", elem_classes=["btn-secondary-action"], size="sm")

            case_input_box = gr.Textbox(
                label="Case Description / Mystery Details",
                placeholder="Enter or paste any investigation case in free-form natural language.\nExample: 'A laptop disappeared from a college computer laboratory between 2 PM and 4 PM. Three students had access...'",
                lines=4,
                max_lines=8,
                value=""
            )

            with gr.Row(elem_classes=["action-bar-row"]):
                investigate_btn = gr.Button(
                    "🔍 RUN INVESTIGATION",
                    variant="primary",
                    elem_classes=["btn-primary-investigate"],
                    scale=3
                )

        # Error notification banner
        error_box = gr.Markdown("", visible=False)

        # 3. Dynamic Case Snapshot Dashboard
        snapshot_display = gr.HTML(render_case_snapshot_html(None))

        # 4. Agent Pipeline Visual Progress
        pipeline_status_html = gr.HTML(render_agent_pipeline_html(0))

        # 5. Case Reference Tabs (Dynamic Timeline, Evidence, Suspects)
        with gr.Tabs():
            with gr.TabItem("🕒 Case Timeline"):
                timeline_display = gr.HTML(format_timeline_markdown(None))

            with gr.TabItem("📦 Evidence Repository"):
                evidence_display = gr.HTML(format_evidence_repository_markdown(None))

            with gr.TabItem("👥 Persons & Entities"):
                suspect_display = gr.HTML(format_suspect_profiles_markdown(None))

        # 6. Investigation Results Container (Chief is visual focal point)
        with gr.Column(visible=False) as results_container:
            # Chief Synthesis Main Card
            chief_display = gr.HTML("")

            # Collapsible Detailed Agent Reports (collapsed by default)
            with gr.Accordion("▼ VIEW DETAILED AGENT REPORTS (Detective, Evidence, Suspects, Skeptic)", open=False):
                with gr.Tabs():
                    with gr.TabItem("🕵️ 01 Detective (Timeline & Facts)"):
                        detective_raw_display = gr.Markdown("")

                    with gr.TabItem("🔬 02 Evidence (Probative Analysis)"):
                        evidence_raw_display = gr.Markdown("")

                    with gr.TabItem("📋 03 Suspects (Comparative Profiling)"):
                        suspect_raw_display = gr.Markdown("")

                    with gr.TabItem("🧐 04 Skeptic (Stress-Testing & Gaps)"):
                        skeptic_raw_display = gr.Markdown("")

        # 7 & 8. Bottom Action Area (Side-by-side row to maximize screen width & eliminate empty spaces)
        with gr.Row():
            with gr.Column(scale=1, elem_classes=["case-input-container"]):
                gr.Markdown("### 🧪 DYNAMIC EVIDENCE SENSITIVITY TEST")
                gr.Markdown("Test how conclusion and confidence shift when a specific clue is omitted.")
                with gr.Row():
                    evidence_dropdown = gr.Dropdown(
                        label="SELECT EVIDENCE TO REMOVE",
                        choices=[],
                        value=None,
                        scale=2
                    )
                    sensitivity_btn = gr.Button(
                        "🧪 REMOVE EVIDENCE & RUN AGAIN",
                        variant="secondary",
                        elem_classes=["btn-secondary-action"],
                        scale=1
                    )
                sensitivity_display = gr.HTML("")

            with gr.Column(scale=1, elem_classes=["case-input-container"]):
                gr.HTML("""
                <div class="review-console-header">
                    <h3 class="review-console-title">✍️ HUMAN SUPERVISOR REVIEW CONSOLE</h3>
                    <div class="review-console-sub">AI recommendations require human validation before operational sign-off.</div>
                </div>
                """)
                decision_radio = gr.Radio(
                    choices=["ACCEPT", "REVISE", "REJECT"],
                    label="Review Decision",
                    value="ACCEPT"
                )
                notes_input = gr.Textbox(
                    label="Supervisor Investigative Notes",
                    placeholder="E.g., Concur with Chief findings. Authorize fingerprint matching and verify logs.",
                    lines=2
                )
                next_evidence_input = gr.Textbox(
                    label="Next Evidence / Investigative Action Requested",
                    placeholder="E.g., Spectrometry analysis; badge log audit.",
                    lines=1
                )
                submit_review_btn = gr.Button("Submit Review Decision", variant="primary")
                review_feedback = gr.Markdown("")
                review_history_display = gr.HTML(format_human_reviews_table_html([]))

        # Event Wiring
        load_aurora_btn.click(
            fn=on_load_aurora_demo,
            inputs=[],
            outputs=[case_input_box]
        )

        load_college_btn.click(
            fn=on_load_college_demo,
            inputs=[],
            outputs=[case_input_box]
        )

        investigate_btn.click(
            fn=on_run_investigation,
            inputs=[case_input_box],
            outputs=[
                pipeline_status_html,
                detective_raw_display,
                evidence_raw_display,
                suspect_raw_display,
                skeptic_raw_display,
                chief_display,
                results_container,
                error_box,
                snapshot_display,
                timeline_display,
                evidence_display,
                suspect_display,
                evidence_dropdown
            ]
        )

        sensitivity_btn.click(
            fn=on_run_sensitivity_experiment,
            inputs=[case_input_box, evidence_dropdown],
            outputs=[
                sensitivity_display,
                results_container,
                error_box
            ]
        )

        submit_review_btn.click(
            fn=on_submit_human_review,
            inputs=[decision_radio, notes_input, next_evidence_input],
            outputs=[review_history_display, review_feedback]
        )

    return demo


if __name__ == "__main__":
    app = build_app()
    server_name = os.getenv("GRADIO_SERVER_NAME", "0.0.0.0")
    port = int(os.getenv("PORT", os.getenv("GRADIO_SERVER_PORT", "7860")))
    app.launch(server_name=server_name, server_port=port, css=CUSTOM_CSS)
