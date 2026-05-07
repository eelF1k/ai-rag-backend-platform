import pytest

from app.services.llm import LLMService


@pytest.mark.asyncio
async def test_llm_service_fallback_on_provider_failure(monkeypatch):
    async def fake_call_with_retry(self, question: str, contexts: list[dict]):
        _ = (self, question, contexts)
        raise RuntimeError("provider down")

    monkeypatch.setattr("app.services.llm.settings.llm_provider", "openai")
    monkeypatch.setattr("app.services.llm._llm_breaker.allow", lambda: True)
    monkeypatch.setattr("app.services.llm.LLMService._call_with_retry", fake_call_with_retry)

    result = await LLMService().generate_answer("hello", [{"text": "ctx"}])

    assert result["used_fallback"] is True
    assert "fallback" in result["provider"]
    assert "Mock answer" in result["answer"]


@pytest.mark.asyncio
async def test_llm_service_circuit_open_returns_fallback(monkeypatch):
    monkeypatch.setattr("app.services.llm.settings.llm_provider", "openai")
    monkeypatch.setattr("app.services.llm._llm_breaker.allow", lambda: False)

    result = await LLMService().generate_answer("hello", [{"text": "ctx"}])

    assert result["used_fallback"] is True
    assert "circuit-open" in result["provider"]

