# テーブル定義詳細

各テーブルの列定義・制約・インデックス。ER の全体像は [README.md](./README.md) を参照。

## `users` schema（user-service が所有）

### `users.users`

ユーザーアカウントの基本情報。

| 列                | 型           | NULL     | 既定値              | 説明                                 |
| ----------------- | ------------ | -------- | ------------------- | ------------------------------------ |
| `id`              | UUID         | NOT NULL | `gen_random_uuid()` | 主キー。外部公開可能な ID            |
| `email`           | VARCHAR(255) | NOT NULL | —                   | ログイン ID。UNIQUE                  |
| `password_hash`   | VARCHAR(255) | NOT NULL | —                   | bcrypt 等のハッシュ                  |
| `nationality`     | VARCHAR(2)   | NULL     | —                   | ISO 3166-1 alpha-2（例：`JP`, `VN`） |
| `native_language` | VARCHAR(8)   | NULL     | —                   | BCP47（例：`ja`, `vi`, `zh-CN`）     |
| `created_at`      | TIMESTAMPTZ  | NOT NULL | `NOW()`             | —                                    |
| `updated_at`      | TIMESTAMPTZ  | NOT NULL | `NOW()`             | アプリ側でトリガまたは ORM で更新    |

- 制約：`UNIQUE(email)`

### `users.user_profiles`

ユーザー詳細プロフィール（1:1）。

| 列                 | 型          | NULL     | 既定値  | 説明                                                                 |
| ------------------ | ----------- | -------- | ------- | -------------------------------------------------------------------- |
| `user_id`          | UUID        | NOT NULL | —       | PK & FK → `users.users(id)` ON DELETE CASCADE                        |
| `japanese_level`   | VARCHAR(4)  | NULL     | —       | `N1`/`N2`/`N3`/`N4`/`N5`/NULL                                        |
| `residency_status` | VARCHAR(32) | NULL     | —       | `student`/`technical-intern`/`engineer`/`highly-skilled`/`spouse` 等 |
| `occupation`       | VARCHAR(64) | NULL     | —       | 自由入力可                                                           |
| `region`           | VARCHAR(64) | NULL     | —       | 都道府県＋市区町村（例：`東京都-渋谷区`）                            |
| `arrival_date`     | DATE        | NULL     | —       | 来日日（生活段階判定用）                                             |
| `life_stage`       | VARCHAR(16) | NULL     | —       | `arrival`/`settled`/`established`。`arrival_date` から自動算出可     |
| `created_at`       | TIMESTAMPTZ | NOT NULL | `NOW()` | —                                                                    |
| `updated_at`       | TIMESTAMPTZ | NOT NULL | `NOW()` | —                                                                    |

### `users.user_interests`

ユーザーの興味分野（多対多をフラットに保持）。

| 列         | 型          | 説明                                                       |
| ---------- | ----------- | ---------------------------------------------------------- |
| `user_id`  | UUID        | PK & FK → `users.users(id)` ON DELETE CASCADE              |
| `interest` | VARCHAR(64) | PK。例：`japanese-learning`, `housing`, `job`, `community` |

- 複合 PK：`(user_id, interest)`

### `users.user_preferences`

ユーザー設定（1:1）。

| 列                     | 型          | NULL     | 既定値  | 説明                                                                           |
| ---------------------- | ----------- | -------- | ------- | ------------------------------------------------------------------------------ |
| `user_id`              | UUID        | NOT NULL | —       | PK & FK → `users.users(id)` ON DELETE CASCADE                                  |
| `preferred_language`   | VARCHAR(8)  | NOT NULL | `'ja'`  | 表示言語（`native_language` と別管理：日本語学習中の人は `ja` 希望もあり得る） |
| `notification_enabled` | BOOLEAN     | NOT NULL | `TRUE`  | —                                                                              |
| `updated_at`           | TIMESTAMPTZ | NOT NULL | `NOW()` | —                                                                              |

---

## `items` schema（item-service が所有）

### `items.categories`

カテゴリ階層（自己参照）。

| 列          | 型           | NULL     | 説明                                                                                 |
| ----------- | ------------ | -------- | ------------------------------------------------------------------------------------ |
| `id`        | SERIAL       | NOT NULL | PK                                                                                   |
| `slug`      | VARCHAR(64)  | NOT NULL | UNIQUE。`job`, `housing`, `admin`, `medical`, `japanese-learning`, `community-event` |
| `name_ja`   | VARCHAR(128) | NOT NULL | 日本語表示名                                                                         |
| `name_en`   | VARCHAR(128) | NULL     | 英語表示名                                                                           |
| `parent_id` | INTEGER      | NULL     | FK → `items.categories(id)`。トップレベルは NULL                                     |

### `items.items`

推薦対象アイテム。

| 列                   | 型            | NULL     | 既定値              | 説明                                                                       |
| -------------------- | ------------- | -------- | ------------------- | -------------------------------------------------------------------------- |
| `id`                 | UUID          | NOT NULL | `gen_random_uuid()` | PK                                                                         |
| `category_id`        | INTEGER       | NOT NULL | —                   | FK → `items.categories(id)`                                                |
| `title`              | VARCHAR(255)  | NOT NULL | —                   | —                                                                          |
| `description`        | TEXT          | NULL     | —                   | 本文・概要                                                                 |
| `url`                | VARCHAR(1024) | NULL     | —                   | 外部リンク                                                                 |
| `region`             | VARCHAR(64)   | NULL     | —                   | 場所（地域フィルタ用）                                                     |
| `source`             | VARCHAR(64)   | NULL     | —                   | `gov`/`company`/`community` 等                                             |
| `min_japanese_level` | VARCHAR(4)    | NULL     | —                   | このアイテムを利用するのに必要な日本語レベル                               |
| `metadata`           | JSONB         | NULL     | `'{}'::jsonb`       | カテゴリ固有の項目（例：求人なら `{"salary": 1500, "shifts": "morning"}`） |
| `published_at`       | TIMESTAMPTZ   | NULL     | —                   | 公開日                                                                     |
| `expires_at`         | TIMESTAMPTZ   | NULL     | —                   | 失効日（NULL なら無期限）                                                  |
| `created_at`         | TIMESTAMPTZ   | NOT NULL | `NOW()`             | —                                                                          |
| `updated_at`         | TIMESTAMPTZ   | NOT NULL | `NOW()`             | —                                                                          |

