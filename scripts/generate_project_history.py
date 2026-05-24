"""RecoForeJP - 開発履歴 (.docx) ジェネレータ

初期化から現在までを 16 フェーズに分けて時系列で振り返るドキュメント。
generate_dev_guide.py が「リファレンス」とすると、こちらは「ジャーニー」。

【使い方】
    python scripts/generate_project_history.py
    # → docs/開発履歴.docx
"""

from __future__ import annotations

from pathlib import Path

from docx import Document
from docx.enum.table import WD_ALIGN_VERTICAL
from docx.enum.text import WD_ALIGN_PARAGRAPH
from docx.oxml.ns import qn
from docx.shared import Cm, Pt, RGBColor

OUT_PATH = Path(__file__).resolve().parent.parent / "docs" / "開発履歴.docx"


def _set_jp_font(run, size_pt: float = 10.5) -> None:
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
    sizes = {0: 22, 1: 18, 2: 14, 3: 12}
    run.bold = True
    _set_jp_font(run, sizes.get(level, 11))


def _code_block(doc, text: str, lang_hint: str = "") -> None:
    p = doc.add_paragraph()
    p.paragraph_format.left_indent = Cm(0.5)
    p.paragraph_format.space_after = Pt(2)
    if lang_hint:
        meta = p.add_run(f"[{lang_hint}]\n")
        meta.font.name = "Consolas"
        meta.font.size = Pt(8)
        meta.font.color.rgb = RGBColor(0x88, 0x88, 0x88)
    run = p.add_run(text)
    run.font.name = "Consolas"
    run.font.size = Pt(9)
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


def _phase_box(doc, num: int, title: str, prs: str) -> None:
    """フェーズ見出し: 大きい番号 + タイトル + 関連 PR。"""
    _heading(doc, f"Phase {num:02d}  —  {title}", level=1)
    if prs:
        p = doc.add_paragraph()
        run = p.add_run(f"関連: {prs}")
        run.italic = True
        _set_jp_font(run, 9)
        run.font.color.rgb = RGBColor(0x66, 0x66, 0x66)


def _section(doc, label: str, body: str) -> None:
    """フェーズ内のサブセクション。「何を / なぜ / 学び」など。"""
    p = doc.add_paragraph()
    run = p.add_run(f"▶ {label}")
    run.bold = True
    _set_jp_font(run, 11)
    _para(doc, body)


# ---------------------------------------------------------------------------
# 本文
# ---------------------------------------------------------------------------


