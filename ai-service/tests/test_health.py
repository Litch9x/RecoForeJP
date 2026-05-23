"""ヘルスチェックエンドポイントのテスト."""

from ai_service.main import app
from fastapi.testclient import TestClient

client = TestClient(app)


def test_health_returns_ok_status() -> None:
    response = client.get("/health")

    assert response.status_code == 200
    data = response.json()
    assert data["status"] == "ok"
    assert data["service"] == "ai-service"
    assert "timestamp" in data


def test_health_timestamp_is_iso_format() -> None:
    """timestamp が ISO 8601 形式（UTC）で返ること."""
    from datetime import datetime

    response = client.get("/health")
    ts = response.json()["timestamp"]
    # parse できれば OK（例外なし）
    parsed = datetime.fromisoformat(ts)
    assert parsed is not None
