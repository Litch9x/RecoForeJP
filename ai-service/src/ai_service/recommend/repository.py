"""候補アイテムを items schema から取得する読み取り専用リポジトリ.

ai-service は item-service とは別プロセスだが、論文 3.5.4 の方針で
items schema には直接読み取り権限を持つ（マイクロサービス越境の
HTTP 呼び出しを毎回するとレイテンシが厳しいため）。
"""

from collections.abc import Sequence

from sqlalchemy import text
from sqlalchemy.orm import Session

from ai_service.recommend.scorer import ItemFeatures

_SQL_BASE = """
    SELECT
        i.id::text AS id,
        i.title,
        c.slug AS category_slug,
        i.region,
        i.min_japanese_level,
        COALESCE(
            (SELECT array_agg(language ORDER BY language)
               FROM items.item_languages WHERE item_id = i.id),
            ARRAY[]::varchar[]
        ) AS languages,
        COALESCE(
            (SELECT array_agg(t.name ORDER BY t.name)
               FROM items.tags t
               JOIN items.item_tags it ON it.tag_id = t.id
               WHERE it.item_id = i.id),
            ARRAY[]::varchar[]
        ) AS tags
    FROM items.items i
    JOIN items.categories c ON c.id = i.category_id
    WHERE (i.expires_at IS NULL OR i.expires_at > NOW())
"""


def fetch_candidate_items(
    db: Session,
    *,
    region: str | None = None,
    limit: int = 200,
) -> Sequence[ItemFeatures]:
    """有効（未失効）なアイテムを candidate として取得する。

    Args:
        db: SQLAlchemy セッション
        region: 地域フィルタ（任意）。指定すれば該当地域のみ。
        limit: 取得上限（デフォルト 200）

    Returns:
        :class:`ItemFeatures` のシーケンス。スコアリング用に必要な列のみ含む。
    """
    params: dict[str, object] = {"limit": limit}
    sql = _SQL_BASE
    if region is not None:
        sql += " AND i.region = :region"
        params["region"] = region
    sql += " ORDER BY i.published_at DESC NULLS LAST LIMIT :limit"

    rows = db.execute(text(sql), params).mappings().all()
    return [
        ItemFeatures(
            id=row["id"],
            title=row["title"],
            category_slug=row["category_slug"],
            region=row["region"],
            min_japanese_level=row["min_japanese_level"],
            languages=tuple(row["languages"] or ()),
            tags=tuple(row["tags"] or ()),
        )
        for row in rows
    ]
