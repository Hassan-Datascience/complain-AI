# AI Smart Civic Services — Final Recheck & Completion Plan
Hand this entire document to the IDE agent. Go through it section by section, in order.
For each item: verify current status first, then fix/complete only what is missing or broken.
Do not modify or regenerate anything already confirmed working, unless a fix is explicitly requested below.

---

## 1. Provider / Config Audit

- [ ] Confirm `ai_analyzer.py` is fully wired to **Groq** (`llama-3.3-70b-versatile`), with no leftover references to Gemini or Anthropic anywhere in the codebase (check `config.py`, `.env`, `.env.example`, `requirements.txt`, imports).
- [ ] Confirm `requirements.txt` only lists the `groq` package for the LLM piece — remove `google-generativeai`, `anthropic`, or `openai` if any are still present.
- [ ] Confirm `.env.example` shows `GROQ_API_KEY=` (placeholder, no real key) — the real key stays only in `.env`.
- [ ] Confirm `.gitignore` includes `.env` and that `.env` has never been committed. Run `git status` and `git log --all --full-history -- .env` to check — if it was ever committed, flag this to me immediately, don't just fix `.gitignore` and move on, since the key would still be in git history.

## 2. Known Issue — Priority Misclassification on Flooding Language

The Water Leak test case (burst pipe, flooding, low water pressure) was predicted as **Low priority** when it should reasonably be **Medium/High**. Do the following:
- [ ] Add 15-20 more training rows to `data/training_data.csv` specifically covering flooding/water-emergency language ("burst pipe", "flooding", "water pressure loss", "gushing water", "street flooded") labeled at Medium/High/Critical priority as appropriate.
- [ ] Retrain only the priority model (do not touch the category model).
- [ ] Re-run the same Water Leak test complaint plus the original 10 unseen test cases from before, and report full before/after comparison.
- [ ] If accuracy on the original 10 test cases drops because of this retraining, report that honestly too — don't just report the improvement.

## 3. Analytics Edge Cases

- [ ] Test `/analytics/stats` with zero resolved complaints in the database. If it errors (e.g. division by zero), fix it to return a graceful message like "not enough resolved complaints yet for statistics" instead of crashing.
- [ ] Mark at least 2-3 complaints as "Resolved" via `/complaints/{id}/status`, then re-test `/analytics/stats` and confirm mean/median/variance/quartiles now return real computed numbers.
- [ ] Test `/analytics/summary` and `/analytics/trends` similarly with the current data and confirm no errors.

## 4. Test Suite Re-verification

- [ ] Run `tests/test_ai_pipeline.py` in full and confirm all tests pass with the current Groq-based pipeline (this suite may still reference the old provider from before the Gemini/Groq switch — update any provider-specific mocks or assertions if needed).
- [ ] Report the full pass/fail output, not just "all passed."

## 5. Full API Smoke Test (repeat, since code has changed since last check)

- [ ] Start the server, POST 3 new complaints (one per category not yet tested: Waste, Safety, Other), confirm category + priority + department + Groq summary all populate correctly, and confirm `ai_summary_fallback: false`.
- [ ] GET each back by ID and confirm persistence matches exactly.
- [ ] Test at least one deliberate error case: submit a complaint with description under 10 characters and confirm it returns a clean 422 validation error, not a crash.

## 6. README Finalization

Update `README.md` with the following, following the outline in Section 12i of the original dev plan:
- [ ] Problem statement, features, architecture (reference flow diagram description)
- [ ] AI technology section: TF-IDF + trained classifier for category/priority, Groq (`llama-3.3-70b-versatile`) for summarization — explain input/output/limitations for each
- [ ] Final accuracy numbers: category ~90% and priority accuracy (use the updated number from Section 2 above, after retraining) on unseen data — clearly labeled as "evaluated on held-out unseen complaints, not training data"
- [ ] Document known limitations honestly, including any remaining misclassifications from the unseen-data test table (e.g. the gasoline-smell water complaint, and the flooding/priority issue if not fully resolved after retraining)
- [ ] Setup & installation instructions (venv, pip install, .env setup, train_classifier.py, uvicorn run command)
- [ ] Example API usage (curl or Swagger UI walkthrough)
- [ ] Full AI testing evidence table (the 10 unseen test cases with predictions)

## 7. Final Structural Audit

Go through the original project structure (Section 1 of the dev plan) and confirm every listed file exists and is non-empty:
```
app/main.py, app/config.py
app/models/complaint.py, citizen.py, department.py
app/services/ai_analyzer.py, complaint_manager.py, database_manager.py, stats_service.py
app/routes/complaints.py, admin.py, analytics.py
app/ml/train_classifier.py, category_model.pkl, priority_model.pkl, vectorizer.pkl
app/schemas.py
data/training_data.csv
requirements.txt, README.md, .env.example, .gitignore
```
Report any missing or empty files.

## 8. Final Report Format

After completing all sections above, give me a single consolidated status report with:
- A checklist of every item above marked done/fixed/not-applicable
- The final priority accuracy number after retraining
- Confirmation that `.env` was never committed to git
- Confirmation that all tests pass
- A list of anything you could not complete and why

---

## Explicitly Out of Scope for This Pass
- No frontend work (decision pending separately)
- No deployment (will be done manually later)
- No optional extras (duplicate detection, department recommendation via ML, RAG assistant, AI Vision) — only revisit these if everything above is confirmed complete
