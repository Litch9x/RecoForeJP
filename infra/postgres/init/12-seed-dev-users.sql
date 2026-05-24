-- RecoForeJP - シード: 開発・テスト用ユーザー
-- ⚠️ パスワードハッシュは bcrypt("password123") - 開発用のみ
--    本番環境ではこのファイルは適用しないこと

-- 固定 UUID を使うことで、サービス間連携やテストで参照しやすくする

-- ----------------------------------------------------------------------
-- User 1: ベトナム出身の留学生（来日 6 ヶ月、N3）
-- ----------------------------------------------------------------------
INSERT INTO users.users (id, email, password_hash, nationality, native_language) VALUES
    ('00000000-0000-0000-0000-000000000001',
     'nguyen.student@example.com',
     '$2b$10$GmsSAoiabUIXvmYdPpO9B.jL8xAB7Ocw325XZssN.puaTchcAiv26',
     'VN', 'vi');

INSERT INTO users.user_profiles (user_id, japanese_level, residency_status, occupation, region, arrival_date, life_stage) VALUES
    ('00000000-0000-0000-0000-000000000001',
     'N3', 'student', '大学生', '東京都-新宿区',
     '2025-11-15', 'settled');

INSERT INTO users.user_interests (user_id, interest) VALUES
    ('00000000-0000-0000-0000-000000000001', 'japanese-learning'),
    ('00000000-0000-0000-0000-000000000001', 'job'),
    ('00000000-0000-0000-0000-000000000001', 'community-event');

INSERT INTO users.user_preferences (user_id, preferred_language, notification_enabled) VALUES
    ('00000000-0000-0000-0000-000000000001', 'ja', TRUE);

-- ----------------------------------------------------------------------
-- User 2: インド出身の IT エンジニア（来日 1 ヶ月、N5）
-- ----------------------------------------------------------------------
INSERT INTO users.users (id, email, password_hash, nationality, native_language) VALUES
    ('00000000-0000-0000-0000-000000000002',
     'raj.engineer@example.com',
     '$2b$10$GmsSAoiabUIXvmYdPpO9B.jL8xAB7Ocw325XZssN.puaTchcAiv26',
     'IN', 'en');

INSERT INTO users.user_profiles (user_id, japanese_level, residency_status, occupation, region, arrival_date, life_stage) VALUES
    ('00000000-0000-0000-0000-000000000002',
     'N5', 'engineer', 'ソフトウェアエンジニア', '東京都-港区',
     '2026-04-20', 'arrival');

INSERT INTO users.user_interests (user_id, interest) VALUES
    ('00000000-0000-0000-0000-000000000002', 'housing'),
    ('00000000-0000-0000-0000-000000000002', 'admin'),
    ('00000000-0000-0000-0000-000000000002', 'japanese-learning');

INSERT INTO users.user_preferences (user_id, preferred_language, notification_enabled) VALUES
    ('00000000-0000-0000-0000-000000000002', 'en', TRUE);

-- ----------------------------------------------------------------------
-- User 3: 中国出身の長期居住者（来日 5 年、N1、永住）
-- ----------------------------------------------------------------------
INSERT INTO users.users (id, email, password_hash, nationality, native_language) VALUES
    ('00000000-0000-0000-0000-000000000003',
     'wang.resident@example.com',
     '$2b$10$GmsSAoiabUIXvmYdPpO9B.jL8xAB7Ocw325XZssN.puaTchcAiv26',
     'CN', 'zh-CN');

INSERT INTO users.user_profiles (user_id, japanese_level, residency_status, occupation, region, arrival_date, life_stage) VALUES
    ('00000000-0000-0000-0000-000000000003',
     'N1', 'permanent', '会社員', '神奈川県-横浜市',
     '2021-04-01', 'established');

INSERT INTO users.user_interests (user_id, interest) VALUES
    ('00000000-0000-0000-0000-000000000003', 'community-event'),
    ('00000000-0000-0000-0000-000000000003', 'medical');

INSERT INTO users.user_preferences (user_id, preferred_language, notification_enabled) VALUES
    ('00000000-0000-0000-0000-000000000003', 'ja', FALSE);
