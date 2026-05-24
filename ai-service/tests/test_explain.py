"""説明文生成のテスト：テンプレフォールバック + Mock LLM 経路."""

from ai_service.llm.client import LLMClient, get_llm
from ai_service.llm.explain import (
    _translate_reason,
    explain_recommendation,
    template_explanation,
)
from ai_service.main import app
from fastapi.testclient import TestClient


class StubLLM:
    """LLMClient Protocol を満たす最小スタブ."""

    name = "stub"

    def __init__(self, response: str = "（スタブ生成の説明文）", fail: bool = False) -> None:
        self.response = response
        self.fail = fail
        self.last_system: str | None = None
        self.last_user: str | None = None

    def complete(self, *, system: str, user: str) -> str:
        self.last_system = system
        self.last_user = user
        if self.fail:
            raise RuntimeError("LLM unavailable")
        return self.response


# ---------- _translate_reason: 個別パターン ----------


def test_translate_reason_category() -> None:
    assert "就職" in _translate_reason(
        "category matches your interest (就職)"
    ) or "「就職」" in _translate_reason("category matches your interest (就職)")


def test_translate_reason_region() -> None:
    assert "東京都-渋谷区" in _translate_reason("same region (東京都-渋谷区)")


def test_translate_reason_language() -> None:
    assert _translate_reason("available in vi") == "vi に対応しています"


def test_translate_reason_foreigner_welcome() -> None:
    out = _translate_reason("foreigner-welcome (suitable for beginners)")
    assert "外国人歓迎" in out


def test_translate_reason_passthrough_unknown() -> None:
    assert _translate_reason("some unknown reason") == "some unknown reason"


# ---------- template_explanation ----------


def test_template_explanation_with_reasons() -> None:
    expl = template_explanation(
        "ベトナム語通訳のあるクリニック",
        [
            "category matches your interest (medical)",
            "available in vi",
            "foreigner-welcome (suitable for beginners)",
        ],
    )
    assert expl.provider == "template"
    assert "ベトナム語通訳のあるクリニック" in expl.text
    assert "vi に対応しています" in expl.text
    assert "外国人歓迎" in expl.text


def test_template_explanation_with_no_reasons() -> None:
    expl = template_explanation("簡単タイトル", [])
    assert expl.provider == "template"
    assert "簡単タイトル" in expl.text


# ---------- explain_recommendation: LLM 経路 ----------


def test_explain_recommendation_uses_llm_when_provided() -> None:
    stub = StubLLM(response="このお仕事は外国人歓迎で、英語対応もしています。")
    expl = explain_recommendation(
        item_title="外国人歓迎エンジニア",
        user_context="N5 ベトナム人留学生",
        reasons=["category matches your interest (job)", "available in en"],
        llm=stub,
    )
    assert expl.provider == "stub"
    assert expl.text == "このお仕事は外国人歓迎で、英語対応もしています。"
    assert stub.last_user is not None
    assert "外国人歓迎エンジニア" in stub.last_user


def test_explain_recommendation_falls_back_when_llm_raises() -> None:
    stub = StubLLM(fail=True)
    expl = explain_recommendation(
        item_title="X",
        reasons=["available in ja"],
        llm=stub,
    )
    assert expl.provider == "template"


def test_explain_recommendation_falls_back_on_empty_llm_response() -> None:
    stub = StubLLM(response="   ")  # whitespace only
    expl = explain_recommendation(item_title="X", reasons=["available in ja"], llm=stub)
    assert expl.provider == "template"


def test_explain_recommendation_falls_back_when_llm_is_none() -> None:
    expl = explain_recommendation(item_title="X", reasons=["available in ja"], llm=None)
    assert expl.provider == "template"
    assert "ja に対応しています" in expl.text


# ---------- /explain エンドポイント ----------


client = TestClient(app)


def _override_llm_none():
    return None


def _override_llm_stub() -> StubLLM:
    return StubLLM(response="LLM が生成した日本語の説明")


def test_explain_endpoint_uses_template_when_no_llm() -> None:
    app.dependency_overrides[get_llm] = _override_llm_none
    try:
        response = client.post(
            "/explain",
            json={
                "item_title": "テスト案件",
                "user_context": "N3 ユーザー",
                "reasons": ["category matches your interest (job)", "available in ja"],
            },
        )
        assert response.status_code == 200
        body = response.json()
        assert body["provider"] == "template"
        assert "テスト案件" in body["text"]
    finally:
        app.dependency_overrides.pop(get_llm, None)


def test_explain_endpoint_uses_llm_when_available() -> None:
    app.dependency_overrides[get_llm] = _override_llm_stub
    try:
        response = client.post(
            "/explain",
            json={
                "item_title": "テスト案件",
                "reasons": ["available in en"],
            },
        )
        assert response.status_code == 200
        body = response.json()
        assert body["provider"] == "stub"
        assert body["text"] == "LLM が生成した日本語の説明"
    finally:
        app.dependency_overrides.pop(get_llm, None)


def test_explain_endpoint_validates_empty_title() -> None:
    response = client.post("/explain", json={"item_title": "", "reasons": []})
    assert response.status_code == 422


def test_get_llm_returns_none_when_no_api_key_configured() -> None:
    """環境変数 OPENAI_API_KEY が未設定 → None（テンプレフォールバックに回る）."""
    # この test 環境では .env も openai_api_key も無いはず
    client_obj: LLMClient | None = get_llm()
    assert client_obj is None
