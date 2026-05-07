# AI Backend Platform (RAG + Async + Observability)

Backend pet-проєкт Python Backend Engineer.

## Мета
Побудувати й масштабувати AI-орієнтовані backend-сервіси з:
- FastAPI + asyncio
- REST API + внутрішні/зовнішні інтеграції
- RAG-пайплайном (retrieve -> rerank -> generate)
- векторним пошуком ChromaDB
- MySQL + MongoDB
- кешуванням через Redis
- retry, timeout і обробкою помилок
- метриками, логами, трасуванням
- Docker + CI/CD (+ Kubernetes маніфести як бонус)

## Заплановані модулі
- `backend/app/api` - REST ендпоінти
- `backend/app/rag` - оркестрація RAG і retrieval
- `backend/app/services` - бізнес-логіка та async-потоки
- `backend/app/db` - адаптери MySQL + MongoDB
- `backend/app/observability` - метрики/логування/трасування
- `backend/app/workers` - фонові задачі та черги
- `infra/` - docker-compose, CI, k8s маніфести
- `docs/` - архітектура, runbook, API, нотатки з продуктивності

## Стек (цільовий)
- Python, FastAPI, asyncio
- MySQL, MongoDB
- ChromaDB (з можливістю додати Qdrant adapter пізніше)
- Redis
- OpenAI-compatible LLM провайдер (з mock fallback)
- Prometheus метрики, structured logging, OpenTelemetry tracing
- Docker Compose, GitHub Actions, приклад gitlab-ci

## Запуск через Docker
```bash
docker compose up --build
```

Сервіси:
- API: `http://localhost:8000`
- Документація API: `http://localhost:8000/docs`
- MySQL: `localhost:3306`
- MongoDB: `localhost:27017`
- Redis: `localhost:6379`
- ChromaDB HTTP: `localhost:8001`

## Швидкі перевірки
- `GET /` -> метадані сервісу
- `GET /api/v1/health` -> статус health
- `GET /api/v1/ready` -> статус readiness
- `GET /api/v1/metrics` -> метрики Prometheus
- `POST /api/v1/ingestion/text` -> async ingestion і chunking тексту
- `POST /api/v1/ingestion/text/async` -> постановка ingestion задачі у фонову чергу
- `GET /api/v1/search?q=...` -> векторний retrieval з ChromaDB
- `POST /api/v1/rag/answer` -> retrieval + rerank + відповідь LLM (mock fallback)

Нотатки:
- Відповіді search/rerank/rag використовують Redis cache (cache-aside, TTL через `CACHE_TTL_S`).
- Фоновий ingestion worker працює як сервіс `worker` у Docker Compose.

Load smoke:
- `python backend/tools/load_smoke.py --base-url http://127.0.0.1:8000 --requests 30 --concurrency 10`

CI/CD:
- GitHub Actions pipeline: `.github/workflows/ci.yml`
- Приклад GitLab CI: `gitlab-ci.yml`

Kubernetes:
- Маніфести: `infra/k8s/` (`config.yaml`, `workloads.yaml`, `services.yaml`)
- Швидкий деплой: `kubectl apply -k infra/k8s`
- Гайд: `docs/k8s-deploy.md`

## Локальний запуск без Docker
```bash
pip install -r requirements.txt
python -m uvicorn app.main:app --app-dir backend --host 127.0.0.1 --port 8000
```

## Production readiness checklist
- Перевірити доступність MySQL/MongoDB/Redis/Chroma до старту API.
- Встановити реальні `LLM_API_KEY` та обмеження timeout/retry.
- Увімкнути централізований збір логів і метрик.
- Прогнати load smoke перед релізом і зафіксувати базові SLO-метрики.

## Що показати на співбесіді
- Як працює ланцюжок `ingestion -> retrieval -> rerank -> answer`.
- Як кешування та retries знижують latency та кількість помилок.
- Як метрики `latency/error` допомагають знайти bottleneck у проді.

