# The Better Investor — Phase 3: Advanced AI & Behavioral Coaching

**Smarter Investing Starts Here.**

The Better Investor is an education-first investing platform. It helps users learn investing fundamentals, evaluate portfolio concentration risk, and ask AI-powered educational questions.

> **Educational only:** This product does **not** provide personalized financial advice.

## Phase 3 status

- [x] Advanced AI assistant with configurable explanation depth (simple / deep)
- [x] Guardrail/policy layer upgraded with book-based guidance themes
- [x] Behavioral coaching engine with confidence scores and educational guidance per signal
- [x] Standalone `/api/assistant/behavioral/analyze` endpoint
- [x] `policy_metadata` field added to every assistant response
- [x] `behavioral_coaching` detailed field added (alongside backward-compatible `behavioral_signals`)
- [x] Structured logging for policy decisions and behavioral signal detections
- [x] Frontend depth toggle (Simple / Deep Dive) on AI assistant page
- [x] Frontend behavioral coaching cards displayed inline with AI responses
- [x] Phase 3 tests (10 new test cases covering depth, behavioral API, and policy metadata)

## Phase 3 — what was added

### Backend: guardrail / policy layer (`backend/app/policies/guardrails.py`)

`AssistantPolicy` is a stateless, reusable middleware-style service (not hardcoded in route handlers):

- **Explanation depth support**: `get_system_prompt(depth)` returns a `"simple"` or `"deep"` system prompt.
- **Book-based guidance themes**: both system prompts embed educational themes from *A Random Walk Down Wall Street* (Malkiel) and *The 5 Mistakes Every Investor Makes* (Hanson):
  - Long-term perspective
  - Diversification
  - Low-cost index funds
  - Emotional discipline (panic selling, FOMO, overconfidence)
  - Avoiding market timing
- **`finalize()` now returns `(text, disclaimer_appended: bool)`** for audit logging.
- **Structured logging**: every policy block and pass is logged with `policy_block` / `policy_pass` log events.
- **`PolicyMetadata` dataclass** carries block status, depth, disclaimer flag, reason, and detected flags.

### Backend: behavioral coaching engine (`backend/app/services/behavioral/signals.py`)

`BehavioralSignalService` now provides two methods:

| Method | Returns | Notes |
|---|---|---|
| `detect_signals(message)` | `list[str]` | Signal names only — backward-compatible with Phase 2 |
| `analyze(message)` | `list[BehavioralSignal]` | Full detail: signal, confidence (0–1), coaching text, matched phrases |

Signals detected:

| Signal | Confidence | Trigger phrases |
|---|---|---|
| `panic_selling` | 0.85 | "panic sell", "sell everything", "market is crashing" |
| `fomo` | 0.80 | "fomo", "missing out", "everyone is buying" |
| `overconfidence` | 0.80 | "can't lose", "sure winner", "easy money" |
| `chasing_hot_stocks` | 0.75 | "hot stock", "meme stock", "to the moon" |
| `lack_of_diversification` | 0.90 | "all in", "one stock", "single stock portfolio" |

Confidence receives a small bonus when multiple trigger phrases are matched in the same message. Every detection is logged with `behavioral_signal_detected`.

### Backend: assistant service (`backend/app/services/ai/service.py`)

`AssistantService.chat()` now accepts:

| Parameter | Type | Default | Notes |
|---|---|---|---|
| `message` | `str` | required | User question or statement |
| `history` | `list[dict]` | `[]` | Prior conversation turns |
| `depth` | `str` | `"simple"` | `"simple"` or `"deep"` |

Response shape (all fields present):

```json
{
  "response": "...",
  "disclaimer": "The Better Investor is for educational purposes only...",
  "behavioral_signals": ["fomo", "overconfidence"],
  "behavioral_coaching": [
    {
      "signal": "fomo",
      "confidence": 0.83,
      "coaching": "Fear of missing out is one of the most common reasons..."
    }
  ],
  "policy_metadata": {
    "blocked": false,
    "depth": "simple",
    "disclaimer_appended": true,
    "block_reason": null,
    "flags": []
  }
}
```

