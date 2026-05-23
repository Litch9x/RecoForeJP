-- RecoForeJP - シード: 開発・テスト用アイテム
-- 各カテゴリにつき数件、現実的な内容を用意（推薦アルゴリズム動作確認用）

-- ----------------------------------------------------------------------
-- 求人 (job)
-- ----------------------------------------------------------------------
INSERT INTO items.items (id, category_id, title, description, region, source, min_japanese_level, metadata, published_at)
SELECT
    '10000000-0000-0000-0000-000000000001'::uuid,
    c.id,
    '外国人歓迎 IT エンジニア募集（六本木）',
    '英語で業務 OK のスタートアップ。日本語学習サポートあり。リモート週3 可。',
    '東京都-港区', 'company-direct', 'N5',
    '{"salary_min": 4000000, "salary_max": 7000000, "employment_type": "fulltime", "remote_ok": true}'::jsonb,
    NOW() - INTERVAL '3 days'
FROM items.categories c WHERE c.slug = 'job-fulltime';

INSERT INTO items.items (id, category_id, title, description, region, source, min_japanese_level, metadata, published_at)
SELECT
    '10000000-0000-0000-0000-000000000002'::uuid,
    c.id,
    'ベトナム語話者向けカスタマーサポート（時給1500円）',
    'ベトナム人顧客対応のため、ベトナム語ネイティブ歓迎。日本語は日常会話レベルで OK。',
    '東京都-渋谷区', 'company-direct', 'N4',
    '{"hourly_wage": 1500, "employment_type": "parttime", "shifts": ["morning","afternoon"]}'::jsonb,
    NOW() - INTERVAL '1 day'
FROM items.categories c WHERE c.slug = 'job-parttime';

INSERT INTO items.items (id, category_id, title, description, region, source, min_japanese_level, metadata, published_at)
SELECT
    '10000000-0000-0000-0000-000000000003'::uuid,
    c.id,
    '飲食店ホールスタッフ（新宿・夜勤あり）',
    '居酒屋でのホール業務。日本語接客が必要。週末勤務優遇。',
    '東京都-新宿区', 'company-direct', 'N3',
    '{"hourly_wage": 1300, "employment_type": "parttime", "shifts": ["evening","night"]}'::jsonb,
    NOW() - INTERVAL '5 days'
FROM items.categories c WHERE c.slug = 'job-parttime';

-- ----------------------------------------------------------------------
-- 住居 (housing)
-- ----------------------------------------------------------------------
INSERT INTO items.items (id, category_id, title, description, region, source, min_japanese_level, metadata, published_at)
SELECT
    '20000000-0000-0000-0000-000000000001'::uuid,
    c.id,
    '外国人OK 渋谷区 1K アパート（保証人不要）',
    '英語対応の不動産屋経由。保証人不要、初期費用安め。駅徒歩 5 分。',
    '東京都-渋谷区', 'agency', 'N5',
    '{"rent": 75000, "size_m2": 22, "station_minutes": 5, "no_guarantor": true}'::jsonb,
    NOW() - INTERVAL '2 days'
FROM items.categories c WHERE c.slug = 'housing-apartment';

INSERT INTO items.items (id, category_id, title, description, region, source, min_japanese_level, metadata, published_at)
SELECT
    '20000000-0000-0000-0000-000000000002'::uuid,
    c.id,
    '国際学生寮（早稲田）',
    '早稲田大学近く。多国籍の留学生が住むシェアハウス型寮。家具家電付き。',
    '東京都-新宿区', 'university', 'N5',
    '{"rent": 55000, "furnished": true, "size_m2": 12, "target": "international-student"}'::jsonb,
    NOW() - INTERVAL '10 days'
FROM items.categories c WHERE c.slug = 'housing-dorm';

INSERT INTO items.items (id, category_id, title, description, region, source, min_japanese_level, metadata, published_at)
SELECT
    '20000000-0000-0000-0000-000000000003'::uuid,
    c.id,
    'シェアハウス横浜（多国籍・即入居可）',
    '横浜駅徒歩 10 分。10 ヶ国以上の入居者。共有スペースあり。',
    '神奈川県-横浜市', 'agency', 'N5',
    '{"rent": 60000, "shared": true, "common_areas": ["kitchen","lounge","gym"]}'::jsonb,
    NOW() - INTERVAL '7 days'
FROM items.categories c WHERE c.slug = 'housing-share';

