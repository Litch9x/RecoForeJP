"""``ai.item_embeddings`` への永続化と類似度検索（pgvector 連携）.

設計方針:
- ORM ではなく SQL + SQLAlchemy bind parameters。pgvector の型は ``pgvector.sqlalchemy.Vector``
  を bindparam に与えることで透過的に動作する。
- 検索は cosine distance（演算子 ``<=>``）を使い、HNSW インデックスを活用。
  類似度（similarity）= ``1 - distance`` で返却（高いほど類似）。
"""

from __future__ import annotations

from collections.abc import Sequence
from dataclasses import dataclass
from uuid import UUID

from pgvector.sqlalchemy import Vector
from sqlalchemy import bindparam, text
from sqlalchemy.orm import Session


@dataclass(frozen=True)
class NearestItem:
    """類似度検索の 1 件."""

    item_id: str
    title: str | None
    similarity: float  # 0.0 〜 1.0（高いほど近い）


class ItemEmbeddingStore:
    """``ai.item_embeddings`` のリポジトリ。"""

    DIMENSION = 384

    def __init__(self, db: Session) -> None:
        self.db = db

    def upsert(self, item_id: UUID | str, embedding: Sequence[float]) -> None:
        """item_id をキーに埋め込みベクトルを upsert（既存なら置換）."""
        stmt = text(
            """
            INSERT INTO ai.item_embeddings (item_id, embedding, updated_at)
            VALUES (:item_id, :embedding, NOW())
            ON CONFLICT (item_id) DO UPDATE
              SET embedding = EXCLUDED.embedding,
                  updated_at = NOW()
            """
        ).bindparams(bindparam("embedding", type_=Vector(self.DIMENSION)))
        self.db.execute(stmt, {"item_id": str(item_id), "embedding": list(embedding)})
        self.db.commit()

    def find_nearest(
        self,
        query: Sequence[float],
        *,
        limit: int = 10,
    ) -> list[NearestItem]:
        """クエリベクトルに近い順に最大 limit 件返す（items テーブルと JOIN してタイトルも取得）."""
        stmt = text(
            """
            SELECT
                ie.item_id::text AS item_id,
                i.title,
                1 - (ie.embedding <=> :query) AS similarity
            FROM ai.item_embeddings ie
            LEFT JOIN items.items i ON i.id = ie.item_id
            ORDER BY ie.embedding <=> :query
            LIMIT :limit
            """
        ).bindparams(bindparam("query", type_=Vector(self.DIMENSION)))
        rows = self.db.execute(stmt, {"query": list(query), "limit": limit}).mappings().all()
        return [
            NearestItem(
                item_id=row["item_id"],
                title=row["title"],
                similarity=float(row["similarity"]),
            )
            for row in rows
        ]
