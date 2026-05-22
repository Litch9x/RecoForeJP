-- RecoForeJP - PostgreSQL 初期化スクリプト
-- pgvector エクステンションを有効化（埋め込みベクトルの保存・検索用）

CREATE EXTENSION IF NOT EXISTS vector;
