from pydantic import BaseModel, Field


class IngestionRequest(BaseModel):
    source_name: str = Field(..., min_length=1, max_length=255)
    text: str = Field(..., min_length=1)
    chunk_size: int = Field(default=500, ge=100, le=5000)
    overlap: int = Field(default=50, ge=0, le=500)


class IngestionResponse(BaseModel):
    job_id: int
    status: str
    chunks_count: int
    preview_chunks: list[str]


class IngestionQueuedResponse(BaseModel):
    job_id: int
    status: str

