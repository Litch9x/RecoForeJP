"""RecoForeJP - オフライン推薦評価スクリプト（論文 §5.3）

シードユーザー 3 名 + 手動 ground truth で、推薦アルゴリズムを 3 条件で評価する:

  1. content_only   — ユーザー属性のみ（weight_content=1, weight_semantic=0）
  2. semantic_only  — 自然言語クエリのみ（weight_content=0, weight_semantic=1）
  3. hybrid         — 両者を 0.5 / 0.5 で加重和

評価指標は metrics.py の Precision@K / Recall@K / NDCG@K（K=5, 10）。

【使い方】
    docker compose -f infra/docker-compose.yml up -d
    python scripts/seed_embeddings.py
    python scripts/eval_recommendations.py
    # → コンソールに表が出る + eval-results.json が書き出される

【出力】
  - 標準出力: 人間向けサマリテーブル
  - eval-results.json: 機械可読、論文 §5 に貼れる
"""

from __future__ import annotations

import json
import os
import sys
import urllib.error
import urllib.request
from collections.abc import Iterable
from pathlib import Path
from typing import Any

# 同リポの ai-service 内モジュールを import するため sys.path に追加
_REPO = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(_REPO / "ai-service" / "src"))

from ai_service.eval.metrics import (  # noqa: E402
    ndcg_at_k,
    precision_at_k,
    recall_at_k,
)

AI_SERVICE_URL = os.environ.get("AI_SERVICE_URL", "http://localhost:8000")
K_VALUES = (5, 10)


# ---------------------------------------------------------------------------
# Ground truth: 3 名のシードユーザーに対して relevant item id を手動で付与
# 判断基準: カテゴリ一致 + 地域一致 + 母語サポートのいずれか強いマッチ
#
# items の ID 接頭辞:
#   10000000-* job       (3 件)
#   20000000-* housing   (3 件)
#   30000000-* admin     (2 件)
#   40000000-* medical   (2 件)
#   50000000-* japanese-learning (2 件)
#   60000000-* community-event   (2 件)
# ---------------------------------------------------------------------------
TEST_CASES: list[dict[str, Any]] = [
    {
        "name": "U1: VN/N3/Tokyo-Shinjuku, interests=[job, ja-learning, community]",
        "user": {
            "japanese_level": "N3",
            "region": "東京都-新宿区",
            "preferred_language": "ja",
            "interest_categories": ["job", "japanese-learning", "community-event"],
        },
        "query": "外国人歓迎の仕事と日本語クラス",
        "relevant": {
            "10000000-0000-0000-0000-000000000002",  # ベトナム語 CS
            "10000000-0000-0000-0000-000000000003",  # ホールスタッフ新宿
            "50000000-0000-0000-0000-000000000001",  # やさしい日本語新宿
            "50000000-0000-0000-0000-000000000002",  # JLPT N3
            "60000000-0000-0000-0000-000000000001",  # 国際交流パーティー新宿
            "60000000-0000-0000-0000-000000000002",  # ベトナム人会
        },
    },
    {
        "name": "U2: IN/N5/Tokyo-Minato, interests=[housing, admin, ja-learning]",
        "user": {
            "japanese_level": "N5",
            "region": "東京都-港区",
            "preferred_language": "en",
            "interest_categories": ["housing", "admin", "japanese-learning"],
        },
        "query": "外国人 OK の住居と行政手続き",
        "relevant": {
            "20000000-0000-0000-0000-000000000001",  # 渋谷区アパート
            "20000000-0000-0000-0000-000000000002",  # 国際学生寮
            "20000000-0000-0000-0000-000000000003",  # シェアハウス横浜
            "30000000-0000-0000-0000-000000000001",  # 在留資格更新やさしい日本語
            "30000000-0000-0000-0000-000000000002",  # マイナンバー
            "50000000-0000-0000-0000-000000000001",  # やさしい日本語
            "40000000-0000-0000-0000-000000000001",  # 英語対応病院（en + 港区）
        },
    },
    {
        "name": "U3: CN/N1/Yokohama, interests=[community, medical]",
        "user": {
            "japanese_level": "N1",
            "region": "神奈川県-横浜市",
            "preferred_language": "ja",
            "interest_categories": ["community-event", "medical"],
        },
        "query": "病院と地域イベント",
        "relevant": {
            "60000000-0000-0000-0000-000000000001",  # 国際交流パーティー
            "60000000-0000-0000-0000-000000000002",  # ベトナム人会横浜
            "40000000-0000-0000-0000-000000000001",  # 英語対応病院
            "40000000-0000-0000-0000-000000000002",  # ベトナム語通訳
            "20000000-0000-0000-0000-000000000003",  # シェアハウス横浜（region）
        },
    },
]

