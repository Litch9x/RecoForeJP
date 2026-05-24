"""コンテンツベース推薦モジュール（論文 3.3.1）.

ユーザー属性（日本語レベル・在留地域・興味・希望言語）と
アイテム属性（カテゴリ・地域・対応言語・タグ・必要日本語レベル）の
**属性マッチング** で簡易スコアを算出する。

Sub-modules:
- :mod:`.scorer` -- 純粋関数 ``score_item``（DB 非依存、ユニットテスト対象）
- :mod:`.repository` -- 候補アイテムを items schema から取得（読み取り専用）
- :mod:`.dto` -- API リクエスト/レスポンスの Pydantic モデル
- :mod:`.service` -- repository + scorer を組み合わせるオーケストレーション
- :mod:`.router` -- FastAPI ルーター（POST /recommend）
"""
