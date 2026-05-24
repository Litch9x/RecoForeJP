"""埋め込み API の Pydantic モデル."""

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
