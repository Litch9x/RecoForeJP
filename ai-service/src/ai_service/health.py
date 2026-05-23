"""ヘルスチェックエンドポイント.

他サービス（api-gateway, user-service, item-service）と同じレスポンス形式で返す。
"""

from datetime import UTC, datetime

from fastapi import APIRouter

router = APIRouter(tags=["health"])


@router.get("/health")
def health() -> dict[str, str]:
    return {
        "status": "ok",
        "service": "ai-service",
        "timestamp": datetime.now(UTC).isoformat(),
    }
