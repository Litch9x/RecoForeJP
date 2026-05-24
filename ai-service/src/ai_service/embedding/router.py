"""埋め込み関連エンドポイント (/embed, /embeddings/items/{id})."""

from datetime import UTC, datetime
from typing import Annotated
from uuid import UUID

from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from ai_service.db import get_db
from ai_service.embedding.dto import (
    EmbedRequest,
    EmbedResponse,
    UpsertItemEmbeddingRequest,
    UpsertItemEmbeddingResponse,
)
from ai_service.embedding.encoder import TextEncoder, get_encoder
from ai_service.embedding.store import ItemEmbeddingStore

router = APIRouter(tags=["embedding"])

DbSession = Annotated[Session, Depends(get_db)]
EncoderDep = Annotated[TextEncoder, Depends(get_encoder)]


@router.post("/embed", response_model=EmbedResponse)
def embed_texts(request: EmbedRequest, encoder: EncoderDep) -> EmbedResponse:
    """テキスト列を 384 次元の正規化ベクトル列に変換する.

    ``mode``:
    - ``passage``: アイテム説明文など、検索対象側
    - ``query``: 検索クエリ・ユーザー意図側

    モデルは初回呼び出し時にダウンロードされる（約 110MB）。
    """
    vectors = encoder.encode(request.texts, mode=request.mode)
    return EmbedResponse(
        vectors=vectors,
        dimension=encoder.dimension,
        model=encoder.model_name,
        mode=request.mode,
    )


@router.post("/embeddings/items/{item_id}", response_model=UpsertItemEmbeddingResponse)
def upsert_item_embedding(
    item_id: UUID,
    request: UpsertItemEmbeddingRequest,
    db: DbSession,
    encoder: EncoderDep,
) -> UpsertItemEmbeddingResponse:
    """アイテムテキストを埋め込み化して ``ai.item_embeddings`` に upsert."""
    vector = encoder.encode([request.text], mode="passage")[0]
    store = ItemEmbeddingStore(db)
    store.upsert(item_id, vector)
    return UpsertItemEmbeddingResponse(
        item_id=str(item_id),
        dimension=encoder.dimension,
        updated_at=datetime.now(UTC),
    )
