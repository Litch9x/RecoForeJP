"""LLM クライアントの抽象と OpenAI 実装.

設計方針:
- ``LLMClient`` Protocol を満たす実装ならどれでも差し替え可能（OpenAI / Ollama / mock）。
- OpenAI SDK はオプション依存（``[llm]`` extras）。未インストールでも ai-service は起動する。
- API キーが未設定なら ``get_llm()`` は ``None`` を返し、呼び出し側はテンプレ
  フォールバックを使う。
"""

from __future__ import annotations

from typing import Protocol

from ai_service.config import settings


class LLMClient(Protocol):
    """Chat 形式の生成 LLM クライアント."""

    name: str

    def complete(self, *, system: str, user: str) -> str:
        """system + user メッセージから応答テキストを返す."""
        ...


class OpenAIClient:
    """OpenAI Chat Completions の薄いラッパ."""

    name = "openai"

    def __init__(self, api_key: str, model: str) -> None:
        # 重量級 import を __init__ に閉じ込める（未使用なら起動時に import されない）
        from openai import OpenAI

        self._client = OpenAI(api_key=api_key)
        self.model = model

    def complete(self, *, system: str, user: str) -> str:
        response = self._client.chat.completions.create(
            model=self.model,
            messages=[
                {"role": "system", "content": system},
                {"role": "user", "content": user},
            ],
            temperature=0.4,
        )
        content = response.choices[0].message.content
        return content or ""


def get_llm() -> LLMClient | None:
    """環境変数を見て利用可能な LLM クライアントを返す。なければ None.

    None が返ったら呼び出し側はテンプレフォールバック説明を使うこと。
    """
    if not settings.openai_api_key:
        return None
    try:
        return OpenAIClient(api_key=settings.openai_api_key, model=settings.openai_model)
    except ImportError:
        # openai パッケージ未インストール
        return None
