"""POST /embed エンドポイント."""

from typing import Annotated

from fastapi import APIRouter, Depends

from ai_service.embedding.dto import EmbedRequest, EmbedResponse
from ai_service.embedding.encoder import TextEncoder, get_encoder

router = APIRouter(tags=["embedding"])

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
