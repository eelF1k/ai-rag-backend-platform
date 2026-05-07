from pydantic import BaseModel, Field


class RAGAnswerRequest(BaseModel):
    question: str = Field(..., min_length=2, max_length=2000)
    top_k: int = Field(default=5, ge=1, le=20)
    strategy: str = Field(default="hybrid", pattern="^(hybrid|lexical)$")


class RAGAnswerResponse(BaseModel):
    answer: str
    provider: str
    used_fallback: bool
    contexts_used: int
    contexts: list[dict]

