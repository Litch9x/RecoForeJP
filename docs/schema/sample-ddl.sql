-- =============================================================================
-- RecoForeJP - リファレンス DDL
--
-- このファイルは設計確認用であり、本番マイグレーションには使わない。
-- 実際の DDL は各サービスの migration ツールで作成する（RECO-11 で対応）:
--   - user-service / item-service: Flyway (V1__init.sql, V2__...)
--   - ai-service: Alembic
--
-- PostgreSQL 16 + pgvector 前提。
-- =============================================================================

-- ----------------------- schemas & extensions -------------------------------
CREATE SCHEMA IF NOT EXISTS users;
CREATE SCHEMA IF NOT EXISTS items;
CREATE SCHEMA IF NOT EXISTS ai;

CREATE EXTENSION IF NOT EXISTS vector;   -- pgvector
CREATE EXTENSION IF NOT EXISTS pgcrypto; -- gen_random_uuid() の保険

-- =============================================================================
-- users schema
-- =============================================================================

CREATE TABLE users.users (
    id              UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    email           VARCHAR(255) UNIQUE NOT NULL,
    password_hash   VARCHAR(255) NOT NULL,
    nationality     VARCHAR(2),
    native_language VARCHAR(8),
    created_at      TIMESTAMPTZ NOT NULL DEFAULT NOW(),
    updated_at      TIMESTAMPTZ NOT NULL DEFAULT NOW()
);

CREATE TABLE users.user_profiles (
    user_id          UUID PRIMARY KEY REFERENCES users.users(id) ON DELETE CASCADE,
    japanese_level   VARCHAR(4),
    residency_status VARCHAR(32),
    occupation       VARCHAR(64),
    region           VARCHAR(64),
    arrival_date     DATE,
    life_stage       VARCHAR(16),
    created_at       TIMESTAMPTZ NOT NULL DEFAULT NOW(),
    updated_at       TIMESTAMPTZ NOT NULL DEFAULT NOW(),
    CONSTRAINT chk_japanese_level CHECK (japanese_level IS NULL OR japanese_level IN ('N1','N2','N3','N4','N5')),
    CONSTRAINT chk_life_stage     CHECK (life_stage IS NULL OR life_stage IN ('arrival','settled','established'))
);

CREATE TABLE users.user_interests (
    user_id  UUID NOT NULL REFERENCES users.users(id) ON DELETE CASCADE,
    interest VARCHAR(64) NOT NULL,
    PRIMARY KEY (user_id, interest)
);

CREATE TABLE users.user_preferences (
    user_id              UUID PRIMARY KEY REFERENCES users.users(id) ON DELETE CASCADE,
    preferred_language   VARCHAR(8) NOT NULL DEFAULT 'ja',
    notification_enabled BOOLEAN    NOT NULL DEFAULT TRUE,
    updated_at           TIMESTAMPTZ NOT NULL DEFAULT NOW()
);

-- =============================================================================
-- items schema
-- =============================================================================

CREATE TABLE items.categories (
    id        SERIAL PRIMARY KEY,
    slug      VARCHAR(64) UNIQUE NOT NULL,
    name_ja   VARCHAR(128) NOT NULL,
    name_en   VARCHAR(128),
    parent_id INTEGER REFERENCES items.categories(id)
);

CREATE TABLE items.items (
    id                 UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    category_id        INTEGER NOT NULL REFERENCES items.categories(id),
    title              VARCHAR(255) NOT NULL,
    description        TEXT,
    url                VARCHAR(1024),
    region             VARCHAR(64),
    source             VARCHAR(64),
    min_japanese_level VARCHAR(4),
    metadata           JSONB NOT NULL DEFAULT '{}'::jsonb,
    published_at       TIMESTAMPTZ,
    expires_at         TIMESTAMPTZ,
    created_at         TIMESTAMPTZ NOT NULL DEFAULT NOW(),
    updated_at         TIMESTAMPTZ NOT NULL DEFAULT NOW()
);
CREATE INDEX idx_items_category   ON items.items(category_id);
CREATE INDEX idx_items_region     ON items.items(region);
CREATE INDEX idx_items_expires_at ON items.items(expires_at);

