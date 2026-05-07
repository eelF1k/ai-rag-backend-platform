import pytest

from app.workers.ingestion_worker import process_next_message


@pytest.mark.asyncio
async def test_worker_processes_single_message(monkeypatch):
    async def fake_pop(self, timeout_s: int = 5):
        _ = (self, timeout_s)
        return {
            "job_id": 7,
            "source_name": "doc-1",
            "text": "text for chunking",
            "chunk_size": 500,
            "overlap": 50,
        }

    called = {"processed": False}

    async def fake_process_ingestion(job_id: int, payload):
        _ = payload
        called["processed"] = job_id == 7
        return {"chunks": ["a"], "indexed": 1}

    monkeypatch.setattr("app.services.queue.QueueService.pop_ingestion", fake_pop)
    monkeypatch.setattr("app.workers.ingestion_worker.process_ingestion", fake_process_ingestion)

    processed = await process_next_message()
    assert processed is True
    assert called["processed"] is True

