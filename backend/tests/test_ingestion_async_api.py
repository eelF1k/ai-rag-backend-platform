from fastapi.testclient import TestClient

from app.main import app


def test_ingestion_async_enqueue(monkeypatch):
    class FakeJob:
        id = 321

    async def fake_create(self, source_name: str):
        _ = (self, source_name)
        return FakeJob()

    captured = {}

    async def fake_enqueue(self, message: dict):
        _ = self
        captured.update(message)

    async def fake_audit_add(self, actor: str, action: str, payload: dict):
        _ = (self, actor, action, payload)
        return None

    monkeypatch.setattr("app.repositories.ingestion_jobs.IngestionJobRepository.create", fake_create)
    monkeypatch.setattr("app.services.queue.QueueService.enqueue_ingestion", fake_enqueue)
    monkeypatch.setattr("app.repositories.audit_events.AuditEventRepository.add", fake_audit_add)

    with TestClient(app) as client:
        response = client.post(
            "/api/v1/ingestion/text/async",
            json={"source_name": "doc", "text": "hello world"},
        )

    assert response.status_code == 200
    assert response.json() == {"job_id": 321, "status": "queued"}
    assert captured["job_id"] == 321
    assert captured["source_name"] == "doc"

