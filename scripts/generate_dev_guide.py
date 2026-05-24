"""RecoForeJP - 開発ガイド (.docx) ジェネレータ

プロジェクトのコーディング流れ・ライブラリ・テスト・Docker・E2E を網羅した
Word ドキュメントを docs/開発ガイド.docx に書き出す。

【使い方】
    pip install python-docx
    python scripts/generate_dev_guide.py
    # → docs/開発ガイド.docx
"""

from __future__ import annotations

from pathlib import Path

from docx import Document
from docx.enum.style import WD_STYLE_TYPE
from docx.enum.table import WD_ALIGN_VERTICAL
from docx.enum.text import WD_ALIGN_PARAGRAPH
from docx.oxml.ns import qn
from docx.shared import Cm, Pt, RGBColor

OUT_PATH = Path(__file__).resolve().parent.parent / "docs" / "開発ガイド.docx"


def _set_jp_font(run, size_pt: float = 10.5) -> None:
    """日本語フォント（メイリオ）を確実に効かせる。"""
    run.font.name = "Meiryo"
    run.font.size = Pt(size_pt)
    rPr = run._element.get_or_add_rPr()
    rFonts = rPr.find(qn("w:rFonts"))
    if rFonts is None:
        from docx.oxml import OxmlElement

        rFonts = OxmlElement("w:rFonts")
        rPr.append(rFonts)
    for tag in ("eastAsia", "ascii", "hAnsi", "cs"):
        rFonts.set(qn(f"w:{tag}"), "Meiryo")


def _para(doc, text: str, size: float = 10.5, bold: bool = False) -> None:
    p = doc.add_paragraph()
    run = p.add_run(text)
    run.bold = bold
    _set_jp_font(run, size)


def _heading(doc, text: str, level: int = 1) -> None:
    p = doc.add_heading("", level=level)
    run = p.add_run(text)
    sizes = {0: 22, 1: 18, 2: 14, 3: 12, 4: 11}
    run.bold = True
    _set_jp_font(run, sizes.get(level, 11))


def _code_block(doc, text: str, lang_hint: str = "") -> None:
    """等幅フォントで枠っぽい見た目のコードブロックを描画する。"""
    p = doc.add_paragraph()
    p.paragraph_format.left_indent = Cm(0.5)
    p.paragraph_format.space_after = Pt(2)
    p.paragraph_format.space_before = Pt(2)
    if lang_hint:
        meta = p.add_run(f"[{lang_hint}]\n")
        meta.font.name = "Consolas"
        meta.font.size = Pt(8)
        meta.font.color.rgb = RGBColor(0x88, 0x88, 0x88)
    run = p.add_run(text)
    run.font.name = "Consolas"
    run.font.size = Pt(9)
    # 背景を薄いグレーに
    from docx.oxml import OxmlElement

    shd = OxmlElement("w:shd")
    shd.set(qn("w:fill"), "F4F4F4")
    p._p.get_or_add_pPr().append(shd)


def _bullet(doc, text: str) -> None:
    p = doc.add_paragraph(style="List Bullet")
    run = p.add_run(text)
    _set_jp_font(run, 10.5)


def _table(doc, rows: list[list[str]], header: bool = True) -> None:
    table = doc.add_table(rows=len(rows), cols=len(rows[0]))
    table.style = "Light Grid"
    for i, row in enumerate(rows):
        for j, cell_text in enumerate(row):
            cell = table.cell(i, j)
            cell.vertical_alignment = WD_ALIGN_VERTICAL.CENTER
            cell.text = ""
            p = cell.paragraphs[0]
            run = p.add_run(cell_text)
            _set_jp_font(run, 10)
            if header and i == 0:
                run.bold = True


def _toc_line(doc, text: str, indent: int = 0) -> None:
    p = doc.add_paragraph()
    p.paragraph_format.left_indent = Cm(0.5 * indent)
    run = p.add_run(text)
    _set_jp_font(run, 10.5)


# ---------------------------------------------------------------------------
# コンテンツ
# ---------------------------------------------------------------------------


