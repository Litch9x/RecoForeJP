"""sentence-transformers でテキストをベクトル化するエンコーダ.

デフォルトモデル: ``intfloat/multilingual-e5-small``
- 384 次元
- 多言語（日本語含む）対応
- 軽量（モデルサイズ約 110MB）

E5 系モデルは入力に ``passage: `` / ``query: `` のプレフィックスを付けると性能が出る。
- ``passage``: 検索対象のドキュメント側（アイテム説明文など）
- ``query``: 検索クエリ側（ユーザーの自然言語入力）
"""

from __future__ import annotations

from typing import TYPE_CHECKING, Literal

if TYPE_CHECKING:
    from sentence_transformers import SentenceTransformer


EncodeMode = Literal["passage", "query"]


class TextEncoder:
    """sentence-transformers の薄いラッパ。モデルは初回 :meth:`encode` 呼び出しで遅延ロード。"""

    DEFAULT_MODEL = "intfloat/multilingual-e5-small"
    DIMENSION = 384

    def __init__(self, model_name: str = DEFAULT_MODEL) -> None:
        self.model_name = model_name
        self._model: SentenceTransformer | None = None

    @property
    def dimension(self) -> int:
        return self.DIMENSION

    def _ensure_loaded(self) -> SentenceTransformer:
        if self._model is None:
            # 重量級 import を関数内に閉じ込めることで、テスト時にこの分岐に入らなければ起動が速い
            from sentence_transformers import SentenceTransformer

            self._model = SentenceTransformer(self.model_name)
        return self._model

    def encode(self, texts: list[str], *, mode: EncodeMode = "passage") -> list[list[float]]:
        """テキスト列を 384 次元ベクトル列に変換する（正規化済み）.

        Args:
            texts: 入力テキスト（空文字は呼び出し側で除外すること）。
            mode: ``passage`` (検索対象) または ``query`` (クエリ)。
        """
        model = self._ensure_loaded()
        prefixed = [f"{mode}: {t}" for t in texts]
        vectors = model.encode(prefixed, normalize_embeddings=True)
        return vectors.tolist()


# モジュールレベル singleton。FastAPI Depends 用。
_encoder: TextEncoder | None = None


def get_encoder() -> TextEncoder:
    """共有エンコーダを返す。テストでは ``app.dependency_overrides`` で差し替え可能。"""
    global _encoder
    if _encoder is None:
        _encoder = TextEncoder()
    return _encoder
