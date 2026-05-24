"""scorer の純粋関数ユニットテスト（DB 非依存）."""

from ai_service.recommend.scorer import ItemFeatures, UserContext, _jlpt_level_ok, score_item


def _item(**kwargs) -> ItemFeatures:
    """テスト用のデフォルト値を持つ ItemFeatures ファクトリ。"""
    defaults = {
        "id": "item-1",
        "title": "Sample",
        "category_slug": "job",
        "region": None,
        "min_japanese_level": None,
        "languages": (),
        "tags": (),
    }
    defaults.update(kwargs)
    return ItemFeatures(**defaults)


def _user(**kwargs) -> UserContext:
    defaults = {
        "japanese_level": "N3",
        "region": None,
        "preferred_language": "ja",
        "interest_categories": (),
    }
    defaults.update(kwargs)
    return UserContext(**defaults)


# ---------- _jlpt_level_ok ----------


def test_jlpt_no_requirement_always_ok():
    assert _jlpt_level_ok("N5", None) is True
    assert _jlpt_level_ok(None, None) is True


def test_jlpt_unknown_user_only_n5_items_pass():
    assert _jlpt_level_ok(None, "N5") is True
    assert _jlpt_level_ok(None, "N4") is False


def test_jlpt_user_at_or_above_required_ok():
    assert _jlpt_level_ok("N3", "N3") is True
    assert _jlpt_level_ok("N1", "N3") is True
    assert _jlpt_level_ok("N5", "N3") is False


# ---------- score_item ----------


def test_score_zero_when_user_japanese_below_item_requirement():
    user = _user(japanese_level="N5")
    item = _item(min_japanese_level="N2")
    result = score_item(user, item)
    assert result.score == 0.0
    assert any("filtered" in r for r in result.reasons)


def test_score_includes_category_match():
    user = _user(interest_categories=("job", "housing"))
    item = _item(category_slug="job")
    result = score_item(user, item)
    assert result.score >= 3.0
    assert any("category matches" in r for r in result.reasons)


def test_score_includes_region_match():
    user = _user(region="東京都-渋谷区")
    item = _item(region="東京都-渋谷区")
    result = score_item(user, item)
    assert result.score >= 2.0


def test_score_region_no_match_when_mismatched():
    user = _user(region="東京都-渋谷区")
    item = _item(region="神奈川県-横浜市")
    result = score_item(user, item)
    assert result.score == 0.0  # no other signals match


def test_score_includes_language_match():
    user = _user(preferred_language="vi")
    item = _item(languages=("ja", "vi"))
    result = score_item(user, item)
    # language match (2.0) + multilingual bonus for non-ja user (1.0)
    assert result.score >= 3.0


def test_foreigner_welcome_bonus_only_for_low_level_users():
    item = _item(tags=("foreigner-welcome",))

    # 低レベル → ボーナス
    low_user = _user(japanese_level="N5")
    assert score_item(low_user, item).score >= 1.5

    # 上級者にはボーナスなし
    high_user = _user(japanese_level="N1")
    assert score_item(high_user, item).score == 0.0


def test_score_combines_multiple_signals():
    user = _user(
        japanese_level="N3",
        region="東京都-港区",
        preferred_language="en",
        interest_categories=("job",),
    )
    item = _item(
        category_slug="job",
        region="東京都-港区",
        languages=("ja", "en"),
        tags=("foreigner-welcome",),
    )
    # category(3) + region(2) + language(2) + multilingual(1) = 8.0
    # （foreigner-welcome は N3 ユーザーには対象外）
    result = score_item(user, item)
    assert result.score == 8.0
    assert len(result.reasons) == 4
