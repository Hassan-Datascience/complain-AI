# AI Smart Civic Services — End-to-End Backend Platform

**Batch:** Advance AI & Data Science  
**AI Approach:** Hybrid — Trained ML Model (TF-IDF + Categorical & Priority Classifiers) + LLM API (Actionable Summarization)  
**Scope:** Backend + AI Engine + SQLite Persistence + Advanced Statistical Analytics + REST API Documentation  

---

## 1. Problem Statement

Municipalities face a massive volume of citizen complaints daily across various channels. Manual triaging, department routing, and priority estimation create severe bottlenecks, resulting in delayed emergency responses and citizen dissatisfaction. 

**AI Smart Civic Services** solves this by providing an autonomous, end-to-end backend platform that:
- Instantly classifies complaint descriptions into municipal service categories.
- Predicts complaint urgency/priority levels (`Low`, `Medium`, `High`, `Critical`).
- Generates concise, actionable 1-sentence summaries for field service teams using LLMs.
- Automatically maps categories to municipal departments (e.g. `Water/Drainage` → `Water Board`).
- Computes comprehensive statistical analytics on resolution times to highlight systemic bottlenecks.

---

## 2. Platform Features

- **Automated AI Triaging**: Categorizes complaints (`Road`, `Water/Drainage`, `Waste`, `Electricity`, `Safety`, `Other`) and predicts priority.
- **LLM-Powered Summarization**: Generates standardized action summaries via Anthropic Claude API with automatic fallback protection.
- **Automatic Department Routing**: Maps complaint categories to appropriate municipal service units upon submission.
- **Advanced Statistical Analytics Engine**: Computes mean, median, mode, min, max, range, variance, standard deviation, quartiles (Q1, Q3), IQR, and outlier delay thresholds on resolution times.
- **Narrative AI Insights**: Generates plain-English statistical interpretations alongside analytical data.
- **RESTful FastAPI Service**: Fully interactive OpenAPI/Swagger documentation at `/docs`.
- **Robust Persistence Layer**: Thread-safe SQLite backend with schema migrations, search indexing, and filtering support.

---

## 3. System Architecture & Flow

### Architecture Diagram
```
                     +---------------------------+
                     |    Citizen / Client       |
                     +-------------+-------------+
                                   |
                                   v  (POST /complaints)
                     +-------------+-------------+
                     |   FastAPI REST Controller |
                     +-------------+-------------+
                                   |
                                   v
                     +-------------+-------------+
                     |     ComplaintManager      | (Business Logic Layer)
                     +-------+-----------+-------+
                             |           |
             +---------------+           +---------------+
             |                                           |
             v                                           v
+------------+------------+                 +------------+------------+
|        AIAnalyzer       |                 |     DatabaseManager     |
| - TF-IDF Classification |                 | - SQLite Persistence    |
| - Priority Prediction   |                 | - Department Mapping    |
| - LLM Summarization     |                 | - Search Indexing       |
+-------------------------+                 +------------+------------+
                                                         |
                                                         v
                                            +------------+------------+
                                            |      StatsService       |
                                            | - Statistical Metrics   |
                                            | - Outlier Detection     |
                                            +-------------------------+
```

### Reference Flow
1. **Citizen Input**: Raw complaint text submitted to `POST /complaints`.
2. **Business Orchestration (`ComplaintManager`)**: Generates unique `complaint_id` (e.g., `CMP-A1B2C3D4`).
3. **AI Pipeline Execution (`AIAnalyzer`)**:
   - Vectorizes text and predicts category & confidence.
   - Predicts urgency/priority level.
   - Summarizes text using Claude LLM (or fallback summary if API key is unconfigured/fails).
4. **Auto-Assignment & Persistence (`DatabaseManager`)**: Maps category to handling department and saves to SQLite `complaints` table.
5. **Analytics (`StatsService`)**: Aggregates records for dashboard statistics and resolution time delay detection.

---

## 4. AI Technology Explanation

### 4a. Classification & Priority (Trained ML Engine)
- **Feature Extraction**: TF-IDF (Term Frequency-Inverse Document Frequency) vectorization with stop-words removal and L2 normalization.
- **Classification Model**: Trained on 210 diverse labeled civic complaint dataset (`data/training_data.csv`).
- **Confidence Calibration**: Computes probability distribution (`predict_proba`) over predicted labels.

### 4b. LLM Actionable Summarization
- **API**: Anthropic Claude API (`claude-sonnet-4-6`).
- **System Prompt**: *"Summarize the citizen complaint in exactly one actionable sentence for a municipal service team. Do not add information not present."*
- **Fallback Strategy**: If the API call times out or fails, the system safely truncates the text, flags `ai_summary_fallback: true`, and prevents server crash.

