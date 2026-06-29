# The Better Investor — Phase 1 MVP

**Slogan:** _Smarter Investing Starts Here._

The Better Investor is an education-first investing assistant and portfolio learning platform for beginner and intermediate investors. This MVP focuses on learning support, market awareness, and portfolio analysis without providing personalized financial advice.

## What is included

- React + TypeScript frontend scaffold with routes for landing, assistant, portfolio, market, learn, pricing, account, login, and register pages
- Flask backend app factory with modular blueprints
- Config-driven provider architecture for AI and market data services
- SQLAlchemy model scaffold for users, portfolios, holdings, watchlists, and chat history
- Educational assistant guardrails and disclaimer handling
- Finnhub-backed market quote endpoint and portfolio analysis endpoint
- Baseline pytest coverage for key routes and services

## Local setup

### Backend

```bash
python -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
flask --app main:app run --debug
```

The API runs on `http://127.0.0.1:5000` by default.

### Frontend

```bash
cd frontend
npm install
npm run dev
```

The Vite frontend runs on `http://127.0.0.1:5173` by default.

## Environment variables

Create your own environment file locally and set the following values:

```bash
SECRET_KEY=replace-me
JWT_SECRET_KEY=replace-me
DATABASE_URL=sqlite:///instance/better_investor.db
AI_PROVIDER=openai
MARKET_DATA_PROVIDER=finnhub
OPENAI_API_KEY=replace-me
OPENAI_MODEL=gpt-4.1-mini
FINNHUB_API_KEY=replace-me
VITE_API_BASE_URL=http://127.0.0.1:5000
```

## Database and migrations

This project uses SQLAlchemy and Flask-Migrate (Alembic under the hood).

```bash
flask --app main:app db upgrade -d backend/migrations
```

If you need to regenerate the initial migration scaffold locally:

```bash
flask --app main:app db init -d backend/migrations
flask --app main:app db migrate -d backend/migrations -m "initial schema"
flask --app main:app db upgrade -d backend/migrations
```

## API overview

- `GET /health`
- `POST /api/auth/register`
- `POST /api/auth/login`
- `GET /api/account/me`
- `POST /api/assistant/chat`
- `POST /api/portfolio/analyze`
- `GET /api/market/quote?symbol=AAPL`

## Product guardrails

- Educational use only; not financial advice
- No guaranteed returns
- No direct buy/sell directives
- Encourage diversification, long-term investing, and emotional discipline
- If users request direct recommendations, the assistant responds with an educational framework instead
