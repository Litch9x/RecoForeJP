"""推薦システムのオフライン評価モジュール（論文 §5.3）。

外部依存をテスト時には持ち込まないよう、metrics モジュールは純関数のみ。
ground truth + ランナーは scripts/eval_recommendations.py に置く。
"""
