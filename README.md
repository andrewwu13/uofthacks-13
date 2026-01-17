# Gen UI - Self-Evolving AI Storefront

A web application that continuously evolves its UI/UX based on real-time customer behavior analysis.

## Quick Start

```bash
# Start all services with Docker
cd docker
docker-compose up -d

# Or run locally:

# Backend
cd backend
pip install -r requirements.txt
uvicorn app.main:app --reload

# Frontend
cd frontend
npm install
npm run dev
```

## Architecture

See [docs/architecture.md](docs/architecture.md) for detailed system architecture.

## Project Structure

```
├── frontend/          # React + Vite application
├── backend/           # FastAPI server
├── agents/            # LangGraph multi-agent system
├── workers/           # Background workers (Kafka consumers)
├── cache/             # Caching layer (Redis, semantic)
├── integrations/      # Third-party integrations
├── shared/            # Shared utilities
├── docker/            # Docker configuration
└── docs/              # Documentation
```

## Environment Variables

Copy `.env.example` to `.env` and configure:

```bash
cp .env.example .env
```

Required variables:
- `OPENAI_API_KEY` - For LLM agents
- `SHOPIFY_*` - Shopify integration
- `REDIS_URL` - Redis connection
- `MONGODB_URL` - MongoDB connection

## License

See [LICENSE.md](LICENSE.md)