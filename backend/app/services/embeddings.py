import hashlib
from concurrent.futures import ThreadPoolExecutor
from typing import Any

from app.db.chroma import add_documents, query_documents

_executor = ThreadPoolExecutor(max_workers=4)


class EmbeddingsService:
    async def index_chunks(self, source_name: str, chunks: list[str]) -> dict[str, Any]:
        ids = [self._chunk_id(source_name, idx, chunk) for idx, chunk in enumerate(chunks)]
        metadatas = [{"source_name": source_name, "chunk_index": idx} for idx, _ in enumerate(chunks)]

        loop = __import__("asyncio").get_running_loop()
        await loop.run_in_executor(_executor, add_documents, ids, chunks, metadatas)

        return {
            "indexed": len(chunks),
            "ids": ids,
        }

    async def search(self, query: str, limit: int = 5) -> dict[str, Any]:
        loop = __import__("asyncio").get_running_loop()
        result = await loop.run_in_executor(_executor, query_documents, query, limit)
        return result

    @staticmethod
    def _chunk_id(source_name: str, idx: int, text: str) -> str:
        digest = hashlib.sha256(f"{source_name}:{idx}:{text}".encode("utf-8")).hexdigest()[:16]
        return f"{source_name}-{idx}-{digest}"
