# API Reference

## Base URL

```
http://localhost:8000/api
```

## Endpoints

### Layout

#### GET /layout
Get current layout for a session.

**Query Parameters:**
- `session_id` (required): Session ID
- `page` (optional): Page type (default: "home")

**Response:**
```json
{
  "version": "1.0.0",
  "session_id": "abc123",
  "timestamp": 1705500000,
  "sections": [...]
}
```

#### POST /layout/refresh
Force regenerate layout for a session.

---

### Events

#### POST /events
Ingest a batch of telemetry events.

**Body:**
```json
{
  "session_id": "abc123",
  "device_type": "desktop",
  "timestamp": 1705500000,
  "events": [...]
}
```

---

### Session

#### POST /session
Create a new session.

#### GET /session/{session_id}
Get session details.

#### DELETE /session/{session_id}
End a session.

---

### Products

#### GET /products
List products.

#### GET /products/{product_id}
Get single product.

---

## WebSocket

**URL:** `ws://localhost:8000/ws?session_id={session_id}`

**Messages:**
- `layout_update` - New layout available
- `preference_update` - Preferences changed
- `ping` / `pong` - Heartbeat
