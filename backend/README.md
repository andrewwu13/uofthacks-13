# Backend

FastAPI backend for the Self-Evolving AI Storefront.

## Structure

- `app/` - Main application
  - `api/` - REST API endpoints
  - `websocket/` - WebSocket handlers
  - `sse/` - Server-Sent Events
  - `models/` - Pydantic models
  - `services/` - Business logic
  - `db/` - Database clients

## Running

```bash
pip install -r requirements.txt
uvicorn app.main:app --reload
```