def build() -> None:
    doc = Document()

    # ページ余白を少し詰める
    for section in doc.sections:
        section.top_margin = Cm(2)
        section.bottom_margin = Cm(2)
        section.left_margin = Cm(2)
        section.right_margin = Cm(2)

    # ----- 表紙 -----
    title = doc.add_paragraph()
    title.alignment = WD_ALIGN_PARAGRAPH.CENTER
    r = title.add_run("RecoForeJP")
    r.bold = True
    _set_jp_font(r, 28)

    sub = doc.add_paragraph()
    sub.alignment = WD_ALIGN_PARAGRAPH.CENTER
    r = sub.add_run("在日外国人向け AI パーソナライズ推薦システム")
    _set_jp_font(r, 14)

    sub2 = doc.add_paragraph()
    sub2.alignment = WD_ALIGN_PARAGRAPH.CENTER
    r = sub2.add_run("開発ガイド (Coding Flow Document)")
    r.italic = True
    _set_jp_font(r, 12)

    doc.add_paragraph()

    desc = doc.add_paragraph()
    desc.alignment = WD_ALIGN_PARAGRAPH.CENTER
    r = desc.add_run(
        "ライブラリ設定 / 開発 / テスト / Docker / E2E / 評価実験を網羅した"
        "プロジェクト全体の流れドキュメント"
    )
    _set_jp_font(r, 10)

    doc.add_page_break()

    # ----- 目次 -----
    _heading(doc, "目次", level=1)
    toc = [
        "1. プロジェクト概要",
        "2. アーキテクチャ",
        "3. リポジトリ構成",
        "4. 開発環境セットアップ",
        "5. 各サービスのライブラリと設定",
        "  5.1 frontend (Next.js 16)",
        "  5.2 api-gateway (NestJS 11)",
        "  5.3 user-service (Spring Boot 4)",
        "  5.4 item-service (Spring Boot 4)",
        "  5.5 ai-service (FastAPI + sentence-transformers)",
        "  5.6 PostgreSQL + pgvector / Redis",
        "6. 開発フロー（Jira + GitHub + Conventional Commits）",
        "7. ローカル開発（単独起動）",
        "8. Docker / docker-compose",
        "9. データシード",
        "10. テスト戦略",
        "11. E2E 動作確認",
        "12. オフライン評価実験（§5.3）",
        "13. 既知の制約と follow-up",
        "14. 論文との対応マップ",
    ]
    for line in toc:
        indent = 1 if line.startswith("  ") else 0
        _toc_line(doc, line.lstrip(), indent=indent)
    doc.add_page_break()

    # ============================================================
    # 1. プロジェクト概要
    # ============================================================
    _heading(doc, "1. プロジェクト概要", level=1)
    _para(
        doc,
        "RecoForeJP は、日本に住む外国人向けに「就職・住居・行政手続き・"
        "日本語学習・地域イベント」などの生活情報を、日本語能力・在留資格・"
        "興味・行動履歴をもとにパーソナライズして推薦するマイクロサービス型"
        "Web アプリケーションです。修士論文「在日外国人向け AI パーソナライズ"
        "推薦システム」の実装プロジェクト。",
    )
    _para(doc, "技術的な核:", bold=True)
    _bullet(doc, "コンテンツベース推薦（ユーザー属性 × アイテム属性のスコアリング）")
    _bullet(doc, "意味検索（多言語 sentence embedding + pgvector の cosine 近似最近傍）")
    _bullet(doc, "ハイブリッド推薦（content × semantic の加重和）")
    _bullet(doc, "LLM による推薦理由生成（OpenAI optional、未設定時はテンプレフォールバック）")
    _bullet(doc, "JWT + RBAC（USER / ADMIN）認証認可")

    # ============================================================
    # 2. アーキテクチャ
    # ============================================================
    _heading(doc, "2. アーキテクチャ", level=1)
    _para(
        doc,
        "5 つのマイクロサービス + 2 つのデータ層からなる構成。"
        "全 HTTP トラフィックは api-gateway を通過します（論文 §3.5.2 準拠）。",
    )

    _code_block(
        doc,
        """\
Browser
   │ HTTPS / JSON
   ▼
┌──────────────────┐
│ frontend (3001)  │  Next.js 16, App Router, i18n (ja/en)
└────────┬─────────┘
         │ 同一オリジン (/api/*)
         ▼
┌──────────────────┐
│ api-gateway      │  NestJS 11, JWT 発行/検証, RBAC
│  (3000)          │  /auth, /me, /admin, /search, /recommend
└───┬──────────┬───┘
    │          │
┌───▼──┐  ┌───▼──┐  ┌────────────┐
│ user │  │ item │  │ ai-service │  FastAPI, sentence-transformers
│ 8081 │  │ 8082 │  │   (8000)   │  embedding / similarity / LLM
└───┬──┘  └──┬───┘  └─────┬──────┘
    │        │            │
    └────┬───┴────────────┘
         ▼
   ┌──────────────┐  ┌──────────┐
   │ PostgreSQL 16│  │  Redis   │
   │ + pgvector   │  │ (キャッシュ
   │ users/items/ │  │  予定)   │
   │ ai schemas   │  └──────────┘
   └──────────────┘
""",
        lang_hint="topology",
    )

    _para(doc, "責務分離:", bold=True)
    _table(
        doc,
        [
            ["レイヤ", "言語/FW", "責務"],
            ["Presentation", "TypeScript / Next 16", "UI / i18n / 認証状態管理 / サーバプロキシ"],
            ["Gateway", "TypeScript / NestJS 11", "JWT 発行検証 / RBAC / 上流プロキシ"],
            ["Domain", "Java 21 / Spring Boot 4", "user / item の CRUD・バリデーション"],
            ["AI/ML", "Python 3.12 / FastAPI", "embedding / similarity / LLM 説明"],
            ["Data", "PostgreSQL 16 + pgvector", "3 schemas で論理分離"],
        ],
    )

    # ============================================================
    # 3. リポジトリ構成
    # ============================================================
    _heading(doc, "3. リポジトリ構成", level=1)
    _code_block(
        doc,
        """\
RecoForeJP/
├─ frontend/          Next.js 16 (TypeScript, App Router, Tailwind v4)
├─ api-gateway/       NestJS 11 (TypeScript)
├─ user-service/      Spring Boot 4 (Java 21, Gradle)
├─ item-service/      Spring Boot 4 (Java 21, Gradle)
├─ ai-service/        FastAPI (Python 3.12)
├─ infra/
│  ├─ docker-compose.yml
│  ├─ .env.example
│  └─ postgres/init/  PostgreSQL の bootstrap SQL（schema + seed）
├─ docs/              論文・スキーマ設計・本ガイド
├─ scripts/           Python 製ツール（seed_embeddings, eval, Jira 連携）
└─ README.md
""",
        lang_hint="tree",
    )

    # ============================================================
    # 4. 開発環境セットアップ
    # ============================================================
    _heading(doc, "4. 開発環境セットアップ", level=1)

    _heading(doc, "4.1 前提ソフトウェア", level=2)
    _table(
        doc,
        [
            ["ソフトウェア", "バージョン", "用途"],
            ["Git", "2.30+", "バージョン管理"],
            ["Docker Desktop", "4.41+", "フルスタックローカル起動"],
            ["Node.js", "20.17+ / 22 / 24", "frontend, api-gateway 開発"],
            ["npm", "10+", "Node パッケージ管理"],
            ["Java JDK", "21", "user/item-service 開発（Spring Boot 4）"],
            ["Python", "3.12", "ai-service 開発、scripts 実行"],
            ["pip", "25+", "Python パッケージ管理"],
            ["pre-commit", "（任意）", "コミット前自動整形"],
        ],
    )

    _heading(doc, "4.2 初回手順", level=2)
    _code_block(
        doc,
        """\
# 1. クローン
git clone https://github.com/Litch9x/RecoForeJP.git
cd RecoForeJP

# 2. 環境変数を作成
cp infra/.env.example infra/.env
# 必要なら JWT_SECRET, POSTGRES_PASSWORD などを編集

# 3. pre-commit hook を入れる（推奨）
pip install pre-commit
pre-commit install

# 4. フルスタックを起動（初回は ai-service の torch 取得で 5-10 分）
docker compose -f infra/docker-compose.yml up -d --build
docker compose -f infra/docker-compose.yml ps  # 全 healthy になるまで待つ

# 5. アイテムに埋め込みを投入（意味検索 / ハイブリッドが効くようになる）
python scripts/seed_embeddings.py

# 6. ブラウザで触る
# http://localhost:3001/    → ランディング（Accept-Language で /ja or /en）
# http://localhost:3001/ja/search           → 意味検索
# http://localhost:3001/ja/recommendations  → ハイブリッド推薦
# http://localhost:3001/ja/login            → ログイン
""",
        lang_hint="bash",
    )

    _heading(doc, "4.3 シードユーザー", level=2)
    _table(
        doc,
        [
            ["Email", "Password", "Role", "属性"],
            ["nguyen.student@example.com", "password123", "USER", "VN / N3 / 新宿区 / 留学生"],
            ["raj.engineer@example.com", "password123", "USER", "IN / N5 / 港区 / エンジニア"],
            ["wang.resident@example.com", "password123", "ADMIN", "CN / N1 / 横浜市 / 永住"],
        ],
    )
    _para(
        doc,
        "wang.resident は ADMIN ロール — ヘッダ右の「管理」リンクから "
        "/admin/items にアクセスして CRUD 可能。",
    )

    # ============================================================
    # 5. 各サービスのライブラリと設定
    # ============================================================
    _heading(doc, "5. 各サービスのライブラリと設定", level=1)

    _heading(doc, "5.1 frontend (Next.js 16)", level=2)
    _para(doc, "主要依存:", bold=True)
    _table(
        doc,
        [
            ["パッケージ", "バージョン", "用途"],
            ["next", "16.2.6", "App Router / Server Components / proxy.ts"],
            ["react / react-dom", "19+", "UI"],
            ["tailwindcss", "v4", "ユーティリティ CSS（PostCSS 不要）"],
            ["typescript", "5.7+", "型システム"],
            ["eslint + @eslint/js", "9+", "Lint (Flat Config)"],
        ],
    )
    _para(doc, "重要設定:", bold=True)
    _bullet(doc, "next.config.ts で output: 'standalone' を指定（Docker イメージを薄くする）")
    _bullet(doc, "src/proxy.ts（Next 16 で middleware.ts から rename）が locale 判定 + redirect")
    _bullet(doc, "src/i18n/config.ts に locales = ['ja', 'en']、defaultLocale = 'ja'")
    _bullet(doc, "src/i18n/dictionaries.ts に 'server-only' マーカー — クライアントに辞書を漏らさない")
    _bullet(doc, "src/lib/auth.ts で localStorage に JWT を保管（MVP）")
    _bullet(doc, "src/lib/use-auth.ts で useSyncExternalStore による localStorage 購読 hook")
    _code_block(
        doc,
        """\
cd frontend
npm install
npm run dev          # http://localhost:3000 で起動（Next 既定）
npm run build        # 本番ビルド検証
npm run lint         # ESLint
""",
        lang_hint="bash",
    )

    _heading(doc, "5.2 api-gateway (NestJS 11)", level=2)
    _para(doc, "主要依存:", bold=True)
    _table(
        doc,
        [
            ["パッケージ", "バージョン", "用途"],
            ["@nestjs/core / common", "11+", "DI コンテナ + デコレータ"],
            ["@nestjs/jwt", "10+", "JWT 発行/検証（HS256）"],
            ["@nestjs/config", "3+", "環境変数アクセス（isGlobal: true）"],
            ["class-validator / class-transformer", "0.14+", "ValidationPipe のバリデーション"],
            ["jest", "30+", "単体テスト"],
        ],
    )
    _para(doc, "モジュール構成:", bold=True)
    _bullet(doc, "AuthModule: POST /auth/login — user-service の /internal/auth/verify を呼んで JWT 発行")
    _bullet(doc, "MeModule: GET/PUT /me/profile, /me/preferences — JwtAuthGuard 必須、sub から userId 抽出")
    _bullet(doc, "AdminModule: GET/POST/PUT/DELETE /admin/items — RolesGuard + @Roles(['ADMIN'])")
    _bullet(doc, "AiProxyModule: POST /search/items, /recommend/hybrid — ai-service への薄い proxy")
    _bullet(doc, "JwtAuthGuard / RolesGuard / @CurrentUser() デコレータが src/auth/ に集約")
    _code_block(
        doc,
        """\
cd api-gateway
npm install
npm run start:dev    # ホットリロード
npm run build
npm test             # jest 39 件全 pass
""",
        lang_hint="bash",
    )

    _heading(doc, "5.3 user-service (Spring Boot 4 / Java 21)", level=2)
    _para(doc, "主要依存（build.gradle）:", bold=True)
    _bullet(doc, "org.springframework.boot:spring-boot-starter-web")
    _bullet(doc, "org.springframework.boot:spring-boot-starter-data-jpa")
    _bullet(doc, "org.springframework.boot:spring-boot-starter-actuator")
    _bullet(doc, "org.springframework.security:spring-security-crypto（bcrypt のみ、Spring Security 全部入りは使わない）")
    _bullet(doc, "org.postgresql:postgresql（JDBC ドライバ）")
    _bullet(doc, "org.projectlombok:lombok")
    _bullet(doc, "org.testcontainers:testcontainers-bom（IT 用、BOM で version 一元管理）")
    _para(doc, "重要設定:", bold=True)
    _bullet(doc, "application.properties: spring.jpa.hibernate.ddl-auto=validate（schema は infra/postgres/init で管理）")
    _bullet(doc, "spring.jpa.properties.hibernate.default_schema=users")
    _bullet(doc, "@ActiveProfiles('no-db') の単体テストは DataSource autoconfig を除外")
    _bullet(doc, "@Tag('integration') の IT は @SpringBootTest + Testcontainers")
    _code_block(
        doc,
        """\
cd user-service
./gradlew bootRun                # ポート 8081 で起動（DB は localhost:5432 を期待）
./gradlew test                   # 単体（Docker 不要、高速）
./gradlew integrationTest        # IT（Docker 必須、Testcontainers が PG 起動）
""",
        lang_hint="bash",
    )

    _heading(doc, "5.4 item-service (Spring Boot 4 / Java 21)", level=2)
    _para(doc, "user-service と同じテンプレ。所有 schema は items、ポート 8082。")
    _para(doc, "ハマりどころ:", bold=True)
    _bullet(
        doc,
        "Item エンティティの @ManyToOne Category / @ManyToMany Tag / @ElementCollection languages は LAZY デフォルト。"
        "DTO マッピングを controller 層で行うと LazyInitializationException → 暫定で "
        "spring.jpa.open-in-view=true。本来は Service 内で DTO 化すべき（follow-up）。",
    )

    _heading(doc, "5.5 ai-service (FastAPI + sentence-transformers)", level=2)
    _para(doc, "主要依存（pyproject.toml）:", bold=True)
    _bullet(doc, "fastapi + uvicorn（標準）")
    _bullet(doc, "sqlalchemy 2.x + psycopg v3 + pgvector — DB アクセス")
    _bullet(doc, "[ml] extras: sentence-transformers + torch（約 2GB、本番必須）")
    _bullet(doc, "[llm] extras: openai（任意、未設定でテンプレフォールバック）")
    _bullet(doc, "[dev] extras: pytest, ruff, httpx")
    _para(doc, "重要な実装:", bold=True)
    _bullet(doc, "encoder.py: intfloat/multilingual-e5-small（384 次元、多言語）")
    _bullet(doc, "store.py: pgvector の <=> 演算子で cosine 類似度クエリ")
    _bullet(doc, "scorer.py: コンテンツベーススコア（JLPT / 地域 / 言語 / タグ重み）")
    _bullet(doc, "hybrid.py: content_score × weight + semantic_score × weight")
    _bullet(doc, "explain.py: LLM 呼び出し（失敗時はテンプレ）")
    _bullet(doc, "eval/metrics.py: precision_at_k, recall_at_k, ndcg_at_k（論文 §5.3）")
    _code_block(
        doc,
        """\
cd ai-service
python -m venv .venv
.venv\\Scripts\\Activate.ps1            # PowerShell
pip install -e \".[ml,dev]\"             # 開発用
uvicorn ai_service.main:app --reload --port 8000
pytest                                   # 全テスト 47+19=66 件
ruff check src tests
ruff format src tests
""",
        lang_hint="powershell",
    )

    _heading(doc, "5.6 PostgreSQL + pgvector / Redis", level=2)
    _bullet(doc, "Image: pgvector/pgvector:pg16（postgres 16 + pgvector 拡張）")
    _bullet(doc, "Schemas: users / items / ai（物理 FK なしで論理分離）")
    _bullet(doc, "ai.item_embeddings: vector(384), HNSW インデックス予定")
    _bullet(doc, "infra/postgres/init/*.sql が初回起動時に順番に適用される")
    _bullet(doc, "Redis: docker-compose に含まれるが現状未使用（キャッシュ層として将来導入）")

    # ============================================================
    # 6. 開発フロー
    # ============================================================
    _heading(doc, "6. 開発フロー（Jira + GitHub + Conventional Commits）", level=1)
    _code_block(
        doc,
        """\
1. Jira で Story を選ぶ                       例: RECO-XX
2. In Progress に変更
3. feature branch を作成
   例: git checkout -b RECO-XX-short-description
4. 実装 + テスト
5. Conventional Commits でコミット
   feat(ai-service): add hybrid recommendation (RECO-XX)
   fix(api-gateway): handle 401 from user-service (RECO-XX)
   chore(repo): bump dependencies (RECO-XX)
   docs(readme): document login flow (RECO-XX)
6. git push -u origin RECO-XX-...
7. gh pr create で PR を開く
8. レビュー → squash merge → ブランチ削除
9. Jira を Done に
""",
        lang_hint="workflow",
    )
    _para(doc, "Stacked PR のハマりどころ:", bold=True)
    _para(
        doc,
        "base が削除されると child PR が GitHub で自動 close されることがある。"
        "対処: 全 base が main の時のみ親をマージする、または cherry-pick して直接 main に積む。"
        "本プロジェクトでは demo-day で全 PR を main に cherry-pick する方式に切り替えた。",
    )
    _para(doc, "pre-commit hooks:", bold=True)
    _bullet(doc, "末尾空白除去 / 改行統一 (LF) / 大ファイル検出 / マージ衝突マーカー検出")
    _bullet(doc, "Python: ruff（Lint + Format）")
    _bullet(doc, "JS/TS/JSON/YAML/Markdown: prettier")

    # ============================================================
    # 7. ローカル開発
    # ============================================================
    _heading(doc, "7. ローカル開発（単独起動）", level=1)
    _para(
        doc,
        "Docker を使わず各サービスを単独起動するパターン。データ層（PostgreSQL/Redis）だけ "
        "Docker で動かし、アプリケーションサービスはホスト側で hot-reload するのが快適。",
    )
    _code_block(
        doc,
        """\
# データ層だけ起動
docker compose -f infra/docker-compose.yml up -d postgres redis

# 別ターミナルで各サービスを hot-reload 起動
cd ai-service && uvicorn ai_service.main:app --reload --port 8000
cd user-service && ./gradlew bootRun
cd item-service && ./gradlew bootRun
cd api-gateway && npm run start:dev
cd frontend && npm run dev   # Next 既定の 3000 番ポート（要注意: api-gateway と衝突）
""",
        lang_hint="bash",
    )

    # ============================================================
    # 8. Docker / docker-compose
    # ============================================================
    _heading(doc, "8. Docker / docker-compose", level=1)
    _para(doc, "infra/docker-compose.yml は 7 サービス構成（postgres, redis, 5 app）。")
    _table(
        doc,
        [
            ["サービス", "ポート", "depends_on（healthy）"],
            ["postgres", "5432", "—"],
            ["redis", "6379", "—"],
            ["user-service", "8081", "postgres"],
            ["item-service", "8082", "postgres"],
            ["ai-service", "8000", "postgres, redis"],
            ["api-gateway", "3000", "postgres, redis, user, item, ai"],
            ["frontend", "3001", "—（runtime に独立）"],
        ],
    )
    _para(doc, "Dockerfile 設計:", bold=True)
    _bullet(doc, "frontend: 3 stage（deps / builder / runner）。output:standalone を生かす。非 root nextjs user")
    _bullet(doc, "api-gateway: nest build → node dist/main.js")
    _bullet(doc, "user/item-service: gradle bootJar → 21-jre Alpine、appuser 非 root")
    _bullet(doc, "ai-service: python:3.12-slim + pip install '[ml]'（torch 取得で重い）")
    _bullet(doc, "全 Dockerfile に HEALTHCHECK あり（wget で /health を叩く）")
    _bullet(
        doc,
        "ai-service の /health は GET のみ → wget --spider (HEAD) が 405 になる罠を修正済み。"
        "wget -O /dev/null で GET を強制する形に。",
    )

    _para(doc, "環境変数（infra/.env.example）:", bold=True)
    _table(
        doc,
        [
            ["変数", "デフォルト", "意味"],
            ["POSTGRES_USER", "reco", "PG ユーザー"],
            ["POSTGRES_PASSWORD", "reco_password", "PG パスワード"],
            ["JWT_SECRET", "dev-only-change-in-prod", "JWT 署名鍵（本番は openssl rand -hex 32）"],
            ["JWT_EXPIRES_IN_SECONDS", "3600", "JWT 有効期限"],
            ["OPENAI_API_KEY", "（未設定）", "LLM 説明用、未設定時はテンプレ"],
        ],
    )

    # ============================================================
    # 9. データシード
    # ============================================================
    _heading(doc, "9. データシード", level=1)
    _para(doc, "infra/postgres/init/*.sql が docker compose 初回起動時に適用される:")
    _bullet(doc, "01-extensions.sql — pgvector 拡張")
    _bullet(doc, "02-schemas.sql — users, items, ai schemas 作成")
    _bullet(doc, "03/04/05-*-schema.sql — 各 schema のテーブル定義")
    _bullet(doc, "10-12-seed-*.sql — 開発用シード（カテゴリ 12 / タグ 22 / ユーザー 3 / アイテム 14）")
    _para(doc, "アイテムは生のレコードだけ。意味検索のためには別途埋め込み生成が必要:")
    _code_block(
        doc,
        """\
python scripts/seed_embeddings.py
# → item-service GET /items → 各アイテムについて text 構築
#   → ai-service POST /embeddings/items/{id}
#   → ai.item_embeddings に 384 次元ベクトルを upsert（冪等）
""",
        lang_hint="bash",
    )

    _para(doc, "/admin/items から追加したアイテムは api-gateway が自動で embedding 再生成するため、seed_embeddings.py を再実行する必要はない。")

    # ============================================================
    # 10. テスト戦略
    # ============================================================
    _heading(doc, "10. テスト戦略", level=1)
    _table(
        doc,
        [
            ["サービス", "コマンド", "件数", "種別"],
            ["frontend", "（テストなし、lint + build で代用）", "—", "—"],
            ["api-gateway", "npm test", "39", "Jest 単体（fetch を mock）"],
            ["user-service", "./gradlew test", "数件", "Mockito 単体、@ActiveProfiles('no-db')"],
            ["user-service IT", "./gradlew integrationTest", "数件", "Testcontainers + RANDOM_PORT"],
            ["item-service", "./gradlew test", "数件", "Mockito 単体"],
            ["item-service IT", "./gradlew integrationTest", "数件", "Testcontainers"],
            ["ai-service", "pytest", "66", "pytest + FakeEncoder/Store で torch 不要"],
        ],
    )
    _para(doc, "ai-service のテストは torch 不要にするための Fake 注入パターンを採用:", bold=True)
    _bullet(doc, "FakeEncoder: encode(text) → 決定的なベクトル（ハッシュ由来）")
    _bullet(doc, "FakeStore: in-memory dict")
    _bullet(doc, "FastAPI app.dependency_overrides で本物と差し替え")

    # ============================================================
    # 11. E2E 動作確認
    # ============================================================
    _heading(doc, "11. E2E 動作確認", level=1)
    _para(doc, "docker compose up + seed_embeddings 完了後、以下を実行して全機能を確認:")

    _heading(doc, "11.1 ヘルスチェック", level=2)
    _code_block(
        doc,
        """\
for svc in 3000:gateway 3001:frontend 8000:ai 8081:user 8082:item; do
  port=$(echo $svc | cut -d: -f1); name=$(echo $svc | cut -d: -f2)
  path=/health; [ $name = frontend ] && path=/api/health
  code=$(curl -s -o /dev/null -w \"%{http_code}\" \"http://localhost:$port$path\")
  printf \"  %-10s %s\\n\" \"$name\" \"$code\"
done
# すべて 200 が返れば OK
""",
        lang_hint="bash",
    )

    _heading(doc, "11.2 ログインフロー (curl)", level=2)
    _code_block(
        doc,
        """\
# ADMIN ログイン
TOKEN=$(curl -s -X POST http://localhost:3000/auth/login \\
  -H 'Content-Type: application/json' \\
  -d '{\"email\":\"wang.resident@example.com\",\"password\":\"password123\"}' \\
  | python -c \"import json,sys; print(json.load(sys.stdin)['accessToken'])\")

# /me/profile (JWT 必須)
curl -s http://localhost:3000/me/profile -H \"Authorization: Bearer $TOKEN\"

# /admin/items (ADMIN 専用)
curl -s http://localhost:3000/admin/items -H \"Authorization: Bearer $TOKEN\"
""",
        lang_hint="bash",
    )

    _heading(doc, "11.3 ブラウザでの動作確認", level=2)
    _table(
        doc,
        [
            ["URL", "確認ポイント"],
            ["http://localhost:3001/", "Accept-Language で /ja or /en にリダイレクト"],
            ["/ja/search", "「ベトナム語で働ける仕事」等のサンプルで検索 → top1 が妥当"],
            ["/ja/recommendations", "JLPT/興味/クエリを入れて推薦 → reason に「same region」等"],
            ["/ja/login", "wang.resident / password123 で 401→200 切替確認"],
            ["/ja/me", "ログイン後にプロフィール表示、未ログインで「ログインしてください」"],
            ["/ja/admin/items", "ADMIN: 一覧 + フォーム + 削除。USER: forbidden 表示"],
            ["/en/*", "全て英語表示に切替（ヘッダ右の EN ボタンでも切替可）"],
        ],
    )

    # ============================================================
    # 12. オフライン評価実験
    # ============================================================
    _heading(doc, "12. オフライン評価実験（§5.3）", level=1)
    _para(
        doc,
        "scripts/eval_recommendations.py が 3 シードユーザー × 3 条件 "
        "(content_only / semantic_only / hybrid) × K∈{5,10} で grid 評価する。"
        "ground truth は手動ラベル（カテゴリ一致 + 地域 + 母語サポート）。",
    )
    _code_block(
        doc,
        """\
python scripts/eval_recommendations.py
# 標準出力: 整形テーブル
# eval-results.json: 機械可読、論文 §5 に貼り込める
""",
        lang_hint="bash",
    )
    _para(doc, "代表的な結果（3 ユーザー平均）:", bold=True)
    _table(
        doc,
        [
            ["条件", "P@5", "R@5", "NDCG@5", "P@10", "R@10", "NDCG@10"],
            ["content_only", "0.867", "0.754", "0.843", "0.533", "0.905", "0.869"],
            ["semantic_only", "0.667", "0.557", "0.638", "0.567", "0.944", "0.810"],
            ["hybrid", "0.933", "0.802", "0.887", "0.567", "0.952", "0.899"],
        ],
    )
    _para(
        doc,
        "hybrid が全 K で最良。論文の主張（属性 + 意味検索の組合せが単独より優位）を裏付ける結果。"
        "ただし N=3 ユーザー・14 アイテムなので pilot evaluation 位置づけ。本評価は §5.4 被験者実験で補完する想定。",
    )

    # ============================================================
    # 13. 既知の制約と follow-up
    # ============================================================
    _heading(doc, "13. 既知の制約と follow-up", level=1)
    _table(
        doc,
        [
            ["項目", "現状", "follow-up"],
            ["JWT 保管", "localStorage", "httpOnly Cookie への移行"],
            ["item-service OSIV", "true（暫定）", "Service 層で DTO 化し false に戻す"],
            ["embedding 削除", "オーファンを許容", "ai-service に DELETE /embeddings/items/{id}"],
            ["協調フィルタリング", "未実装", "feedback テーブルから user-user / item-item"],
            ["ランキング多様化", "未実装", "MMR の導入"],
            ["クラウドデプロイ", "未実装", "Render / Fly.io 等で公開 URL"],
            ["監視/ログ集約", "未実装", "Prometheus + Grafana + Sentry"],
            ["ai-service Dockerfile キャッシュ", "src 変更で torch 再 install", "uv lock 等で依存だけ先 install"],
            ["被験者実験", "未実施", "留学生 10-30 名でアンケート + クリックログ"],
        ],
    )

    # ============================================================
    # 14. 論文との対応マップ
    # ============================================================
    _heading(doc, "14. 論文との対応マップ", level=1)
    _table(
        doc,
        [
            ["論文章", "実装ファイル / コンポーネント", "状態"],
            ["§3.2 ユーザモデル", "users.users / user_profiles / user_interests", "✅"],
            ["§3.3.1 コンテンツベース推薦", "ai-service/src/ai_service/recommend/scorer.py", "✅"],
            ["§3.3.2 協調フィルタリング", "—", "❌ 未実装"],
            ["§3.3.3 ハイブリッド", "ai-service/src/ai_service/recommend/hybrid.py", "✅"],
            ["§3.3.4 ランキング最適化", "—（単純加重和のみ）", "🟡 簡易"],
            ["§3.4.1-2 多言語埋め込み", "ai-service/src/ai_service/embedding/encoder.py", "✅"],
            ["§3.4.3 LLM 活用", "ai-service/src/ai_service/llm/explain.py", "🟡 OpenAI 任意"],
            ["§3.4.4 意味検索", "ai-service/src/ai_service/embedding/store.py + pgvector", "✅"],
            ["§3.5 アーキテクチャ", "infra/docker-compose.yml + 5 サービス", "✅"],
            ["§4.2.2 多言語 UI", "frontend/src/i18n/* + [lang]/*", "✅"],
            ["§4.3.2 認証認可", "api-gateway/src/auth/* + RBAC", "✅"],
            ["§4.5 DB 設計", "infra/postgres/init/*.sql", "✅"],
            ["§4.6.1 Docker", "全 Dockerfile + docker-compose", "✅"],
            ["§4.6.2 クラウドデプロイ", "—", "❌"],
            ["§4.6.3 監視", "—", "❌"],
            ["§5.3 評価実験", "ai-service/src/ai_service/eval/metrics.py + scripts/eval_recommendations.py", "✅"],
            ["§5.4 被験者実験", "—", "❌"],
        ],
    )

    # ----- フッタ -----
    doc.add_paragraph()
    footer = doc.add_paragraph()
    footer.alignment = WD_ALIGN_PARAGRAPH.CENTER
    r = footer.add_run("— End of Document —")
    r.italic = True
    _set_jp_font(r, 9)

    OUT_PATH.parent.mkdir(parents=True, exist_ok=True)
    doc.save(OUT_PATH)
    print(f"✅ {OUT_PATH.relative_to(OUT_PATH.parent.parent)} を生成しました")
    print(f"   ({OUT_PATH.stat().st_size:,} bytes)")


if __name__ == "__main__":
    build()
