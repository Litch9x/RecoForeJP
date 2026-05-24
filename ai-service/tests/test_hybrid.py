"""ハイブリッド推薦の統合ロジックテスト.

content と semantic の両方のソース（モック）を渡して、正規化 + 重み付き和の挙動を検証。
"""

from collections.abc import Sequence
from uuid import UUID

from ai_service.embedding.encoder import TextEncoder
from ai_service.embedding.store import NearestItem
from ai_service.recommend.dto import HybridRecommendRequest, UserContextDTO
from ai_service.recommend.hybrid import hybrid_recommend
from ai_service.recommend.scorer import ItemFeatures


class FakeEncoder(TextEncoder):
    DIMENSION = 4

    def __init__(self) -> None:
        super().__init__(model_name="fake")

    @property
    def dimension(self) -> int:
        return self.DIMENSION

    def encode(self, texts: list[str], *, mode: str = "passage") -> list[list[float]]:
        return [[1.0, 0.0, 0.0, 0.0] for _ in texts]


class FakeStore:
    """search.service が呼ぶ ``find_nearest`` のみ実装した最小 fake."""

    def __init__(self, results: list[NearestItem]) -> None:
        self._results = results

    def upsert(self, item_id: UUID | str, embedding: Sequence[float]) -> None:  # noqa: ARG002
        raise NotImplementedError("not used in this test")

    def find_nearest(self, query: Sequence[float], *, limit: int = 10) -> list[NearestItem]:  # noqa: ARG002
        return self._results[:limit]


def _content_candidates() -> list[ItemFeatures]:
    """``recommend.recommend`` が候補取得関数経由で参照する素材。"""
    return [
        ItemFeatures(
            id="item-a",
            title="外国人歓迎エンジニア",
            category_slug="job",
            region="東京都-港区",
            min_japanese_level="N5",
            languages=("ja", "en"),
            tags=("foreigner-welcome",),
        ),
        ItemFeatures(
            id="item-b",
            title="日本語学習教材",
            category_slug="japanese-learning",
            region=None,
            min_japanese_level="N5",
            languages=("ja",),
            tags=(),
        ),
        ItemFeatures(
            id="item-c",
            title="医療情報",
            category_slug="medical",
            region=None,
            min_japanese_level=None,
            languages=("ja",),
            tags=(),
        ),
    ]


def _fake_fetcher(_db, *, region: str | None = None) -> Sequence[ItemFeatures]:  # noqa: ARG001
    return _content_candidates()


def _make_request(
    *, query: str | None = None, weight_content: float = 0.5, weight_semantic: float = 0.5
) -> HybridRecommendRequest:
    return HybridRecommendRequest(
        user=UserContextDTO(
            japanese_level="N3",
            region="東京都-港区",
            preferred_language="en",
            interest_categories=["job", "japanese-learning"],
        ),
        query=query,
        limit=10,
        weight_content=weight_content,
        weight_semantic=weight_semantic,
    )


def test_hybrid_without_query_falls_back_to_content_only():
    """query 未指定なら semantic_score は全件 0 で content のみが効く。"""
    res = hybrid_recommend(
        request=_make_request(query=None),
        db=None,  # type: ignore[arg-type]
        encoder=FakeEncoder(),
        candidate_fetcher=_fake_fetcher,
        store_factory=lambda db: FakeStore([]),  # noqa: ARG005
    )

    assert all(it.semantic_score == 0.0 for it in res.items)
    # content_score は正規化済み (max=1.0)
    assert max(it.content_score for it in res.items) == 1.0
    # 最高 hybrid は content max 相当
    assert res.items[0].hybrid_score == 0.5  # w_content=0.5 * 1.0


def test_hybrid_blends_content_and_semantic_via_weights():
    """semantic で高評価 (0.9) のアイテムが content では弱くてもブレンドで浮上することを確認。"""
    semantic_results = [
        # item-c は content では弱い (medical 興味なし) が semantic では強い
        NearestItem(item_id="item-c", title="医療情報", similarity=0.9),
        NearestItem(item_id="item-a", title="外国人歓迎エンジニア", similarity=0.2),
    ]

    res = hybrid_recommend(
        request=_make_request(query="健康診断 英語", weight_content=0.3, weight_semantic=0.7),
        db=None,  # type: ignore[arg-type]
        encoder=FakeEncoder(),
        candidate_fetcher=_fake_fetcher,
        store_factory=lambda db: FakeStore(semantic_results),  # noqa: ARG005
    )

    by_id = {it.item_id: it for it in res.items}

    # item-c: content_norm ≈ 0 (medical 興味なしで除外され content_resp に入らない)
    #         semantic = 0.9 → hybrid = 0.7 * 0.9 = 0.63
    assert by_id["item-c"].semantic_score == 0.9
    assert by_id["item-c"].content_score == 0.0
    assert by_id["item-c"].hybrid_score == 0.63

    # item-a: content 強 (norm = 1.0) + semantic 0.2 → 0.3 * 1.0 + 0.7 * 0.2 = 0.44
    assert by_id["item-a"].content_score == 1.0
    assert by_id["item-a"].semantic_score == 0.2
    assert abs(by_id["item-a"].hybrid_score - 0.44) < 1e-9

    # semantic 重視の重みなので item-c が item-a より上
    assert res.items[0].item_id == "item-c"


def test_hybrid_respects_limit():
    res = hybrid_recommend(
        request=HybridRecommendRequest(
            user=UserContextDTO(interest_categories=["job", "japanese-learning"]),
            limit=1,
        ),
        db=None,  # type: ignore[arg-type]
        encoder=FakeEncoder(),
        candidate_fetcher=_fake_fetcher,
        store_factory=lambda db: FakeStore([]),  # noqa: ARG005
    )
    assert len(res.items) == 1


def test_hybrid_reasons_propagated_from_content():
    """content 由来の reasons[] が結果に保持される。"""
    res = hybrid_recommend(
        request=_make_request(query=None),
        db=None,  # type: ignore[arg-type]
        encoder=FakeEncoder(),
        candidate_fetcher=_fake_fetcher,
        store_factory=lambda db: FakeStore([]),  # noqa: ARG005
    )
    # 少なくとも 1 件は推薦理由を持つ
    assert any(len(it.reasons) > 0 for it in res.items)
