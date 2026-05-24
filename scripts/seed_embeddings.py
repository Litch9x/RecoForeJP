"""RecoForeJP - シード埋め込み一括登録スクリプト

item-service からアイテム一覧を取得し、各アイテムの title + description + categoryNameJa + tags
を結合したテキストを ai-service の POST /embeddings/items/{id} に送信する。
埋め込みが ai.item_embeddings に登録され、/search/items や /recommend/hybrid の
semantic 経路が機能するようになる。

【冪等性】 ai-service の upsert は ON CONFLICT (item_id) DO UPDATE なので、
        何度実行しても安全。

【使い方】
    # フルフロー：docker compose up → seed → 検索
    docker compose -f infra/docker-compose.yml up -d --build
    python scripts/seed_embeddings.py
    # → http://localhost:3001/search で意味検索が動く

【環境変数】
    ITEM_SERVICE_URL  (default: http://localhost:8082)
    AI_SERVICE_URL    (default: http://localhost:8000)
"""

import json
import os
import sys
import time
import urllib.error
import urllib.request

ITEM_SERVICE_URL = os.environ.get("ITEM_SERVICE_URL", "http://localhost:8082")
AI_SERVICE_URL = os.environ.get("AI_SERVICE_URL", "http://localhost:8000")


def die(msg: str, code: int = 1) -> None:
    print(f"❌ {msg}", file=sys.stderr)
    sys.exit(code)


def http_get(url: str, timeout: float = 10.0) -> dict | list:
    """GET → JSON. 失敗時は例外を投げる."""
    with urllib.request.urlopen(url, timeout=timeout) as resp:
        return json.loads(resp.read().decode())


def http_post_json(url: str, body: dict, timeout: float = 60.0) -> dict:
    """POST application/json → JSON."""
    data = json.dumps(body).encode()
    req = urllib.request.Request(
        url, data=data, headers={"Content-Type": "application/json"}, method="POST"
    )
    with urllib.request.urlopen(req, timeout=timeout) as resp:
        return json.loads(resp.read().decode())


def check_health(base_url: str, service_label: str) -> None:
    try:
        body = http_get(f"{base_url}/health", timeout=5.0)
    except urllib.error.URLError as e:
        die(f"{service_label} に到達できません ({base_url}): {e.reason}")
    except Exception as e:  # noqa: BLE001 - 起動失敗を表示するため広く拾う
        die(f"{service_label} のヘルスチェック失敗 ({base_url}): {e}")
    if isinstance(body, dict) and body.get("status") == "ok":
        print(f"  ✅ {service_label} OK ({base_url})")
    else:
        die(f"{service_label} の health 応答が異常: {body!r}")


def fetch_items() -> list[dict]:
    try:
        items = http_get(f"{ITEM_SERVICE_URL}/items", timeout=15.0)
    except Exception as e:  # noqa: BLE001
        die(f"item-service からアイテム取得失敗: {e}")
    if not isinstance(items, list):
        die(f"item-service /items の応答が list でない: {type(items).__name__}")
    return items  # type: ignore[return-value]


def build_text(item: dict) -> str:
    """埋め込み生成元テキストを構築。

    タイトル + 説明 + カテゴリ + タグ を結合して、検索クエリと意味的にマッチしやすくする。
    """
    parts: list[str] = []
    if title := item.get("title"):
        parts.append(str(title))
    if desc := item.get("description"):
        parts.append(str(desc))
    if cat := item.get("categoryNameJa") or item.get("categorySlug"):
        parts.append(f"カテゴリ: {cat}")
    if tags := item.get("tags"):
        if isinstance(tags, list) and tags:
            parts.append("タグ: " + ", ".join(str(t) for t in tags))
    if region := item.get("region"):
        parts.append(f"地域: {region}")
    return " / ".join(parts)


def main() -> None:
    print("📋 サービス疎通確認")
    check_health(ITEM_SERVICE_URL, "item-service")
    check_health(AI_SERVICE_URL, "ai-service")

    print("\n📋 アイテム取得")
    items = fetch_items()
    print(f"  → {len(items)} 件")
    if not items:
        print(
            "⚠️  アイテムが 0 件です。シードデータが投入されているか確認してください。"
        )
        return

    print(
        "\n🧠 埋め込み生成 + ai.item_embeddings へ upsert（初回はモデルロードで時間がかかります）"
    )
    success = 0
    failed = 0
    for i, item in enumerate(items, 1):
        item_id = item.get("id")
        if not item_id:
            print(f"  [{i}/{len(items)}] ⚠️  id 欠落でスキップ: {item}")
            failed += 1
            continue
        text = build_text(item)
        try:
            res = http_post_json(
                f"{AI_SERVICE_URL}/embeddings/items/{item_id}", {"text": text}
            )
        except urllib.error.HTTPError as e:
            print(f"  [{i}/{len(items)}] ❌ {item_id}: HTTP {e.code} {e.reason}")
            failed += 1
            continue
        except Exception as e:  # noqa: BLE001
            print(f"  [{i}/{len(items)}] ❌ {item_id}: {e}")
            failed += 1
            continue
        title = (item.get("title") or "")[:40]
        dim = res.get("dimension", "?")
        print(f"  [{i}/{len(items)}] ✅ {item_id}  dim={dim}  {title}")
        success += 1
        # 初回の連続呼び出しでモデルが温まるまで待つ（過負荷防止）
        time.sleep(0.05)

    print(f"\n✅ 完了: {success} 件成功 / {failed} 件失敗")
    if failed:
        sys.exit(2)


if __name__ == "__main__":
    main()
