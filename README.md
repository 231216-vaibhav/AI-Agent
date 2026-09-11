# 🔍 AI Case Solver: Multi-Agent Mystery Investigation System

> **"The Vanishing Aurora Diamond"** — An autonomous, multi-agent AI investigative pipeline that rigorously analyzes crime scenes, reconstructs timelines, evaluates evidence, profiles suspects, challenges cognitive biases, and synthesizes conclusions with strict evidence citation.

[![Live Demo](https://img.shields.io/badge/🚀_Live_Demo-ai--agent--31b3.onrender.com-00C7B7?style=for-the-badge&logo=render&logoColor=white)](https://ai-agent-31b3.onrender.com/)

[![FastAPI](https://img.shields.io/badge/FastAPI-0.115+-009688?style=flat&logo=fastapi&logoColor=white)](https://fastapi.tiangolo.com)
[![Python](https://img.shields.io/badge/Python-3.10+-3776AB?style=flat&logo=python&logoColor=white)](https://www.python.org/)
[![Pydantic](https://img.shields.io/badge/Pydantic-v2-E92063?style=flat&logo=pydantic&logoColor=white)](https://docs.pydantic.dev/)
[![Google Gemini](https://img.shields.io/badge/Google-Gemini-4285F4?style=flat&logo=google&logoColor=white)](https://deepmind.google/technologies/gemini/)
[![OpenAI](https://img.shields.io/badge/OpenAI-GPT--5-412991?style=flat&logo=openai&logoColor=white)](https://openai.com/)

> 🌐 **Live Interactive App:** [**https://ai-agent-31b3.onrender.com/**](https://ai-agent-31b3.onrender.com/)

---

## 🏛️ Case Brief: "The Vanishing Aurora Diamond"

- **Location:** Grand Gallery, Northbridge Museum
- **The Incident:**
  - **8:00 PM:** Aurora Diamond confirmed locked inside battery-backed display case.
  - **8:20 PM – 8:24 PM:** Museum-wide power failure (**Critical Opportunity Window**).
  - **8:30 PM:** Diamond discovered missing; glass intact with electronic lock opened.
- **Suspects:**
  - **Lena Ortiz:** Chief Archivist; restarted backup generator during blackout; crossed courtyard earlier.
  - **Theo Park:** Guest Speaker; verified alibi on stage under continuous audience camera.
  - **Arjun Vale:** Curatorial Assistant with large debt; keycard opened display case at 8:23 PM; seen with catalogue folder at 8:25 PM.
  - **Sofia Reed:** Investigative Journalist; spoke with guests in lobby during blackout.

---

## 🤖 Multi-Agent Architecture

Five specialized AI agents run sequentially, each enforcing a strict role, bounded context, and structured output schema:

```text
                           Case Data / Evidence Input
                                       │
                                       ▼
 ┌───────────────────────────────────────────────────────────────────────────┐
 │ 1. Detective Agent   → Reconstructs timeline, facts, and critical window  │
 ├───────────────────────────────────────────────────────────────────────────┤
 │ 2. Evidence Agent    → Rigorous evaluation of Evidence items (Fact vs Clue)│
 ├───────────────────────────────────────────────────────────────────────────┤
 │ 3. Suspect Agent     → Profiles Motive, Means, Opportunity, Access, Alibi │
 ├───────────────────────────────────────────────────────────────────────────┤
 │ 4. Skeptic Agent     → Identifies assumptions, contradictions & alternates│
 ├───────────────────────────────────────────────────────────────────────────┤
 │ 5. Chief Agent       → Executive synthesis, evidence citations & review   │
 └───────────────────────────────────────────────────────────────────────────┘
                                       │
                                       ▼
                       Structured Pydantic JSON Output
                                       │
                 ┌─────────────────────┴─────────────────────┐
                 ▼                                           ▼
      FastAPI REST Endpoints                    Gradio Interactive UI
```

### Agent Roles:
1. **Detective Agent:** Establishes objective chronologies, isolates the opportunity window, and extracts verified ground-truth facts.
2. **Evidence Agent:** Classifies each piece of evidence (Fact vs. Inference), differentiates card usage from physical presence, and determines evidence strength.
3. **Suspect Agent:** Constructs comparative matrices evaluating Motive, Means, Opportunity, Access, and Alibi corroboration across all persons of interest.
4. **Skeptic Agent (Devil's Advocate):** Systematically challenges the leading hypothesis, surfaces unverified assumptions, and identifies missing investigations.
5. **Chief Agent:** Produces the final investigative report with strict evidence citations, uncertainty ratings, next steps, and human-in-the-loop review triggers.

---

## ✨ Key Features

- **🛡️ Structured Output Guarantee:** 100% type-safe JSON validated by Pydantic v2 schemas.
- **🔬 Evidence Sensitivity Analysis:** Built-in simulation showing how conclusions shift when critical evidence (e.g., Evidence E) is removed.
- **👤 Human-in-the-Loop Review:** Dedicated endpoints and tracking for supervisor decisions (`ACCEPT`, `REVISE`, `REJECT`).
- **🌐 Dual Implementations:**
  - `backend/`: Production-ready **FastAPI** service with OpenAI / GPT models.
  - `aurora-detective/`: Standalone **Gradio** web dashboard with Google Gemini API.
- **🧪 Comprehensive Test Suite:** Unit, integration, and mock tests with Pytest.

---

## 📁 Repository Structure

```text
.
├── backend/                  # FastAPI Backend Implementation
│   ├── app/
│   │   ├── agents/          # Specialized agent implementations
│   │   ├── services/        # OpenAI client & mock handlers
│   │   ├── case_data.py     # Authoritative case data & evidence sets
│   │   ├── config.py        # Environment configuration
│   │   ├── main.py          # FastAPI application & REST endpoints
│   │   ├── models.py        # Pydantic data schemas
│   │   └── orchestrator.py  # Pipeline coordinator & sensitivity engine
│   ├── tests/               # Pytest suite for backend
│   ├── .env.example
│   └── requirements.txt
│
├── aurora-detective/         # Gradio Standalone Dashboard Implementation
│   ├── agents/              # Gemini-powered agent modules
│   ├── app.py               # Gradio UI application
│   ├── gemini_client.py     # Google GenAI SDK integration
│   ├── models.py            # Pydantic models
│   ├── orchestrator.py      # Investigation orchestrator
│   ├── ui_components.py     # UI renderers and theme
│   ├── tests/               # Pytest suite for Gradio dashboard
│   ├── .env.example
│   └── requirements.txt
│
├── .gitignore
├── requirements.txt
└── README.md
```

---

## 🚀 Quick Start

### 1. Prerequisites
- Python 3.10+
- Virtual environment (recommended)

### 2. Setup

```bash
# Clone the repository
git clone https://github.com/231216-vaibhav/AI-Agent.git
cd AI-Agent

# Create and activate virtual environment
python -m venv venv
# On Windows:
.\venv\Scripts\activate
# On Linux/macOS:
source venv/bin/activate

# Install dependencies
pip install -r requirements.txt
```

---

## 🖥️ Running the Services

### Option A: FastAPI Backend
```bash
cd backend
cp .env.example .env
# Edit .env with your OPENAI_API_KEY

uvicorn app.main:app --reload --port 8000
```
- **API Documentation (Swagger UI):** `http://localhost:8000/docs`
- **Health Check:** `http://localhost:8000/health`

### Option B: Gradio Standalone Dashboard
```bash
cd aurora-detective
cp .env.example .env
# Edit .env with your GEMINI_API_KEY

python app.py
```
- Open `http://localhost:7860` in your browser.

---

## 🧪 Running Tests

```bash
# Test backend
cd backend
pytest -v

# Test Gradio application
cd ../aurora-detective
pytest -v
```

---

## 🔒 Security & Best Practices

- **Zero Key Leakage:** API keys are strictly read from environment variables on the backend and are never sent to client browsers or exposed in logs.
- **Automated Fallbacks & Retries:** Built-in single retry mechanism handles transient API errors gracefully with proper HTTP error codes.
- **Deterministic Mocking:** Comprehensive mock fixtures enable full test coverage without invoking live billable API calls during CI/CD.

---

## 📜 License

MIT License. See [LICENSE](LICENSE) for details.
