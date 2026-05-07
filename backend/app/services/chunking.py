import asyncio


class ChunkingService:
    async def chunk_text(self, text: str, chunk_size: int, overlap: int) -> list[str]:
        await asyncio.sleep(0)
        normalized = " ".join(text.split())
        if not normalized:
            return []

        if overlap >= chunk_size:
            overlap = max(0, chunk_size // 5)

        step = max(1, chunk_size - overlap)
        chunks: list[str] = []
        start = 0
        while start < len(normalized):
            end = min(len(normalized), start + chunk_size)
            chunk = normalized[start:end].strip()
            if chunk:
                chunks.append(chunk)
            start += step
        return chunks

