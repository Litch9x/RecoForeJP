-- RecoForeJP - Schema 作成
-- 各マイクロサービスが所有するスキーマを定義。
-- 詳細は docs/schema/README.md を参照。

CREATE SCHEMA IF NOT EXISTS users;     -- user-service
CREATE SCHEMA IF NOT EXISTS items;     -- item-service
CREATE SCHEMA IF NOT EXISTS ai;        -- ai-service

COMMENT ON SCHEMA users IS 'user-service: アカウント・プロフィール・興味・設定';
COMMENT ON SCHEMA items IS 'item-service: 推薦対象アイテム・カテゴリ・タグ・フィードバック';
COMMENT ON SCHEMA ai    IS 'ai-service: 埋め込みベクトル・検索履歴・推薦ログ';
