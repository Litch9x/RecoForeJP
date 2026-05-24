"""Database session factory.

ai-service は items schema を **読み取り専用** で参照する（推薦のための候補取得）。
書き込みは item-service / user-service が責務を持つ。
"""

from collections.abc import Iterator

from sqlalchemy import create_engine
from sqlalchemy.orm import Session, sessionmaker

from ai_service.config import settings


def _to_sqlalchemy_url(url: str) -> str:
    """Spring/JDBC 風 URL を SQLAlchemy + psycopg v3 形式に整える。

    - ``jdbc:`` プレフィックスを除去
    - ``postgresql://`` を ``postgresql+psycopg://`` に置換（明示的に psycopg v3 を指定）
    """
    if url.startswith("jdbc:"):
        url = url.removeprefix("jdbc:")
    if url.startswith("postgresql://") and "+" not in url.split("://", 1)[0]:
        url = url.replace("postgresql://", "postgresql+psycopg://", 1)
    return url


engine = create_engine(_to_sqlalchemy_url(settings.database_url), pool_pre_ping=True)
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)


def get_db() -> Iterator[Session]:
    """FastAPI Depends 用：リクエスト毎にセッションを払い出して終了時にクローズ。"""
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()
