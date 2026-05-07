# AI Backend Platform (RAG + Async + Observability)

## Назва проєкту
AI Backend Platform (RAG + Async + Observability)

## Це мій пет проєкт про...
Це мій пет проєкт про AI backend-платформу з RAG-пайплайном, асинхронною обробкою, кешуванням і спостережуваністю.

## Технологічний стек
- Python, FastAPI, asyncio
- MySQL, MongoDB, Redis
- ChromaDB
- Docker Compose, Kubernetes
- GitHub Actions, GitLab CI

## Що реалізовано
- API для ingestion, пошуку та RAG-відповідей.
- Векторний retrieval + rerank.
- Кешування через Redis.
- Фоновий worker для ingestion задач.
- Метрики та структуроване логування.

## Структура
- `backend/app/api` — ендпоінти
- `backend/app/services` — бізнес-логіка
- `backend/app/db` — інтеграція з БД
- `backend/app/workers` — фонові воркери
- `infra/` — docker/k8s/ci конфігурація

## Архітектура
- Ingestion зберігає та індексує дані у векторне сховище.
- Search/RAG ендпоінти виконують retrieval та генерацію відповіді.
- Redis використовується як cache-aside шар.
- Метрики та логи відображають стан сервісу.

## Що потрібно встановити для тесту
- Python 3.12+
- Docker Desktop
- (опційно) Kubernetes локальний кластер

## Як запустити
```bash
docker compose up --build
```
Або локально:
```bash
pip install -r requirements.txt
python -m uvicorn app.main:app --app-dir backend --host 127.0.0.1 --port 8000
```

