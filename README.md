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

| サービス        | 技術スタック                  | 役割                                                  |
| --------------- | ----------------------------- | ----------------------------------------------------- |
| `frontend/`     | Next.js, TypeScript, i18n     | 多言語UI、推薦結果表示、検索                          |
| `api-gateway/`  | NestJS, TypeScript            | JWT 認証、ルーティング、レート制限                    |
| `user-service/` | Java 21, Spring Boot, Gradle  | ユーザー登録・プロフィール・設定                      |
| `item-service/` | Java 21, Spring Boot, Gradle  | アイテム CRUD、カテゴリ、フィードバック               |
| `ai-service/`   | Python, FastAPI               | 推薦アルゴリズム、埋め込み、LLM、NLP                  |
| `infra/`        | Docker Compose, k8s manifests | ローカル/本番インフラ定義                             |
| `docs/`         | —                             | 論文、スライド、[スキーマ設計](docs/schema/README.md) |
| `scripts/`      | Python                        | Jira セットアップ等のツール                           |

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
# 拡張機能（pgvector）の確認
docker exec -it reco-postgres psql -U reco -d reco -c "SELECT extname FROM pg_extension;"

# 作成されたスキーマ一覧
docker exec -it reco-postgres psql -U reco -d reco -c "\dn"

# 各スキーマのテーブル一覧
docker exec -it reco-postgres psql -U reco -d reco -c "\dt users.*"
docker exec -it reco-postgres psql -U reco -d reco -c "\dt items.*"
docker exec -it reco-postgres psql -U reco -d reco -c "\dt ai.*"

# シードデータの件数確認
docker exec -it reco-postgres psql -U reco -d reco -c "
  SELECT 'users' AS table, COUNT(*) FROM users.users
  UNION ALL SELECT 'categories', COUNT(*) FROM items.categories
  UNION ALL SELECT 'items', COUNT(*) FROM items.items
  UNION ALL SELECT 'tags', COUNT(*) FROM items.tags;
"
```

期待結果：users=3、categories=12、items=14、tags=22

### マイグレーションの将来構成

現状は `infra/postgres/init/*.sql` が Docker Compose 起動時に一括適用される。これは MVP のための簡易な仕組みで、サービス実装が進んだら以下に移行する：

- `users` schema → `user-service/src/main/resources/db/migration/` (Flyway)
- `items` schema → `item-service/src/main/resources/db/migration/` (Flyway)
- `ai` schema → `ai-service/alembic/versions/` (Alembic)

`infra/postgres/init/` は完全初期化用の bootstrap として残す（`docker compose down -v` 後の再起動で再適用）。

### データ再投入

```bash
# データを消して再起動（init スクリプトがすべて再実行される）
docker compose -f infra/docker-compose.yml down -v
docker compose -f infra/docker-compose.yml up -d
```

## コード品質ツール

すべてのコミットは `pre-commit` フックで自動チェック・自動整形されます。

### 初回セットアップ（1回だけ）

```bash
pip install pre-commit
pre-commit install
```

### 走るチェック

- **ファイル衛生**: 末尾空白除去、改行統一（LF）、大きなファイル検出、マージ衝突マーカー検出
- **Python** (`ruff`): Lint + Format（Black + isort 統合の高速ツール）
- **JS/TS/JSON/YAML/Markdown** (`prettier`): フォーマット統一
- **Java** (`Spotless` via Gradle): 各 Spring Boot サービスで `./gradlew spotlessCheck`（サービス追加後）

### 手動で全ファイル走査

```bash
pre-commit run --all-files
```

エディタ設定の統一は [`.editorconfig`](.editorconfig)、改行コード正規化は [`.gitattributes`](.gitattributes) で行います。

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
