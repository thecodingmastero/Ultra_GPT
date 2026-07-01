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
  - Register/Login endpoints
  - Auth decorator (`auth_required`)
- Portfolio foundation:
  - Holdings model
  - Holdings CRUD endpoints
  - Concentration analysis endpoint
- Educational hub foundation:
  - Lesson model + progress model
  - Lesson list/detail endpoints
  - Lesson progress tracking endpoint
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
- `GET /api/account/me`
- `POST /api/assistant/chat`
- `POST /api/portfolio/analyze`
- `GET /api/portfolio/concentration` (auth)
- `GET /api/holdings` (auth)
- `POST /api/holdings` (auth)
- `PUT /api/holdings/<id>` (auth)
- `DELETE /api/holdings/<id>` (auth)
- `GET /api/market/quote?symbol=AAPL`
- `GET /api/lessons`
- `GET /api/lessons/<id>`
- `POST /api/lessons/<id>/progress` (auth)

## Assistant guardrails

The assistant policy enforces:

- No direct buy/sell directives
- No guaranteed returns
- Education-first framing
- Emphasis on diversification, risk awareness, and long-term principles
- Educational disclaimer appended to responses

## What remains for later phases

- Full OAuth and production-grade account workflows
- Sector allocation and volatility analytics expansion
- Full lesson authoring CMS and quizzes
- Advanced AI/behavioral coaching and Investor Quest module
- Billing and enterprise features
