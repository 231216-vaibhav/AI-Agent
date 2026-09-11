# AI Mystery Detective Team: "The Vanishing Aurora Diamond"

A standalone AI investigative dashboard built with **Gradio**, powered by the **Google Gemini Flash API**, and validated with **Pydantic structured outputs**.

[![Live Demo](https://img.shields.io/badge/🚀_Live_Demo-ai--agent--31b3.onrender.com-00C7B7?style=for-the-badge&logo=render&logoColor=white)](https://ai-agent-31b3.onrender.com/)

> 🌐 **Live Demo URL:** [**https://ai-agent-31b3.onrender.com/**](https://ai-agent-31b3.onrender.com/)

---

## 🏛️ Case Summary

- **Case Name:** The Vanishing Aurora Diamond
- **Location:** Northbridge Museum, Grand Gallery
- **Incident Overview:**
  - **8:00 PM:** Aurora Diamond confirmed inside locked display case.
  - **8:20–8:24 PM:** Power failure in the museum (**Critical Opportunity Window**).
  - **8:30 PM:** Diamond discovered missing with glass intact.
  - *Important:* Discovery at 8:30 PM is **not** the theft time; the theft window is during the blackout.
- **Suspects:**
  - **Lena Ortiz:** Denied promotion; restarted basement generator (8:19–8:26 PM); card opened basement at 8:20 PM; crossed wet courtyard earlier.
  - **Theo Park:** Wanted publicity; alibi verified by continuous stage camera from 8:15–8:29 PM.
  - **Arjun Vale:** Large private debt; worked in archive; card opened archive at 8:12 PM; card opened display case at 8:23 PM; says card was in jacket; left archive at 8:25 PM carrying flat catalogue folder (contents not visible on camera).
  - **Sofia Reed:** Wanted exclusive news story; three guests remember speaking with her in the lobby during blackout; no gallery access.
- **Evidence A–G:**
  - **A:** Battery-backed electronic lock records valid-card access during power failure.
  - **B:** Arjun Vale's card opened display case at 8:23 PM.
  - **C:** Arjun says his card remained in his jacket inside archive.
  - **D:** Camera shows Arjun leaving archive at 8:25 PM with flat catalogue folder (contents not visible).
  - **E:** Blue velvet fibers found inside folder matching display cushion.
  - **F:** Muddy shoeprint near case matches Lena's boot size (crossed courtyard earlier).
  - **G:** Insurance pays museum if diamond remains missing.

---

## 🤖 5-Agent Investigative Pipeline

```
               Gradio User Interface (app.py)
                             │
                             ▼
                 Investigation Orchestrator
                             │
                             ▼
  Agent 1: Detective (Gemini Flash)  --> Reconstructs timeline & confirmed facts
                             │
                             ▼
  Agent 2: Evidence (Gemini Flash)   --> Classifies Evidence A-G (card use != personal presence)
                             │
                             ▼
  Agent 3: Suspect (Gemini Flash)    --> Compares 4 suspects (strictly "PERSON OF INTEREST")
                             │
                             ▼
  Agent 4: Skeptic (Gemini Flash)    --> Challenges leading theory & reveals evidence gaps
                             │
                             ▼
  Agent 5: Chief (Gemini Flash)      --> Executive synthesis with citations & human review flag
                             │
                             ▼
                Human Supervisor Review Station
```

---

## ⚖️ Critical Investigative Rules Adhered To

1. Do NOT invent CCTV events.
2. Do NOT invent timestamps.
3. Do NOT invent witnesses.
4. Do NOT invent physical evidence.
5. Do NOT invent sealant residue.
6. Do NOT invent voluntary surrender.
7. Do NOT invent a conspiracy.
8. Do NOT treat Evidence B as proof that Arjun personally used the card.
9. Do NOT treat Evidence D as proof that the diamond was inside the folder.
10. Do NOT treat Evidence E as conclusive scientific proof without spectrometry.
11. Do NOT call anyone guilty.
12. Final terminology must strictly be **PERSON OF INTEREST**.
13. Human review must be explicit.

---

## 🛠️ Project Structure

```
aurora-detective/
├── app.py                  # Standalone Gradio UI
├── orchestrator.py         # Multi-agent investigation orchestrator & sensitivity engine
├── case_data.py            # Authoritative facts, suspects, and Evidence A-G
├── models.py               # Pydantic structured schemas for all agents
├── gemini_client.py        # Official google-genai client with retry & error handling
│
├── agents/
│   ├── __init__.py
│   ├── detective.py        # Agent 1: Timeline & Fact Reconstruction Specialist
│   ├── evidence.py         # Agent 2: Evidence Classification & Strength Assessment
│   ├── suspect.py          # Agent 3: Suspect Profiler & Comparative Analysis
│   ├── skeptic.py          # Agent 4: Critical Counter-Investigator / Devil's Advocate
│   └── chief.py            # Agent 5: Executive Synthesizer with Citations
│
├── tests/
│   ├── __init__.py
│   ├── mock_gemini.py      # Deterministic mock responses for testing
│   ├── test_case_data.py   # Case facts and Evidence E removal tests
│   ├── test_models.py      # Pydantic schema validation tests
│   ├── test_agents.py      # Unit tests for each of the 5 agents
│   └── test_orchestrator.py# Pipeline & sensitivity analysis tests
│
├── .env                    # Environment variables
├── .env.example            # Environment template
├── requirements.txt        # Dependencies
└── README.md               # Documentation
```

---

## ⚙️ Environment Configuration

Create a `.env` file inside `aurora-detective/`:

```bash
GEMINI_API_KEY=your_gemini_api_key_here
GEMINI_MODEL=gemini-2.5-flash
```

> **Security Note:** `GEMINI_API_KEY` is strictly confined to the backend process and is **never** exposed in the Gradio user interface or client-side assets.

---

## 🧪 Automated Testing

Run the test suite using pytest:

```bash
cd aurora-detective
python -m pytest -v
```

All 17 tests run completely offline and verify:
- Authoritative case data & Evidence A–G
- Removal of only Evidence E in the sensitivity experiment
- All Pydantic models and validations
- Individual execution of Detective, Evidence, Suspect, Skeptic, and Chief
- End-to-end orchestration and human review recording

---

## 🚀 Launching the Gradio Application

Launch the standalone Gradio web interface:

```bash
cd aurora-detective
python app.py
```

The application will launch and be available in your browser at:
`http://127.0.0.1:7860`

### Interactive Features in the UI:
1. **Case Overview & Authoritative Reference:** Complete metadata, timeline milestones, Evidence A–G cards, and suspect profiles.
2. **Run AI Investigation:** Executes all 5 Gemini Flash agents sequentially with live status indicators and structured reports.
3. **Evidence Sensitivity Experiment (`REMOVE EVIDENCE E & RUN AGAIN`):** Reruns the entire 5-agent pipeline without Evidence E and presents a side-by-side comparative analysis of Person of Interest, Confidence, and Strongest Evidence.
4. **Human Review Station:** Allows the supervisor to select `ACCEPT`, `REVISE`, or `REJECT`, log investigative notes, record next forensic action steps, and view the session review history.
