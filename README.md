# RecoForeJP

**在日外国人向け AI パーソナライズ推薦システム**（卒業論文プロジェクト）

日本語能力、在留資格、興味、行動履歴などをもとに、就職・住居・行政手続き・日本語学習・地域イベント情報をパーソナライズして推薦するマイクロサービス型 Web アプリケーション。

## アーキテクチャ

```
              ┌──────────────────┐
              │  Frontend (Web)  │   Next.js / TypeScript
              └────────┬─────────┘
                       │ HTTPS
              ┌────────▼─────────┐
              │   API Gateway    │   NestJS / TypeScript
              │  (Auth, Routing) │
              └───┬──────────┬───┘
       ┌─────────┘          └─────────┐
       │                              │
  ┌────▼─────────┐ ┌──────────┐ ┌─────▼─────────┐
  │ user-service │ │item-svc  │ │  ai-service   │
  │ Java / Spring│ │Java/Spring│ │ Python/FastAPI│
  └──────┬───────┘ └────┬─────┘ └───────┬───────┘
         │              │               │
         └──────────────┼───────────────┘
                        │
                 ┌──────▼──────┐
                 │ PostgreSQL  │  (pgvector for embeddings)
                 │   Redis     │
                 └─────────────┘
```

## サービス一覧

| サービス | 技術スタック | 役割 |
|---------|-------------|------|
| `frontend/` | Next.js, TypeScript, i18n | 多言語UI、推薦結果表示、検索 |
| `api-gateway/` | NestJS, TypeScript | JWT 認証、ルーティング、レート制限 |
| `user-service/` | Java 21, Spring Boot, Gradle | ユーザー登録・プロフィール・設定 |
| `item-service/` | Java 21, Spring Boot, Gradle | アイテム CRUD、カテゴリ、フィードバック |
| `ai-service/` | Python, FastAPI | 推薦アルゴリズム、埋め込み、LLM、NLP |
| `infra/` | Docker Compose, k8s manifests | ローカル/本番インフラ定義 |
| `docs/` | — | 論文、スライド、図、ER 図 |
| `scripts/` | Python | Jira セットアップ等のツール |

## 開発状況

🚧 **初期構築フェーズ**。各サービスはディレクトリ作成のみ。詳細は [Jira (RecoForeJP)](https://shinjp.atlassian.net/jira/software/projects/RECO/backlog) を参照。

## ローカル開発環境の起動

### 前提

- Docker Desktop（または Docker Engine + Docker Compose v2）
- 空いているポート: 5432（PostgreSQL）、6379（Redis）

### 手順

```bash
# 1. 環境変数ファイルを作成
cp infra/.env.example infra/.env

# 2. データ層を起動（PostgreSQL + Redis）
docker compose -f infra/docker-compose.yml up -d

# 3. 起動確認
docker compose -f infra/docker-compose.yml ps

# 4. 停止
docker compose -f infra/docker-compose.yml down

# データも消したい場合
docker compose -f infra/docker-compose.yml down -v
```

### PostgreSQL への接続確認

```bash
docker exec -it reco-postgres psql -U reco -d reco -c "SELECT extname FROM pg_extension;"
# vector が表示されれば pgvector 有効
```

## 開発ワークフロー

1. Jira で Story を選び、`In Progress` に変更
2. 専用 feature branch を作成（例: `RECO-7-docker-compose`）
3. 実装
4. Conventional Commits 形式でコミット（メッセージにチケット ID を含める）
5. GitHub に push し、Pull Request を作成
6. レビュー → マージ
7. Jira の Story を `Done` に移動

### コミットメッセージ例

```
feat(api-gateway): add JWT authentication middleware (RECO-13)
fix(ai-service): handle empty embedding response (RECO-25)
chore(repo): bootstrap monorepo structure (RECO-6)
docs(readme): document architecture diagram (RECO-6)
```

## ライセンス

未定（卒論プロジェクト）。
