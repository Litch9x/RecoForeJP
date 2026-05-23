"""FastAPI アプリケーションのエントリポイント."""

from fastapi import FastAPI

from ai_service import __version__
from ai_service.health import router as health_router


def create_app() -> FastAPI:
    """アプリケーションファクトリ。テストでも同じインスタンス構築方法を使う。"""
    app = FastAPI(
        title="RecoForeJP AI Service",
        version=__version__,
        description="推薦アルゴリズム、テキスト埋め込み、LLM 連携、意味検索を提供する。",
    )
    app.include_router(health_router)
    return app


app = create_app()
