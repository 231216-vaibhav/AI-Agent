# AI Mystery Detective Team: "The Vanishing Aurora Diamond"

Backend service for an AI investigative team powered by **OpenAI GPT-5** using FastAPI, the official OpenAI Python SDK, and structured Pydantic outputs.

---

## Architecture & Flow

Five specialized GPT-5 agents run sequentially to investigate the mystery of the Vanishing Aurora Diamond:

```
Frontend (Stitch Dashboard)
         │
         ▼
 POST /investigate
         │
         ▼
Investigation Orchestrator
         │
         ▼
 Agent 1: Detective (GPT-5)   --> Reconstructs timeline, confirmed facts, opportunity window
         │
         ▼
 Agent 2: Evidence (GPT-5)    --> Rigorous evaluation of Evidence A-G (distinguishes card vs personal use)
         │
         ▼
 Agent 3: Suspect (GPT-5)     --> Compares 4 suspects (motive, means, opportunity, access, alibi)
         │
         ▼
 Agent 4: Skeptic (GPT-5)     --> Challenges leading theory, exposes assumptions & contradictions
         │
         ▼
 Agent 5: Chief (GPT-5)       --> Executive synthesis with evidence citations & human review flag
         │
         ▼
  Structured JSON
         │
         ▼
Frontend Dashboard
```

---

## Tech Stack

- **Language:** Python 3.10+ (tested on Python 3.14)
- **Framework:** FastAPI
- **AI Model:** OpenAI GPT-5 (configurable via `OPENAI_MODEL`)
- **SDK:** Official OpenAI Python SDK (`openai>=1.40.0`)
- **Data Validation:** Pydantic v2
- **Environment Management:** python-dotenv
- **Server:** Uvicorn
- **Testing:** Pytest, HTTPX

---

## Project Structure

```
backend/
├── app/
│   ├── main.py              # FastAPI application & endpoints
│   ├── config.py            # Environment configuration (.env loader)
│   ├── models.py            # Pydantic models for structured agent outputs & API
│   ├── case_data.py         # Authoritative case data (facts, suspects, evidence A-G)
│   ├── orchestrator.py      # Multi-agent pipeline & sensitivity comparison
│   ├── agents/
│   │   ├── __init__.py
│   │   ├── detective.py     # Agent 1: Timeline & Fact Reconstruction
│   │   ├── evidence.py      # Agent 2: Evidence Item Evaluation
│   │   ├── suspect.py       # Agent 3: Suspect Comparative Profiling
│   │   ├── skeptic.py       # Agent 4: Critical Counter-Investigation
│   │   └── chief.py         # Agent 5: Synthesis & Evidence Citations
│   └── services/
│       ├── __init__.py
│       └── openai_client.py # Reusable OpenAI client with automatic retry
├── tests/
│   ├── __init__.py
│   ├── mock_helpers.py      # Deterministic mock responses for testing
│   ├── test_case_data.py    # Authoritative data & Evidence E filtering tests
│   ├── test_models.py       # Pydantic schema validation tests
│   ├── test_agents.py       # Individual agent unit tests
│   ├── test_orchestrator.py # Pipeline & sensitivity analysis tests
│   └── test_api.py          # FastAPI integration tests (TestClient)
├── .env.example
├── .gitignore
├── requirements.txt
└── README.md
```

---

## Environment & Security

Create a `.env` file in the `backend/` directory:

```bash
OPENAI_API_KEY=your_openai_api_key_here
OPENAI_MODEL=gpt-5
```

### Security Guarantees:
- `OPENAI_API_KEY` is **strictly kept on the backend**.
- It is never returned in API responses, never exposed to client-side scripts, and never written to logs.
- Automatic single-retry mechanism: if an API call fails or cannot be parsed, it retries once. If it still fails, HTTP 502 (Bad Gateway) is returned. AI responses are never fabricated.

---

## API Endpoints

### 1. `GET /health`
Returns backend health status, active model, and whether the API key is configured.

### 2. `GET /case`
Returns authoritative case data:
- Incident events (8:00 PM case lock, 8:20–8:24 PM blackout, 8:30 PM discovery)
- 4 Suspects: Lena Ortiz, Theo Park, Arjun Vale, Sofia Reed
- Evidence A through G

### 3. `POST /investigate`
Executes the full 5-agent investigation pipeline and returns structured JSON:
```json
{
  "case_id": "001",
  "status": "complete",
  "detective": { ... },
  "evidence": [ ... ],
  "suspects": { ... },
  "skeptic": { ... },
  "chief": {
    "leading_person_of_interest": "Arjun Vale",
    "confidence": "MEDIUM",
    "reasoning": [ ... ],
    "strongest_evidence": [ ... ],
    "evidence_citations": [
      {
        "claim": "Arjun Vale is the leading person of interest.",
        "evidence_ids": ["B", "C", "D", "E"]
      }
    ],
    "human_review_required": true
  }
}
```

### 4. `POST /investigate/modified`
Demonstrates **evidence sensitivity** by:
1. Running the pipeline with all Evidence A–G.
2. Removing **only Evidence E** (the blue velvet fibers in Arjun's folder).
3. Rerunning the exact same 5-agent pipeline without hardcoding.
4. Comparing:
   - `leading_person_of_interest`
   - `confidence`
   - `strongest_evidence`
   - `best_alternative`
   - `missing_evidence`

### 5. `POST /human-review`
Submits an in-memory review from a human supervisor:
```json
{
  "decision": "ACCEPT",
  "notes": "Approve recommendation to conduct spectrometry on fibers.",
  "next_evidence": ["Spectrometry lab results", "Archive hallway log"]
}
```
*Decisions supported:* `ACCEPT`, `REVISE`, `REJECT`.

### 6. `GET /human-review`
Retrieves all recorded human reviews stored in memory.

---

## Running the Tests

To run the complete test suite:

```bash
cd backend
pytest -v
```

---

## Running the Server

Start the development server with Uvicorn:

```bash
cd backend
uvicorn app.main:app --reload --host 0.0.0.0 --port 8000
```

Access the interactive Swagger documentation at:
`http://localhost:8000/docs`
