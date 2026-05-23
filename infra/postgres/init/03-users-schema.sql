-- RecoForeJP - users schema テーブル定義
-- 所有: user-service (Java/Spring Boot)
-- 将来: 各テーブルは user-service の Flyway migrations へ移行（RECO-13 以降）

-- ----------------------------------------------------------------------
-- users.users: アカウント
-- ----------------------------------------------------------------------
CREATE TABLE users.users (
    id              UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    email           VARCHAR(255) UNIQUE NOT NULL,
    password_hash   VARCHAR(255) NOT NULL,
    nationality     VARCHAR(2),                          -- ISO 3166-1 alpha-2
    native_language VARCHAR(8),                          -- BCP47
    created_at      TIMESTAMPTZ NOT NULL DEFAULT NOW(),
    updated_at      TIMESTAMPTZ NOT NULL DEFAULT NOW()
);
COMMENT ON TABLE users.users IS 'アカウント基本情報';

-- ----------------------------------------------------------------------
-- users.user_profiles: 拡張プロフィール (1:1)
-- ----------------------------------------------------------------------
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
    CONSTRAINT chk_japanese_level CHECK (
        japanese_level IS NULL OR japanese_level IN ('N1','N2','N3','N4','N5')
    ),
    CONSTRAINT chk_life_stage CHECK (
        life_stage IS NULL OR life_stage IN ('arrival','settled','established')
    )
);
COMMENT ON TABLE users.user_profiles IS '日本語レベル・在留資格・地域・生活段階など';

-- ----------------------------------------------------------------------
-- users.user_interests: 興味分野 (多対多をフラットに)
-- ----------------------------------------------------------------------
CREATE TABLE users.user_interests (
    user_id  UUID NOT NULL REFERENCES users.users(id) ON DELETE CASCADE,
    interest VARCHAR(64) NOT NULL,
    PRIMARY KEY (user_id, interest)
);
COMMENT ON TABLE users.user_interests IS 'ユーザーの興味分野（例: job, housing, japanese-learning）';

-- ----------------------------------------------------------------------
-- users.user_preferences: 設定 (1:1)
-- ----------------------------------------------------------------------
CREATE TABLE users.user_preferences (
    user_id              UUID PRIMARY KEY REFERENCES users.users(id) ON DELETE CASCADE,
    preferred_language   VARCHAR(8)  NOT NULL DEFAULT 'ja',
    notification_enabled BOOLEAN     NOT NULL DEFAULT TRUE,
    updated_at           TIMESTAMPTZ NOT NULL DEFAULT NOW()
);
COMMENT ON TABLE users.user_preferences IS 'UI 言語、通知 ON/OFF など';
