# Gen UI - The Self-Evolving AI Storefront

A web application that continuously evolves its UI/UX based on real-time customer behavior analysis.

## 🚀 Quick Start

### Option 1: Docker (Recommended)

```bash
# Start all infrastructure services
docker-compose up redis mongodb -d

# Verify services are running
docker ps
```

### Option 2: Local Development

**Prerequisites:**
- Python 3.11+
- Node.js 18+
- Redis running on `localhost:6379`
- MongoDB running on `localhost:27017`

```bash
# 1. Backend Setup
cd backend
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate
pip install -r requirements.txt

# Start backend server
venv/bin/uvicorn app.main:app --reload

# 2. Frontend Setup (new terminal)
cd frontend
npm install
npm run dev
```

### Option 3: Full Docker Stack

```bash
# Build and start all services (frontend, backend, workers, redis, mongodb, redpanda)
docker-compose up -d

# View logs
docker-compose logs -f backend
```

---

## 🧪 Running Tests

```bash
# Backend unit tests
cd backend
PYTHONPATH=. venv/bin/python -m pytest tests/ -v

# E2E Pipeline test
PYTHONPATH=. venv/bin/python scripts/test_pipeline_e2e.py
```

---

## 🏗️ Architecture

```
┌─────────────────────────────────────────────────────────────────┐
│                        FRONTEND (React)                         │
├─────────────────────────────────────────────────────────────────┤
│  Tracking Layer          Schema Renderer         Realtime       │
│  ┌─────────────┐        ┌──────────────┐      ┌─────────────┐   │
│  │ Mouse/Touch │───────▶│ JSON Layout  │◀─────│ WebSocket   │   │
│  │ Scroll/Int  │        │ → Components │      │ / SSE       │   │
│  └─────────────┘        └──────────────┘      └─────────────┘   │
└────────────┬─────────────────────────────────────────▲──────────┘
             │ Events                                  │ Layout
             ▼                                         │
┌─────────────────────────────────────────────────────────────────┐
│                        BACKEND (FastAPI)                        │
├─────────────────────────────────────────────────────────────────┤
│  POST /telemetry/events ──▶ Pipeline ──▶ Layout Schema          │
│                              │                                  │
│              ┌───────────────┼───────────────┐                  │
│              ▼               ▼               ▼                  │
│          Redis           MongoDB        Vector DB               │
│        (session)        (cold store)   (pref drift)             │
└─────────────────────────────────────────────────────────────────┘
```

See [AGENTS.md](AGENTS.md) for detailed agent architecture.

---

## 📁 Project Structure

```
├── frontend/              # React + Vite application
│   ├── src/tracking/      # Telemetry trackers (mouse, scroll, interactions)
│   ├── src/modules/       # UI component modules
│   └── src/schema/        # Schema-driven rendering
├── backend/               # FastAPI server
│   ├── app/api/           # REST endpoints
│   ├── app/pipeline/      # Post-Reducer DB Pipeline
│   ├── app/models/        # Pydantic models
│   └── app/db/            # Redis, MongoDB, Vector clients
├── agents/                # LangGraph multi-agent system
├── docker-compose.yml     # Docker services configuration
└── AGENTS.md              # Agent architecture documentation
```

---

## ⚙️ Environment Variables

Copy `.env.example` to `.env` and configure:

```bash
cp .env.example .env
```

| Variable | Description | Default |
|----------|-------------|---------|
| `OPENAI_API_KEY` | OpenAI API key for LLM agents | Required |
| `REDIS_URL` | Redis connection string | `redis://localhost:6379` |
| `MONGODB_URL` | MongoDB connection string | `mongodb://localhost:27017` |
| `MONGODB_DB` | MongoDB database name | `uofthacks` |

---

## 📡 API Endpoints

| Endpoint | Method | Description |
|----------|--------|-------------|
| `/telemetry/events` | POST | Receive batched telemetry events |
| `/health` | GET | Health check |
| `/stream/{session_id}` | GET | SSE layout updates |
| `/ws/{session_id}` | WebSocket | Real-time bidirectional |

---

## License

See [LICENSE.md](LICENSE.md)