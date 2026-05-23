-- RecoForeJP - シード: カテゴリ
-- 論文 1.2.1 で挙げられた生活支援情報の主要カテゴリを登録

INSERT INTO items.categories (slug, name_ja, name_en, parent_id) VALUES
    ('job',                '就職・アルバイト', 'Jobs',              NULL),
    ('housing',            '住居・不動産',     'Housing',           NULL),
    ('admin',              '行政手続き',       'Government',        NULL),
    ('medical',            '医療・防災',       'Medical & Safety',  NULL),
    ('japanese-learning',  '日本語学習',       'Japanese Learning', NULL),
    ('community-event',    '地域・イベント',   'Community Events',  NULL);

-- サブカテゴリ（slug の先頭で大分類が分かるよう設計）
INSERT INTO items.categories (slug, name_ja, name_en, parent_id) VALUES
    ('job-fulltime',      '正社員',           'Full-time',           (SELECT id FROM items.categories WHERE slug='job')),
    ('job-parttime',      'アルバイト',       'Part-time',           (SELECT id FROM items.categories WHERE slug='job')),
    ('job-intern',        'インターン',       'Internship',          (SELECT id FROM items.categories WHERE slug='job')),
    ('housing-apartment', 'アパート',         'Apartment',           (SELECT id FROM items.categories WHERE slug='housing')),
    ('housing-share',     'シェアハウス',     'Share House',         (SELECT id FROM items.categories WHERE slug='housing')),
    ('housing-dorm',      '寮',               'Dormitory',           (SELECT id FROM items.categories WHERE slug='housing'));
