"""意味検索 API の Pydantic モデル."""

from pydantic import BaseModel, Field


class SemanticSearchRequest(BaseModel):
    """POST /search/items のリクエスト."""

    query: str = Field(min_length=1, max_length=2000, description="自然言語クエリ")
    limit: int = Field(default=10, ge=1, le=100)


class SearchResultItem(BaseModel):
    item_id: str
    title: str | None
    similarity: float


class SemanticSearchResponse(BaseModel):
    query: str
    results: list[SearchResultItem]
