"""意味検索オーケストレーション：query → 埋め込み → pgvector で nearest."""

from ai_service.embedding.encoder import TextEncoder
from ai_service.embedding.store import ItemEmbeddingStore
from ai_service.search.dto import SearchResultItem, SemanticSearchResponse


def search_items(
    *,
    query: str,
    limit: int,
    encoder: TextEncoder,
    store: ItemEmbeddingStore,
) -> SemanticSearchResponse:
    """自然言語クエリから意味的に近いアイテムを返す.

    Args:
        query: ユーザーが入力する自由テキスト。
        limit: 返す上限件数。
        encoder: テキストエンコーダ（テストでは Fake に差し替え）。
        store: アイテム埋め込みストア（テストでは Fake に差し替え）。
    """
    query_vec = encoder.encode([query], mode="query")[0]
    nearest = store.find_nearest(query_vec, limit=limit)
    return SemanticSearchResponse(
        query=query,
        results=[
            SearchResultItem(
                item_id=n.item_id,
                title=n.title,
                similarity=n.similarity,
            )
            for n in nearest
        ],
    )
