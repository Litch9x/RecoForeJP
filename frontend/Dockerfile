# ============================================================
# frontend - Next.js multi-stage Dockerfile (standalone output)
# ref: node_modules/next/dist/docs/01-app/03-api-reference/05-config/01-next-config-js/output.md
# ============================================================

# ---- Stage 1: deps ----
FROM node:20-alpine AS deps
WORKDIR /app
COPY package.json package-lock.json ./
RUN npm ci

# ---- Stage 2: builder ----
FROM node:20-alpine AS builder
WORKDIR /app

# テレメトリ無効化（ビルド時にネットワーク不要に）
ENV NEXT_TELEMETRY_DISABLED=1

COPY --from=deps /app/node_modules ./node_modules
COPY . .
RUN npm run build

# ---- Stage 3: runner ----
FROM node:20-alpine AS runner
WORKDIR /app

ENV NODE_ENV=production
ENV NEXT_TELEMETRY_DISABLED=1
ENV PORT=3001
ENV HOSTNAME=0.0.0.0

# 非 root ユーザー
RUN addgroup -g 1001 -S nodejs && adduser -u 1001 -G nodejs -S nextjs

# 公開アセット + standalone server + 静的アセットをコピー
COPY --from=builder /app/public ./public
COPY --from=builder --chown=nextjs:nodejs /app/.next/standalone ./
COPY --from=builder --chown=nextjs:nodejs /app/.next/static ./.next/static

# wget は HEALTHCHECK 用（alpine 内蔵）
USER nextjs

EXPOSE 3001

HEALTHCHECK --interval=30s --timeout=5s --start-period=10s --retries=3 \
    CMD wget --quiet --tries=1 --spider http://localhost:3001/api/health || exit 1

CMD ["node", "server.js"]