### New API endpoints (Phase 3)

| Method | Path | Description |
|---|---|---|
| `POST` | `/api/assistant/chat` | *(extended)* now accepts optional `depth` field (`"simple"` / `"deep"`) |
| `POST` | `/api/assistant/query` | *(extended)* same as `/chat` |
| `POST` | `/api/assistant/behavioral/analyze` | Standalone behavioral analysis — returns signals with confidence and coaching |

#### `/api/assistant/chat` — updated request body

```json
{
  "message": "I have FOMO and everyone is buying this hot stock.",
  "history": [],
  "depth": "deep"
}
```

`depth` defaults to `"simple"` if omitted. Returns HTTP 400 for unrecognised values.

#### `/api/assistant/behavioral/analyze`

Request:
```json
{ "message": "I want to go all in on a meme stock." }
```

Response:
```json
{
  "signals": [
    {
      "signal": "lack_of_diversification",
      "confidence": 0.90,
      "coaching": "Concentrating a portfolio in a single stock or sector..."
    }
  ],
  "signal_names": ["lack_of_diversification"],
  "analyzed": true
}
```

### Frontend changes

| File | What changed |
|---|---|
| `frontend/src/pages/AssistantPage.tsx` | Added depth toggle (Simple / Deep Dive), behavioral coaching section below AI responses, updated `ChatResponse` type to include `behavioral_coaching` and `policy_metadata` |
| `frontend/src/components/common/BehavioralCoachingCard.tsx` | New component: renders a coaching card per detected signal (signal label, confidence %, coaching text) |
| `frontend/src/theme/global.css` | Added `.depth-toggle`, `.coaching-card`, `.coaching-section` CSS classes |

### Observability

All policy decisions and behavioral signals emit structured log records via Python's standard `logging` module:

| Logger | Event | Fields |
|---|---|---|
| `backend.app.policies.guardrails` | `policy_block` | `reason`, `message_preview` |
| `backend.app.policies.guardrails` | `policy_pass` | `message_preview` |
| `backend.app.services.behavioral.signals` | `behavioral_signal_detected` | `signal`, `confidence`, `match_count` |

No secrets or PII are logged; `message_preview` is truncated to 120 characters.

---

## Phase 2 audit status

- [x] AI assistant foundation with educational-first guardrails and wired endpoints
- [x] Portfolio analysis endpoint and baseline concentration/diversification output
- [x] Market quote + chart contract endpoints for major US symbols/ETFs
- [x] Educational hub lesson/progress endpoints
- [x] Behavioral coaching scaffolding (signal detector service hook in assistant flow)
- [x] Investor Quest routes/module scaffolding with explicit no-chat-XP rule
- [x] User/account foundations: profile, saved portfolios, watchlist routes, lesson progress, achievement counters
- [x] Pricing plans represented in backend and UI (Free, Single $10/month, Family, Business)
- [x] App shell branding/colors/responsive core navigation
- [x] Modular architecture + passing build/test checks



Phase 2A establishes modular scaffolding across frontend and backend for the following domains:

### Data models added

| Model | File | Purpose |
|---|---|---|
| `BehaviorEvent` | `backend/app/models/behavior_event.py` | Records detected behavioral coaching signals (panic selling, FOMO, etc.) |
| `QuestProfile` | `backend/app/models/quest.py` | User's Investor Quest progress (level, XP) |
| `Badge` | `backend/app/models/quest.py` | Awards earned within Investor Quest |
| `ChallengeProgress` | `backend/app/models/quest.py` | Tracks per-user challenge completion and XP |
| `SubscriptionPlan` | `backend/app/models/subscription.py` | Defines available billing tiers |
| `SubscriptionStatus` | `backend/app/models/subscription.py` | Records a user's active plan state |
| `WatchlistItem` | `backend/app/models/watchlist_item.py` | Normalized per-symbol watchlist entry |

### New API endpoints (Phase 2A stubs)