-- ----------------------------------------------------------------------
-- 行政 (admin)
-- ----------------------------------------------------------------------
INSERT INTO items.items (id, category_id, title, description, region, source, min_japanese_level, metadata, published_at)
SELECT
    '30000000-0000-0000-0000-000000000001'::uuid,
    c.id,
    '在留資格更新の手続きガイド（やさしい日本語）',
    '在留期間更新の必要書類・流れ・注意点を、やさしい日本語で解説。',
    NULL, 'gov', 'N4',
    '{"document_type": "guide", "languages_available": ["ja-easy","en","vi","zh-CN"]}'::jsonb,
    NOW() - INTERVAL '30 days'
FROM items.categories c WHERE c.slug = 'admin';

INSERT INTO items.items (id, category_id, title, description, region, source, min_japanese_level, metadata, published_at)
SELECT
    '30000000-0000-0000-0000-000000000002'::uuid,
    c.id,
    'マイナンバーカード申請方法（オンライン）',
    '住民登録後にマイナンバーカードをオンラインで申請する手順。',
    NULL, 'gov', 'N3',
    '{"document_type": "procedure", "online_supported": true}'::jsonb,
    NOW() - INTERVAL '60 days'
FROM items.categories c WHERE c.slug = 'admin';

-- ----------------------------------------------------------------------
-- 医療 (medical)
-- ----------------------------------------------------------------------
INSERT INTO items.items (id, category_id, title, description, region, source, min_japanese_level, metadata, published_at)
SELECT
    '40000000-0000-0000-0000-000000000001'::uuid,
    c.id,
    '英語対応病院（東京・港区）',
    '英語で診察可能な総合病院。予約はオンラインで受付。',
    '東京都-港区', 'directory', 'N5',
    '{"languages": ["en","ja"], "specialties": ["internal","pediatric","ent"]}'::jsonb,
    NOW() - INTERVAL '90 days'
FROM items.categories c WHERE c.slug = 'medical';

INSERT INTO items.items (id, category_id, title, description, region, source, min_japanese_level, metadata, published_at)
SELECT
    '40000000-0000-0000-0000-000000000002'::uuid,
    c.id,
    'ベトナム語通訳のあるクリニック（新宿）',
    '事前予約でベトナム語通訳が同席するクリニック。健康保険対応。',
    '東京都-新宿区', 'directory', 'N5',
    '{"languages": ["vi","ja"], "interpreter": "by-appointment"}'::jsonb,
    NOW() - INTERVAL '15 days'
FROM items.categories c WHERE c.slug = 'medical';

-- ----------------------------------------------------------------------
-- 日本語学習 (japanese-learning)
-- ----------------------------------------------------------------------
INSERT INTO items.items (id, category_id, title, description, region, source, min_japanese_level, metadata, published_at)
SELECT
    '50000000-0000-0000-0000-000000000001'::uuid,
    c.id,
    'やさしい日本語クラス（無料・新宿区）',
    'ボランティア団体運営。毎週土曜、初級者向け、無料。',
    '東京都-新宿区', 'community', 'N5',
    '{"price": 0, "level": "beginner", "frequency": "weekly"}'::jsonb,
    NOW() - INTERVAL '4 days'
FROM items.categories c WHERE c.slug = 'japanese-learning';

INSERT INTO items.items (id, category_id, title, description, region, source, min_japanese_level, metadata, published_at)
SELECT
    '50000000-0000-0000-0000-000000000002'::uuid,
    c.id,
    'JLPT N3 対策講座（オンライン）',
    '4 週間で N3 文法を総復習。模擬試験付き。月額制。',
    NULL, 'school', 'N4',
    '{"price": 9800, "level": "intermediate", "online": true, "duration_weeks": 4}'::jsonb,
    NOW() - INTERVAL '6 days'
FROM items.categories c WHERE c.slug = 'japanese-learning';

-- ----------------------------------------------------------------------
-- 地域イベント (community-event)
-- ----------------------------------------------------------------------
INSERT INTO items.items (id, category_id, title, description, region, source, min_japanese_level, metadata, published_at, expires_at)
SELECT
    '60000000-0000-0000-0000-000000000001'::uuid,
    c.id,
    '国際交流パーティー（新宿）',
    '毎月開催。日本人と外国人が気軽に交流。日本語＆英語で進行。',
    '東京都-新宿区', 'community', 'N5',
    '{"price": 1500, "format": "in-person", "monthly": true}'::jsonb,
    NOW() - INTERVAL '2 days',
    NOW() + INTERVAL '20 days'
FROM items.categories c WHERE c.slug = 'community-event';

INSERT INTO items.items (id, category_id, title, description, region, source, min_japanese_level, metadata, published_at, expires_at)
SELECT
    '60000000-0000-0000-0000-000000000002'::uuid,
    c.id,
    'ベトナム人会 月例会（横浜）',
    '横浜在住のベトナム人向け交流会。情報交換・お悔やみ会含む。',
    '神奈川県-横浜市', 'community', 'N5',
    '{"price": 0, "format": "in-person", "target_nationality": "VN"}'::jsonb,
    NOW() - INTERVAL '8 days',
    NOW() + INTERVAL '14 days'