CREATE TABLE items.tags (
    id   SERIAL PRIMARY KEY,
    name VARCHAR(64) UNIQUE NOT NULL
);

CREATE TABLE items.item_tags (
    item_id UUID    NOT NULL REFERENCES items.items(id) ON DELETE CASCADE,
    tag_id  INTEGER NOT NULL REFERENCES items.tags(id)  ON DELETE CASCADE,
    PRIMARY KEY (item_id, tag_id)
);

CREATE TABLE items.item_languages (
    item_id  UUID        NOT NULL REFERENCES items.items(id) ON DELETE CASCADE,
    language VARCHAR(8)  NOT NULL,
    PRIMARY KEY (item_id, language)
);

CREATE TABLE items.feedbacks (
    id            BIGSERIAL PRIMARY KEY,
    user_id       UUID    NOT NULL,  -- logical FK to users.users(id)
    item_id       UUID    NOT NULL REFERENCES items.items(id) ON DELETE CASCADE,
    feedback_type VARCHAR(16) NOT NULL,
    rating        SMALLINT,
    created_at    TIMESTAMPTZ NOT NULL DEFAULT NOW(),
    CONSTRAINT chk_feedback_type CHECK (feedback_type IN ('view','click','favorite','rating')),
    CONSTRAINT chk_rating_value  CHECK (
        (feedback_type = 'rating' AND rating BETWEEN 1 AND 5)
        OR (feedback_type <> 'rating' AND rating IS NULL)
    )
);
CREATE INDEX idx_feedbacks_user ON items.feedbacks(user_id, created_at DESC);
CREATE INDEX idx_feedbacks_item ON items.feedbacks(item_id, created_at DESC);

-- =============================================================================
-- ai schema
-- =============================================================================

CREATE TABLE ai.user_embeddings (
    user_id    UUID PRIMARY KEY,    -- logical FK
    embedding  vector(384) NOT NULL,
    updated_at TIMESTAMPTZ NOT NULL DEFAULT NOW()
);

CREATE TABLE ai.item_embeddings (
    item_id    UUID PRIMARY KEY,    -- logical FK
    embedding  vector(384) NOT NULL,
    updated_at TIMESTAMPTZ NOT NULL DEFAULT NOW()
);
CREATE INDEX idx_item_embeddings_hnsw
    ON ai.item_embeddings
    USING hnsw (embedding vector_cosine_ops);

CREATE TABLE ai.search_queries (
    id         BIGSERIAL PRIMARY KEY,
    user_id    UUID,           -- nullable: 未ログインも可
    query      TEXT NOT NULL,
    language   VARCHAR(8),
    embedding  vector(384),
    created_at TIMESTAMPTZ NOT NULL DEFAULT NOW()
);
CREATE INDEX idx_search_queries_user ON ai.search_queries(user_id, created_at DESC);

CREATE TABLE ai.recommendation_logs (
    id         BIGSERIAL PRIMARY KEY,
    user_id    UUID NOT NULL,   -- logical FK
    item_id    UUID NOT NULL,   -- logical FK
    score      REAL NOT NULL,
    reason     TEXT,
    algorithm  VARCHAR(32),
    shown_at   TIMESTAMPTZ NOT NULL DEFAULT NOW(),
    clicked_at TIMESTAMPTZ,
    CONSTRAINT chk_algorithm CHECK (
        algorithm IS NULL
        OR algorithm IN ('content','collaborative','hybrid','llm')
    )
);
CREATE INDEX idx_reco_logs_user      ON ai.recommendation_logs(user_id, shown_at DESC);
CREATE INDEX idx_reco_logs_algorithm ON ai.recommendation_logs(algorithm, shown_at DESC);
