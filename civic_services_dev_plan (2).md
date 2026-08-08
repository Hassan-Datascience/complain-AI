# AI Smart Civic Services — End-to-End Backend Development Plan
**Batch:** Advance AI & Data Science
**AI Approach:** Hybrid — Trained ML model (classification + priority) + LLM API (summarization)
**Scope:** Backend + AI + Database + Statistics + Deployment (frontend excluded)

---

## 1. Project Structure

```
civic-services/
├── app/
│   ├── main.py                  # FastAPI entrypoint
│   ├── config.py                # env vars, settings
│   ├── models/
│   │   ├── complaint.py         # Complaint OOP class
│   │   ├── citizen.py           # Citizen class
│   │   └── department.py        # Department class
│   ├── services/
│   │   ├── ai_analyzer.py       # AIAnalyzer class (core AI logic)
│   │   ├── complaint_manager.py # ComplaintManager class (business logic)
│   │   ├── database_manager.py  # DatabaseManager class (SQLite ops)
│   │   └── stats_service.py     # StatsService class (analytics)
│   ├── routes/
│   │   ├── complaints.py        # complaint CRUD + AI trigger endpoints
│   │   ├── admin.py             # admin management endpoints
│   │   └── analytics.py         # dashboard/stats endpoints
│   ├── ml/
│   │   ├── train_classifier.py  # training script (offline, run once)
│   │   ├── category_model.pkl   # saved trained model
│   │   ├── priority_model.pkl   # saved trained model
│   │   └── vectorizer.pkl       # saved TF-IDF vectorizer
│   └── schemas.py               # Pydantic request/response models
├── data/
│   └── training_data.csv        # labeled complaint dataset
├── civic.db                     # SQLite database
├── requirements.txt
├── README.md
└── .env                         # API keys (never commit — gitignore this)
```

---

## 2. Data Model (SQLite Schema)

```sql
CREATE TABLE complaints (
    complaint_id TEXT PRIMARY KEY,
    description TEXT NOT NULL,
    category TEXT,
    priority TEXT,
    location TEXT,
    date TEXT,
    status TEXT DEFAULT 'Open',
    assigned_department TEXT,
    ai_summary TEXT,
    ai_confidence REAL,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

CREATE TABLE departments (
    department_id TEXT PRIMARY KEY,
    name TEXT,
    category_handled TEXT
);
```

Map categories → departments (e.g. Water/Drainage → Water Board, Road → Roads Dept, Electricity → Power Dept). This mapping is what drives `assigned_department` auto-assignment — a nice extra AI-adjacent touch (rule-based on top of AI category output).

---

## 3. OOP Architecture (Batch requires this regardless, and it scores separately)

**`Complaint`** — data class: id, description, category, priority, location, date, status, department, ai_output. Has `to_dict()` for API responses.

**`Citizen`** — id, name, contact (minimal, only if you want auth; optional for hackathon scope).

**`AIAnalyzer`** — the core AI class. Responsibilities:
- `classify(text) -> category, confidence`
- `predict_priority(text) -> priority, confidence`
- `summarize(text) -> short_summary` (calls LLM API)
- `analyze(text) -> full dict combining all three`

**`ComplaintManager`** — business logic layer. Takes raw complaint input, calls `AIAnalyzer`, maps category→department, and passes result to `DatabaseManager` to persist. This is the "reference flow" — Citizen input → ComplaintManager → AIAnalyzer → DatabaseManager.

**`DatabaseManager`** — all SQLite CRUD: `insert_complaint`, `get_complaint`, `list_complaints(filters)`, `update_status`, `assign_department`.

**`StatsService`** — analytics layer: category frequency, priority distribution, mean/median resolution time, variance/std dev, quartiles/IQR (relevant even outside the Statistics batch — strengthens your "Statistics/Analytics" rubric line worth 15 marks).

---

## 4. AI Implementation Detail

### 4a. Classification + Priority (trained ML model)
- **Input:** complaint description text
- **Pipeline:** TF-IDF vectorizer → Logistic Regression or XGBoost classifier
- **Output:** category label (Road/Water/Waste/Electricity/Drainage/Safety/Other) + priority label (Low/Medium/High/Critical) + confidence score
- **Why this choice:** demonstrates real applied ML (preprocessing, training, evaluation) rather than just calling an API — this is what "meaningful data preprocessing and evaluation" in the rubric is asking for.
- **Data:** since a labeled civic-complaints dataset likely doesn't exist off-shelf, generate a synthetic labeled dataset (150-300 rows) covering each category/priority combination realistically, or use an LLM to help bootstrap labeled examples, then manually verify a sample. Document this in the README as your "defensible data source" (Step 5 in the spec explicitly allows this).

