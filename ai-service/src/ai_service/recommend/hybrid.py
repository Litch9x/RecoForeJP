"""ハイブリッド推薦（論文 3.3.3）.

コンテンツベース（属性マッチ、RECO-21）と意味検索（埋め込み類似度、RECO-23）の
両方のスコアを **正規化 → 重み付き和** で統合する。

スコアスケール:
- content: 0〜約 9.5（重み合計の上限）→ 候補集合内の最大値で割って 0..1 に正規化
- semantic: 0..1（cosine 類似度）はすでに正規化済み

統合:
    hybrid_score = w_content * content_norm + w_semantic * semantic

クエリ未指定（``query is None``）の場合は意味検索を行わず、コンテンツベースのみで結果を返す。
"""

from __future__ import annotations

from collections.abc import Callable, Sequence
from dataclasses import dataclass, field
from typing import TYPE_CHECKING

from ai_service.recommend.dto import (
    HybridRecommendedItem,
    HybridRecommendRequest,
    HybridRecommendResponse,
    RecommendRequest,
)
from ai_service.recommend.repository import fetch_candidate_items
from ai_service.recommend.service import recommend
from ai_service.search.service import search_items

if TYPE_CHECKING:
    from sqlalchemy.orm import Session

    from ai_service.embedding.encoder import TextEncoder
    from ai_service.embedding.store import ItemEmbeddingStore
    from ai_service.recommend.scorer import ItemFeatures

# 注入用エイリアス
CandidateFetcher = Callable[..., Sequence["ItemFeatures"]]
StoreFactory = Callable[["Session"], "ItemEmbeddingStore"]


# --- 内部累計用 dataclass ---


@dataclass
class _Accumulator:
    title: str | None = None
    content_raw: float = 0.0
    semantic: float = 0.0
    reasons: list[str] = field(default_factory=list)


def hybrid_recommend(
    *,
    request: HybridRecommendRequest,
    db: Session,
    encoder: TextEncoder,
    candidate_fetcher: CandidateFetcher = fetch_candidate_items,
    store_factory: StoreFactory | None = None,
    over_fetch_multiplier: int = 3,
) -> HybridRecommendResponse:
    """content + semantic をブレンドして上位 limit 件を返す。

    Args:
        request: API リクエスト DTO。``query`` 未指定なら content のみ。
        db: DB セッション（candidate_fetcher と store に渡される）。
        encoder: テキストエンコーダ（テストでは Fake に差し替え）。
        candidate_fetcher: 候補アイテム取得関数（テスト差し替え可）。
        store_factory: ``db`` を受け取って store を返す factory（テスト差し替え可）。
        over_fetch_multiplier: 上位 N を最終的に返すために `N * multiplier` 件を内部で取得。
    """
    over_fetch_limit = max(request.limit * over_fetch_multiplier, request.limit)

    # 1) コンテンツベース推薦
    content_resp = recommend(
        db,
        RecommendRequest(user=request.user, region=request.region, limit=over_fetch_limit),
        candidate_fetcher=candidate_fetcher,
    )

    # 2) 意味検索（query があれば）
    semantic_results = []
    if request.query and store_factory is not None:
        store = store_factory(db)
        semantic_resp = search_items(
            query=request.query, limit=over_fetch_limit, encoder=encoder, store=store
        )
        semantic_results = semantic_resp.results

    # 3) item_id をキーに統合
    acc: dict[str, _Accumulator] = {}

    for it in content_resp.items:
        a = acc.setdefault(it.id, _Accumulator())
        a.title = it.title
        a.content_raw = it.score
        a.reasons = list(it.reasons)

    for sr in semantic_results:
        a = acc.setdefault(sr.item_id, _Accumulator())
        if a.title is None:
            a.title = sr.title
        a.semantic = sr.similarity

    # 4) content スコアの正規化（候補集合内最大値で割る、空なら 1.0）
    max_content = max((a.content_raw for a in acc.values()), default=0.0)
    if max_content <= 0:
        max_content = 1.0

    # 5) hybrid_score 計算
    blended: list[HybridRecommendedItem] = []
    for item_id, a in acc.items():
        content_norm = a.content_raw / max_content
        hybrid = request.weight_content * content_norm + request.weight_semantic * a.semantic
        blended.append(
            HybridRecommendedItem(
                item_id=item_id,
                title=a.title,
                hybrid_score=hybrid,
                content_score=content_norm,
                semantic_score=a.semantic,
                reasons=a.reasons,
            )
        )

    # 6) ソート + 上限
    blended.sort(key=lambda x: x.hybrid_score, reverse=True)
    return HybridRecommendResponse(items=blended[: request.limit])
