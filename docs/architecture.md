# System Architecture

This document describes the architecture of the Self-Evolving AI Storefront.

## Overview

```mermaid
flowchart TB
    subgraph Frontend["Frontend (React)"]
        TR[Tracking Layer]
        SR[Schema Renderer]
        WS[WebSocket Client]
    end

    subgraph Backend["Backend (FastAPI)"]
        EA[Event API]
        LA[Layout API]
        WSS[WebSocket Server]
    end

    subgraph Agents["Agent Layer (LangGraph)"]
        S1[Motor State Stream]
        S2[Context Analyst]
        S3[Variance Auditor]
        SA[Stability Agent]
        XA[Exploratory Agent]
    end

    subgraph Data["Data Layer"]
        RD[(Redis)]
        MG[(MongoDB)]
        VD[(Vector DB)]
    end

    subgraph Queue["Event Streaming"]
        KF[Kafka/RedPanda]
    end

    TR --> EA
    EA --> KF
    KF --> S1 & S2 & S3
    S1 & S2 & S3 --> SA & XA
    SA & XA --> LA
    LA --> WSS
    WSS --> SR
    
    S1 -.-> RD
    SA & XA --> RD
    SA & XA --> MG
    SA & XA --> VD
```

## Data Flow

1. **Tracking** → Frontend collects mouse/touch telemetry
2. **Ingestion** → Events batched and sent to Event API
3. **Streaming** → Events published to Kafka/RedPanda
4. **Processing** → Three streams analyze telemetry in parallel
5. **Generation** → Stability + Exploratory agents produce layouts
6. **Delivery** → Layouts pushed via WebSocket/SSE
7. **Rendering** → Frontend renders schema-driven components

## Three-Stream Processing

| Stream | Frequency | Purpose | Cost |
|--------|-----------|---------|------|
| Motor State | ~100ms | Velocity/acceleration analysis | $0 |
| Context Analyst | 5s batch | Correlate state + UI interactions | Low |
| Variance Auditor | 5s batch | Evaluate "loud" module responses | Low |

## Caching Strategy

- **Redis**: Session state, motor state, layout hash
- **Semantic Cache**: Embedding-based LLM response cache
- **Layout Cache**: JSON directives by page + device type
