"""
RecoForeJP - Jira アーキテクチャ変更スクリプト

旧構成: EPIC「バックエンド NestJS [MVP]」+ その下の Story 群を削除
新構成: 以下 3 つの EPIC + Story 群を追加
  - API Gateway (NestJS) [MVP]
  - User Service (Java/Spring Boot) [MVP]
  - Item Service (Java/Spring Boot) [MVP]

使い方:
  python scripts/update_jira_architecture.py            # ドライラン（削除/作成内容を表示するだけ）
  python scripts/update_jira_architecture.py --execute  # 実行（y/N 確認あり）
"""

import base64
import json
import os
import sys
import time
import urllib.parse
import urllib.request
import urllib.error

EMAIL = os.environ.get("JIRA_EMAIL", "")
TOKEN = os.environ.get("JIRA_API_TOKEN", "")
SITE = os.environ.get("JIRA_SITE", "")
PROJECT_KEY = os.environ.get("JIRA_PROJECT_KEY", "")

OLD_EPIC_SUMMARY = "バックエンド NestJS [MVP]"

NEW_EPICS = [
    ("API Gateway (NestJS) [MVP]", [
        "NestJS API Gateway 雛形 + ヘルスチェック",
        "JWT 認証ミドルウェア（サインアップ・ログイン）",
        "ルーティング設定（user-service / item-service / ai-service へのプロキシ）",
        "レート制限・CORS 設定",
        "リクエストロギング・エラーハンドリング",
    ]),
    ("User Service (Java/Spring Boot) [MVP]", [
        "Spring Boot プロジェクト初期化（Gradle + Java 21）",
        "User エンティティ & PostgreSQL 連携（Spring Data JPA）",
        "ユーザー登録 API",
        "ユーザープロフィール API（日本語レベル・在留資格・興味分野）",
        "ユーザー設定 API（言語・通知など）",
        "REST API テスト（JUnit 5 + Testcontainers）",
    ]),
    ("Item Service (Java/Spring Boot) [MVP]", [
        "Spring Boot プロジェクト初期化（Gradle + Java 21）",
        "Item エンティティ & PostgreSQL 連携",
        "アイテム CRUD API",
        "カテゴリ & タグ管理 API",
        "フィードバック記録 API（user_actions テーブル連携）",
        "REST API テスト（JUnit 5 + Testcontainers）",
    ]),
]


def die(msg, code=1):
    print(f"❌ {msg}")
    sys.exit(code)


def auth_header():
    raw = f"{EMAIL}:{TOKEN}".encode()
    return "Basic " + base64.b64encode(raw).decode()


def api(method, path, body=None):
    url = f"https://{SITE}{path}"
    data = json.dumps(body).encode() if body else None
    req = urllib.request.Request(url, data=data, method=method)
    req.add_header("Authorization", auth_header())
    req.add_header("Accept", "application/json")
    req.add_header("Content-Type", "application/json")
    try:
        with urllib.request.urlopen(req) as resp:
            text = resp.read().decode()
            return json.loads(text) if text else {}
    except urllib.error.HTTPError as e:
        err = e.read().decode()
        raise RuntimeError(f"HTTP {e.code} on {method} {path}: {err}")


def search_all_epics():
    jql = f'project = {PROJECT_KEY} AND issuetype = Epic'
    qs = urllib.parse.urlencode({"jql": jql, "maxResults": 100, "fields": "summary"})
    return api("GET", f"/rest/api/3/search?{qs}").get("issues", [])


def find_children(parent_key):
    jql = f'project = {PROJECT_KEY} AND parent = {parent_key}'
    qs = urllib.parse.urlencode({"jql": jql, "maxResults": 100, "fields": "summary,issuetype"})
    return api("GET", f"/rest/api/3/search?{qs}").get("issues", [])


def delete_issue(key):
    api("DELETE", f"/rest/api/3/issue/{key}?deleteSubtasks=true")


