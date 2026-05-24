"""埋め込み API の Pydantic モデル."""

from datetime import datetime
from typing import Literal

from pydantic import BaseModel, Field


class EmbedRequest(BaseModel):
    """POST /embed のリクエスト本文."""

    texts: list[str] = Field(min_length=1, max_length=100)
    mode: Literal["passage", "query"] = "passage"


class EmbedResponse(BaseModel):
    vectors: list[list[float]]
    dimension: int
    model: str
    mode: Literal["passage", "query"]


class UpsertItemEmbeddingRequest(BaseModel):
    """POST /embeddings/items/{item_id} のリクエスト本文."""

    text: str = Field(min_length=1, description="埋め込み生成元テキスト（title + description 等）")


class UpsertItemEmbeddingResponse(BaseModel):
    item_id: str
    dimension: int
    updated_at: datetime
