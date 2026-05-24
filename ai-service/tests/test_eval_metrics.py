"""ai_service.eval.metrics の単体テスト。"""

from __future__ import annotations

import math

import pytest

from ai_service.eval.metrics import (
    dcg_at_k,
    idcg_at_k,
    ndcg_at_k,
    precision_at_k,
    recall_at_k,
)


class TestPrecisionAtK:
    def test_all_relevant_in_top_k(self) -> None:
        assert precision_at_k(["a", "b", "c"], {"a", "b", "c"}, k=3) == 1.0

    def test_no_relevant(self) -> None:
        assert precision_at_k(["a", "b", "c"], {"x", "y"}, k=3) == 0.0

    def test_partial(self) -> None:
        # top-5 中 2 件 hit
        assert precision_at_k(["a", "b", "c", "d", "e"], {"a", "c"}, k=5) == pytest.approx(0.4)

    def test_k_larger_than_results(self) -> None:
        # 3 件しか結果が無くても分母は k=10
        assert precision_at_k(["a", "b", "c"], {"a", "b", "c"}, k=10) == pytest.approx(0.3)

    def test_k_zero_raises(self) -> None:
        with pytest.raises(ValueError):
            precision_at_k(["a"], {"a"}, k=0)


class TestRecallAtK:
    def test_all_relevant_in_top_k(self) -> None:
        assert recall_at_k(["a", "b", "c"], {"a", "b", "c"}, k=3) == 1.0

    def test_partial(self) -> None:
        # 4 個の relevant のうち 2 個を top-5 で拾う
        assert recall_at_k(["a", "b", "c", "d", "e"], {"a", "b", "x", "y"}, k=5) == pytest.approx(0.5)

    def test_empty_relevant_returns_zero(self) -> None:
        assert recall_at_k(["a", "b"], set(), k=2) == 0.0

    def test_k_zero_raises(self) -> None:
        with pytest.raises(ValueError):
            recall_at_k(["a"], {"a"}, k=0)


class TestDCGAtK:
    def test_relevant_at_rank_1_gives_max(self) -> None:
        # rel at pos 1 → 1 / log2(2) = 1
        assert dcg_at_k(["a", "x", "y"], {"a"}, k=3) == pytest.approx(1.0)

    def test_relevant_at_rank_2(self) -> None:
        # rel at pos 2 → 1 / log2(3)
        expected = 1 / math.log2(3)
        assert dcg_at_k(["x", "a", "y"], {"a"}, k=3) == pytest.approx(expected)

    def test_no_relevant_zero(self) -> None:
        assert dcg_at_k(["x", "y"], {"a"}, k=2) == 0.0


class TestIDCGAtK:
    def test_idcg_3_relevant_k_5(self) -> None:
        # 1/log2(2) + 1/log2(3) + 1/log2(4)
        expected = 1.0 + 1 / math.log2(3) + 1 / math.log2(4)
        assert idcg_at_k(3, k=5) == pytest.approx(expected)

    def test_idcg_more_relevant_than_k(self) -> None:
        # k=2 なら上位 2 件のみ
        expected = 1.0 + 1 / math.log2(3)
        assert idcg_at_k(10, k=2) == pytest.approx(expected)

    def test_zero_relevant(self) -> None:
        assert idcg_at_k(0, k=5) == 0.0


class TestNDCGAtK:
    def test_perfect_ranking_is_one(self) -> None:
        # 全 relevant が先頭に並んでいる
        assert ndcg_at_k(["a", "b", "c"], {"a", "b", "c"}, k=3) == pytest.approx(1.0)

    def test_reverse_ranking_less_than_one(self) -> None:
        # relevant が末尾に追いやられている
        score = ndcg_at_k(["x", "y", "a"], {"a"}, k=3)
        assert 0 < score < 1

    def test_no_relevant_returns_zero(self) -> None:
        assert ndcg_at_k(["a", "b"], set(), k=2) == 0.0

    def test_known_value(self) -> None:
        # relevant = {a, b}, ranked = [a, x, b]
        # DCG = 1/log2(2) + 1/log2(4) = 1 + 0.5 = 1.5
        # IDCG = 1/log2(2) + 1/log2(3) = 1 + 0.6309... ≈ 1.6309
        # NDCG = 1.5 / 1.6309 ≈ 0.9197
        score = ndcg_at_k(["a", "x", "b"], {"a", "b"}, k=3)
        assert score == pytest.approx(1.5 / (1.0 + 1 / math.log2(3)))
