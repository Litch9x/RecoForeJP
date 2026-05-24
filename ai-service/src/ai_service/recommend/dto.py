"""推薦 API の Pydantic モデル."""

from pydantic import BaseModel, Field


class UserContextDTO(BaseModel):
    """推薦対象ユーザーの属性（リクエストから受け取る）。"""

    japanese_level: str | None = Field(default=None, pattern=r"^N[1-5]$")
    region: str | None = None
    preferred_language: str = Field(default="ja", pattern=r"^[a-z]{2}(-[A-Z]{2})?$")
    interest_categories: list[str] = Field(default_factory=list)


class RecommendRequest(BaseModel):
    """POST /recommend のリクエスト本文。"""

    user: UserContextDTO
    region: str | None = Field(default=None, description="候補アイテムの地域フィルタ（任意）")
    limit: int = Field(default=10, ge=1, le=100)


class RecommendedItem(BaseModel):
    id: str
    title: str
    category_slug: str
    region: str | None = None
    score: float
    reasons: list[str]


class RecommendResponse(BaseModel):
    items: list[RecommendedItem]
