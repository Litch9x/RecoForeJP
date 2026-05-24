"""埋め込みエンドポイントのテスト.

実モデル（sentence-transformers）はロードせず、決定論的な FakeEncoder で動作確認する。
（実モデルは初回ダウンロードが ~110MB かかり CI/開発フィードバックが遅くなるため。）
"""

from ai_service.embedding.encoder import TextEncoder, get_encoder
from ai_service.main import app
from fastapi.testclient import TestClient


class FakeEncoder(TextEncoder):
    """テスト専用：固定値ベクトルを返す（モデルロード不要）."""

    DIMENSION = 4

    def __init__(self) -> None:
        super().__init__(model_name="fake-encoder")

    @property
    def dimension(self) -> int:
        return self.DIMENSION

    def encode(self, texts: list[str], *, mode: str = "passage") -> list[list[float]]:
        # 入力テキストの長さで決定的にスケール（出力検証が容易になる）
        return [[float(len(t) % 10) / 10.0] * self.DIMENSION for t in texts]


client = TestClient(app)


def setup_module() -> None:
    """全テストで FakeEncoder を使う."""
    app.dependency_overrides[get_encoder] = FakeEncoder


def teardown_module() -> None:
    app.dependency_overrides.clear()


def test_embed_passage_returns_normalized_vectors() -> None:
    response = client.post("/embed", json={"texts": ["hello", "world"], "mode": "passage"})

    assert response.status_code == 200
    body = response.json()
    assert body["dimension"] == 4
    assert body["model"] == "fake-encoder"
    assert body["mode"] == "passage"
    assert len(body["vectors"]) == 2
    assert all(len(v) == 4 for v in body["vectors"])


def test_embed_default_mode_is_passage() -> None:
    response = client.post("/embed", json={"texts": ["x"]})
    assert response.status_code == 200
    assert response.json()["mode"] == "passage"


def test_embed_query_mode() -> None:
    response = client.post("/embed", json={"texts": ["search query"], "mode": "query"})
    assert response.status_code == 200
    assert response.json()["mode"] == "query"


def test_embed_empty_texts_returns_422() -> None:
    response = client.post("/embed", json={"texts": [], "mode": "passage"})
    assert response.status_code == 422  # Pydantic min_length=1


def test_embed_too_many_texts_returns_422() -> None:
    response = client.post("/embed", json={"texts": ["x"] * 101, "mode": "passage"})
    assert response.status_code == 422  # max_length=100


def test_embed_invalid_mode_returns_422() -> None:
    response = client.post("/embed", json={"texts": ["x"], "mode": "nonsense"})
    assert response.status_code == 422  # Literal validation


def test_encoder_dimension_is_known_without_loading_model() -> None:
    """TextEncoder.dimension は遅延ロード対象ではなくクラス定数."""
    enc = TextEncoder()  # モデル未ロード
    assert enc.dimension == 384
    assert enc._model is None  # 確認：遅延ロードが効いている