| Method | Path | Description |
|---|---|---|
| `POST` | `/api/assistant/query` | Alias for `/api/assistant/chat` — Phase 2A canonical path |
| `GET` | `/api/market/quote/<ticker>` | Path-param variant of the quote endpoint |
| `GET` | `/api/market/chart/<ticker>` | Chart data stub (Phase 2B will add full OHLCV data) |
| `GET` | `/api/education/lessons` | Education-prefix lesson list |
| `POST` | `/api/education/progress` | Generic progress stub |
| `GET` | `/api/quest/profile` | Fetch (or create) authenticated user's quest profile |
| `POST` | `/api/quest/challenge/submit` | Submit a completed challenge and earn XP |
| `GET` | `/api/watchlist/items` | List authenticated user's saved watchlist symbols |
| `POST` | `/api/watchlist/items` | Add a symbol to the authenticated user's watchlist |
| `DELETE` | `/api/watchlist/items/<id>` | Remove a symbol from the authenticated user's watchlist |
| `GET` | `/api/billing/plans` | Return all available subscription plan definitions |

### New frontend routes / pages

| Path | Component | Description |
|---|---|---|
| `/quest` | `InvestorQuestPage` | Investor Quest shell with profile, XP, badges, and demo challenge |
| `/billing` | `PricingPage` | Alias for pricing — billing-focused nav entry |

Navigation now includes: **Ask AI → Portfolio Lab → Market → Learn → Investor Quest → Billing → Account**

### AI guardrail policy

`backend/app/policies/guardrails.py` contains `AssistantPolicy` which:

- Blocks direct buy/sell directives
- Blocks guaranteed-return claims
- Appends the educational-only disclaimer to all responses
- Provides the system prompt for educational framing

The guardrail is invoked by **both** `/api/assistant/chat` and the new `/api/assistant/query` alias.

---

## Phase 1 MVP delivered

- React + TypeScript frontend scaffold with pages/routes for:
  - Landing (`/`)
  - Dashboard (`/dashboard`)
  - Ask AI (`/ask-ai`)
  - Portfolio Lab (`/portfolio-lab`)
  - Learn (`/learn`)
  - Profile (`/profile`)
- Flask backend scaffold with modular layers:
  - `backend/app/api/routes`
  - `backend/app/services`
  - `backend/app/providers` (AI + market data)
  - `backend/app/repositories` + `backend/app/models`
  - `backend/app/policies/guardrails.py`
- Provider abstraction contracts:
  - `AIProvider`
  - `MarketDataProvider`
  - `FinnhubMarketDataProvider`
  - `StubAIProvider` (safe default)
- JWT auth foundation:
  - User model
  - Register/Login/Logout endpoints
  - Auth decorator (`auth_required`)
  - Profile read/update endpoint (`/api/account/me`)
- Portfolio foundation:
  - Holdings model
  - Holdings CRUD endpoints (frontend + backend)
  - Concentration + sector breakdown analysis endpoint
- Educational hub foundation:
  - Lesson model + progress model
  - Lesson list/detail endpoints
  - Lesson progress tracking/list endpoints
- Env templates:
  - `backend/.env.example`
  - `frontend/.env.example`
- Tests + CI scaffold:
  - Backend tests for auth, holdings, lessons, market/portfolio, and assistant guardrails
  - Frontend smoke test
  - GitHub Actions workflow in `.github/workflows/ci.yml`

## Deploying to Render

This project ships with a `render.yaml` that defines **two Render services**:

| Service | Type | Name |
|---|---|---|
| Flask backend | Web Service (Python) | `thebetterinvestor-backend` |
| FastAPI backend | Web Service (Python) | `ultra-gpt-fastapi` |
| React/Vite frontend | Static Site | `thebetterinvestor-frontend` |

### Step-by-step

1. **Connect your repo** to Render at <https://dashboard.render.com> → *New → Blueprint*.
   Render will detect `render.yaml` automatically.

