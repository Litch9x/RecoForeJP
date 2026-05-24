"""LLM 関連 API の Pydantic モデル."""

from pydantic import BaseModel, Field


class ExplainRequest(BaseModel):
    """POST /explain のリクエスト本文."""

    item_title: str = Field(min_length=1, max_length=255)
    user_context: str | None = Field(
        default=None,
        max_length=500,
        description="ユーザー状況の簡潔な記述（例: 'N5 ベトナム人留学生'）",
    )
    reasons: list[str] = Field(
        default_factory=list,
        max_length=20,
        description="recommender が出した推薦理由（英語混じり可）",
    )


class ExplainResponse(BaseModel):
    text: str
    provider: str  # "openai" / "template" / etc.
