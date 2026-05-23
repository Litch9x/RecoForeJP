# ============================================================
# api-gateway - Multi-stage Dockerfile
# ============================================================

# ---- Stage 1: build ----
FROM node:20-alpine AS builder

WORKDIR /app

# 依存性インストール（package*.json だけコピーして cache 活用）
COPY package.json package-lock.json ./
RUN npm ci

# ソースをコピーしてビルド（TypeScript -> dist/）
COPY . .
RUN npm run build

# ---- Stage 2: runtime ----
FROM node:20-alpine

WORKDIR /app

ENV NODE_ENV=production
ENV PORT=3000

# 本番依存のみインストール
COPY package.json package-lock.json ./
RUN npm ci --omit=dev && npm cache clean --force

# ビルド成果物をコピー
COPY --from=builder /app/dist ./dist

# 非 root ユーザーで実行（セキュリティ）
USER node

EXPOSE 3000

# ヘルスチェック（Docker 自体の HEALTHCHECK）
HEALTHCHECK --interval=30s --timeout=5s --start-period=10s --retries=3 \
    CMD wget --quiet --tries=1 --spider http://localhost:3000/health || exit 1

CMD ["node", "dist/main"]