2. **Set secret environment variables** in the Render dashboard (not stored in `render.yaml`):

   | Variable | Service | Notes |
   |---|---|---|
   | `FINNHUB_API_KEY` | backend | Your Finnhub API key |
   | `OPENAI_API_KEY` | backend | Required when `AI_PROVIDER=openai` |
   | `DATABASE_URL` | backend | Render Postgres connection string (free tier SQLite is ephemeral) |
   | `VITE_API_BASE_URL` | frontend | Full URL of the deployed backend, e.g. `https://thebetterinvestor-backend.onrender.com` |

   `SECRET_KEY` and `JWT_SECRET_KEY` are auto-generated by `render.yaml`.

3. **Deploy** — Render will:
   - Install Python deps and run DB migrations (backend build step).
   - Start the backend with `gunicorn` bound to `0.0.0.0:$PORT`.
   - Build the React app with `npm run build` and serve the `dist/` folder as a static site.

4. **Post-deploy verification checklist**:
   - [ ] Backend health check passes: `GET https://<backend-url>/` returns `{"status":"ok"}`
   - [ ] Frontend loads at its Render static-site URL without console errors
   - [ ] Frontend API calls reach the backend (check browser Network tab — no `localhost` URLs)
   - [ ] `VITE_API_BASE_URL` in the frontend service matches the backend service URL exactly (including `https://`)
   - [ ] Auth (register / login) works end-to-end

### Architecture notes

- **Do not** use `http://localhost:5000` in any production environment variable — it will break on Render.
- The backend binds to `0.0.0.0:$PORT` where `PORT` is injected by Render automatically.
- CORS is configured to allow all origins (`*`) by default, so the frontend can call the backend across separate Render domains.
- For a persistent database, replace the `DATABASE_URL` env var with a Render Postgres connection string.

---

## Quick start

## 1) Backend (Flask)

```bash
python -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
cp backend/.env.example .env
flask --app main:app run --debug
```

Backend runs at `http://127.0.0.1:5000`.

## 2) FastAPI backend (lightweight chat service)

A minimal FastAPI service lives in `fastapi_backend/`. It exposes the two core
endpoints needed by the frontend and can be deployed as its own Render Web
Service.

### Local run

```bash
cd fastapi_backend
python -m venv .venv
source .venv/bin/activate   # Windows: .venv\Scripts\activate
pip install -r requirements.txt
uvicorn app.main:app --reload --port 8000
```

The service will be available at `http://localhost:8000`.

Interactive docs (Swagger UI): `http://localhost:8000/docs`

### Endpoints

| Method | Path | Description |
|--------|------|-------------|
| `GET` | `/health` | Returns `{"ok": true, "service": "ultra-gpt-fastapi"}` |
| `POST` | `/chat` | Accepts `{"message": "…"}`, returns `{"reply": "…"}` |

### Environment variables

No required environment variables for the stub implementation.  
When you wire up a real AI provider, add `OPENAI_API_KEY` (or your provider's
key) and read it with `os.environ.get("OPENAI_API_KEY")` inside
`fastapi_backend/app/main.py`.

### Deploying to Render

The `render.yaml` in the repository root already defines the service
`ultra-gpt-fastapi`:

```yaml
- type: web
  name: ultra-gpt-fastapi
  rootDir: fastapi_backend
  buildCommand: pip install -r requirements.txt
  startCommand: uvicorn app.main:app --host 0.0.0.0 --port $PORT
  healthCheckPath: /health
```

Steps:

1. Connect the repo in the Render dashboard → *New → Blueprint*.
2. Render detects `render.yaml` and creates the service automatically.
3. After deploy, your FastAPI service URL will be something like
   `https://ultra-gpt-fastapi.onrender.com`.
4. Point your frontend at the service:

```ts
// In your frontend — e.g. src/services/http.ts or a .env variable
const FASTAPI_BASE_URL = "https://ultra-gpt-fastapi.onrender.com";

// Example chat call
await fetch(`${FASTAPI_BASE_URL}/chat`, {
  method: "POST",
  headers: { "Content-Type": "application/json" },
  body: JSON.stringify({ message: userInput }),
});
```

