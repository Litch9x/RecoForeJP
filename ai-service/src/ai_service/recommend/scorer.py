"""コンテンツベース推薦のスコア計算（純粋関数）.

DB 非依存。ユーザー属性とアイテム属性の dataclass を受け取り、
スコアと「なぜ推薦されたか」の理由列を返す。

スコアリング方針（論文 3.3.1 / 3.2.3 参照）:

1. **ハードフィルタ**: アイテムが要求する日本語レベルがユーザーの能力を超える場合 → 0 点（除外）
2. **ソフトスコア**:
   - カテゴリがユーザー興味と一致 → +3.0（最重要：明示的な興味）
   - 地域一致 → +2.0
   - アイテム対応言語にユーザー希望言語が含まれる → +2.0
   - ``foreigner-welcome`` タグ かつ ユーザーが N5/N4 → +1.5（初級者支援）
   - ユーザー希望言語が日本語以外 かつ アイテムが多言語対応 → +1.0
"""

from dataclasses import dataclass, field

# JLPT: N5 が最も簡単、N1 が最難。数値が大きいほど能力が高い。
JLPT_RANK: dict[str, int] = {"N5": 1, "N4": 2, "N3": 3, "N2": 4, "N1": 5}


@dataclass(frozen=True)
class UserContext:
    """スコアリング対象ユーザーの属性。"""

    japanese_level: str | None = None
    region: str | None = None
    preferred_language: str = "ja"
    interest_categories: tuple[str, ...] = ()


@dataclass(frozen=True)
class ItemFeatures:
    """スコアリング対象アイテムの属性（DB 取得結果）。"""

    id: str
    title: str
    category_slug: str
    region: str | None = None
    min_japanese_level: str | None = None
    languages: tuple[str, ...] = ()
    tags: tuple[str, ...] = ()


@dataclass(frozen=True)
class ScoreResult:
    """スコア + 推薦理由（説明可能 AI として、なぜ薦めたかを返す）。"""

    score: float
    reasons: tuple[str, ...] = field(default_factory=tuple)


def _jlpt_level_ok(user_level: str | None, item_required: str | None) -> bool:
    """アイテム要求レベル ≤ ユーザーレベル ならば True。

    - ``item_required`` が None なら制約なし → True
    - ``user_level`` が不明なら、最も簡単（N5）要求のものだけ許可
    """
    if not item_required:
        return True
    if not user_level:
        return item_required == "N5"
    user_rank = JLPT_RANK.get(user_level, 0)
    item_rank = JLPT_RANK.get(item_required, 999)
    return user_rank >= item_rank


def score_item(user: UserContext, item: ItemFeatures) -> ScoreResult:
    """属性マッチに基づきスコアと理由を返す。

    スコア 0 はフィルタアウトされた（推薦すべきでない）ことを表す。
    """
    if not _jlpt_level_ok(user.japanese_level, item.min_japanese_level):
        return ScoreResult(
            0.0,
            (f"filtered: requires {item.min_japanese_level} (you are {user.japanese_level})",),
        )

    score = 0.0
    reasons: list[str] = []

    # カテゴリマッチ：最も強い信号
    if item.category_slug in user.interest_categories:
        score += 3.0
        reasons.append(f"category matches your interest ({item.category_slug})")

    # 地域マッチ
    if user.region and item.region and user.region == item.region:
        score += 2.0
        reasons.append(f"same region ({item.region})")

    # 言語マッチ
    if user.preferred_language in item.languages:
        score += 2.0
        reasons.append(f"available in {user.preferred_language}")

    # 外国人歓迎 × 初級者：論文 1.1.3 の言語的障壁緩和
    if "foreigner-welcome" in item.tags and user.japanese_level in ("N5", "N4"):
        score += 1.5
        reasons.append("foreigner-welcome (suitable for beginners)")

    # 多言語対応ボーナス：日本語以外を希望するユーザーへ
    if user.preferred_language != "ja" and len(item.languages) > 1:
        score += 1.0
        reasons.append("multilingual support available")

    return ScoreResult(score, tuple(reasons))
