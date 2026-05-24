"""意味検索エンドポイントのテスト.

DB / 実モデルなしで動作確認するため、FakeEncoder + FakeStore を dependency_overrides で差し替える。
"""

from collections.abc import Sequence
from uuid import UUID

from ai_service.db import get_db
from ai_service.embedding.encoder import TextEncoder, get_encoder
from ai_service.embedding.store import NearestItem
from ai_service.main import app
from fastapi.testclient import TestClient


class FakeEncoder(TextEncoder):
    DIMENSION = 4

    def __init__(self) -> None:
        super().__init__(model_name="fake")

    @property
    def dimension(self) -> int:
        return self.DIMENSION

    def encode(self, texts: list[str], *, mode: str = "passage") -> list[list[float]]:
        return [[float(len(t) % 10) / 10.0] * self.DIMENSION for t in texts]


class FakeStore:
    """ItemEmbeddingStore と同じ shape の Duck-typed fake."""

    DIMENSION = 4

    def __init__(self) -> None:
        self.last_query: Sequence[float] | None = None
        self.upserts: list[tuple[str, list[float]]] = []

    def upsert(self, item_id: UUID | str, embedding: Sequence[float]) -> None:
        self.upserts.append((str(item_id), list(embedding)))

    def find_nearest(self, query: Sequence[float], *, limit: int = 10) -> list[NearestItem]:
        self.last_query = list(query)
        # 決定論的な fake 結果（query には依存しない）
        results = [
            NearestItem(
                item_id="10000000-0000-0000-0000-000000000001",
                title="外国人歓迎エンジニア",
                similarity=0.92,
            ),
            NearestItem(
                item_id="20000000-0000-0000-0000-000000000001",
                title="渋谷区アパート",
                similarity=0.85,
            ),
        ]
        return results[:limit]


# モジュールごとに dependency overrides を仕込む
_fake_store = FakeStore()


def _fake_db():
    """get_db のオーバーライド先。実 DB を返さず、ItemEmbeddingStore のコンストラクタが
    受け取れる任意のオブジェクトを返せばよい（ここでは None）。"""
    yield None  # type: ignore[misc]


def setup_module() -> None:
    app.dependency_overrides[get_encoder] = FakeEncoder
    app.dependency_overrides[get_db] = _fake_db

    # ItemEmbeddingStore を組み立てる箇所がいくつかあるので、
    # クラスごと差し替えるのではなく、ルーター側で db -> FakeStore を生成するよう
    # search.router.search_items_endpoint をパッチ
    import ai_service.search.router as search_router_module

    # 元の関数を保存
    search_router_module._original_search = search_router_module.search_items_endpoint  # type: ignore[attr-defined]

    # ルーター関数を直接書き換えるのは難しいので、search_items_endpoint 内で生成する
    # ItemEmbeddingStore をパッチする方が楽だが、今は ItemEmbeddingStore コンストラクタを
    # 差し替えるアプローチを取る。
    search_router_module.ItemEmbeddingStore = lambda db: _fake_store  # type: ignore[assignment]

    # embedding/router でも同様にパッチ（upsert テスト用）
    import ai_service.embedding.router as embed_router_module

    embed_router_module.ItemEmbeddingStore = lambda db: _fake_store  # type: ignore[assignment]


def teardown_module() -> None:
    app.dependency_overrides.clear()
    # パッチを戻す
    import ai_service.embedding.router as embed_router_module
    import ai_service.search.router as search_router_module
    from ai_service.embedding.store import ItemEmbeddingStore as RealStore

    search_router_module.ItemEmbeddingStore = RealStore  # type: ignore[assignment]
    embed_router_module.ItemEmbeddingStore = RealStore  # type: ignore[assignment]


client = TestClient(app)


def test_semantic_search_returns_results_with_similarity_sorted_by_caller() -> None:
    response = client.post("/search/items", json={"query": "ベトナム語が話せる仕事", "limit": 10})

    assert response.status_code == 200
    body = response.json()
    assert body["query"] == "ベトナム語が話せる仕事"
    assert len(body["results"]) == 2
    assert body["results"][0]["similarity"] == 0.92
    # fake store はクエリベクトルを記録している
    assert _fake_store.last_query is not None
    assert len(_fake_store.last_query) == 4


def test_semantic_search_respects_limit() -> None:
    response = client.post("/search/items", json={"query": "x", "limit": 1})
    assert response.status_code == 200
    assert len(response.json()["results"]) == 1


def test_semantic_search_empty_query_returns_422() -> None:
    response = client.post("/search/items", json={"query": "", "limit": 10})
    assert response.status_code == 422


def test_upsert_item_embedding_returns_dimension_and_stores() -> None:
    item_id = "10000000-0000-0000-0000-000000000abc"
    response = client.post(
        f"/embeddings/items/{item_id}",
        json={"text": "Test item"},
    )

    assert response.status_code == 200
    body = response.json()
    assert body["item_id"] == item_id
    assert body["dimension"] == 4
    # fake store に upsert が記録されている
    assert any(uid == item_id for uid, _ in _fake_store.upserts)


def test_upsert_item_embedding_empty_text_returns_422() -> None:
    response = client.post(
        "/embeddings/items/10000000-0000-0000-0000-000000000abc",
        json={"text": ""},
    )
    assert response.status_code == 422


def test_upsert_item_embedding_invalid_uuid_returns_422() -> None:
    response = client.post(
        "/embeddings/items/not-a-uuid",
        json={"text": "x"},
    )
    assert response.status_code == 422