- インデックス：`(category_id)`, `(region)`, `(expires_at)` — フィルタ高速化

### `items.tags` / `items.item_tags`

汎用タグ（多対多）。

| `items.tags` 列 | 型          | 説明   |
| --------------- | ----------- | ------ |
| `id`            | SERIAL      | PK     |
| `name`          | VARCHAR(64) | UNIQUE |

| `items.item_tags` 列 | 型      | 説明                                          |
| -------------------- | ------- | --------------------------------------------- |
| `item_id`            | UUID    | PK & FK → `items.items(id)` ON DELETE CASCADE |
| `tag_id`             | INTEGER | PK & FK → `items.tags(id)` ON DELETE CASCADE  |

### `items.item_languages`

アイテムが対応する言語（多対多）。

| 列         | 型         | 説明                                          |
| ---------- | ---------- | --------------------------------------------- |
| `item_id`  | UUID       | PK & FK → `items.items(id)` ON DELETE CASCADE |
| `language` | VARCHAR(8) | PK。BCP47（例：`ja`, `en`, `vi`）             |

### `items.feedbacks`

ユーザー行動・評価ログ。論文の閲覧・クリック・お気に入り・評価を統合。

| 列              | 型          | NULL     | 説明                                                               |
| --------------- | ----------- | -------- | ------------------------------------------------------------------ |
| `id`            | BIGSERIAL   | NOT NULL | PK                                                                 |
| `user_id`       | UUID        | NOT NULL | **論理 FK** → `users.users(id)`（schema 跨ぎの物理 FK は張らない） |
| `item_id`       | UUID        | NOT NULL | FK → `items.items(id)` ON DELETE CASCADE                           |
| `feedback_type` | VARCHAR(16) | NOT NULL | `view`/`click`/`favorite`/`rating`                                 |
| `rating`        | SMALLINT    | NULL     | 1〜5。`feedback_type='rating'` のときだけ NOT NULL                 |
| `created_at`    | TIMESTAMPTZ | NOT NULL | —                                                                  |

- インデックス：`(user_id, created_at DESC)`, `(item_id, created_at DESC)`
- CHECK：`(feedback_type='rating' AND rating BETWEEN 1 AND 5) OR (feedback_type<>'rating' AND rating IS NULL)`

---

## `ai` schema（ai-service が所有）

### `ai.user_embeddings`

ユーザーベクトル（1:1）。

| 列           | 型            | 説明                                        |
| ------------ | ------------- | ------------------------------------------- |
| `user_id`    | UUID          | PK。**論理 FK** → `users.users(id)`         |
| `embedding`  | `vector(384)` | `intfloat/multilingual-e5-small` の出力次元 |
| `updated_at` | TIMESTAMPTZ   | —                                           |

### `ai.item_embeddings`

アイテムベクトル（1:1）。

| 列           | 型            | 説明                                |
| ------------ | ------------- | ----------------------------------- |
| `item_id`    | UUID          | PK。**論理 FK** → `items.items(id)` |
| `embedding`  | `vector(384)` | —                                   |
| `updated_at` | TIMESTAMPTZ   | —                                   |

- インデックス：`USING hnsw (embedding vector_cosine_ops)` — 近似最近傍検索

### `ai.search_queries`

自然言語検索の履歴。

| 列           | 型            | NULL     | 説明                                                             |
| ------------ | ------------- | -------- | ---------------------------------------------------------------- |
| `id`         | BIGSERIAL     | NOT NULL | PK                                                               |
| `user_id`    | UUID          | NULL     | 未ログイン検索もあり得る                                         |
| `query`      | TEXT          | NOT NULL | 入力された自然言語                                               |
| `language`   | VARCHAR(8)    | NULL     | 自動判定または UI から取得                                       |
| `embedding`  | `vector(384)` | NULL     | クエリのベクトル化（オフライン処理する場合は遅延 NULL → 後埋め） |
| `created_at` | TIMESTAMPTZ   | NOT NULL | —                                                                |

- インデックス：`(user_id, created_at DESC)`

### `ai.recommendation_logs`

推薦結果の表示・クリック記録（評価実験用）。

| 列           | 型          | NULL     | 説明                                     |
| ------------ | ----------- | -------- | ---------------------------------------- |
| `id`         | BIGSERIAL   | NOT NULL | PK                                       |
| `user_id`    | UUID        | NOT NULL | **論理 FK**                              |
| `item_id`    | UUID        | NOT NULL | **論理 FK**                              |
| `score`      | REAL        | NOT NULL | アルゴリズムが出した推薦スコア           |
| `reason`     | TEXT        | NULL     | 推薦理由（LLM 生成文など）               |
| `algorithm`  | VARCHAR(32) | NULL     | `content`/`collaborative`/`hybrid`/`llm` |
| `shown_at`   | TIMESTAMPTZ | NOT NULL | —                                        |
| `clicked_at` | TIMESTAMPTZ | NULL     | NULL の間はクリックされていない          |

- インデックス：`(user_id, shown_at DESC)`, `(algorithm, shown_at DESC)` — 評価実験で集計しやすく
