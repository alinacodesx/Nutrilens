# NutriLens — AI-Powered Food Health Analyzer

## Overview

NutriLens is a web application that analyzes any packaged food (by name or barcode) and gives a personalized health verdict — Safe, Caution, or Avoid — based on the user's health condition. V1 used a hardcoded, rule-based ingredient list; V2 (this version) replaces that with a real AI reasoning pipeline built on live nutrition data.

---

## Problem

* Food labels are difficult for most people to interpret quickly
* Harmful ingredients (excess sugar, saturated fat, sodium) often go unnoticed
* Generic nutrition advice doesn't account for individual health conditions
* Most "food analyzer" projects rely on small, hardcoded datasets that don't scale to real products

---

## Solution — Phase 1 (Current)

NutriLens V2 Phase 1 replaces the static rule-based engine with a single, reliable AI pipeline:

1. **Live nutrition lookup** via the OpenFoodFacts API (any food name or barcode, not a fixed list)
2. **AI health reasoning** via Gemini function-calling — the model returns a strictly structured verdict (`safe` / `caution` / `avoid` / `insufficient_data`), never free-form text
3. **Guardrails against hallucination** — if nutrition data is missing, the AI is instructed to say so explicitly rather than guess

This was deliberately scoped as a **single-agent** system (one clean pipeline, one reasoning call) rather than a multi-agent architecture, to ship something working and testable first. Multi-agent orchestration is planned for a later phase.

---

## How It Works

1. User enters a food name or barcode, and selects a health condition
2. Flask fetches live nutrition + ingredient data from the OpenFoodFacts API
3. If the product isn't found, the AI call is skipped entirely (no data → no reasoning, and no wasted API call)
4. If found, the nutrition data + condition are sent to Gemini via function-calling, using a schema that forces the response into `{verdict, reason}` — no parsing of free-text output, no unreliable JSON-mode
5. The condition is remembered for the session, so it doesn't have to be re-selected on every search
6. Result is rendered with a clear verdict badge and a short, data-grounded explanation

---

## Key Engineering Decisions

* **Function-calling over plain-text prompting** — guarantees a valid, predictable response shape (`enum`-constrained verdict) instead of parsing free text that could break on any model output variation
* **Minimal output schema** (`verdict` + `reason` only) — deliberately excluded fields like `health_score` or `recommended_frequency` that would give the AI room to state fabricated precision or make medical-adjacent claims without real backing
* **`insufficient_data` as a first-class verdict** — the AI is explicitly told to admit missing data rather than infer a plausible-sounding answer, which is the core hallucination guardrail in this project
* **No AI call on missing product data** — if OpenFoodFacts has no match, the app shows a clear message and skips Gemini entirely (saves cost and avoids reasoning over data that doesn't exist)
* **Best-match filtering on name search** — OpenFoodFacts' free-text search can return loosely related products; results are filtered against the search term before use
* **One retry on OpenFoodFacts calls** — the legacy search endpoint is occasionally rate-limited/flaky; a single short retry smooths over transient failures without adding real complexity

---

## Known Limitations (Phase 1, by design)

* Ingredient text is returned in whatever language the product was originally submitted in on OpenFoodFacts (often not English) — no translation layer built yet
* Regional/local-market products (e.g. some Indian packaged snacks) have inconsistent coverage in OpenFoodFacts' database
* Session-based condition storage is temporary (per-browser-session), not a persistent user profile — intentional for Phase 1's single-user scope

---

## Tech Stack

* Python, Flask
* Gemini API (function-calling / tool-use)
* OpenFoodFacts API
* HTML, CSS
* Gunicorn (production server)
* Deployed on Render

---

## Architecture

```
User Input (food + condition)
        │
        ▼
   Flask Route (/analyze)
        │
        ▼
 OpenFoodFacts API ──► Not found? ──► Skip AI, show message
        │ found
        ▼
 Gemini Function-Calling
   (schema-enforced verdict)
        │
        ▼
   Result Page (verdict + reason)
```

---

## Project Structure

```bash
NutriLens/
│── app.py              # Flask routes, session handling
│── logic.py             # OpenFoodFacts lookup + Gemini function-calling
│── templates/
│   │── index.html
│   └── result.html
│── static/
│   └── style.css
│── requirements.txt
│── .env                 # GEMINI_API_KEY (not committed)
└── README.md
```

---

## Run Locally

1. Clone the repository:
```bash
git clone https://github.com/alinacodesx/NutriLens.git
cd NutriLens
```
2. Install dependencies:
```bash
pip install -r requirements.txt
```
3. Add your Gemini API key in a `.env` file:
```
GEMINI_API_KEY=your_key_here
```
4. Run the application:
```bash
python app.py
```
5. Open in browser:
```
http://127.0.0.1:5000/
```

---

## Live Demo

🔗 [nutrilens-0nfp.onrender.com](https://nutrilens-0nfp.onrender.com)

*(Free-tier hosting — the app may take ~50 seconds to wake up after inactivity.)*

---

## Roadmap

* **Phase 1 (Current):** Single-agent AI pipeline — OpenFoodFacts + Gemini function-calling, deployed
* **Phase 2 (Planned):** Persistent user profiles (SQLite), multi-agent architecture, improved search relevance
* **Phase 3 (Planned):** Voice/TTS interaction layer

---

## Version History

* **V1:** Rule-based ingredient analysis over a hardcoded food dataset
* **V2 Phase 1 (Current):** AI-powered pipeline with live data + function-calling, deployed

---

## Key Learnings

* Designing a minimal, guardrailed output schema to reduce AI hallucination risk in a health-adjacent context
* Function-calling vs. plain-text/JSON-mode prompting, and why structured output matters for reliability
* Handling flaky/rate-limited third-party APIs gracefully (retries, fallback states)
* End-to-end deployment: environment variables, production WSGI servers (gunicorn), and debugging repo/deployment structure mismatches
* Practicing scope discipline — deliberately deferring features (health scores, recommended frequency, multi-agent orchestration) that added complexity or hallucination risk without core value

---

## Feedback

Open to suggestions and improvements