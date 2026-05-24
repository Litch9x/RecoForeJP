"""POST /explain エンドポイント."""

from typing import Annotated

from fastapi import APIRouter, Depends

from ai_service.llm.client import LLMClient, get_llm
from ai_service.llm.dto import ExplainRequest, ExplainResponse
from ai_service.llm.explain import explain_recommendation

router = APIRouter(tags=["llm"])

LLMClientDep = Annotated[LLMClient | None, Depends(get_llm)]


@router.post("/explain", response_model=ExplainResponse)
def explain_endpoint(request: ExplainRequest, llm: LLMClientDep) -> ExplainResponse:
    """1 件の推薦結果に対する自然な日本語の説明を返す（論文 3.4.3）.

    LLM クライアントが利用可能（OPENAI_API_KEY が設定済み + openai パッケージあり）
    なら LLM 経由、未設定ならテンプレフォールバック。どちらでも応答形式は同じ。
    """
    explanation = explain_recommendation(
        item_title=request.item_title,
        user_context=request.user_context,
        reasons=request.reasons,
        llm=llm,
    )
    return ExplainResponse(text=explanation.text, provider=explanation.provider)