# 比較する 3 条件
CONDITIONS: list[dict[str, Any]] = [
    {"name": "content_only",  "weight_content": 1.0, "weight_semantic": 0.0, "use_query": False},
    {"name": "semantic_only", "weight_content": 0.0, "weight_semantic": 1.0, "use_query": True},
    {"name": "hybrid",        "weight_content": 0.5, "weight_semantic": 0.5, "use_query": True},
]


def http_post_json(url: str, body: dict[str, Any], timeout: float = 60.0) -> dict[str, Any]:
    data = json.dumps(body).encode()
    req = urllib.request.Request(
        url, data=data, headers={"Content-Type": "application/json"}, method="POST",
    )
    with urllib.request.urlopen(req, timeout=timeout) as resp:
        return json.loads(resp.read().decode())


def recommend(case: dict[str, Any], cond: dict[str, Any], limit: int = 10) -> list[str]:
    """1 ユーザー × 1 条件で推薦を取り、item_id の順位配列を返す。"""
    body = {
        "user": case["user"],
        "query": case["query"] if cond["use_query"] else None,
        "region": None,
        "limit": limit,
        "weight_content": cond["weight_content"],
        "weight_semantic": cond["weight_semantic"],
    }
    try:
        res = http_post_json(f"{AI_SERVICE_URL}/recommend/hybrid", body)
    except urllib.error.HTTPError as e:
        print(f"  ❌ HTTP {e.code} {e.reason}: {e.read().decode()[:200]}", file=sys.stderr)
        return []
    return [item["item_id"] for item in res.get("items", [])]


def compute_metrics(ranked: list[str], relevant: set[str]) -> dict[str, float]:
    out: dict[str, float] = {}
    for k in K_VALUES:
        out[f"P@{k}"] = precision_at_k(ranked, relevant, k)
        out[f"R@{k}"] = recall_at_k(ranked, relevant, k)
        out[f"NDCG@{k}"] = ndcg_at_k(ranked, relevant, k)
    return out


def mean(xs: Iterable[float]) -> float:
    xs = list(xs)
    return sum(xs) / len(xs) if xs else 0.0


def fmt_row(label: str, m: dict[str, float]) -> str:
    cells = [f"{m[k]:.3f}" for k in ["P@5", "R@5", "NDCG@5", "P@10", "R@10", "NDCG@10"]]
    return f"  {label:18}  " + "  ".join(f"{c:>7}" for c in cells)


def main() -> None:
    print(f"📊 オフライン推薦評価 ({AI_SERVICE_URL})\n")
    header = "  " + " " * 18 + "  " + "  ".join(
        f"{c:>7}" for c in ["P@5", "R@5", "NDCG@5", "P@10", "R@10", "NDCG@10"]
    )

    all_results: dict[str, Any] = {"conditions": {c["name"]: [] for c in CONDITIONS}}

    for case in TEST_CASES:
        print(f"━━━ {case['name']} ━━━")
        print(f"  relevant: {len(case['relevant'])} 件 / クエリ: 「{case['query']}」")
        print(header)
        for cond in CONDITIONS:
            ranked = recommend(case, cond, limit=max(K_VALUES))
            metrics = compute_metrics(ranked, case["relevant"])
            print(fmt_row(cond["name"], metrics))
            all_results["conditions"][cond["name"]].append(
                {"user": case["name"], **metrics},
            )
        print()

    # 集計: 各条件の K 毎の平均
    print("━━━ 集計（3 ユーザー平均） ━━━")
    print(header)
    summary: dict[str, dict[str, float]] = {}
    for cond in CONDITIONS:
        cond_rows = all_results["conditions"][cond["name"]]
        avg = {
            k: mean(row[k] for row in cond_rows)
            for k in ["P@5", "R@5", "NDCG@5", "P@10", "R@10", "NDCG@10"]
        }
        summary[cond["name"]] = avg
        print(fmt_row(cond["name"], avg))

    all_results["summary"] = summary

    out_path = _REPO / "eval-results.json"
    out_path.write_text(json.dumps(all_results, ensure_ascii=False, indent=2))
    print(f"\n✅ {out_path.relative_to(_REPO)} に書き出しました")


if __name__ == "__main__":
    main()
