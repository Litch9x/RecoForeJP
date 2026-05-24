# ============================================================
# ai-service - Python / FastAPI Dockerfile
# ============================================================

FROM python:3.12-slim

WORKDIR /app

# wget は HEALTHCHECK 用（slim には入っているが念のため）
RUN apt-get update && apt-get install -y --no-install-recommends wget \
    && rm -rf /var/lib/apt/lists/*

# 非 root ユーザー
RUN useradd --create-home --shell /bin/bash appuser

# 依存関係を先にインストール（layer caching）
# [ml] extras を含めて sentence-transformers + torch を導入（本番では必須・約 2GB）
COPY pyproject.toml ./
RUN pip install --no-cache-dir ".[ml]"

# アプリケーションコード
COPY src /app/src
ENV PYTHONPATH=/app/src
ENV PYTHONUNBUFFERED=1
ENV PORT=8000

USER appuser

EXPOSE 8000

HEALTHCHECK --interval=30s --timeout=5s --start-period=10s --retries=3 \
    CMD wget --quiet --tries=1 --spider http://localhost:8000/health || exit 1

CMD ["uvicorn", "ai_service.main:app", "--host", "0.0.0.0", "--port", "8000"]
