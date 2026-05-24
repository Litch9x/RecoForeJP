"""FastAPI アプリケーションのエントリポイント."""

from fastapi import FastAPI

from ai_service import __version__
from ai_service.embedding.router import router as embedding_router
from ai_service.health import router as health_router
from ai_service.llm.router import router as llm_router
from ai_service.recommend.router import router as recommend_router
from ai_service.search.router import router as search_router


def create_app() -> FastAPI:
    """アプリケーションファクトリ。テストでも同じインスタンス構築方法を使う。"""
    app = FastAPI(
        title="RecoForeJP AI Service",
        version=__version__,
        description="推薦アルゴリズム、テキスト埋め込み、LLM 連携、意味検索を提供する。",
    )
    app.include_router(health_router)
    app.include_router(recommend_router)
    app.include_router(embedding_router)
    app.include_router(search_router)
    app.include_router(llm_router)
    return app


app = create_app()
