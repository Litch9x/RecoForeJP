"""推薦システムの代表的なオフライン評価指標。

すべて binary relevance 前提（item is relevant or not）。
段階的 relevance（rel ∈ {0, 1, 2, 3}）対応は今後の TODO。

論文の対応:
  §5.3.2 適合率・再現率
  §5.3.3 NDCG 評価
"""

from __future__ import annotations

import math
from collections.abc import Sequence


def precision_at_k(ranked_ids: Sequence[str], relevant_ids: set[str], k: int) -> float:
    """Precision@K = |relevant ∩ top-k| / k

    top-k 件のうち何件が relevant か。0 ≤ P@K ≤ 1。
    K が ranked_ids より大きい場合は K に padding せず、実際の長さで K を使う
    （Precision@10 で 5 件しか返らない場合でも分母は K=10 ではなく min(len, k) として
    計算するのが慣例だが、ここでは「上位 K 件で何件当たったか」を答えるシンプルな
    定義を採用し、分母は k 固定）。
    """
    if k <= 0:
        raise ValueError("k must be positive")
    top_k = ranked_ids[:k]
    hit = sum(1 for item_id in top_k if item_id in relevant_ids)
    return hit / k


def recall_at_k(ranked_ids: Sequence[str], relevant_ids: set[str], k: int) -> float:
    """Recall@K = |relevant ∩ top-k| / |relevant|

    relevant 全体の何 % を top-k で拾えたか。0 ≤ R@K ≤ 1。
    relevant が 0 件の場合は 0.0 を返す（0 除算回避）。
    """
    if k <= 0:
        raise ValueError("k must be positive")
    if not relevant_ids:
        return 0.0
    top_k = ranked_ids[:k]
    hit = sum(1 for item_id in top_k if item_id in relevant_ids)
    return hit / len(relevant_ids)


def dcg_at_k(ranked_ids: Sequence[str], relevant_ids: set[str], k: int) -> float:
    """DCG@K (binary relevance, log2 discount)

    DCG@K = Σ_{i=1..k} rel_i / log2(i + 1)
    位置 i は 1-indexed。
    """
    if k <= 0:
        raise ValueError("k must be positive")
    total = 0.0
    for i, item_id in enumerate(ranked_ids[:k], start=1):
        if item_id in relevant_ids:
            total += 1.0 / math.log2(i + 1)
    return total


def idcg_at_k(num_relevant: int, k: int) -> float:
    """IDCG@K: 理想ランキングの DCG（relevant が全部上位に並んだ場合）。"""
    if k <= 0:
        raise ValueError("k must be positive")
    n = min(num_relevant, k)
    return sum(1.0 / math.log2(i + 1) for i in range(1, n + 1))


def ndcg_at_k(ranked_ids: Sequence[str], relevant_ids: set[str], k: int) -> float:
    """NDCG@K = DCG@K / IDCG@K

    順位品質の正規化指標。0 ≤ NDCG@K ≤ 1。
    relevant が 0 件の場合は 0.0（idcg が 0）。
    """
    idcg = idcg_at_k(len(relevant_ids), k)
    if idcg == 0.0:
        return 0.0
    return dcg_at_k(ranked_ids, relevant_ids, k) / idcg
