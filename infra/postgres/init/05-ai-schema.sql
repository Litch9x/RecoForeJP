-- RecoForeJP - ai schema テーブル定義
-- 所有: ai-service (Python/FastAPI)
-- 将来: 各テーブルは ai-service の Alembic migrations へ移行

-- ----------------------------------------------------------------------
-- ai.user_embeddings: ユーザーベクトル (1:1)
-- ----------------------------------------------------------------------
CREATE TABLE ai.user_embeddings (
    user_id    UUID PRIMARY KEY,           -- logical FK -> users.users(id)
    embedding  vector(384) NOT NULL,       -- multilingual-e5-small の出力次元
    updated_at TIMESTAMPTZ NOT NULL DEFAULT NOW()
);
COMMENT ON TABLE ai.user_embeddings IS 'ユーザー属性・興味をベクトル化したもの';

-- ----------------------------------------------------------------------
-- ai.item_embeddings: アイテムベクトル (1:1)
-- ----------------------------------------------------------------------
CREATE TABLE ai.item_embeddings (
    item_id    UUID PRIMARY KEY,           -- logical FK -> items.items(id)
    embedding  vector(384) NOT NULL,
    updated_at TIMESTAMPTZ NOT NULL DEFAULT NOW()
);

-- HNSW: 近似最近傍検索（pgvector 0.5+）
-- リスト数・効率は実データ規模で調整。コサイン類似度を使用。
CREATE INDEX idx_item_embeddings_hnsw
    ON ai.item_embeddings
    USING hnsw (embedding vector_cosine_ops);

COMMENT ON TABLE ai.item_embeddings IS 'アイテム本文・タグから生成したベクトル';

-- ----------------------------------------------------------------------
-- ai.search_queries: 自然言語検索履歴
-- ----------------------------------------------------------------------
CREATE TABLE ai.search_queries (
    id         BIGSERIAL PRIMARY KEY,
    user_id    UUID,                       -- nullable: 未ログイン検索もあり
    query      TEXT NOT NULL,
    language   VARCHAR(8),
    embedding  vector(384),                -- 後で埋める場合があるので nullable
    created_at TIMESTAMPTZ NOT NULL DEFAULT NOW()
);
CREATE INDEX idx_search_queries_user ON ai.search_queries(user_id, created_at DESC);
COMMENT ON TABLE ai.search_queries IS '自然言語クエリのログ（行動分析用）';

-- ----------------------------------------------------------------------
-- ai.recommendation_logs: 推薦表示・クリック履歴
-- ----------------------------------------------------------------------
CREATE TABLE ai.recommendation_logs (
    id         BIGSERIAL PRIMARY KEY,
    user_id    UUID NOT NULL,              -- logical FK
    item_id    UUID NOT NULL,              -- logical FK
    score      REAL NOT NULL,
    reason     TEXT,
    algorithm  VARCHAR(32),
    shown_at   TIMESTAMPTZ NOT NULL DEFAULT NOW(),
    clicked_at TIMESTAMPTZ,
    CONSTRAINT chk_algorithm CHECK (
        algorithm IS NULL OR algorithm IN ('content','collaborative','hybrid','llm')
    )
);
CREATE INDEX idx_reco_logs_user      ON ai.recommendation_logs(user_id, shown_at DESC);
CREATE INDEX idx_reco_logs_algorithm ON ai.recommendation_logs(algorithm, shown_at DESC);
COMMENT ON TABLE ai.recommendation_logs IS '推薦の表示とクリックを記録（評価実験用）';
