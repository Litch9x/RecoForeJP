-- RecoForeJP - items schema テーブル定義
-- 所有: item-service (Java/Spring Boot)
-- 将来: 各テーブルは item-service の Flyway migrations へ移行

-- ----------------------------------------------------------------------
-- items.categories: カテゴリ階層
-- ----------------------------------------------------------------------
CREATE TABLE items.categories (
    id        SERIAL PRIMARY KEY,
    slug      VARCHAR(64) UNIQUE NOT NULL,
    name_ja   VARCHAR(128) NOT NULL,
    name_en   VARCHAR(128),
    parent_id INTEGER REFERENCES items.categories(id)
);
COMMENT ON TABLE items.categories IS 'アイテムカテゴリ（job, housing, admin, ...）';

-- ----------------------------------------------------------------------
-- items.items: 推薦対象アイテム
-- ----------------------------------------------------------------------
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
COMMENT ON TABLE items.items IS '推薦対象（求人・住居・行政情報など）';

-- ----------------------------------------------------------------------
-- items.tags / items.item_tags: タグ（多対多）
-- ----------------------------------------------------------------------
CREATE TABLE items.tags (
    id   SERIAL PRIMARY KEY,
    name VARCHAR(64) UNIQUE NOT NULL
);

CREATE TABLE items.item_tags (
    item_id UUID    NOT NULL REFERENCES items.items(id) ON DELETE CASCADE,
    tag_id  INTEGER NOT NULL REFERENCES items.tags(id)  ON DELETE CASCADE,
    PRIMARY KEY (item_id, tag_id)
);

-- ----------------------------------------------------------------------
-- items.item_languages: 対応言語（多対多）
-- ----------------------------------------------------------------------
CREATE TABLE items.item_languages (
    item_id  UUID       NOT NULL REFERENCES items.items(id) ON DELETE CASCADE,
    language VARCHAR(8) NOT NULL,
    PRIMARY KEY (item_id, language)
);
COMMENT ON TABLE items.item_languages IS 'アイテムが対応する言語（ja, en, vi, ...）';

-- ----------------------------------------------------------------------
-- items.feedbacks: フィードバック / 行動ログ
-- ----------------------------------------------------------------------
CREATE TABLE items.feedbacks (
    id            BIGSERIAL PRIMARY KEY,
    user_id       UUID NOT NULL,  -- logical FK -> users.users(id)
    item_id       UUID NOT NULL REFERENCES items.items(id) ON DELETE CASCADE,
    feedback_type VARCHAR(16) NOT NULL,
    rating        SMALLINT,
    created_at    TIMESTAMPTZ NOT NULL DEFAULT NOW(),
    CONSTRAINT chk_feedback_type CHECK (
        feedback_type IN ('view','click','favorite','rating')
    ),
    CONSTRAINT chk_rating_value CHECK (
        (feedback_type = 'rating' AND rating BETWEEN 1 AND 5)
        OR (feedback_type <> 'rating' AND rating IS NULL)
    )
);
CREATE INDEX idx_feedbacks_user ON items.feedbacks(user_id, created_at DESC);
CREATE INDEX idx_feedbacks_item ON items.feedbacks(item_id, created_at DESC);
COMMENT ON TABLE items.feedbacks IS '閲覧・クリック・お気に入り・評価を集約';
