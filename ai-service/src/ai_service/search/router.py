"""POST /search/items エンドポイント."""

from typing import Annotated

from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from ai_service.db import get_db
from ai_service.embedding.encoder import TextEncoder, get_encoder
from ai_service.embedding.store import ItemEmbeddingStore
from ai_service.search.dto import SemanticSearchRequest, SemanticSearchResponse
from ai_service.search.service import search_items

router = APIRouter(tags=["search"])

DbSession = Annotated[Session, Depends(get_db)]
EncoderDep = Annotated[TextEncoder, Depends(get_encoder)]


@router.post("/search/items", response_model=SemanticSearchResponse)
def search_items_endpoint(
    request: SemanticSearchRequest,
    db: DbSession,
    encoder: EncoderDep,
) -> SemanticSearchResponse:
    """意味検索：自然言語クエリ → 近いアイテム top N（cosine 類似度）.

    事前に ``POST /embeddings/items/{item_id}`` で対象アイテムの埋め込みを保存して
    おく必要がある。Pgvector の HNSW インデックスを使った近似最近傍検索。
    """
    store = ItemEmbeddingStore(db)
    return search_items(query=request.query, limit=request.limit, encoder=encoder, store=store)