def create_issue(issue_type, summary, parent_key=None):
    fields = {
        "project": {"key": PROJECT_KEY},
        "summary": summary,
        "issuetype": {"name": issue_type},
    }
    if parent_key:
        fields["parent"] = {"key": parent_key}
    res = api("POST", "/rest/api/3/issue", {"fields": fields})
    return res["key"]


def main():
    args = sys.argv[1:]
    execute = "--execute" in args

    # 1. Env check
    missing = [n for n, v in [
        ("JIRA_EMAIL", EMAIL), ("JIRA_API_TOKEN", TOKEN),
        ("JIRA_SITE", SITE), ("JIRA_PROJECT_KEY", PROJECT_KEY),
    ] if not v]
    if missing:
        die(f"環境変数が未設定: {', '.join(missing)}")
    print(f"✅ env vars OK (project={PROJECT_KEY})")

    # 2. Find old Epic by exact summary match
    print(f"\n🔍 旧 Epic を検索: '{OLD_EPIC_SUMMARY}'")
    epics = search_all_epics()
    matches = [e for e in epics if e["fields"]["summary"].strip() == OLD_EPIC_SUMMARY]
    if not matches:
        die(f"旧 Epic '{OLD_EPIC_SUMMARY}' が見つかりません。すでに削除済みの可能性があります。")
    if len(matches) > 1:
        die(f"同名 Epic が複数あります。手動で確認してください: {[m['key'] for m in matches]}")
    old_epic = matches[0]
    old_epic_key = old_epic["key"]
    print(f"  → 見つかりました: {old_epic_key}")

    # 3. List children
    children = find_children(old_epic_key)
    print(f"\n📋 削除対象:")
    print(f"  Epic  {old_epic_key}  {OLD_EPIC_SUMMARY}")
    for c in children:
        print(f"  └─ {c['fields']['issuetype']['name']:6s} {c['key']}  {c['fields']['summary']}")

    # 4. Show new structure
    print(f"\n📋 新規作成:")
    for epic_name, stories in NEW_EPICS:
        print(f"  Epic   {epic_name}")
        for s in stories:
            print(f"  └─ Story {s}")

    n_delete = 1 + len(children)
    n_create = len(NEW_EPICS) + sum(len(s) for _, s in NEW_EPICS)
    print(f"\n合計: 削除 {n_delete} 件 / 作成 {n_create} 件")

    if not execute:
        print("\n⚠️  ドライランモードです。実際に変更するには --execute を付けて再実行してください:")
        print("    python scripts/update_jira_architecture.py --execute")
        return

    # 5. Confirm
    print()
    ans = input(f"本当に実行しますか? 削除は取り消せません [y/N]: ").strip().lower()
    if ans != "y":
        print("中止しました。")
        return

    # 6. Delete children first, then Epic
    print("\n🗑️  削除中...")
    for c in children:
        try:
            delete_issue(c["key"])
            print(f"  ✅ {c['key']}")
        except Exception as e:
            print(f"  ❌ {c['key']}: {e}")
        time.sleep(0.3)
    try:
        delete_issue(old_epic_key)
        print(f"  ✅ {old_epic_key} (Epic)")
    except Exception as e:
        print(f"  ❌ {old_epic_key}: {e}")
    time.sleep(0.3)

    # 7. Create new Epics + Stories
    print("\n🚀 新規作成中...")
    for epic_name, stories in NEW_EPICS:
        try:
            epic_key = create_issue("Epic", epic_name)
        except Exception as e:
            print(f"  ❌ Epic '{epic_name}': {e}")
            continue
        print(f"  📦 {epic_key}  {epic_name}")
        time.sleep(0.3)
        for s in stories:
            try:
                sk = create_issue("Story", s, parent_key=epic_key)
                print(f"    📝 {sk}  {s}")
            except Exception as e:
                print(f"    ❌ Story '{s}': {e}")
            time.sleep(0.3)

    print("\n✅ 完了")


if __name__ == "__main__":
    main()
