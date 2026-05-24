"""POST /recommend エンドポイント."""

from typing import Annotated

from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from ai_service.db import get_db
from ai_service.recommend.dto import RecommendRequest, RecommendResponse
from ai_service.recommend.service import recommend

router = APIRouter(tags=["recommend"])

# モダン FastAPI の Depends パターン（ruff B008 を回避）
DbSession = Annotated[Session, Depends(get_db)]


@router.post("/recommend", response_model=RecommendResponse)
def recommend_endpoint(request: RecommendRequest, db: DbSession) -> RecommendResponse:
    """ユーザー属性から推薦リストを返す（コンテンツベース・属性マッチ）.

    現状はシードされた items から `expires_at` で絞り、スコア順 Top N。
    将来的に協調フィルタリング・埋め込み類似度・LLM 連携と統合予定。
    """
    return recommend(db, request)
