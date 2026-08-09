# Stitch Frontend Integration Plan
Hand this to the IDE agent along with the extracted `stitch_smart_civic_ai_dashboard` folder.
Goal: wire the static Stitch-generated HTML pages to the existing live FastAPI backend, with zero mock/fake data left in place.

---

## 0. What we're starting with

- 7 static HTML pages (Tailwind via CDN, "Emerald Grid" dark+green design system already baked into each file's `tailwind.config`)
- Pages: `home_submit_complaint`, `track_complaint_status`, `admin_login`, `admin_dashboard`, `all_complaints`, `complaint_detail_admin`, `analytics_insights`
- No JavaScript logic yet — currently pure static markup with placeholder/demo numbers
- Backend already live locally with these endpoints: `POST/GET /complaints`, `GET /complaints/{id}`, `PATCH /complaints/{id}/status`, `PATCH /complaints/{id}/assign`, `GET /analytics/summary`, `GET /analytics/stats`, `GET /analytics/trends`

---

## 1. File Structure Setup

Move the Stitch export into the project and serve it via FastAPI's static file support so there's one running app, one port, no CORS headaches:

```
civic-services/
├── app/                          (existing backend, untouched)
├── frontend/
│   ├── index.html                (renamed from home_submit_complaint/code.html)
│   ├── track.html                (from track_complaint_status)
│   ├── admin-login.html          (from admin_login)
│   ├── admin-dashboard.html      (from admin_dashboard)
│   ├── admin-complaints.html     (from all_complaints)
│   ├── admin-complaint-detail.html (from complaint_detail_admin)
│   ├── admin-analytics.html      (from analytics_insights)
│   ├── assets/                   (any shared images if needed)
│   └── js/
│       ├── api.js                (shared fetch wrapper, see Section 3)
│       ├── submit.js
│       ├── track.js
│       ├── dashboard.js
│       ├── complaints-list.js
│       ├── complaint-detail.js
│       └── analytics.js
```

In `app/main.py`, mount the frontend folder:
```python
from fastapi.staticfiles import StaticFiles
app.mount("/app", StaticFiles(directory="frontend", html=True), name="frontend")
```
This keeps `/complaints`, `/analytics/*` etc. as pure JSON API routes, and serves the UI at `/app/index.html` etc. — no route collisions.

---

## 2. Remove All Fake/Decorative Content

The Stitch designs include placeholder content invented for visual polish. Do NOT keep any of this wired to fake numbers — either connect it to a real backend value or remove it entirely:

- **Home page**: "Civic Response Time: 24h avg" and "85% resolved within 7 days" stat — remove, or compute from `/analytics/stats` if a matching field exists; do not hardcode.
- **Home page**: "Recently Resolved Nearby" list — remove entirely. There is no location-proximity or "nearby" feature in the backend. Do not fake this.
- **Home page**: map image / drag-pin visual — keep the location **text input**, remove the fake map graphic (no maps API is integrated). Note this as a possible future enhancement, not a current feature.
- **Home page**: photo upload field — keep it visible in the UI (matches the spec's "optional image upload"), but disable actual submission of the file for now since the backend doesn't process images yet. Add a small note or leave it non-blocking (form should submit fine without a photo).
- **Admin dashboard**: any hardcoded KPI numbers (e.g. "1,248 Total", "342 Open") must be replaced with live values from `/analytics/summary` and `/complaints` counts — never leave static demo numbers in the final version.
- **All Complaints table / Recent Complaints**: hardcoded rows (e.g. "#C-9921") must be replaced with real data from `GET /complaints`.
- **Analytics page**: any invented trend numbers must be replaced with live `/analytics/trends` and `/analytics/stats` data.

Go through every page's `code.html` and grep for hardcoded numbers/names before wiring — replace each one with a JS-populated value or remove the element.

---

## 3. Shared API Wrapper (`frontend/js/api.js`)

Create one shared fetch helper so error handling is consistent across all pages:

```javascript
const API_BASE = "http://127.0.0.1:8000"; // change to deployed URL later, single place to update

async function apiRequest(path, options = {}) {
  try {
    const res = await fetch(`${API_BASE}${path}`, {
      headers: { "Content-Type": "application/json" },
      ...options,
    });
    if (!res.ok) {
      const errBody = await res.json().catch(() => ({}));
      throw new Error(errBody.detail || `Request failed: ${res.status}`);
    }
    return await res.json();
  } catch (err) {
    console.error("API error:", err);
    throw err;
  }
}
```
Every page-specific JS file imports/uses this instead of raw `fetch` calls, so error states are handled the same way everywhere (see Section 6).

---

## 4. Page-by-Page Wiring

### `index.html` (Home / Submit) — `js/submit.js`
- On form submit: `POST /complaints` with `{description, location, date}` (per `ComplaintCreate` schema — description min 10 chars, validate client-side too before sending)
- On success: show the confirmation state already designed in the Stitch page — populate it with the real returned `complaint_id`, `category`, `priority` (color-coded badge per existing status colors), and `ai_summary`
- On failure (422 validation, network error): show inline error message, do not silently fail

### `track.html` (Track Status) — `js/track.js`
- On submit: `GET /complaints/{id}`
- Populate result card with real status, category, priority, department, ai_summary
- 404 case: show "Complaint not found" state cleanly

### `admin-login.html` — no wiring needed yet
- Backend has no auth system built. Leave this as a static screen for now, OR make the "Login" button simply navigate to `admin-dashboard.html` directly (no real auth check) so the demo flow isn't blocked. Do not fake a login validation that doesn't exist.

### `admin-dashboard.html` — `js/dashboard.js`
- KPI cards: `GET /analytics/summary` for total/open/in-progress/resolved/critical counts
- Category donut chart: same summary endpoint's category distribution
- Priority volume chart: `GET /analytics/trends`
- Recent complaints table: `GET /complaints` (take latest 5-10, already sorted by `created_at DESC` per `DatabaseManager.list_complaints`)

### `admin-complaints.html` (All Complaints) — `js/complaints-list.js`
- On load and on filter change: `GET /complaints` with query params matching the filter dropdowns (category, priority, status, department, date range) — map directly to `DatabaseManager.list_complaints` filter keys
- Row click: navigate to `admin-complaint-detail.html?id={complaint_id}`

### `admin-complaint-detail.html` — `js/complaint-detail.js`
- Read `id` from URL query param, `GET /complaints/{id}` on load
- Status update dropdown + save button: `PATCH /complaints/{id}/status`
- Department reassignment dropdown + save button: `PATCH /complaints/{id}/assign`
- After either action succeeds, refresh the displayed data (don't just assume success — re-fetch and confirm)

### `admin-analytics.html` — `js/analytics.js`
- Resolution stats grid: `GET /analytics/stats`
- If backend returns the "not enough resolved complaints" message (see Section 3 of the completed backend recheck), display that message in place of the stat grid rather than showing broken/empty numbers
- Trends chart: `GET /analytics/trends`
- Outlier list: from `/analytics/stats` IQR fence data, if present in the response

---

## 5. CORS

If frontend is NOT served via the FastAPI static mount (Section 1) and instead runs on a separate dev server/port, add CORS middleware to `app/main.py`:
```python
from fastapi.middleware.cors import CORSMiddleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # tighten to specific origin before final deployment
    allow_methods=["*"],
    allow_headers=["*"],
)
```
If using the static mount approach from Section 1, this isn't needed since everything is same-origin.

---

## 6. Error & Loading States (required, not optional)

For every page that fetches data:
- Show a loading indicator while the request is in flight (the design system already has a dark/green aesthetic — a simple spinner or skeleton in the accent green is enough, don't over-engineer)
- Show a clear error state if the API call fails (network error, 500, etc.) — never leave the page blank or stuck on a spinner forever
- This directly satisfies the original spec's error-handling requirement, now extended to the frontend layer

---

## 7. Testing Checklist Before Calling This Done

- [ ] Submit a real complaint through `index.html`, confirm it appears in `admin-complaints.html` moments later
- [ ] Confirm dashboard KPI numbers update after a new submission (refresh or re-fetch)
- [ ] Confirm status/department updates from the detail page actually persist (re-fetch after update)
- [ ] Confirm zero hardcoded/fake numbers remain anywhere in the 7 pages — do a final pass searching for any leftover static demo values from the original Stitch export
- [ ] Confirm all pages render correctly with zero complaints in the database (empty states, not broken layouts)
- [ ] Confirm the photo upload field doesn't block form submission since it's not wired to anything yet
