# AI Backend Platform (RAG + Async + Observability)

Backend-first pet project to match Python Backend Engineer requirements for AI products.

## Goal
Build and scale AI-oriented backend services with:
- FastAPI + asyncio
- REST API + internal/external integrations
- RAG pipeline (retrieve -> rerank -> generate)
- ChromaDB vector search
- MySQL + MongoDB
- Redis caching
- retries, timeouts, error handling
- metrics, logs, tracing
- Docker + CI/CD (+ Kubernetes manifests as bonus)

## Planned modules
- `backend/app/api` - REST endpoints
- `backend/app/rag` - RAG orchestration and retrieval
- `backend/app/services` - business logic and async workflows
- `backend/app/db` - MySQL + MongoDB adapters
- `backend/app/observability` - metrics/logging/tracing
- `backend/app/workers` - background jobs and queues
- `infra/` - docker-compose, CI, k8s manifests
- `docs/` - architecture, runbook, API, performance notes

## Stack (target)
- Python, FastAPI, asyncio
- MySQL, MongoDB
- ChromaDB (and optional Qdrant adapter later)
- Redis
- OpenAI-compatible LLM provider (with mock fallback)
- Prometheus metrics, structured logging, OpenTelemetry tracing
- Docker Compose, GitHub Actions, gitlab-ci example

## Roadmap (commit by commit)
0. Init repository and architecture skeleton
1. FastAPI scaffold + config + health endpoints
2. Docker compose (api + mysql + mongo + redis + chroma)
3. Async DB layer (MySQL + Mongo) and repository pattern
4. Document ingestion API + chunking
5. Embeddings service + Chroma indexing
6. Retrieval API + rerank stage
7. RAG answer endpoint with LLM + fallback mock
8. Retries/timeouts/circuit-breaker patterns
9. Caching layer (Redis) + query optimization
10. Observability (metrics + logs + tracing)
11. Background workers (Redis streams or queue)
12. Tests (unit + integration) and load smoke
13. CI/CD (GitHub Actions + gitlab-ci.yml)
14. k8s manifests + docs polish

## Run with Docker
```bash
docker compose up --build
```

Services:
- API: `http://localhost:8000`
- API docs: `http://localhost:8000/docs`
- MySQL: `localhost:3306`
- MongoDB: `localhost:27017`
- Redis: `localhost:6379`
- ChromaDB HTTP: `localhost:8001`

## Quick checks
- `GET /` -> service metadata
- `GET /api/v1/health` -> health status
- `GET /api/v1/ready` -> readiness status
- `POST /api/v1/ingestion/text` -> async text chunking ingestion
- `GET /api/v1/search?q=...` -> vector retrieval from ChromaDB