### 4b. Summarization (LLM API)
- **Input:** complaint description text
- **Prompt:** short, constrained — "Summarize this civic complaint in one actionable sentence for a service team. Do not add information not present."
- **Output:** 1-2 sentence actionable summary
- **Failure handling:** if API call fails/times out, fall back to a truncated version of the original text and flag `ai_summary_fallback: true` — this satisfies the "AI/API failure" error-handling requirement (Step 12).

### 4c. Limitations to document (required by the spec)
- Model trained on limited/synthetic data → may misclassify edge-case or multi-issue complaints
- No perfect accuracy guarantee — report actual test results honestly (Step 13 explicitly forbids claiming perfect accuracy)
- LLM summarization can occasionally over-generalize; mitigated by constrained prompting

---

## 5. API Endpoints (FastAPI)

| Method | Endpoint | Purpose |
|---|---|---|
| POST | `/complaints` | Submit new complaint → triggers AI pipeline → stores result |
| GET | `/complaints` | List complaints (supports query params: category, priority, status, date, location, department) |
| GET | `/complaints/{id}` | Get single complaint with full AI output |
| PATCH | `/complaints/{id}/status` | Admin updates status (Open/Assigned/In Progress/Resolved) |
| PATCH | `/complaints/{id}/assign` | Admin manually reassigns department |
| GET | `/analytics/summary` | Category frequency, priority distribution, counts |
| GET | `/analytics/stats` | Mean/median/mode/variance/std dev/quartiles on resolution times |
| GET | `/analytics/trends` | Complaints over time (daily/weekly counts) |

---

## 6. Statistics Module (feeds analytics endpoints)

Compute and expose:
- Category frequency distribution
- Priority distribution
- Mean, median, mode, min, max, range of resolution time (Resolved date − created date, for resolved complaints)
- Variance and standard deviation of resolution time
- Quartiles (Q1, Q3), IQR, and outlier fences (complaints taking unusually long → flag for admin attention)
- Short plain-English interpretation string returned alongside numbers (e.g. "Water complaints take 40% longer to resolve than average — consider reallocating resources") — the spec explicitly wants explanation, not just numbers

---

## 7. Error Handling Checklist

- Empty/invalid complaint text → 400 with clear message
- AI model file missing/load failure → graceful 500 with logged error, don't crash server
- LLM API timeout/failure → fallback summary (see 4b)
- Invalid filter/query params on GET endpoints → ignore invalid ones, don't 500
- Database connection/write failure → retry once, then return 503 with message
- Missing required fields in POST body → Pydantic validation handles this automatically (FastAPI)

---

## 8. Testing the AI (Step 13 requirement)

Prepare 8-10 realistic test complaints across all categories/priorities, run them through the pipeline, and record in README:
- Input text
- Predicted category + confidence
- Predicted priority + confidence
- Generated summary
- Whether prediction was "sensible" (your honest assessment) — spec explicitly wants this, not a claim of perfection

---

## 9. Deployment

- **Backend:** Railway (you already have workflow experience here from NEWS_WEB)
- **Database:** SQLite file persisted in Railway volume, or migrate to a small hosted Postgres if Railway's ephemeral filesystem is a concern for demo persistence
- **Env vars:** LLM API key stored in Railway environment variables, never committed — add `.env` to `.gitignore` immediately
- **Public API docs:** FastAPI auto-generates `/docs` (Swagger UI) — this alone can serve as your live demo interface for the hackathon if you don't want to build a frontend, since judges can hit endpoints directly

---

## 10. Submission Deliverables Checklist

- [ ] GitHub repo, clean structure (as above), `.env` excluded
- [ ] Public deployed URL (Railway)
- [ ] README: problem statement, features, architecture, AI technology explanation, setup/run instructions
- [ ] Architecture diagram (simple flow: Citizen → API → ComplaintManager → AIAnalyzer → DatabaseManager → Admin/Analytics)
- [ ] AI testing evidence section in README (the 8-10 test cases from Step 8 above)
- [ ] Demo video (3-5 min) — since no frontend, this can be a Swagger UI walkthrough + terminal + dashboard analytics JSON output

---

## 11. Suggested Build Order (so you're never blocked)

