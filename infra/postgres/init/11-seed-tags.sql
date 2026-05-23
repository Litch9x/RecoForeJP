-- RecoForeJP - シード: タグ
-- 検索・フィルタでよく使われるタグの初期セット

INSERT INTO items.tags (name) VALUES
    -- 言語対応
    ('multilingual-support'),
    ('vietnamese-ok'),
    ('english-ok'),
    ('chinese-ok'),

    -- 在留資格・属性向け
    ('foreigner-welcome'),
    ('student-friendly'),
    ('no-guarantor-required'),
    ('no-japanese-required'),
    ('beginner-japanese-ok'),

    -- 立地・条件
    ('near-station'),
    ('remote-ok'),
    ('night-shift'),
    ('weekend-ok'),

    -- 業界（job 向け）
    ('it-engineering'),
    ('food-service'),
    ('manufacturing'),
    ('hospitality'),
    ('translation-interpretation'),

    -- イベント種別
    ('international-exchange'),
    ('free'),
    ('online'),
    ('hands-on');