FROM items.categories c WHERE c.slug = 'community-event';

-- ----------------------------------------------------------------------
-- アイテムへのタグ付け（主要なもののみ抜粋）
-- ----------------------------------------------------------------------
INSERT INTO items.item_tags (item_id, tag_id)
SELECT i.id, t.id FROM items.items i, items.tags t
WHERE (i.id, t.name) IN (
    ('10000000-0000-0000-0000-000000000001'::uuid, 'foreigner-welcome'),
    ('10000000-0000-0000-0000-000000000001'::uuid, 'english-ok'),
    ('10000000-0000-0000-0000-000000000001'::uuid, 'remote-ok'),
    ('10000000-0000-0000-0000-000000000001'::uuid, 'it-engineering'),
    ('10000000-0000-0000-0000-000000000002'::uuid, 'vietnamese-ok'),
    ('10000000-0000-0000-0000-000000000002'::uuid, 'foreigner-welcome'),
    ('10000000-0000-0000-0000-000000000003'::uuid, 'food-service'),
    ('10000000-0000-0000-0000-000000000003'::uuid, 'night-shift'),
    ('20000000-0000-0000-0000-000000000001'::uuid, 'foreigner-welcome'),
    ('20000000-0000-0000-0000-000000000001'::uuid, 'no-guarantor-required'),
    ('20000000-0000-0000-0000-000000000001'::uuid, 'near-station'),
    ('20000000-0000-0000-0000-000000000002'::uuid, 'student-friendly'),
    ('20000000-0000-0000-0000-000000000003'::uuid, 'foreigner-welcome'),
    ('30000000-0000-0000-0000-000000000001'::uuid, 'beginner-japanese-ok'),
    ('30000000-0000-0000-0000-000000000001'::uuid, 'multilingual-support'),
    ('40000000-0000-0000-0000-000000000001'::uuid, 'english-ok'),
    ('40000000-0000-0000-0000-000000000002'::uuid, 'vietnamese-ok'),
    ('50000000-0000-0000-0000-000000000001'::uuid, 'free'),
    ('50000000-0000-0000-0000-000000000001'::uuid, 'beginner-japanese-ok'),
    ('50000000-0000-0000-0000-000000000002'::uuid, 'online'),
    ('60000000-0000-0000-0000-000000000001'::uuid, 'international-exchange'),
    ('60000000-0000-0000-0000-000000000002'::uuid, 'free'),
    ('60000000-0000-0000-0000-000000000002'::uuid, 'international-exchange')
);

-- ----------------------------------------------------------------------
-- アイテムの対応言語
-- ----------------------------------------------------------------------
INSERT INTO items.item_languages (item_id, language) VALUES
    ('10000000-0000-0000-0000-000000000001', 'ja'),
    ('10000000-0000-0000-0000-000000000001', 'en'),
    ('10000000-0000-0000-0000-000000000002', 'ja'),
    ('10000000-0000-0000-0000-000000000002', 'vi'),
    ('10000000-0000-0000-0000-000000000003', 'ja'),
    ('20000000-0000-0000-0000-000000000001', 'ja'),
    ('20000000-0000-0000-0000-000000000001', 'en'),
    ('20000000-0000-0000-0000-000000000002', 'ja'),
    ('20000000-0000-0000-0000-000000000002', 'en'),
    ('20000000-0000-0000-0000-000000000003', 'ja'),
    ('20000000-0000-0000-0000-000000000003', 'en'),
    ('30000000-0000-0000-0000-000000000001', 'ja'),
    ('30000000-0000-0000-0000-000000000001', 'en'),
    ('30000000-0000-0000-0000-000000000001', 'vi'),
    ('30000000-0000-0000-0000-000000000001', 'zh-CN'),
    ('30000000-0000-0000-0000-000000000002', 'ja'),
    ('40000000-0000-0000-0000-000000000001', 'ja'),
    ('40000000-0000-0000-0000-000000000001', 'en'),
    ('40000000-0000-0000-0000-000000000002', 'ja'),
    ('40000000-0000-0000-0000-000000000002', 'vi'),
    ('50000000-0000-0000-0000-000000000001', 'ja'),
    ('50000000-0000-0000-0000-000000000002', 'ja'),
    ('60000000-0000-0000-0000-000000000001', 'ja'),
    ('60000000-0000-0000-0000-000000000001', 'en'),
    ('60000000-0000-0000-0000-000000000002', 'ja'),
    ('60000000-0000-0000-0000-000000000002', 'vi');
