"""推薦オーケストレーション：候補取得 → スコアリング → 整形."""

from collections.abc import Callable, Sequence

from sqlalchemy.orm import Session

from ai_service.recommend.dto import RecommendedItem, RecommendRequest, RecommendResponse
from ai_service.recommend.repository import fetch_candidate_items
from ai_service.recommend.scorer import ItemFeatures, UserContext, score_item

# テスト可能性のため、候補取得関数を差し替えられる型エイリアス。
CandidateFetcher = Callable[..., Sequence[ItemFeatures]]


def recommend(
    db: Session,
    request: RecommendRequest,
    *,
    candidate_fetcher: CandidateFetcher = fetch_candidate_items,
) -> RecommendResponse:
    """ユーザー属性から推薦リストを生成する。

    Args:
        db: DB セッション（``candidate_fetcher`` に渡される）。
        request: API リクエスト DTO。
        candidate_fetcher: 候補アイテム取得関数（テストでは fake に差し替え可能）。
    """
    user = UserContext(
        japanese_level=request.user.japanese_level,
        region=request.user.region,
        preferred_language=request.user.preferred_language,
        interest_categories=tuple(request.user.interest_categories),
    )

    candidates = candidate_fetcher(db, region=request.region)

    scored = [(item, score_item(user, item)) for item in candidates]
    scored = [(item, result) for item, result in scored if result.score > 0]
    scored.sort(key=lambda pair: pair[1].score, reverse=True)
    top = scored[: request.limit]

    return RecommendResponse(
        items=[
            RecommendedItem(
                id=item.id,
                title=item.title,
                category_slug=item.category_slug,
                region=item.region,
                score=result.score,
                reasons=list(result.reasons),
            )
            for item, result in top
        ]
    )
