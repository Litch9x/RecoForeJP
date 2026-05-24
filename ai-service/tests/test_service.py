"""service.recommend のテスト：repository を fake に差し替え、DB 非依存で動作確認."""

from collections.abc import Sequence

from ai_service.recommend.dto import RecommendRequest, UserContextDTO
from ai_service.recommend.scorer import ItemFeatures
from ai_service.recommend.service import recommend


def _items() -> list[ItemFeatures]:
    return [
        ItemFeatures(
            id="a",
            title="外国人歓迎エンジニア",
            category_slug="job",
            region="東京都-港区",
            min_japanese_level="N5",
            languages=("ja", "en"),
            tags=("foreigner-welcome", "english-ok"),
        ),
        ItemFeatures(
            id="b",
            title="ベトナム語OK アルバイト",
            category_slug="job",
            region="東京都-渋谷区",
            min_japanese_level="N4",
            languages=("ja", "vi"),
            tags=("vietnamese-ok",),
        ),
        ItemFeatures(
            id="c",
            title="N1 専門職",
            category_slug="job",
            region="東京都-千代田区",
            min_japanese_level="N1",  # ユーザー N3 では除外される
            languages=("ja",),
            tags=(),
        ),
        ItemFeatures(
            id="d",
            title="N3 住居（マッチしない地域）",
            category_slug="housing",  # 興味外
            region="北海道-札幌市",
            min_japanese_level=None,
            languages=("ja",),
            tags=(),
        ),
    ]


def _fake_fetcher(_db, *, region: str | None = None) -> Sequence[ItemFeatures]:  # noqa: ARG001
    return _items()


def test_recommend_filters_by_japanese_level_and_sorts_by_score():
    req = RecommendRequest(
        user=UserContextDTO(
            japanese_level="N3",
            region="東京都-港区",
            preferred_language="en",
            interest_categories=["job"],
        ),
        limit=10,
    )

    res = recommend(db=None, request=req, candidate_fetcher=_fake_fetcher)  # type: ignore[arg-type]

    ids = [it.id for it in res.items]
    # item "c" は N1 要求で除外
    assert "c" not in ids
    # item "d" は category=housing で興味なし & 地域・言語マッチもないので score=0 → 除外
    assert "d" not in ids
    # 最高スコアは "a"（category + region + language + multilingual 全マッチ）
    assert ids[0] == "a"
    # 各 item には理由（reasons）が付与されている
    assert all(len(it.reasons) > 0 for it in res.items)


def test_recommend_respects_limit():
    req = RecommendRequest(
        user=UserContextDTO(interest_categories=["job"]),
        limit=1,
    )
    res = recommend(db=None, request=req, candidate_fetcher=_fake_fetcher)  # type: ignore[arg-type]
    assert len(res.items) == 1


def test_recommend_returns_empty_when_all_items_filtered_by_language_level():
    """全アイテムが N1 要求 + ユーザー N5 → すべてフィルタアウト。"""

    def only_high_level(_db, *, region: str | None = None):  # noqa: ARG001
        return [
            ItemFeatures(
                id="x",
                title="N1 required",
                category_slug="job",
                min_japanese_level="N1",
                languages=("ja",),
            )
        ]

    req = RecommendRequest(user=UserContextDTO(japanese_level="N5"))
    res = recommend(db=None, request=req, candidate_fetcher=only_high_level)  # type: ignore[arg-type]
    assert res.items == []
