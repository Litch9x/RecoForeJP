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

# [ml] extras を含めて sentence-transformers + torch を導入（本番では必須・約 2GB）
# pyproject.toml が src/ レイアウトを参照するので、src/ も一緒に COPY してから install する。
COPY pyproject.toml ./
COPY src /app/src
RUN pip install --no-cache-dir ".[ml]"
ENV PYTHONPATH=/app/src
ENV PYTHONUNBUFFERED=1
ENV PORT=8000

USER appuser

EXPOSE 8000

# NOTE: `wget --spider` は HEAD を送るが FastAPI の /health は GET のみで 405 を返すため
# 使えない。`-O /dev/null` で GET にする。
HEALTHCHECK --interval=30s --timeout=5s --start-period=10s --retries=3 \
    CMD wget --quiet --tries=1 -O /dev/null http://localhost:8000/health || exit 1

CMD ["uvicorn", "ai_service.main:app", "--host", "0.0.0.0", "--port", "8000"]