### 4c. Model Limitations
- **Synthetic Training Scope**: Trained on 210 labeled records; may misclassify complex multi-issue edge cases.
- **Probabilistic Nature**: Accuracy is ~99-100% on training sample, but non-deterministic real-world text may occasionally misroute.
- **LLM Dependency**: Requires active network access to Anthropic API for real-time Claude summarization.

---

## 5. Setup & Installation

### Step 1: Clone Repository & Create Environment
```bash
git clone <repository_url>
cd complain-AI
python -m venv venv
# On Windows:
venv\Scripts\activate
# On Linux/macOS:
source venv/bin/activate
```

### Step 2: Install Dependencies
```bash
pip install -r requirements.txt
```

### Step 3: Configure Environment Variables
Copy `.env.example` to `.env` and set your API key:
```bash
cp .env.example .env
```
In `.env`:
```ini
ANTHROPIC_API_KEY=your_anthropic_api_key_here
DB_PATH=civic.db
MODEL_DIR=app/ml
```

### Step 4: Train ML Classifier & Generate Model Artifacts
```bash
python -m app.ml.train_classifier
```

### Step 5: Run FastAPI Server
```bash
uvicorn app.main:app --reload --port 8000
```
Access interactive API docs at: **http://localhost:8000/docs**

---

## 6. API Usage & Endpoints

| Method | Endpoint | Description |
|---|---|---|
| `POST` | `/complaints` | Submit new complaint (triggers AI pipeline & auto routing) |
| `GET` | `/complaints` | List complaints (filters: `category`, `priority`, `status`, `department`, `date_from`, `date_to`) |
| `GET` | `/complaints/{id}` | Get single complaint by ID |
| `PATCH` | `/complaints/{id}/status` | Admin status update (`Open`, `Assigned`, `In Progress`, `Resolved`) |
| `PATCH` | `/complaints/{id}/assign` | Admin manual department re-assignment |
| `GET` | `/analytics/summary` | Categorical, priority, and status count distributions |
| `GET` | `/analytics/stats` | Mean, median, mode, std dev, quartiles, IQR, outliers, and narrative |
| `GET` | `/analytics/trends` | Submission volume trends over time |

### Sample POST `/complaints` Payload
```json
{
  "description": "Massive crater pothole on Expressway near exit 4 causing heavy wheel damage.",
  "location": "Expressway Exit 4"
}
```

### Sample Response
```json
{
  "complaint_id": "CMP-B7E2A91D",
  "description": "Massive crater pothole on Expressway near exit 4 causing heavy wheel damage.",
  "category": "Road",
  "priority": "High",
  "location": "Expressway Exit 4",
  "date": "2026-08-09T01:00:00",
  "status": "Open",
  "assigned_department": "Roads Department",
  "ai_summary": "Repair massive crater pothole on Expressway near exit 4.",
  "ai_confidence": 0.96,
  "ai_summary_fallback": false
}
```

---

## 7. AI Testing Evidence & Evaluation

Below are 10 representative test cases run through the evaluation suite (`python -m unittest tests/test_ai_pipeline.py`):

| Test Complaint Input | Predicted Category | Predicted Priority | Confidence | Assessment |
|---|---|---|---|---|
| *Massive pothole on Expressway causing tire punctures and traffic jams.* | **Road** | **High** | 0.96 | Accurate |
| *Contaminated tap water running dark brown in Sector 9 apartments.* | **Water/Drainage** | **Critical** | 0.95 | Accurate |
| *Community dumpster overflowing with rotting garbage attracting pests.* | **Waste** | **High** | 0.94 | Accurate |
| *Live electrical cable snapped and lying across entrance to school.* | **Electricity** | **High** | 0.92 | Accurate |
| *Stray dog pack acting aggressively near kindergarten playground.* | **Safety** | **High** | 0.93 | Accurate |
| *Public park fountain turned off and lawn overgrown with weeds.* | **Other** | **Low** | 0.97 | Accurate |
| *Broken sewer line leaking raw sewage into street gutter.* | **Water/Drainage** | **Critical** | 0.96 | Accurate |
| *Streetlights out on Elm Street for 4 consecutive nights.* | **Electricity** | **Low** | 0.91 | Accurate |
| *Derelict abandoned car left blocking fire hydrant.* | **Safety** | **Medium** | 0.89 | Accurate |
| *Loud commercial music played until 3 AM in residential zone.* | **Other** | **Medium** | 0.95 | Accurate |

---

## 8. Deployment Guidelines

### Railway / Server Deployment
1. Set Environment Variables on host platform:
   - `ANTHROPIC_API_KEY`
   - `DB_PATH=/app/data/civic.db`
   - `MODEL_DIR=/app/ml`
2. Build & Start Command:
   ```bash
   python -m app.ml.train_classifier && uvicorn app.main:app --host 0.0.0.0 --port $PORT
   ```
3. Public Documentation URL will be available automatically at `/docs`.