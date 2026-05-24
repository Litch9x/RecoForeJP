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


# --------------------------------------------------------------------------
# Hybrid（content + semantic）
# --------------------------------------------------------------------------


class HybridRecommendRequest(BaseModel):
    """POST /recommend/hybrid のリクエスト本文.

    ``query`` が指定されると意味検索（RECO-23）が有効化される。未指定なら
    コンテンツベース（RECO-21）のみ。
    """

    user: UserContextDTO
    query: str | None = Field(
        default=None, description="意味検索クエリ（未指定ならコンテンツベースのみ）"
    )
    region: str | None = Field(default=None, description="候補アイテムの地域フィルタ（任意）")
    limit: int = Field(default=10, ge=1, le=100)
    weight_content: float = Field(default=0.5, ge=0.0, le=1.0)
    weight_semantic: float = Field(default=0.5, ge=0.0, le=1.0)


class HybridRecommendedItem(BaseModel):
    item_id: str
    title: str | None
    hybrid_score: float
    content_score: float  # 0..1 に正規化済
    semantic_score: float  # 0..1（cosine 類似度）
    reasons: list[str]  # content 側の推薦理由


class HybridRecommendResponse(BaseModel):
    items: list[HybridRecommendedItem]
