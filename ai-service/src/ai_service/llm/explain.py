"""推薦結果の説明文生成（論文 3.4.3 説明可能 AI / 多文化対応支援）.

入力: アイテム情報 + 推薦理由（content/hybrid recommender が出す英語まじりの reasons[]）
出力: 自然な日本語の説明（LLM があれば LLM 生成、なければテンプレ翻訳）

重要: LLM 未設定でも必ず動作するフォールバックを必須実装する。論文の評価実験で
LLM 経由 vs テンプレ経由 の品質比較もできるように設計。
"""

from __future__ import annotations

import re
from dataclasses import dataclass

from ai_service.llm.client import LLMClient


@dataclass(frozen=True)
class Explanation:
    text: str
    provider: str  # "openai" / "template" / etc.


# ---------------------------------------------------------------------------
# Template fallback (LLM 不要、常に動く)
# ---------------------------------------------------------------------------

_REASON_PATTERNS: list[tuple[re.Pattern[str], str]] = [
    (
        re.compile(r"category matches your interest \((.+?)\)"),
        "興味のあるカテゴリ「{0}」に該当します",
    ),
    (re.compile(r"same region \((.+?)\)"), "{0}にあります"),
    (re.compile(r"available in (\S+)"), "{0} に対応しています"),
    (
        re.compile(r"foreigner-welcome \(suitable for beginners\)"),
        "外国人歓迎なので、日本語が初級でも安心です",
    ),
    (re.compile(r"multilingual support available"), "多言語対応のサポートがあります"),
    (
        re.compile(r"filtered: requires (\S+) \(you are (\S+)\)"),
        "必要な日本語レベル ({0}) を満たしていません (現在 {1})",
    ),
]


def _translate_reason(reason: str) -> str:
    """英語まじりの reason 文を、決定論的に日本語へ。マッチしない場合はそのまま返す。"""
    for pattern, template in _REASON_PATTERNS:
        m = pattern.search(reason)
        if m:
            return template.format(*m.groups())
    return reason


def template_explanation(item_title: str, reasons: list[str]) -> Explanation:
    """LLM なしで生成する説明（テンプレ翻訳のみ）."""
    if not reasons:
        text = f"「{item_title}」がおすすめです。"
    else:
        translated = [f"・{_translate_reason(r)}" for r in reasons]
        text = f"「{item_title}」のおすすめ理由:\n" + "\n".join(translated)
    return Explanation(text=text, provider="template")


# ---------------------------------------------------------------------------
# LLM-based explanation
# ---------------------------------------------------------------------------

_SYSTEM_PROMPT = (
    "あなたは在日外国人向けの推薦システムが返す結果を、"
    "ユーザーにわかりやすい日本語で説明するアシスタントです。"
    "出力は丁寧かつ簡潔（最大 3 文）に。専門用語は避ける。"
    "事実に基づくこと、推測しないこと。"
)


def _build_user_prompt(*, item_title: str, user_context: str | None, reasons: list[str]) -> str:
    parts = [f"アイテム: {item_title}"]
    if user_context:
        parts.append(f"ユーザー状況: {user_context}")
    parts.append("推薦システムが挙げた理由（英語混じり）:")
    parts.extend(f"- {r}" for r in reasons)
    parts.append("\n上記をもとに、自然な日本語で 1〜3 文に要約してください。")
    return "\n".join(parts)


def explain_recommendation(
    *,
    item_title: str,
    user_context: str | None = None,
    reasons: list[str],
    llm: LLMClient | None = None,
) -> Explanation:
    """1 件の推薦に対する説明文を返す.

    LLM が提供された場合は LLM 生成、未提供（None）ならテンプレフォールバック。
    どちらの経路でも必ず ``Explanation`` を返す（API 側でハンドリング不要）。
    """
    if llm is None:
        return template_explanation(item_title, reasons)

    try:
        prompt = _build_user_prompt(
            item_title=item_title, user_context=user_context, reasons=reasons
        )
        text = llm.complete(system=_SYSTEM_PROMPT, user=prompt).strip()
        if not text:
            return template_explanation(item_title, reasons)
        return Explanation(text=text, provider=llm.name)
    except Exception:
        # LLM 呼び出し失敗時はフォールバック（落とさない）
        return template_explanation(item_title, reasons)