CORS is pre-configured to allow `https://thebetterinvestor.onrender.com`,
`http://localhost:3000`, and `http://localhost:5173`.

## 2) Frontend (React + TypeScript)

```bash
cd frontend
npm install
cp .env.example .env
npm run dev
```

Frontend runs at `http://127.0.0.1:5173`.

## API highlights

### Auth & Account
- `POST /api/auth/register`
- `POST /api/auth/login`
- `POST /api/auth/logout`
- `GET /api/account/me`
- `PUT /api/account/me`

### AI Assistant
- `POST /api/assistant/chat`
- `POST /api/assistant/query` *(Phase 2A alias)*

### Portfolio
- `POST /api/portfolio/analyze`
- `GET /api/portfolio/concentration` (auth)
- `GET /api/holdings` (auth)
- `POST /api/holdings` (auth)
- `PUT /api/holdings/<id>` (auth)
- `DELETE /api/holdings/<id>` (auth)

### Market Data
- `GET /api/market/quote?symbol=AAPL`
- `GET /api/market/quote/<ticker>` *(Phase 2A path-param)*
- `GET /api/market/chart/<ticker>` *(Phase 2A stub)*
- `GET /api/market/profile?symbol=AAPL`

### Education
- `GET /api/lessons`
- `GET /api/lessons/<id>`
- `GET /api/lessons/progress` (auth)
- `POST /api/lessons/<id>/progress` (auth)
- `GET /api/education/lessons` *(Phase 2A alias)*
- `POST /api/education/progress` *(Phase 2A stub)*

### Investor Quest
- `GET /api/quest/profile` (auth) *(Phase 2A)*
- `POST /api/quest/challenge/submit` (auth) *(Phase 2A)*

### Billing
- `GET /api/billing/plans` *(Phase 2A)*

### Watchlist
- `GET /api/watchlist/items` (auth)
- `POST /api/watchlist/items` (auth)
- `DELETE /api/watchlist/items/<id>` (auth)

## Environment and data notes

- Default local DB is SQLite (`sqlite:///instance/better_investor.db`).
- PostgreSQL is supported by setting `DATABASE_URL`, for example:
  - `postgresql://<username>:<password>@localhost:5432/better_investor`
- Required secrets for non-dev usage:
  - `SECRET_KEY`
  - `JWT_SECRET_KEY`
  - `FINNHUB_API_KEY` (market data)
- Finnhub fallback behavior:
  - Missing/invalid API key and API rate limits return clear 502 API messages.

## Apply database migrations

After setting up the backend, apply migrations to create all tables including the Phase 2A models:

```bash
flask --app main:app db upgrade -d backend/migrations
```

If starting fresh with SQLite, `db.create_all()` is used automatically in the test suite.

## Assistant guardrails

The assistant policy enforces:

- No direct buy/sell directives
- No guaranteed returns
- Education-first framing
- Emphasis on diversification, risk awareness, and long-term principles
- Educational disclaimer appended to responses

## Investor Quest rules

XP and badges are earned **only** through:

- Quiz completion
- Challenge completion
- Simulation milestones

Plain assistant chats do **not** award XP. The quest service is intentionally separated from the assistant event pipeline.

## What remains for later phases

These items are intentionally deferred to keep Phase 2 focused on stable foundational scaffolding, while reserving higher-risk provider integrations and advanced product logic for subsequent phases.

### Phase 2B (Core Intelligence)
- Full AI assistant behavioral coaching feedback generation
- Portfolio analyzer v2 (volatility scoring, diversification metric)
- Market data: full OHLCV chart data integration
- Persist `BehaviorEvent` records from assistant/user actions

### Phase 2C (Learning + Gamification)
- Full quiz engine wired to lessons
- Investing simulations
- Achievement tracking and badge awarding logic
- Investor Quest leaderboard

### Phase 2D (Monetization + Hardening)
- Plan gating (feature flags per subscription tier)
- Stripe or payment provider integration
- Performance pass
- Security hardening pass
- Mobile responsiveness QA
