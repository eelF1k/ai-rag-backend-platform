from typing import Sequence

from chromadb import HttpClient
from chromadb.api.models.Collection import Collection

from app.core.settings import settings


def get_collection(name: str = "documents") -> Collection:
    client = HttpClient(host=settings.chroma_host, port=settings.chroma_port)
    return client.get_or_create_collection(name=name)


def add_documents(ids: Sequence[str], documents: Sequence[str], metadatas: Sequence[dict]):
    collection = get_collection()
    collection.add(ids=list(ids), documents=list(documents), metadatas=list(metadatas))


def query_documents(query_text: str, limit: int = 5):
    collection = get_collection()
    return collection.query(query_texts=[query_text], n_results=limit)
