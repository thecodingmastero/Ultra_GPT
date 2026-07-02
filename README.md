# The Better Investor — Phase 3: Production Hardening

**Smarter Investing Starts Here.**

The Better Investor is an education-first investing platform. It helps users learn investing fundamentals, evaluate portfolio concentration risk, and ask AI-powered educational questions.

> **Educational only:** This product does **not** provide personalized financial advice.

## Phase 3 completion status

- [x] **Market Data** — TTL in-memory caching, retry logic, real OHLCV chart endpoint (`GET /api/market/chart/<ticker>`)
- [x] **Portfolio Analytics** — Volatility heuristic (HHI), diversification score, sector count, learning suggestions
- [x] **AI Safety Hardening** — Strengthened guardrails: urgency blocking, extended buy/sell directive patterns, refined system prompt
- [x] **Educational Hub** — `/api/education/progress` now persists progress for authenticated users (was a stub)
- [x] **Investor Quest** — Quiz submission endpoint (`POST /api/quest/quiz/submit`), milestone badge awarding, challenge catalogue (`GET /api/quest/challenges`), badge `earned_at` timestamps
- [x] **Subscription Gating** — `PlanEntitlementService` with `Feature` enum, `plan_required` decorator, `/api/account/plan` endpoint
- [x] **Observability** — Structured log events for assistant requests, market data errors, portfolio failures
- [x] **Frontend UX** — `UpgradePrompt` component, plan-aware portfolio page, updated Investor Quest with quiz/challenge catalogue and badge display
- [x] **Tests** — 65 tests (33 pre-existing + 32 new Phase 3 tests covering caching, chart, analytics, guardrails, quiz, badges, entitlements)

## Phase 2 audit status (carried forward)

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


## Phase 2A Foundation — what was added

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
| `GET` | `/api/market/chart/<ticker>` | OHLCV candle data via Finnhub (Phase 3: real data, supports `?resolution=D&count=30`) |
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

## Phase 3 additions at a glance

### New backend files
| File | Purpose |
|---|---|
| `backend/app/services/market_data/cache.py` | Thread-safe TTL cache for market data (quotes, profiles, charts) |
| `backend/app/core/entitlements.py` | `Feature` enum, `_PLAN_FEATURES` matrix, `plan_required` decorator |
| `backend/tests/test_phase3.py` | 32 new tests for Phase 3 features |

### New/updated API endpoints (Phase 3)
| Method | Path | Description |
|---|---|---|
| `GET` | `/api/market/chart/<ticker>` | Real OHLCV candle data from Finnhub `/stock/candle`; supports `?resolution=D&count=30` |
| `POST` | `/api/quest/quiz/submit` | Submit a quiz with score; XP scales 5–25 based on performance; idempotent |
| `GET` | `/api/quest/challenges` | Public catalogue of available quizzes and challenges |
| `GET` | `/api/account/plan` | Returns authenticated user's plan_id and feature entitlement list |
| `POST` | `/api/education/progress` | Now auth-required and persists via `LessonsRepository` (was stub) |

### New frontend files
| File | Purpose |
|---|---|
| `frontend/src/services/plan.ts` | Fetches user plan and exposes `planLabel()` helper |
| `frontend/src/components/common/UpgradePrompt.tsx` | Inline upgrade call-to-action component |

## What remains for Phase 4

These items are explicitly deferred:

### Phase 4A (Real-money Integrations)
- Stripe payment provider integration for Single/Family/Business subscriptions
- Webhook handling for subscription status changes
- Invoice/receipt management

### Phase 4B (Advanced Gamification)
- Interactive quiz engine with real multiple-choice questions per lesson
- Investing simulation sandbox (paper trading with virtual portfolio)
- Investor Quest leaderboard (cross-user rankings)
- Streak tracking and daily learning reminders

### Phase 4C (Data & Observability)
- `BehaviorEvent` persistence from assistant/user interactions
- Structured logging to external service (Datadog, Sentry, etc.)
- Usage analytics dashboard
- Market data provider redundancy (fallback to alternative if Finnhub unavailable)

### Phase 4D (Social & Compliance)
- Family multi-profile management UI
- Team dashboard for Business plan
- Data export / GDPR compliance tools
- Accessibility audit (WCAG 2.1 AA)

