"""
RecoForeJP - Jira Bulk Ticket Creator

論文プロジェクトの Epic/Story を Jira に一括登録するスクリプト。
標準ライブラリのみで動作（外部パッケージ不要）。

使い方:
  事前に PowerShell で以下の環境変数を設定:
    $env:JIRA_EMAIL         = "your-email@example.com"
    $env:JIRA_API_TOKEN     = "ATATT3xFf..."
    $env:JIRA_SITE          = "shinjp.atlassian.net"
    $env:JIRA_PROJECT_KEY   = "RECO"

  実行:
    python scripts/setup_jira.py            # 確認 → y/n プロンプト → 作成
    python scripts/setup_jira.py --verify   # 接続確認のみ（作成しない）
    python scripts/setup_jira.py --yes      # 確認なしで作成
"""

import base64
import json
import os
import sys
import time
import urllib.request
import urllib.error

# --- Config from env -------------------------------------------------------
EMAIL = os.environ.get("JIRA_EMAIL", "")
TOKEN = os.environ.get("JIRA_API_TOKEN", "")
SITE = os.environ.get("JIRA_SITE", "")
PROJECT_KEY = os.environ.get("JIRA_PROJECT_KEY", "")

# --- Ticket plan -----------------------------------------------------------
# 形式: [(Epic タイトル, [Story タイトル, ...]), ...]
PLAN = [
    ("プロジェクト基盤・開発環境 [MVP]", [
        "monorepo + Git 環境構築",
        "Docker 開発環境（compose 雛形）",
        "コード品質ツール導入（Lint / Format / pre-commit）",
    ]),
    ("データベース設計 [MVP]", [
        "スキーマ設計（ER 図・テーブル定義）",
        "マイグレーション & シードデータ",
    ]),
    ("バックエンド NestJS [MVP]", [
        "NestJS プロジェクト初期化 & ヘルスチェック API",
        "ユーザー認証（JWT サインアップ / ログイン）",
        "ユーザープロフィール API",
        "アイテム CRUD API",
        "フィードバック記録 API",
        "推薦結果取得 API（AI サービス仲介）",
    ]),
    ("AI 推薦サービス FastAPI [MVP の核]", [
        "FastAPI 雛形 + ヘルスチェック",
        "コンテンツベース推薦（属性マッチ）",
        "テキスト埋め込み生成（sentence-transformers）",
        "pgvector 連携・類似度検索",
        "類似ユーザ分析（協調フィルタリング）",
        "ハイブリッド推薦モデル統合",
        "LLM 連携（意図抽出・説明文生成）",
        "意味検索エンドポイント",
    ]),
    ("フロントエンド Next.js [MVP]", [
        "Next.js プロジェクト初期化",
        "認証 UI（サインアップ・ログイン）",
        "プロフィール設定画面（日本語レベル・興味・在留資格）",
        "推薦一覧画面（カード型）",
        "アイテム詳細画面",
        "自然言語検索フォーム",
        "フィードバック UI（お気に入り・評価）",
    ]),
    ("多言語対応 [後期]", [
        "i18n セットアップ（next-i18next）",
        "日本語・英語・ベトナム語リソース作成",
        "多言語埋め込みモデル導入（mBERT / XLM-R）",
        "やさしい日本語変換機能（LLM 活用）",
    ]),
    ("CI/CD [後期]", [
        "GitHub Actions: Lint & テスト自動化",
        "GitHub Actions: Docker イメージビルド",
        "PR テンプレート & ブランチ保護",
    ]),
    ("デプロイ・運用 [後期]", [
        "クラウド選定（Fly.io / Render / AWS 等）",
        "本番環境構築",
        "監視（Sentry / ログ収集）",
    ]),
    ("評価実験 [論文 第5章]", [
        "評価指標の定義（Precision / Recall / NDCG）",
        "テストデータ準備",
        "推薦精度評価実験",
        "ユーザー満足度アンケート設計・実施",
        "実験結果集計・グラフ化",
    ]),
    ("論文執筆 [継続]", [
        "第3章 提案手法 詳細化",
        "第4章 システム実装 詳細化",
        "第5章 評価実験 執筆",
        "第6章 結論・今後の課題 執筆",
        "発表スライド作成",
        "最終提出版チェック",
    ]),
]

# --- Helpers ---------------------------------------------------------------
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

# --- Main ------------------------------------------------------------------
def main():
    args = sys.argv[1:]
    verify_only = "--verify" in args
    skip_confirm = "--yes" in args

    # 1. Env check
    missing = [n for n, v in [
        ("JIRA_EMAIL", EMAIL), ("JIRA_API_TOKEN", TOKEN),
        ("JIRA_SITE", SITE), ("JIRA_PROJECT_KEY", PROJECT_KEY),
    ] if not v]
    if missing:
        die(f"環境変数が未設定: {', '.join(missing)}")
    print(f"✅ env vars OK (project={PROJECT_KEY}, site={SITE})")

    # 2. Connection check
    try:
        proj = api("GET", f"/rest/api/3/project/{PROJECT_KEY}")
    except Exception as e:
        die(f"Jira 接続失敗: {e}")
    style = proj.get("style", "?")
    print(f"✅ 接続成功: project='{proj['name']}' (style={style})")

    # 3. Issue type check
    types = {t["name"] for t in proj.get("issueTypes", [])}
    print(f"   利用可能な issue type: {sorted(types)}")
    for need in ["Epic", "Story"]:
        if need not in types:
            die(f"issue type '{need}' が見つかりません。Jira 画面で追加してください。")

    # 4. Summary
    n_epics = len(PLAN)
    n_stories = sum(len(s) for _, s in PLAN)
    print(f"\n📋 作成予定: Epic {n_epics} 件, Story {n_stories} 件 (合計 {n_epics + n_stories})")

    if verify_only:
        print("\n--verify モードのため作成しません。")
        return

    # 5. Confirm
    if not skip_confirm:
        ans = input("\n作成を実行しますか? [y/N]: ").strip().lower()
        if ans != "y":
            print("中止しました。")
            return

    # 6. Create
    print("\n🚀 作成開始...")
    created = []
    for epic_title, stories in PLAN:
        try:
            epic_key = create_issue("Epic", epic_title)
        except Exception as e:
            print(f"  ❌ Epic 失敗 '{epic_title}': {e}")
            continue
        print(f"  📦 {epic_key}  {epic_title}")
        created.append(epic_key)
        time.sleep(0.3)

        for story_title in stories:
            try:
                story_key = create_issue("Story", story_title, parent_key=epic_key)
            except Exception as e:
                print(f"    ❌ Story 失敗 '{story_title}': {e}")
                continue
            print(f"    📝 {story_key}  {story_title}")
            created.append(story_key)
            time.sleep(0.3)

    print(f"\n✅ 完了: {len(created)} 件作成")

if __name__ == "__main__":
    main()