def build() -> None:
    doc = Document()
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
    r = sub.add_run("開発履歴 — 初期化から動く卒論システム完成まで")
    _set_jp_font(r, 14)

    sub2 = doc.add_paragraph()
    sub2.alignment = WD_ALIGN_PARAGRAPH.CENTER
    r = sub2.add_run("16 フェーズで振り返るプロジェクトジャーニー")
    r.italic = True
    _set_jp_font(r, 11)

    doc.add_page_break()

    # ----- 序文 -----
    _heading(doc, "はじめに", level=1)
    _para(
        doc,
        "このドキュメントは RecoForeJP プロジェクトの「開発の流れ」を時系列で"
        "振り返るものです。リファレンス的な「開発ガイド.docx」とは違い、"
        "「最初に何をして、次に何を解決し、なぜそうしたか」をストーリーとして"
        "読めるよう構成しています。",
    )
    _para(
        doc,
        "全 40 コミット・8 マージ済み PR・5 cherry-pick PR を 16 フェーズに整理。"
        "各フェーズは下記の構成:",
    )
    _bullet(doc, "▶ 何を: そのフェーズで作ったもの")
    _bullet(doc, "▶ なぜ: 動機・前段との関係")
    _bullet(doc, "▶ 学び: ハマったこと、設計上の判断")

    doc.add_page_break()

    # ============================================================
    # Phase 01
    # ============================================================
    _phase_box(
        doc,
        1,
        "リポジトリ初期化 + Monorepo ブートストラップ",
        "PR #1 (RECO-6)",
    )
    _section(
        doc,
        "何を",
        "GitHub リポジトリを切り、5 つのサービス（frontend, api-gateway, "
        "user-service, item-service, ai-service）+ infra + docs + scripts の "
        "ディレクトリ骨格を用意。README にアーキ図を書き、Jira 連携 "
        "（scripts/setup_jira.py で Epic と Story を一括作成）も整備。",
    )
    _section(
        doc,
        "なぜ",
        "卒論の主題が「マイクロサービス + AI 推薦」なので、最初から "
        "サービス境界を切っておくことが必要。Monorepo にしたのは "
        "「1 つの PR で複数サービスを同時に触れる」「依存追跡が楽」のため。",
    )
    _section(
        doc,
        "学び",
        "Jira を実務想定で運用するため、ストーリーを最初に 30+ 件まとめて作った。"
        "「やる順番が見える」のは個人プロジェクトでも効果大。"
        "途中で「Java サービスを追加」「NestJS は API gateway に降格」と方針転換しても "
        "Jira 側で Epic を作り替えれば追跡可能。",
    )

    # ============================================================
    # Phase 02
    # ============================================================
    _phase_box(doc, 2, "Docker Compose + 開発インフラ", "PR #2, #3 (RECO-7, RECO-8)")
    _section(
        doc,
        "何を",
        "PostgreSQL 16 + pgvector と Redis を Docker Compose で起動可能に。"
        "infra/.env.example を作り、infra/docker-compose.yml で env_file を読む構成。"
        "同時に pre-commit + EditorConfig + .gitattributes（CRLF/LF 正規化）を入れた。",
    )
    _section(
        doc,
        "なぜ",
        "推薦システムは pgvector が肝なので、最初にデータ層が立ち上がる状態を作る。"
        "5 サービスの開発が始まる前に「クローン → docker compose up」で必ず動く状態を保証したい。",
    )
    _section(
        doc,
        "学び",
        "pgvector/pgvector:pg16 image を採用 → 拡張 install 不要、起動が速い。"
        "pre-commit を最初から入れておくと、後から CI を足したくなった時の準備が済む。",
    )

    # ============================================================
    # Phase 03
    # ============================================================
    _phase_box(doc, 3, "DB スキーマ設計 + シードデータ", "PR #4, #5 (RECO-10, RECO-11)")
    _section(
        doc,
        "何を",
        "docs/schema/ に ER 図 (Mermaid) とテーブル仕様、参考 DDL を書き出した上で、"
        "infra/postgres/init/*.sql に実 DDL を分割配置。3 schema (users / items / ai)、"
        "JLPT enum 制約、physical FK なし論理分離。dev seed として "
        "users 3 / categories 12 / items 14 / tags 22 を投入。",
    )
    _section(
        doc,
        "なぜ",
        "サービス境界に応じて schema を分けることで、後で「user-service を別 DB に切り出す」"
        "ような移行が容易。physical FK なしは BFFI (Bounded Context per Schema) の考え方。",
    )
    _section(
        doc,
        "学び",
        "ER 図を Mermaid で書いたので GitHub 上でレンダリングできる（PDF 化しなくていい）。"
        "seed の bcrypt ハッシュは後で「実は password123 を表していなかった」と判明 "
        "（PR #31 で修正）。コメントは正しくても、実値は別途検証必須。",
    )

    # ============================================================
    # Phase 04
    # ============================================================
    _phase_box(doc, 4, "api-gateway scaffolding", "PR #6 (RECO-59)")
    _section(
        doc,
        "何を",
        "NestJS 11 + TypeScript で骨組みを作り、GET /health を実装。"
        "Dockerfile + docker-compose 統合。pre-commit に prettier を追加。",
    )
    _section(
        doc,
        "なぜ",
        "API Gateway を最初に立てておくと、後続の各サービスがすぐ統合できる "
        "（実装は最後に Module を追加するだけ）。",
    )
    _section(
        doc,
        "学び",
        "NestJS のモジュール構造（AppModule / HealthModule に分割）を最初から守ると、"
        "後で AuthModule, MeModule, AdminModule, AiProxyModule を足すときに迷わない。",
    )

    # ============================================================
    # Phase 05
    # ============================================================
    _phase_box(doc, 5, "user-service フル実装", "PR #7-#11 (RECO-65 to RECO-69)")
    _section(
        doc,
        "何を",
        "Spring Boot 4 / Java 21 / Gradle で 5 つの PR に分けて実装:\n"
        "  ① Scaffold + /health\n"
        "  ② User / UserProfile エンティティ + JPA Repository\n"
        "  ③ POST /users 登録（bcrypt + Bean Validation）\n"
        "  ④ /users/{id}/profile + interests（upsert セマンティクス）\n"
        "  ⑤ /users/{id}/preferences (preferred_language + notifications)",
    )
    _section(
        doc,
        "なぜ",
        "認証認可を扱う最重要サービス。bcrypt は spring-security-crypto だけを使い、"
        "Spring Security 全部入りは避けた（複雑化を嫌った）。",
    )
    _section(
        doc,
        "学び",
        "Spring Boot 4 で package 構造が変わった（org.springframework.boot.jdbc.autoconfigure.*）。"
        "テストの単体/IT 分割を最初からやった（@Tag('integration') + Gradle integrationTest task）。"
        "@ActiveProfiles('no-db') で DataSource autoconfig 除外 → Docker なしでも単体テストが走る。",
    )

    # ============================================================
    # Phase 06
    # ============================================================
    _phase_box(doc, 6, "item-service フル実装", "PR #12-#15 (RECO-72 to RECO-76)")
    _section(
        doc,
        "何を",
        "user-service と同じテンプレで:\n"
        "  ① Scaffold + /health\n"
        "  ② Category (self-ref parent) / Tag / Item / Feedback エンティティ\n"
        "  ③ Item CRUD（category/tag の参照整合検証 + JSONB metadata）\n"
        "  ④ Feedback API (view/click/favorite/rating)",
    )
    _section(
        doc,
        "なぜ",
        "推薦対象アイテムを管理する。Item には JSONB metadata、@ManyToMany Tag、"
        "@ElementCollection<String> languages を持たせて、柔軟性を確保。",
    )
    _section(
        doc,
        "学び",
        "@org.junit.jupiter.api.Tag と com.recoforejp.itemservice.catalog.Tag が "
        "名前衝突 → FQN で回避。Testcontainers BOM 導入で依存 version 一元化。"
        "あとで LazyInitializationException 問題が出てくる予兆あり（@ManyToOne LAZY）。",
    )

    # ============================================================
    # Phase 07
    # ============================================================
    _phase_box(doc, 7, "ai-service: 推薦アルゴリズムの実装", "PR #16-#21 (RECO-20 to RECO-26)")
    _section(
        doc,
        "何を",
        "Python 3.12 / FastAPI で 6 PR:\n"
        "  ① Scaffold + /health\n"
        "  ② コンテンツベース推薦 (scorer.py — JLPT / 地域 / 言語 / タグ重み)\n"
        "  ③ POST /embed (sentence-transformers multilingual-e5-small 384d)\n"
        "  ④ pgvector + ItemEmbeddingStore + POST /search/items（HNSW 近似最近傍）\n"
        "  ⑤ ハイブリッド推薦 (content × semantic 加重和)\n"
        "  ⑥ LLM 説明生成 (OpenAI optional, テンプレフォールバック)",
    )
    _section(
        doc,
        "なぜ",
        "論文 §3.3-3.4 の核となる部分。多言語埋め込みを使うことで "
        "「英語クエリで日本語アイテムが当たる」状態を作りたかった。"
        "LLM は OPENAI_API_KEY が無くてもデモが動くよう、最初からフォールバックを実装。",
    )
    _section(
        doc,
        "学び",
        "依存を [ml] (sentence-transformers + torch) と [llm] (openai) に分離 → "
        "テスト時は torch を入れずに済む（FakeEncoder + FakeStore で差し替え）。"
        "FastAPI の Annotated[Session, Depends(get_db)] パターンで Ruff B008 警告を回避。"
        "47 件の pytest が torch なしで走る — CI に乗せやすい。",
    )

    # ============================================================
    # Phase 08
    # ============================================================
    _phase_box(doc, 8, "frontend スキャフォールド + 主要画面", "PR #22-#24 (RECO-29, 32, 34)")
    _section(
        doc,
        "何を",
        "Next.js 16 + App Router + Tailwind v4 で 3 PR:\n"
        "  ① Scaffold + /api/health + output:standalone + Dockerfile\n"
        "  ② /recommendations 画面（フォーム + カード）\n"
        "  ③ /search 画面（自然言語クエリ）\n"
        "/api/recommendations と /api/search は Next.js Route Handler で "
        "ai-service にサーバ側プロキシ（CORS 回避）",
    )
    _section(
        doc,
        "なぜ",
        "ブラウザから直接動作確認できる状態を作って、ai-service の出来を可視化。"
        "サーバ側プロキシは CORS 設定不要・環境変数を browser に漏らさない利点。",
    )
    _section(
        doc,
        "学び",
        "Next 16 は breaking changes 多数（middleware.ts → proxy.ts、turbopack 等）。"
        "create-next-app が node_modules/next/dist/docs/ を読めと指示する AGENTS.md を生成。"
        "訓練データに頼らず実際のドキュメントを読む規律が必要だった。",
    )

    # ============================================================
    # Phase 09
    # ============================================================
    _phase_box(doc, 9, "シード埋め込みスクリプト", "PR #25")
    _section(
        doc,
        "何を",
        "scripts/seed_embeddings.py — item-service GET /items で全アイテム取得 → "
        "title + description + カテゴリ + タグ + 地域を結合 → ai-service POST "
        "/embeddings/items/{id} へ。stdlib のみ (urllib)。冪等。",
    )
    _section(
        doc,
        "なぜ",
        "docker compose up で起動しても ai.item_embeddings は空 → 意味検索は 0 件。"
        "「up → seed → 触る」の 3 ステップで完結する開発体験にした。",
    )
    _section(
        doc,
        "学び",
        "初回呼び出しはモデルロードで timeout → 2 回目以降は warm して全件通る。"
        "後で Admin UI からアイテム追加 → 自動 embedding 再生成（PR #33）の伏線。",
    )

    # ============================================================
    # Phase 10
    # ============================================================
    _phase_box(doc, 10, "JWT 認証 3 連 PR", "PR #26, #27, #28")
    _section(
        doc,
        "何を",
        "認証を 3 つの責務に分けて 3 PR:\n"
        "  PR-A: user-service POST /internal/auth/verify (bcrypt 照合のみ)\n"
        "  PR-B: api-gateway POST /auth/login (verify を呼んで JWT 発行)\n"
        "  PR-C: api-gateway JwtAuthGuard + GET/PUT /me/profile, /me/preferences "
        "(user-service へプロキシ)",
    )
    _section(
        doc,
        "なぜ",
        "責務分離: user-service はパスワードハッシュを知る、api-gateway は JWT を知る、"
        "両者は重複しない。/me/* は「自分の userId を知らずに使える」設計 "
        "（フロント側が JWT の sub を取り出さなくて済む）。",
    )
    _section(
        doc,
        "学び",
        "Stacked PR (#28 が #27 の branch 上) は GitHub UI で扱いやすいが、"
        "base branch が delete されると child PR が自動 close される罠あり。"
        "AuthUser interface が isolatedModules + emitDecoratorMetadata 下で "
        "import type 必須 (TS1272)。",
    )

    # ============================================================
    # Phase 11
    # ============================================================
    _phase_box(doc, 11, "i18n 基盤 + ログイン UI", "PR #29, #30")
    _section(
        doc,
        "何を",
        "PR #29: Next 16 公式の [lang] 動的セグメントパターンで i18n 基盤構築。"
        "src/i18n/dictionaries.ts (server-only)、src/proxy.ts で Accept-Language 判定、"
        "LanguageSwitcher で UI 切替。ランディング画面を ja/en 翻訳。\n\n"
        "PR #30: /[lang]/login + /[lang]/me + AuthStatus + Next Route Handler の "
        "サーバ側プロキシ (/api/auth/login, /api/auth/me)。",
    )
    _section(
        doc,
        "なぜ",
        "「在日外国人向け」を謳うのに日本語 only は致命的（論文 §4.2.2）。"
        "Next.js 16 の official guide が next-intl 等の外部ライブラリ無しで動くと教えてくれた。"
        "ログイン UI で PR #26-28 の JWT 認証が実利用可能になる。",
    )
    _section(
        doc,
        "学び",
        "react-hooks/set-state-in-effect (React 19 新規ルール) でハマる → "
        "useSyncExternalStore で localStorage 購読 hook (useAuth) に書き換え。"
        "Hydration mismatch を mounted フラグで回避していたが、こちらの方が正攻法。"
        "辞書本体は server-only マーカーでクライアント漏出を防ぐ。"
        "辞書定数 (locales) と本体を別ファイルに分けないと proxy.ts も client component も "
        "import できなくなる罠あり。",
    )

    # ============================================================
    # Phase 12
    # ============================================================
    _phase_box(doc, 12, "デモ day + 3 つのバグ修正", "PR #31")
    _section(
        doc,
        "何を",
        "全 7 PR が積み上がった状態で初めて docker compose up + seed + ブラウザ確認。"
        "そこで 3 つの本物のバグが露呈:\n"
        "  ① ai-service Dockerfile: pip install '[ml]' が src/ 不在で失敗 (COPY 順)\n"
        "  ② DB seed の bcrypt: コメントは password123 だが実値は別の文字列\n"
        "  ③ item-service GET /items: LazyInitializationException で 500",
    )
    _section(
        doc,
        "なぜ",
        "code は書けても「動くか」は別問題。stacked PR を 7 個積んでから実機検証したのは "
        "判断ミスだった。早期に compose up → 検証のサイクルを回すべきだった。",
    )
    _section(
        doc,
        "学び",
        "① は Dockerfile の COPY 順を直すだけ。② は bcrypt.hashpw で再生成し SQL に書き戻す "
        "（DB ボリュームが空のうちなら反映される）。③ は spring.jpa.open-in-view=true で暫定対応 "
        "（本来は Service で DTO 化すべき、follow-up）。"
        "教訓: 3-4 PR ごとに必ず一度 compose up で動作確認する。",
    )

    # ============================================================
    # Phase 13
    # ============================================================
    _phase_box(doc, 13, "Admin 機能 3 連 PR (RBAC)", "PR #32, #33, #34")
    _section(
        doc,
        "何を",
        "PR-A: backend RBAC: users.users に role 列 + UserRole enum + "
        "/internal/auth/verify が role を返す + api-gateway が JWT に role claim を詰める + "
        "RolesGuard + @Roles(['ADMIN']) デコレータ + /admin/ping テストエンドポイント。\n\n"
        "PR-B: api-gateway /admin/items (CRUD) → item-service プロキシ。"
        "POST/PUT 成功時に ai-service /embeddings/items/{id} を自動再生成。\n\n"
        "PR-C: frontend /[lang]/admin/items 画面（一覧 + フォーム + 削除）+ "
        "AuthStatus に「管理」リンク。",
    )
    _section(
        doc,
        "なぜ",
        "「管理機能ありますか」とユーザーに聞かれて「無い」と答えた → 補充の依頼を受けて 3 PR。"
        "新規追加アイテムが即座に意味検索に出る (sim=0.850 で top1) という体験は "
        "ハイブリッド推薦のデモとして強い。",
    )
    _section(
        doc,
        "学び",
        "PR-B で api-gateway に depends_on: ai-service: service_healthy を追加した瞬間、"
        "api-gateway が起動しなくなった。原因は ai-service の /health healthcheck が "
        "wget --spider (HEAD) で 405 → ずっと unhealthy だったこと。"
        "今まで誰も depend していなかったので無害だった隠れバグが露呈。"
        "→ Dockerfile と docker-compose の両方の healthcheck を -O /dev/null (GET) に修正。",
    )

    # ============================================================
    # Phase 14
    # ============================================================
    _phase_box(doc, 14, "全トラフィックを api-gateway 経由に正準化", "PR #35")
    _section(
        doc,
        "何を",
        "それまで唯一フロントが直接叩いていた ai-service (/api/search → ai-service、"
        "/api/recommendations → ai-service) を api-gateway 経由に切替。"
        "AiProxyModule を新設し、認証不要の公開エンドポイント (/search/items, /recommend/hybrid) "
        "として透過プロキシ。frontend の Route Handler を apiGatewayUrl() に変更。",
    )
    _section(
        doc,
        "なぜ",
        "論文 §3.5.2 のアーキ図と実装を一致させる。将来 rate-limit / メトリクス / ログ集約は "
        "gateway 一箇所に挿入できる。フロントは ai-service URL を知る必要なし。",
    )
    _section(
        doc,
        "学び",
        "薄いプロキシは退屈だが、後から「全リクエストにヘッダ X を付ける」「特定パスを cache」 "
        "「rate limit」を入れるとき、ここがあるかないかで難易度が変わる。",
    )

    # ============================================================
    # Phase 15
    # ============================================================
    _phase_box(doc, 15, "i18n 翻訳完成 (/search + /recommendations)", "PR #36")
    _section(
        doc,
        "何を",
        "PR #29 で基盤を入れたが、/search と /recommendations は日本語のままだった。"
        "ja/en 辞書に search/recommend セクションを追加し、SearchForm, SearchResultList, "
        "RecommendationForm, RecommendationList の全文言を dict prop 経由に書き換え。"
        "サンプルクエリも locale 別に翻訳（'ベトナム語で働ける CS' ↔ "
        "'customer support that uses Vietnamese'）。",
    )
    _section(
        doc,
        "なぜ",
        "ロードマップ C — これで「動く卒論システム」の i18n が完成。"
        "論文の主張「多言語ユーザーに対応」が UI として裏付けられる。",
    )
    _section(
        doc,
        "学び",
        "クライアントコンポーネントが多言語化されると、props 経由の dict 渡しが煩雑。"
        "今のサイズなら問題ないが、ページ数が増えたら React Context で配ったほうが楽。"
        "interest chips の slug→label マッピングは「japanese-learning → japaneseLearning」"
        "のような変換が必要（JSON key に - は使えない）。",
    )

    # ============================================================
    # Phase 16
    # ============================================================
    _phase_box(doc, 16, "オフライン評価実験 (§5.3)", "PR #37")
    _section(
        doc,
        "何を",
        "ai_service.eval.metrics モジュール:\n"
        "  - precision_at_k, recall_at_k, dcg/idcg/ndcg_at_k\n"
        "  - 純関数（テストしやすい）、binary relevance、log2 discount\n"
        "  - 19 件の単体テスト (境界値 + 既知値)\n\n"
        "scripts/eval_recommendations.py:\n"
        "  - 3 シードユーザー × 3 条件 (content_only / semantic_only / hybrid)\n"
        "  - K∈{5,10} grid 評価、ground truth は手動ラベル\n"
        "  - eval-results.json 出力",
    )
    _section(
        doc,
        "なぜ",
        "卒論で一番欠けていた §5。「hybrid が単独より優れている」を数値で示したい。"
        "コード側で完結する作業なので最優先で実装した。",
    )
    _section(
        doc,
        "結果",
        "3 ユーザー平均で hybrid NDCG@5=0.887 > content 0.843 > semantic 0.638。"
        "論文の主張を裏付ける結果（ただし N=3, items=14 なので pilot evaluation 位置づけ）。"
        "本評価は §5.4 被験者実験で補完する想定。",
    )

    # ============================================================
    # マイルストーン表
    # ============================================================
    _heading(doc, "全体タイムライン（マイルストーン）", level=1)
    _table(
        doc,
        [
            ["Phase", "成果物", "PR"],
            ["1", "Monorepo + Jira", "#1"],
            ["2-3", "Docker compose + DB スキーマ + シード", "#2-#5"],
            ["4", "api-gateway scaffold", "#6"],
            ["5", "user-service フル実装", "#7-#11"],
            ["6", "item-service フル実装", "#12-#15"],
            ["7", "ai-service 推薦アルゴリズム", "#16-#21"],
            ["8", "frontend 主要 2 画面", "#22-#24"],
            ["9", "seed_embeddings", "#25"],
            ["10", "JWT 認証 3 連", "#26-#28"],
            ["11", "i18n + ログイン UI", "#29-#30"],
            ["12", "デモ day + 3 バグ修正", "#31"],
            ["13", "Admin 機能 3 連 (RBAC)", "#32-#34"],
            ["14", "gateway 経由化正準化", "#35"],
            ["15", "i18n 翻訳完成", "#36"],
            ["16", "オフライン評価実験", "#37"],
        ],
    )

    # ============================================================
    # 学び（横断）
    # ============================================================
    _heading(doc, "プロジェクト全体で学んだこと", level=1)

    _heading(doc, "1. 小さい PR を積み重ねる", level=2)
    _para(
        doc,
        "1 PR = 1 責務に絞ると、レビュー / ロールバック / マージ衝突対処が劇的に楽。"
        "今回 37 PR を出したが、平均 1 PR あたり ~350 行。Stacked PR は便利だが "
        "「base branch 削除で child が close」の罠に何度かハマった → cherry-pick 救済が定番技に。",
    )

    _heading(doc, "2. デモを早く・頻繁に", level=2)
    _para(
        doc,
        "Phase 12 で 7 PR 積んでからの初回 compose up で 3 バグ。"
        "本来は 3-4 PR ごとに必ず一度動作確認すべきだった。"
        "「unit test 緑」と「実機で動く」は別物。ヘルスチェックすら HEAD/GET の違いで壊れる。",
    )

    _heading(doc, "3. 責務分離を最初から守る", level=2)
    _para(
        doc,
        "user-service はパスワードを、api-gateway は JWT を、ai-service は embedding を、"
        "それぞれ「だけ」扱う。後から AuthZ や RBAC を入れるとき、"
        "「ここに足せばよい」が一意に定まる → 拡張コストが激減。",
    )

    _heading(doc, "4. 多言語埋め込みの威力", level=2)
    _para(
        doc,
        "multilingual-e5-small (384d) は英語クエリで日本語アイテムを 0.85+ の sim で当てる。"
        "「medical care with English support」→「英語対応病院（東京・港区）」が top1 になるのは "
        "卒論の説得力として大きい。トレーニング不要、Apache 2.0、384d で軽い。",
    )

    _heading(doc, "5. ai-service の依存分離", level=2)
    _para(
        doc,
        "[ml] (torch ~800MB) を optional extras にして、テスト時は FakeEncoder + FakeStore で "
        "差し替え。47 件の pytest が CI で torch なしで走る。"
        "本番は docker build 時に '[ml]' 込みで install。",
    )

    _heading(doc, "6. Next.js 16 は別物", level=2)
    _para(
        doc,
        "middleware → proxy、ValidationPipe の挙動、React 19 の set-state-in-effect 警告、"
        "Response(\"\", {status:204}) が TypeError 等、訓練データに頼ると外す。"
        "AGENTS.md の指示通り node_modules/next/dist/docs/ を読むのが正解だった。",
    )

    _heading(doc, "7. テストと実装の分離", level=2)
    _para(
        doc,
        "user-service の @ActiveProfiles('no-db') + @MockitoBean Repository、"
        "ai-service の dependency_overrides で encoder/store を差し替え、"
        "api-gateway の jest.spyOn(global, 'fetch') 等、"
        "「重い依存」を持ち込まない仕組みを最初から仕込むと CI 速度・開発体験が劇的に改善。",
    )

    # ============================================================
    # 次フェーズ
    # ============================================================
    _heading(doc, "次フェーズ（実装フェーズ完了後）", level=1)
    _table(
        doc,
        [
            ["優先", "項目", "工数感"],
            ["1", "論文 §3-5 執筆（コード素材は揃っている）", "大"],
            ["2", "§5.4 被験者実験（10-30 名、アンケート + クリックログ）", "中"],
            ["3", "§3.3.2 協調フィルタリング（feedback テーブル使用）", "中"],
            ["4", "§4.6.2 クラウドデプロイ（任意、Render / Fly.io）", "中"],
            ["5", "§4.6.3 監視（Prometheus + Grafana）", "中"],
            ["6", "ranking 多様化 (MMR)、ranked relevance 評価", "中"],
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
