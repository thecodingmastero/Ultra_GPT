# The Better Investor — Phase 1 MVP

**Smarter Investing Starts Here.**

The Better Investor is an education-first investing platform. It helps users learn investing fundamentals, evaluate portfolio concentration risk, and ask AI-powered educational questions.

> **Educational only:** This product does **not** provide personalized financial advice.

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

- `POST /api/auth/register`
- `POST /api/auth/login`
- `POST /api/auth/logout`
- `GET /api/account/me`
- `PUT /api/account/me`
- `POST /api/assistant/chat`
- `POST /api/portfolio/analyze`
- `GET /api/portfolio/concentration` (auth)
- `GET /api/holdings` (auth)
- `POST /api/holdings` (auth)
- `PUT /api/holdings/<id>` (auth)
- `DELETE /api/holdings/<id>` (auth)
- `GET /api/market/quote?symbol=AAPL`
- `GET /api/market/profile?symbol=AAPL`
- `GET /api/lessons`
- `GET /api/lessons/<id>`
- `GET /api/lessons/progress` (auth)
- `POST /api/lessons/<id>/progress` (auth)

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

## Assistant guardrails

The assistant policy enforces:

- No direct buy/sell directives
- No guaranteed returns
- Education-first framing
- Emphasis on diversification, risk awareness, and long-term principles
- Educational disclaimer appended to responses

## What remains for later phases

- Full OAuth and production-grade account workflows
- Deeper portfolio analytics (volatility/diversification scoring expansion)
- Full lesson authoring CMS and quizzes
- Advanced AI/behavioral coaching and Investor Quest module
- Billing and enterprise features
