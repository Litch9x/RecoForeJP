"""推薦エンドポイント (/recommend, /recommend/hybrid)."""

from typing import Annotated

from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from ai_service.db import get_db
from ai_service.embedding.encoder import TextEncoder, get_encoder
from ai_service.embedding.store import ItemEmbeddingStore
from ai_service.recommend.dto import (
    HybridRecommendRequest,
    HybridRecommendResponse,
    RecommendRequest,
    RecommendResponse,
)
from ai_service.recommend.hybrid import hybrid_recommend
from ai_service.recommend.service import recommend

router = APIRouter(tags=["recommend"])

# モダン FastAPI の Depends パターン（ruff B008 を回避）
DbSession = Annotated[Session, Depends(get_db)]
EncoderDep = Annotated[TextEncoder, Depends(get_encoder)]


@router.post("/recommend", response_model=RecommendResponse)
def recommend_endpoint(request: RecommendRequest, db: DbSession) -> RecommendResponse:
    """ユーザー属性から推薦リストを返す（コンテンツベース・属性マッチ）.

    シードされた items から `expires_at` で絞り、スコア順 Top N。
    意味検索もブレンドしたい場合は :py:func:`hybrid_endpoint` を使う。
    """
    return recommend(db, request)


@router.post("/recommend/hybrid", response_model=HybridRecommendResponse)
def hybrid_endpoint(
    request: HybridRecommendRequest,
    db: DbSession,
    encoder: EncoderDep,
) -> HybridRecommendResponse:
    """コンテンツベース推薦と意味検索を **正規化 → 重み付き和** で統合する（論文 3.3.3）.

    ``query`` が指定されると意味検索が有効化される。未指定ならコンテンツベースのみ。
    意味検索を効かせるには事前に ``POST /embeddings/items/{id}`` で
    対象アイテムの埋め込みを保存しておく必要がある。
    """
    return hybrid_recommend(
        request=request,
        db=db,
        encoder=encoder,
        store_factory=ItemEmbeddingStore,
    )
