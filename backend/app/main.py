"""FastAPI application for AI Mystery Detective Team: "The Vanishing Aurora Diamond".
Exposes endpoints for case facts, five-agent investigation, evidence sensitivity analysis,
and human investigator reviews.
"""

import uuid
import logging
from datetime import datetime, timezone
from typing import List, Dict, Any

from fastapi import FastAPI, HTTPException, Request, status
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse

from app.config import settings
from app.case_data import get_authoritative_case
from app.models import (
    InvestigateResponse,
    InvestigateModifiedResponse,
    HumanReviewInput,
    HumanReviewRecord
)
from app.orchestrator import investigation_orchestrator
from app.services.openai_client import OpenAIClientError

# Setup logging
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [%(levelname)s] %(name)s: %(message)s"
)
logger = logging.getLogger("investigation.api")

app = FastAPI(
    title="AI Mystery Detective Team: The Vanishing Aurora Diamond",
    description="Multi-agent investigative backend powered by OpenAI GPT-5",
    version="1.0.0"
)

# Enable CORS for external dashboards (e.g. Stitch frontend)
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# In-memory human review store
in_memory_reviews: List[HumanReviewRecord] = []


@app.exception_handler(OpenAIClientError)
async def openai_client_exception_handler(request: Request, exc: OpenAIClientError):
    """Handles OpenAI API failures, returning HTTP 502 without exposing sensitive keys."""
    logger.error("OpenAI Client Error during request to %s: %s", request.url.path, str(exc))
    return JSONResponse(
        status_code=status.HTTP_502_BAD_GATEWAY,
        content={"detail": str(exc), "error_type": "OpenAIClientError"}
    )


@app.get("/health", tags=["System"])
async def health_check() -> Dict[str, Any]:
    """Health check endpoint returning backend status and active model."""
    return {
        "status": "healthy",
        "service": "AI Mystery Detective Backend",
        "model": settings.OPENAI_MODEL,
        "api_key_configured": settings.is_api_key_set()
    }


@app.get("/case", tags=["Case Data"])
async def get_case() -> Dict[str, Any]:
    """Returns the complete authoritative case facts, suspects, and evidence A-G."""
    return get_authoritative_case()


@app.post("/investigate", response_model=InvestigateResponse, tags=["Investigation"])
async def run_investigate() -> InvestigateResponse:
    """Executes the complete 5-agent investigation pipeline on the authoritative case:
    Detective -> Evidence -> Suspect -> Skeptic -> Chief.
    """
    logger.info("Received request for POST /investigate")
    return investigation_orchestrator.run_investigation()


@app.post("/investigate/modified", response_model=InvestigateModifiedResponse, tags=["Investigation"])
async def run_investigate_modified() -> InvestigateModifiedResponse:
    """Runs original investigation (Evidence A-G), then reruns pipeline without Evidence E,
    and returns direct comparison demonstrating evidence sensitivity.
    """
    logger.info("Received request for POST /investigate/modified")
    return investigation_orchestrator.run_modified_investigation()


@app.post("/human-review", response_model=HumanReviewRecord, tags=["Human Review"])
async def submit_human_review(review_input: HumanReviewInput) -> HumanReviewRecord:
    """Submits a human investigator review (ACCEPT, REVISE, REJECT) stored in memory."""
    record = HumanReviewRecord(
        id=f"REV-{uuid.uuid4().hex[:8].upper()}",
        decision=review_input.decision,
        notes=review_input.notes,
        next_evidence=review_input.next_evidence,
        timestamp=datetime.now(timezone.utc).isoformat()
    )
    in_memory_reviews.append(record)
    logger.info("Logged human review %s: Decision=%s", record.id, record.decision)
    return record


@app.get("/human-review", response_model=List[HumanReviewRecord], tags=["Human Review"])
async def get_human_reviews() -> List[HumanReviewRecord]:
    """Retrieves all human review records currently stored in memory."""
    return in_memory_reviews