1. SQLite schema + `DatabaseManager` class — **already built and tested, see `database_manager.py` handed over separately. Do not regenerate this file — use it as-is.**
2. `Complaint`, `Citizen`, `Department` classes
3. Synthetic training dataset + `train_classifier.py` → save `.pkl` models
4. `AIAnalyzer` class (wire in classification + priority models, then LLM summarization)
5. `ComplaintManager` class tying it together
6. FastAPI routes (`complaints.py`, `admin.py`)
7. `StatsService` + `analytics.py` routes
8. Error handling pass across all endpoints
9. AI testing (Step 13) + document results
10. Deploy to Railway, verify `/docs` works publicly
11. Write README + architecture diagram
12. Record demo video

---

## 12. Implementation Specs (exact values — do not improvise these)

These are the concrete, locked-in specifics an autonomous build should follow exactly, so nothing drifts from what's already been designed/tested above.

### 12a. Fixed category list
```
Road, Water/Drainage, Waste, Electricity, Safety, Other
```
(Matches the spec's example categories, `Water/Drainage` merged into one label since the spec's example journey uses "Water/Drainage" as a single category.)

### 12b. Fixed priority list
```
Low, Medium, High, Critical
```

### 12c. Department mapping (seed data for `departments` table)
```
category_handled     -> name
Road                 -> Roads Department
Water/Drainage       -> Water Board
Waste                -> Sanitation Department
Electricity          -> Power Department
Safety               -> Public Safety Department
Other                -> General Services Department
```
Use `DatabaseManager.seed_departments()` (already implemented) to insert these on app startup in `main.py`.

### 12d. `requirements.txt`
```
fastapi==0.115.0
uvicorn[standard]==0.30.6
pydantic==2.9.2
scikit-learn==1.5.2
pandas==2.2.3
joblib==1.4.2
anthropic==0.34.2
python-dotenv==1.0.1
```
(Use `anthropic` SDK for the LLM summarization call, since that's the API key most naturally available. XGBoost only needed if you swap Logistic Regression for XGBoost in `train_classifier.py` — add `xgboost==2.1.1` if so.)

### 12e. `config.py` — required env vars
```
ANTHROPIC_API_KEY      # for AI summarization
DB_PATH                # default "civic.db"
MODEL_DIR              # default "app/ml"
```
Load via `python-dotenv`; never hardcode the key. `.env` must be in `.gitignore` before the first commit.

### 12f. `schemas.py` — Pydantic request/response models (exact shape)
```python
class ComplaintCreate(BaseModel):
    description: str          # required, min_length=10
    location: str | None = None
    date: str | None = None   # ISO format, defaults to now if omitted

class ComplaintResponse(BaseModel):
    complaint_id: str
    description: str
    category: str | None
    priority: str | None
    location: str | None
    date: str | None
    status: str
    assigned_department: str | None
    ai_summary: str | None
    ai_confidence: float | None

class StatusUpdate(BaseModel):
    status: str   # must be one of: Open, Assigned, In Progress, Resolved

class DepartmentAssign(BaseModel):
    department: str
```
`ComplaintCreate.description` validation (`min_length=10`) is what satisfies the "empty/invalid complaint text → 400" error-handling requirement — FastAPI/Pydantic returns 422 automatically, no custom code needed.

### 12g. Synthetic training dataset — generation approach
Target: 200 rows in `data/training_data.csv` with columns `description,category,priority`.
- Generate ~30-35 rows per category (6 categories), spread realistically across all 4 priority levels within each category (e.g. a small pothole = Low, a collapsed main road = Critical).
- Vary sentence structure and vocabulary per row — don't just template-swap one sentence, or the classifier will overfit to phrasing rather than content.
- After generating, manually spot-check ~20 random rows for label sanity before training — document this spot-check in the README as the "data validation" step (satisfies Step 5's "clean and validate it").

### 12h. LLM summarization — exact prompt template
```
System: You are a civic service assistant. Summarize the following citizen
complaint in exactly one actionable sentence for a municipal service team.
Do not add information not present in the complaint. Do not include
greetings or explanations — output only the summary sentence.

User: {complaint_description}
```
Model: `claude-sonnet-4-6` (via `anthropic` SDK), `max_tokens=100`, `temperature=0.2` (low temperature — this is an extraction/compression task, not creative writing).

### 12i. README outline (so the agent doesn't freestyle structure)
```
1. Problem Statement (civic problem, target users)
2. Features (bullet list)
3. Architecture (diagram + reference flow description from Section 11 of this plan)
4. AI Technology Explanation
   - What each AI feature receives, does, returns
   - Model choice justification
   - Limitations (see Section 4c of this plan)
5. Setup & Installation (venv, pip install -r requirements.txt, .env setup, run train_classifier.py, run uvicorn)
6. Usage (example curl/Swagger UI requests)
7. AI Testing Evidence (the 8-10 test cases from Section 8)
8. Deployment (live Railway URL)
```
