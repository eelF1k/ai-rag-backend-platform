from typing import Any

import httpx

from app.core.settings import settings


class LLMService:
    async def generate_answer(self, question: str, contexts: list[dict[str, Any]]) -> dict[str, Any]:
        if settings.llm_provider == "mock":
            return self._mock_answer(question=question, contexts=contexts)

        try:
            text = await self._call_openai_compatible(question=question, contexts=contexts)
            return {"answer": text, "provider": settings.llm_provider, "used_fallback": False}
        except Exception:
            # Graceful fallback keeps endpoint available in dev/local environments.
            fallback = self._mock_answer(question=question, contexts=contexts)
            fallback["provider"] = f"{settings.llm_provider}-fallback"
            fallback["used_fallback"] = True
            return fallback

    async def _call_openai_compatible(self, question: str, contexts: list[dict[str, Any]]) -> str:
        if not settings.llm_api_base or not settings.llm_api_key:
            raise RuntimeError("LLM API base/key are not configured")

        system_prompt = "You are a concise assistant. Use provided context only."
        context_block = "\n\n".join(
            f"[{idx + 1}] {item.get('text', '')}" for idx, item in enumerate(contexts)
        )
        user_prompt = f"Question: {question}\n\nContext:\n{context_block}\n\nAnswer briefly."

        payload = {
            "model": "gpt-4o-mini",
            "messages": [
                {"role": "system", "content": system_prompt},
                {"role": "user", "content": user_prompt},
            ],
            "temperature": 0.2,
        }
        headers = {"Authorization": f"Bearer {settings.llm_api_key}"}

        async with httpx.AsyncClient(timeout=settings.request_timeout_s) as client:
            response = await client.post(
                f"{settings.llm_api_base.rstrip('/')}/chat/completions",
                json=payload,
                headers=headers,
            )
            response.raise_for_status()
            data = response.json()

        return data["choices"][0]["message"]["content"]

    @staticmethod
    def _mock_answer(question: str, contexts: list[dict[str, Any]]) -> dict[str, Any]:
        snippets = [str(item.get("text", ""))[:140] for item in contexts[:3]]
        if snippets:
            answer = (
                f"Mock answer for: '{question}'. "
                f"Relevant context snippets: {' | '.join(snippets)}"
            )
        else:
            answer = f"Mock answer for: '{question}'. No relevant context found."
        return {"answer": answer, "provider": "mock", "used_fallback": False}

