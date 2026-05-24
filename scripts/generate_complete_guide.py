"""RecoForeJP - 完全ガイド (.docx) ジェネレータ

プログラミング未経験者向けに、プロジェクトの初期建築から現在の状態まで、
何を準備し、何を動かし、どう拡張するかを一つの文書に集約。

【使い方】
    python scripts/generate_complete_guide.py
    # → docs/完全ガイド.docx
"""

from __future__ import annotations

from pathlib import Path

from docx import Document
from docx.enum.table import WD_ALIGN_VERTICAL
from docx.enum.text import WD_ALIGN_PARAGRAPH
from docx.oxml.ns import qn
from docx.shared import Cm, Pt, RGBColor

OUT_PATH = Path(__file__).resolve().parent.parent / "docs" / "完全ガイド.docx"


# ---------------------------------------------------------------------------
# 共通レイアウト関数（dev_guide / project_history と同じ）
# ---------------------------------------------------------------------------


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
    sizes = {0: 22, 1: 18, 2: 14, 3: 12, 4: 11}
    run.bold = True
    _set_jp_font(run, sizes.get(level, 11))


def _code(doc, text: str, lang_hint: str = "") -> None:
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


def _numbered(doc, text: str) -> None:
    p = doc.add_paragraph(style="List Number")
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


def _callout(doc, label: str, body: str, color: str = "FFF8E1") -> None:
    """目立つ注意書きボックス。"""
    p = doc.add_paragraph()
    p.paragraph_format.left_indent = Cm(0.5)
    p.paragraph_format.space_after = Pt(4)
    p.paragraph_format.space_before = Pt(4)
    run = p.add_run(f"💡 {label}\n")
    run.bold = True
    _set_jp_font(run, 10)
    run2 = p.add_run(body)
    _set_jp_font(run2, 10)
    from docx.oxml import OxmlElement

    shd = OxmlElement("w:shd")
    shd.set(qn("w:fill"), color)
    p._p.get_or_add_pPr().append(shd)


def _section_break(doc) -> None:
    """章間に薄い区切り。"""
    p = doc.add_paragraph()
    p.alignment = WD_ALIGN_PARAGRAPH.CENTER
    run = p.add_run("— — —")
    run.font.color.rgb = RGBColor(0xCC, 0xCC, 0xCC)
    _set_jp_font(run, 10)


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

    # ============================================================
    # 表紙
    # ============================================================
    title = doc.add_paragraph()
    title.alignment = WD_ALIGN_PARAGRAPH.CENTER
    r = title.add_run("はじめての RecoForeJP")
    r.bold = True
    _set_jp_font(r, 28)

    sub = doc.add_paragraph()
    sub.alignment = WD_ALIGN_PARAGRAPH.CENTER
    r = sub.add_run("プログラミング未経験でも進められる完全ガイド")
    _set_jp_font(r, 14)

    doc.add_paragraph()

    desc = doc.add_paragraph()
    desc.alignment = WD_ALIGN_PARAGRAPH.CENTER
    r = desc.add_run(
        "「コードのことは何もわからないけれど、このプロジェクトを動かして、\n"
        "中身を理解して、自分で次の一歩を進めたい」\nそんな人のための一冊。"
    )
    _set_jp_font(r, 11)

    doc.add_page_break()

    # ============================================================
    # このガイドについて
    # ============================================================
    _heading(doc, "このガイドについて", level=1)
    _para(
        doc,
        "このガイドは、RecoForeJP（在日外国人向け AI 推薦システム）という"
        "プロジェクトを、コードを書いたことがない人でも：",
    )
    _bullet(doc, "何のためのソフトウェアなのかを理解する")
    _bullet(doc, "自分のパソコンで起動して触ってみる")
    _bullet(doc, "中身の仕組みを少しずつ覗いてみる")
    _bullet(doc, "自分で新しいデータを足したり、設定を変えたりする")
    _bullet(doc, "問題が起きたとき、何が起きているか追跡する")
    _bullet(doc, "次にやるべき作業を見つける")
    _para(doc, "そんなことができるよう、丁寧に順を追って案内します。")

    _para(doc, "")
    _para(doc, "読み方のヒント:", bold=True)
    _bullet(doc, "頭から順に読む必要はありません。「やりたいこと」の章だけ読んで OK")
    _bullet(doc, "💡 マークの付いた囲みは、よくある質問・つまずきポイント")
    _bullet(doc, "灰色の枠は「ターミナル」に打ち込むコマンドです（次章で説明）")
    _bullet(doc, "巻末に「用語集」あり。知らない言葉が出てきたら確認")

    doc.add_page_break()

    # ============================================================
    # 目次
    # ============================================================
    _heading(doc, "目次", level=1)
    toc = [
        ("第 1 部", "プロジェクトを理解する"),
        ("  1.", "このプロジェクトは何？"),
        ("  2.", "全体の仕組み（一枚絵で見る）"),
        ("  3.", "使われている技術の超ざっくり説明"),
        ("第 2 部", "準備する"),
        ("  4.", "必要なソフトウェアをインストール"),
        ("  5.", "プロジェクトを自分のパソコンに持ってくる"),
        ("  6.", "ターミナル（黒い画面）の使い方"),
        ("第 3 部", "動かしてみる"),
        ("  7.", "5 分で全機能を起動する"),
        ("  8.", "ブラウザで触ってみる"),
        ("  9.", "中で動いているデータを覗く"),
        ("第 4 部", "プロジェクトを進める"),
        ("  10.", "新しいアイテム（求人や住居）を追加する"),
        ("  11.", "推薦精度を評価する"),
        ("  12.", "コードを少し変えてみる"),
        ("  13.", "新しい機能を追加するときの流れ"),
        ("第 5 部", "困ったときに"),
        ("  14.", "よくあるエラーと対処"),
        ("  15.", "ログ（記録）を読む"),
        ("  16.", "完全リセットの仕方"),
        ("第 6 部", "卒論につなげる"),
        ("  17.", "論文の各章で何を書けるか"),
        ("  18.", "次にやるべき作業の優先順位"),
        ("付録", ""),
        ("  A.", "用語集"),
        ("  B.", "コマンド一覧（チートシート）"),
        ("  C.", "ファイル構成早見表"),
    ]
    for marker, text in toc:
        p = doc.add_paragraph()
        run = p.add_run(f"{marker}  {text}")
        if not marker.startswith(" "):
            run.bold = True
        _set_jp_font(run, 10.5)
    doc.add_page_break()

    # ============================================================
    # 第 1 部
    # ============================================================
    _heading(doc, "第 1 部  プロジェクトを理解する", level=0)

    _heading(doc, "1. このプロジェクトは何？", level=1)
    _para(
        doc,
        "RecoForeJP は、日本に住む外国人のための「生活情報レコメンドサービス」です。"
        "Netflix がユーザーに合った映画を勧めるように、このシステムは"
        "ユーザーひとりひとりに合った求人・住居・行政手続き・日本語学習講座・"
        "地域イベントを勧めます。",
    )
    _para(doc, "なぜこれが必要？", bold=True)
    _para(
        doc,
        "在日外国人は、就職活動・住宅探し・行政手続きで多くの壁にぶつかります。"
        "日本語が苦手だったり、自分の国の文化と違ったり、信頼できる情報源を知らなかったり。"
        "Google で検索しても日本人向けの情報ばかり。"
        "「日本語 N3 のベトナム人留学生」と「中国出身の永住者」では"
        "求める情報がまったく違うのに、既存サービスはそこまで考えてくれません。",
    )
    _para(doc, "このシステムが解決すること:", bold=True)
    _bullet(doc, "日本語レベル（JLPT N1〜N5）に合った難易度の情報")
    _bullet(doc, "国籍・母語に応じた多言語対応の情報")
    _bullet(doc, "地域（東京 / 横浜など）に絞った情報")
    _bullet(doc, "興味分野（仕事 / 住居 / 医療など）に絞った情報")
    _bullet(doc, "「英語が使える IT エンジニア募集」のような自然な言葉での検索")

    _callout(
        doc,
        "ポジション",
        "これは卒業研究プロジェクトです。商用サービスではありません。"
        "アイテムは 14 件のテストデータのみ。実運用するには数千件のデータと、"
        "信頼できる情報源の契約が別途必要です。",
    )

    _section_break(doc)

    _heading(doc, "2. 全体の仕組み（一枚絵で見る）", level=1)
    _para(
        doc,
        "システムは「役割の違う 5 つの小さなプログラム」と「2 つのデータ保管庫」"
        "から構成されています。レストランで例えると:",
    )
    _table(
        doc,
        [
            ["プログラム", "レストランの例え", "実際の役割"],
            ["frontend", "客席のメニュー / 注文用紙", "ブラウザに表示される画面"],
            ["api-gateway", "受付・案内係", "認証チェック・各厨房への振り分け"],
            ["user-service", "会員カード管理係", "ユーザー情報・プロフィール"],
            ["item-service", "メニュー管理係", "求人・住居等のデータ管理"],
            ["ai-service", "ソムリエ（おすすめ係）", "AI による推薦・意味検索"],
            ["PostgreSQL", "在庫倉庫", "データを保管する場所"],
            ["Redis", "今日のおすすめ黒板", "速いキャッシュ（現状未使用）"],
        ],
    )
    _para(doc, "リクエストの流れ:", bold=True)
    _code(
        doc,
        """\
   あなた (ブラウザ)
      │
      ▼
   frontend  (画面を表示する人)
      │
      ▼
   api-gateway  (受付・あなたが誰か確認)
      │
      ├──→ user-service  (プロフィール取得)
      ├──→ item-service  (アイテムリスト取得)
      └──→ ai-service    (おすすめ計算)
              │
              ▼
        PostgreSQL  (データの倉庫)
""",
    )
    _para(
        doc,
        "ポイント: あなた（ユーザー）はいつも frontend（画面）と話します。"
        "frontend は内部で api-gateway に聞き、api-gateway が裏で各サービスに分配します。"
        "あなたから見ると 1 つのサービスのように見えます。",
    )

    _section_break(doc)

    _heading(doc, "3. 使われている技術の超ざっくり説明", level=1)
    _para(doc, "各サービスは違う「プログラミング言語」と「道具一式（フレームワーク）」で書かれています。"
              "言語を分けたのは、それぞれが得意な分野が違うから。")
    _table(
        doc,
        [
            ["サービス", "言語", "なぜこの言語？"],
            ["frontend", "TypeScript (Next.js)", "Web 画面作りで一番人気。多言語対応や認証連携が楽"],
            ["api-gateway", "TypeScript (NestJS)", "API ルーティング・認証の定石フレームワーク"],
            ["user-service", "Java (Spring Boot)", "企業システムで定番。信頼性が高い"],
            ["item-service", "Java (Spring Boot)", "同上、user-service と同じ流儀"],
            ["ai-service", "Python (FastAPI)", "AI / 機械学習ライブラリが圧倒的に Python で揃ってる"],
            ["DB", "PostgreSQL + pgvector", "AI 用ベクトル検索ができる SQL DB"],
        ],
    )
    _callout(
        doc,
        "「言語が複数」って大変じゃないの？",
        "はい、それぞれ流儀が違うので学習コストはあります。ただし「サービスごとに完全独立」"
        "なので、AI 部分を触らない限り Python を知らなくても問題ありません。"
        "実際の開発でも、人によって担当を分けるのが普通です。",
    )

    doc.add_page_break()

    # ============================================================
    # 第 2 部
    # ============================================================
    _heading(doc, "第 2 部  準備する", level=0)

    _heading(doc, "4. 必要なソフトウェアをインストール", level=1)
    _para(doc, "最低限これだけで動きます:")
    _table(
        doc,
        [
            ["ソフト", "用途", "入手先"],
            ["Docker Desktop", "全サービスを動かす土台", "docker.com/products/docker-desktop"],
            ["Git", "コードを取得・管理", "git-scm.com"],
            ["（ブラウザ）", "画面を見る", "Chrome / Edge / Firefox"],
        ],
    )
    _para(doc, "発展的に何かを変えるなら追加で:")
    _table(
        doc,
        [
            ["ソフト", "用途", "入手先"],
            ["VS Code", "コードを見る・編集する", "code.visualstudio.com"],
            ["Python 3.12", "scripts/ 配下のツール実行", "python.org"],
            ["Node.js 20+", "frontend / api-gateway の単独起動", "nodejs.org"],
            ["Java 21", "user/item-service の単独起動", "adoptium.net"],
        ],
    )
    _callout(
        doc,
        "Docker Desktop だけで全部動きます",
        "Python / Node / Java は、自分のパソコンに直接インストールしなくても、"
        "Docker のおかげで完全に隔離された環境で全部動きます。"
        "「コードをちょっと見るだけ」なら Docker Desktop + Git だけで十分。",
    )

    _heading(doc, "4.1 Docker Desktop のインストール", level=2)
    _numbered(doc, "https://www.docker.com/products/docker-desktop/ にアクセス")
    _numbered(doc, "Windows 版をダウンロード → インストーラ起動")
    _numbered(doc, "再起動を求められたら従う")
    _numbered(doc, "起動するとタスクトレイにクジラのアイコンが出る")
    _numbered(doc, "「Engine running」と表示されれば準備完了")

    _heading(doc, "4.2 Git のインストール", level=2)
    _numbered(doc, "https://git-scm.com/ から Windows 版をダウンロード")
    _numbered(doc, "インストーラ起動 → 全部デフォルトのままで OK")
    _numbered(doc, "確認: PowerShell を開いて以下を実行")
    _code(doc, "git --version", lang_hint="PowerShell")
    _para(doc, "「git version 2.xx.x」のように表示されれば成功。")

    _section_break(doc)

    _heading(doc, "5. プロジェクトを自分のパソコンに持ってくる", level=1)
    _para(doc, "PowerShell（黒い画面、次章で説明）を開いて以下を順に実行:")
    _code(
        doc,
        """\
# プロジェクトを置きたいフォルダに移動（例: d:\\DEV\\personal-projects）
cd d:\\DEV\\personal-projects

# GitHub からダウンロード
git clone https://github.com/Litch9x/RecoForeJP.git

# プロジェクトの中に入る
cd RecoForeJP
""",
        lang_hint="PowerShell",
    )
    _para(doc, "成功すると以下のようなフォルダ構成が手元にできます:")
    _code(
        doc,
        """\
RecoForeJP/
├─ frontend/         画面のコード
├─ api-gateway/      受付係のコード
├─ user-service/     ユーザー管理のコード
├─ item-service/     アイテム管理のコード
├─ ai-service/       AI 部分のコード
├─ infra/            Docker 設定とDB の初期データ
├─ docs/             ドキュメント（このガイドもここ）
├─ scripts/          便利ツール（Python）
└─ README.md         概要
""",
    )

    _section_break(doc)

    _heading(doc, "6. ターミナル（黒い画面）の使い方", level=1)
    _para(
        doc,
        "プログラマが「ターミナル」「コンソール」「PowerShell」と言うのは、"
        "全部「コマンドを文字で打ち込んで実行する画面」のこと。Windows なら "
        "PowerShell が標準。",
    )
    _heading(doc, "6.1 開き方", level=2)
    _bullet(doc, "Windows キー → 「PowerShell」と入力 → Enter")
    _bullet(doc, "または、フォルダで Shift+右クリック → 「PowerShell ウィンドウをここで開く」")
    _bullet(doc, "VS Code を開いている場合: 上部メニュー「ターミナル」→「新しいターミナル」")

    _heading(doc, "6.2 知っておくべき基本コマンド", level=2)
    _table(
        doc,
        [
            ["コマンド", "意味", "例"],
            ["cd フォルダ名", "そのフォルダに移動", "cd d:\\DEV\\RecoForeJP"],
            ["cd ..", "1 つ上のフォルダに戻る", "—"],
            ["ls", "今いるフォルダの中身を見る", "—"],
            ["pwd", "今どこにいるか表示", "—"],
            ["cls", "画面をきれいにする", "—"],
            ["↑ キー", "前に打ったコマンドを呼び戻す", "—"],
            ["Tab キー", "ファイル名・コマンド名を自動補完", "—"],
            ["Ctrl+C", "実行中のコマンドを止める", "—"],
        ],
    )
    _callout(
        doc,
        "コマンドをコピペするときの注意",
        "このガイドの灰色の枠の中身は、そのまま PowerShell にペースト（右クリック）"
        "して Enter で実行できます。打ち間違いを避けるため、コピペがおすすめ。",
    )

    doc.add_page_break()

    # ============================================================
    # 第 3 部
    # ============================================================
    _heading(doc, "第 3 部  動かしてみる", level=0)

    _heading(doc, "7. 5 分で全機能を起動する", level=1)
    _para(doc, "RecoForeJP フォルダの中で、PowerShell を開いて順に実行します:")

    _heading(doc, "7.1 環境設定ファイルを作る", level=2)
    _code(
        doc,
        """\
# サンプルから .env をコピー
copy infra\\.env.example infra\\.env
""",
        lang_hint="PowerShell",
    )
    _para(doc, "（中身は最初はサンプルのままで OK。後から本番化するときに変更）")

    _heading(doc, "7.2 全サービスをまとめて起動", level=2)
    _code(
        doc,
        """\
docker compose -f infra/docker-compose.yml up -d --build
""",
        lang_hint="PowerShell",
    )
    _callout(
        doc,
        "初回は 10 分くらいかかります",
        "AI 部分が「torch」という重いライブラリ（800MB）をダウンロードするため。"
        "2 回目以降は数秒で起動します。コーヒーでも飲んで待ちましょう。",
    )
    _para(doc, "進行が見えなくても、Docker Desktop の「Containers」タブを見ると進捗が分かります。")

    _heading(doc, "7.3 全部立ち上がったか確認", level=2)
    _code(
        doc,
        """\
docker compose -f infra/docker-compose.yml ps
""",
        lang_hint="PowerShell",
    )
    _para(doc, "7 つの行が表示され、全て「healthy」と出れば成功。「starting」が混ざってたらもう少し待ちます。")

    _heading(doc, "7.4 AI に推薦データを覚えさせる", level=2)
    _para(doc, "起動しただけでは AI はアイテムを知りません。14 件のテストデータを「埋め込み」として登録:")
    _code(
        doc,
        """\
python scripts/seed_embeddings.py
""",
        lang_hint="PowerShell",
    )
    _para(doc, "「14 件成功」と出れば完了。Python が入っていない場合は次のコマンドで Docker 経由でも実行可能:")
    _code(
        doc,
        """\
docker run --rm --network reco-net -v ${PWD}:/app python:3.12 python /app/scripts/seed_embeddings.py
""",
        lang_hint="PowerShell（Python なしの場合）",
    )

    _heading(doc, "7.5 完了確認", level=2)
    _para(doc, "ブラウザで http://localhost:3001/ を開く → 自動的に /ja か /en にリダイレクトされ、ランディングページが表示されれば成功。")

    _section_break(doc)

    _heading(doc, "8. ブラウザで触ってみる", level=1)
    _para(doc, "全部で 6 つのページがあります。順に試してみましょう。")

    _heading(doc, "8.1 ランディング (http://localhost:3001/)", level=2)
    _bullet(doc, "ブラウザの言語設定が日本語なら /ja、英語なら /en に自動振り分け")
    _bullet(doc, "右上の「JA / EN」ボタンで切替可能")
    _bullet(doc, "サービス構成の説明とリンク集が出る")

    _heading(doc, "8.2 意味検索 (/ja/search)", level=2)
    _para(doc, "自然な日本語または英語で検索 → 384 次元のベクトルに変換 → 似ているアイテムを返す。")
    _bullet(doc, "クエリ欄に「ベトナム語で働けるカスタマーサポート」と入れて検索")
    _bullet(doc, "サンプルボタンも 4 つあるのでクリックで試せる")
    _bullet(doc, "結果に「sim=0.907」のような数値 → 0〜1 で大きいほど類似度が高い")
    _bullet(doc, "英語ページで「medical care with English support」→ 日本語アイテムが当たるのが多言語埋め込みの威力")

    _heading(doc, "8.3 ハイブリッド推薦 (/ja/recommendations)", level=2)
    _para(
        doc,
        "属性（日本語レベル・地域・興味）+ 任意のクエリで推薦。"
        "「content（属性マッチ）」「semantic（意味マッチ）」を重みで配合。",
    )
    _bullet(doc, "JLPT N3 / 新宿区 / 興味=就職 + 日本語学習 で取得 → 上位は「やさしい日本語クラス（新宿区）」「IT エンジニア募集」など")
    _bullet(doc, "スライダで content と semantic の重みを変えると結果が変わるのを確認できる")
    _bullet(doc, "各結果の「reasons」に「same region」「available in ja」など、なぜ選ばれたかの理由")

    _heading(doc, "8.4 ログイン (/ja/login)", level=2)
    _para(doc, "シードユーザーが 3 人います:")
    _table(
        doc,
        [
            ["Email", "Password", "Role", "属性"],
            ["nguyen.student@example.com", "password123", "USER", "VN / N3 / 新宿区 / 留学生"],
            ["raj.engineer@example.com", "password123", "USER", "IN / N5 / 港区 / エンジニア"],
            ["wang.resident@example.com", "password123", "ADMIN", "CN / N1 / 横浜市 / 永住"],
        ],
    )

    _heading(doc, "8.5 マイページ (/ja/me)", level=2)
    _bullet(doc, "ログイン後にプロフィール（JLPT・地域・興味）が見られる")
    _bullet(doc, "未ログインなら「ログインしてください」表示")
    _bullet(doc, "右上にメールアドレス + 「ログアウト」ボタン")

    _heading(doc, "8.6 管理画面 (/ja/admin/items) — ADMIN 専用", level=2)
    _bullet(doc, "wang.resident でログインすると右上に「管理」ボタンが出る")
    _bullet(doc, "クリックすると 14 件のアイテム一覧 + 追加フォーム + 削除ボタン")
    _bullet(doc, "新規追加するとすぐ /ja/search で検索結果に出る（AI に自動で覚えさせる）")
    _bullet(doc, "USER でアクセスすると「ADMIN ロールが必要」と出る")

    _section_break(doc)

    _heading(doc, "9. 中で動いているデータを覗く", level=1)
    _para(doc, "データベース（PostgreSQL）の中身を直接確認できます:")
    _code(
        doc,
        """\
# DB に接続して全ユーザーを見る
docker exec -it reco-postgres psql -U reco -d reco -c "SELECT email, role, nationality FROM users.users;"

# 全アイテムを見る
docker exec -it reco-postgres psql -U reco -d reco -c "SELECT id, title, region FROM items.items LIMIT 5;"

# 登録された埋め込みの件数
docker exec -it reco-postgres psql -U reco -d reco -c "SELECT COUNT(*) FROM ai.item_embeddings;"
""",
        lang_hint="PowerShell",
    )

    _para(doc, "サービスのログ（運転中の記録）を見る:")
    _code(
        doc,
        """\
# AI サービスのログをライブで見る（Ctrl+C で止める）
docker logs -f reco-ai-service

# 直近 50 行だけ
docker logs --tail 50 reco-api-gateway
""",
        lang_hint="PowerShell",
    )

    doc.add_page_break()

    # ============================================================
    # 第 4 部
    # ============================================================
    _heading(doc, "第 4 部  プロジェクトを進める", level=0)

    _heading(doc, "10. 新しいアイテム（求人や住居）を追加する", level=1)
    _para(doc, "方法は 3 つあります:")

    _heading(doc, "10.1 ブラウザの管理画面から（一番簡単）", level=2)
    _numbered(doc, "/ja/login で wang.resident@example.com / password123 でログイン")
    _numbered(doc, "右上「管理」→ /ja/admin/items へ")
    _numbered(doc, "下のフォームを埋めて「追加」")
    _numbered(doc, "自動で AI が埋め込み生成 → すぐに検索で出てくる")
    _para(doc, "フォームの必須項目: カテゴリ slug（job / housing / admin / medical / japanese-learning / community のいずれか）+ タイトル")

    _heading(doc, "10.2 シードデータに追加（永続化したい場合）", level=2)
    _para(doc, "infra/postgres/init/13-seed-dev-items.sql に SQL を書き足し、データベースを再初期化:")
    _code(
        doc,
        """\
# まず DB を空にして再起動（すべてのデータが消えるので注意）
docker compose -f infra/docker-compose.yml down -v
docker compose -f infra/docker-compose.yml up -d

# 埋め込みを再生成
python scripts/seed_embeddings.py
""",
        lang_hint="PowerShell",
    )

    _heading(doc, "10.3 コマンドラインから（curl）", level=2)
    _code(
        doc,
        """\
# まずトークン取得
$body = '{"email":"wang.resident@example.com","password":"password123"}'
$res = Invoke-RestMethod -Uri "http://localhost:3000/auth/login" -Method POST -ContentType "application/json" -Body $body
$token = $res.accessToken

# アイテム追加
$item = @{
  categorySlug = "job"
  title = "ベトナム語サポートの飲食店スタッフ"
  description = "新宿、夜勤あり、外国人歓迎"
  region = "東京都-新宿区"
  source = "manual"
  languages = @("ja","vi")
  tags = @("foreigner-welcome")
} | ConvertTo-Json
Invoke-RestMethod -Uri "http://localhost:3000/admin/items" -Method POST `
  -ContentType "application/json" -Headers @{Authorization="Bearer $token"} -Body $item
""",
        lang_hint="PowerShell",
    )

    _section_break(doc)

    _heading(doc, "11. 推薦精度を評価する", level=1)
    _para(doc, "「ハイブリッド推薦は本当に単独より良いの？」を数値で示すスクリプトがあります:")
    _code(
        doc,
        """\
python scripts/eval_recommendations.py
""",
        lang_hint="PowerShell",
    )
    _para(doc, "結果は以下のような表になります:")
    _code(
        doc,
        """\
━━━ 集計（3 ユーザー平均） ━━━
                  P@5    R@5  NDCG@5   P@10   R@10  NDCG@10
  content_only  0.867  0.754  0.843  0.533  0.905    0.869
  semantic_only 0.667  0.557  0.638  0.567  0.944    0.810
  hybrid        0.933  0.802  0.887  0.567  0.952    0.899
""",
        lang_hint="出力例",
    )
    _para(doc, "指標の読み方:")
    _bullet(doc, "P@5 = 上位 5 件のうち何件が正解か（最大 1.0 = 全部正解）")
    _bullet(doc, "R@5 = 正解全部のうち何割を上位 5 件で拾えたか")
    _bullet(doc, "NDCG@5 = 順位の良さも加味した品質スコア（最大 1.0）")
    _para(doc, "**hybrid が全項目で最良 = 論文の主張を裏付ける結果**。これがそのまま卒論 §5.3 の表になります。")

    _section_break(doc)

    _heading(doc, "12. コードを少し変えてみる", level=1)
    _para(doc, "小さな変更で挙動が変わる感覚をつかむのに良い例を 3 つ:")

    _heading(doc, "12.1 推薦スコアの重みを変える", level=2)
    _para(doc, "ファイル: ai-service/src/ai_service/recommend/scorer.py")
    _para(doc, "「地域一致のスコア重みを 2.0 → 5.0 に上げる」と、地域が同じアイテムが極端に上位になります。")
    _code(
        doc,
        """\
SCORE_WEIGHTS = {
    "category": 3.0,
    "region": 2.0,     # ← ここを 5.0 に変えてみる
    "language": 2.0,
    ...
}
""",
        lang_hint="python (変更箇所)",
    )
    _para(doc, "変更後の再起動:")
    _code(doc, "docker compose -f infra/docker-compose.yml up -d --build ai-service",
          lang_hint="PowerShell")

    _heading(doc, "12.2 サンプル検索クエリを変える", level=2)
    _para(doc, "ファイル: frontend/src/i18n/messages/ja.json の \"samples\" 配列。"
              "ここを書き換えると /ja/search のサンプルボタンが変わります。")
    _code(doc, "docker compose -f infra/docker-compose.yml up -d --build frontend",
          lang_hint="PowerShell")

    _heading(doc, "12.3 JWT の有効期限を変える", level=2)
    _para(doc, "ファイル: infra/.env の JWT_EXPIRES_IN_SECONDS（既定 3600 = 1 時間）。"
              "短くしてセッション切れの挙動を試したり、長くして開発を楽にしたり。")

    _section_break(doc)

    _heading(doc, "13. 新しい機能を追加するときの流れ", level=1)
    _para(doc, "「ちゃんとした開発の流儀」で進めるなら以下:")
    _numbered(doc, "Jira（タスク管理）で「やること」を Story として作成")
    _numbered(doc, "ターミナルで新しいブランチを作る: git checkout -b RECO-XX-short-name")
    _numbered(doc, "コードを編集 → docker compose up -d --build で動作確認")
    _numbered(doc, "テストを走らせる（必要なら）: npm test / ./gradlew test / pytest")
    _numbered(doc, "git add ... → git commit -m \"feat(area): what (RECO-XX)\"")
    _numbered(doc, "git push -u origin RECO-XX-... → GitHub で Pull Request を作成")
    _numbered(doc, "レビュー → squash merge → ブランチ削除")
    _numbered(doc, "Jira のステータスを Done に")

    _callout(
        doc,
        "1 人で開発でも PR を出すべき？",
        "出した方が良いです。理由: ①変更履歴が明確、②GitHub 上で自分のレビュー履歴になる、"
        "③仕事で同じことをやるので慣れる、④AI（Claude 等）に PR 単位でレビューを頼める。",
    )

    doc.add_page_break()

    # ============================================================
    # 第 5 部
    # ============================================================
    _heading(doc, "第 5 部  困ったときに", level=0)

    _heading(doc, "14. よくあるエラーと対処", level=1)
    _table(
        doc,
        [
            ["症状", "原因の見当", "対処"],
            ["ブラウザで「接続できません」", "Docker が起動していない", "Docker Desktop を起動 → docker compose ps で確認"],
            ["「Cannot connect to Docker daemon」", "Docker Desktop が起動前", "クジラアイコンが「Engine running」になるまで待つ"],
            ["ai-service が unhealthy", "AI モデルのロード中", "1-2 分待ってから docker compose ps を再確認"],
            ["seed_embeddings が timeout", "AI モデル初回ロードの待ち", "もう一度 python scripts/seed_embeddings.py を実行"],
            ["ログイン後 401", "JWT_SECRET が変わった or 期限切れ", "ログアウト → 再ログイン"],
            ["「ベトナム語通訳」が結果に出ない", "埋め込み未登録", "python scripts/seed_embeddings.py を再実行"],
            ["admin で 403", "wang.resident でなく USER でログイン中", "ログアウトして wang.resident でログイン"],
            ["ポート 3001 が使えない", "別アプリが使用中", "そのアプリを止める or infra/.env の FRONTEND_PORT を変える"],
        ],
    )

    _heading(doc, "15. ログ（記録）を読む", level=1)
    _para(doc, "何かおかしいときはまず該当サービスのログを見ます:")
    _code(
        doc,
        """\
# 全部のログを最新順に
docker compose -f infra/docker-compose.yml logs --tail 100

# 特定サービスのログをリアルタイム監視
docker logs -f reco-ai-service

# エラーだけを抽出
docker logs reco-api-gateway 2>&1 | findstr /i "error"
""",
        lang_hint="PowerShell",
    )
    _para(doc, "ログの色:")
    _bullet(doc, "INFO（白/緑）= 正常な動作記録")
    _bullet(doc, "WARN（黄）= 注意。動いてはいるが何か気になる")
    _bullet(doc, "ERROR（赤）= 異常。原因調査が必要")

    _heading(doc, "16. 完全リセットの仕方", level=1)
    _para(doc, "「最初の状態に戻したい」とき:")
    _code(
        doc,
        """\
# 全コンテナを止め、DB を含む全データを消す
docker compose -f infra/docker-compose.yml down -v

# 念のためイメージも消したい場合
docker compose -f infra/docker-compose.yml down -v --rmi all

# クリーンに作り直す
docker compose -f infra/docker-compose.yml up -d --build
python scripts/seed_embeddings.py
""",
        lang_hint="PowerShell",
    )
    _callout(
        doc,
        "down -v は破壊的",
        "-v を付けると DB のすべてのデータが消えます。"
        "/admin/items から追加したアイテムも全部消えるので注意。"
        "シードユーザー 3 人と元のアイテム 14 件は再起動で復活します。",
    )

    doc.add_page_break()

    # ============================================================
    # 第 6 部
    # ============================================================
    _heading(doc, "第 6 部  卒論につなげる", level=0)

    _heading(doc, "17. 論文の各章で何を書けるか", level=1)
    _table(
        doc,
        [
            ["章", "書ける素材", "対応する実装"],
            ["§1 序論", "在日外国人の課題、AI 推薦の意義", "—"],
            ["§2 関連研究", "既存推薦システム、多言語 NLP", "—"],
            ["§3.2 ユーザモデル", "JLPT・在留資格・興味カテゴリ", "users スキーマ"],
            ["§3.3.1 コンテンツベース", "属性マッチングスコア定義", "ai-service/recommend/scorer.py"],
            ["§3.3.3 ハイブリッド", "content × semantic 加重和の定式化", "ai-service/recommend/hybrid.py"],
            ["§3.4 多言語 NLP", "multilingual-e5 + pgvector の選択理由", "ai-service/embedding/"],
            ["§3.5 アーキテクチャ", "5 サービス + DB のトポロジー図", "docker-compose.yml + 図"],
            ["§4 実装", "各サービスの責務、API 設計、画面スクショ", "全コード"],
            ["§5.3 推薦性能評価", "P@K / R@K / NDCG@K の表", "eval_recommendations.py の出力"],
            ["§5.4 ユーザ評価", "被験者 N=10 程度でアンケート", "未実施（要被験者）"],
            ["§6 結論", "成果まとめ、課題、今後", "—"],
        ],
    )

    _heading(doc, "18. 次にやるべき作業の優先順位", level=1)
    _table(
        doc,
        [
            ["優先", "項目", "工数感", "卒論への影響"],
            ["1", "論文 §3-5 を執筆（コード素材は揃っている）", "大", "★★★"],
            ["2", "被験者実験（留学生 10 人にアンケート）", "中", "★★★"],
            ["3", "協調フィルタリング（feedback テーブル活用）", "中", "★★"],
            ["4", "ランキング多様化（MMR）", "中", "★"],
            ["5", "クラウドデプロイ（被験者に URL を配るため）", "小", "★★"],
        ],
    )
    _callout(
        doc,
        "最優先は論文執筆",
        "実装はもう「動く卒論システム」レベルに達しています。"
        "ここから先は「コードを書く」より「文章で説明する」フェーズ。"
        "実装スクショ + eval-results.json の数値を貼り込めば §3-5 の骨子はすぐ完成します。",
    )

    doc.add_page_break()

    # ============================================================
    # 付録
    # ============================================================
    _heading(doc, "付録 A  用語集", level=0)
    glossary = [
        ("API",
         "Application Programming Interface。プログラム同士が話すための約束。"
         "ここでは「URL に POST すると JSON が返ってくる」窓口のこと。"),
        ("AI",
         "Artificial Intelligence。本プロジェクトでは文章の意味をベクトルに変換する機械学習モデルを指す。"),
        ("bcrypt",
         "パスワードをハッシュ化（不可逆な暗号文に変換）するアルゴリズム。元のパスワードは復元できない。"),
        ("Bearer Token",
         "「これを持っている人は本人」と証明する文字列。HTTP の Authorization ヘッダに付ける。"),
        ("commit (コミット)",
         "「ここまでの変更を保存」するタイミング。git のスナップショット単位。"),
        ("CRUD",
         "Create / Read / Update / Delete。データの基本 4 操作。"),
        ("Docker",
         "アプリを「箱詰め」する技術。同じ箱はどのパソコンでも同じように動く。"),
        ("Docker container (コンテナ)",
         "Docker で動いている「箱」1 つ。Linux の小さな仮想マシンに近い。"),
        ("docker-compose",
         "複数のコンテナをまとめて起動・停止するツール。本プロジェクトは 7 コンテナ。"),
        ("embedding (埋め込み)",
         "文章を数百次元の数字配列（ベクトル）に変換する技術。「意味が近い文章 = ベクトルが近い」になる。"),
        ("frontend / backend",
         "frontend = ブラウザに表示される部分。backend = 裏で動く API・DB 等。"),
        ("Git",
         "ファイルのバージョン管理ツール。「いつ・誰が・何を変えたか」を記録できる。"),
        ("GitHub",
         "Git のリポジトリをインターネット上に保管 + 共同作業できるサービス。"),
        ("HTTP",
         "ブラウザと Web サーバが話すときの言葉。GET / POST / PUT / DELETE などの動詞を使う。"),
        ("JLPT",
         "日本語能力試験。N1（上級）〜 N5（初級）の 5 段階。"),
        ("JSON",
         "プログラム同士でデータを送るときの定番フォーマット。{ \"key\": \"value\" } の形。"),
        ("JWT",
         "JSON Web Token。ログイン後に発行される「身分証」。サーバが署名しているので偽造できない。"),
        ("microservice (マイクロサービス)",
         "1 つの大きなアプリを「役割ごと」に分割して、それぞれ独立に動かす設計。"),
        ("Next.js",
         "React で Web 画面を作るフレームワーク。本プロジェクトは v16。"),
        ("NestJS",
         "TypeScript で API を作るフレームワーク。"),
        ("npm",
         "Node.js のパッケージ管理ツール。pip の JavaScript 版。"),
        ("PostgreSQL",
         "オープンソースのリレーショナルデータベース。SQL で操作する。"),
        ("pgvector",
         "PostgreSQL にベクトル検索機能を追加する拡張。意味検索の中核。"),
        ("port (ポート)",
         "コンピュータ内のサービスを区別する番号。例: localhost:3001 = この PC の 3001 番口。"),
        ("Pull Request (PR)",
         "「この変更を取り込んでください」のリクエスト。レビュー後にマージされる。"),
        ("RBAC",
         "Role-Based Access Control。「役職ごとに使える機能を分ける」仕組み。本 PJ は USER / ADMIN。"),
        ("RESTful API",
         "URL とメソッド（GET/POST 等）でリソースを操作する API スタイル。"),
        ("scaffold (スキャフォールド)",
         "ひな型・骨格コードを生成すること。"),
        ("seed (シード)",
         "テスト用の初期データ。infra/postgres/init/12-seed-*.sql 等。"),
        ("Spring Boot",
         "Java で API・Web アプリを作るデファクト標準フレームワーク。"),
        ("SQL",
         "データベースに問い合わせる言語。SELECT * FROM users; など。"),
        ("squash merge",
         "ブランチの複数コミットを 1 つにまとめて main に取り込むマージ方式。履歴が綺麗。"),
        ("TypeScript",
         "JavaScript に型を足した言語。バグを未然に防ぎやすい。"),
        ("Uvicorn",
         "Python の高速 ASGI サーバ。FastAPI を本番起動するときに使う。"),
    ]
    for term, desc in glossary:
        p = doc.add_paragraph()
        r = p.add_run(f"{term}: ")
        r.bold = True
        _set_jp_font(r, 10.5)
        r2 = p.add_run(desc)
        _set_jp_font(r2, 10.5)

    doc.add_page_break()

    # ============================================================
    # 付録 B コマンド一覧
    # ============================================================
    _heading(doc, "付録 B  コマンドチートシート", level=0)

    _heading(doc, "Docker compose", level=2)
    _code(
        doc,
        """\
# 起動（変更あれば自動でビルド）
docker compose -f infra/docker-compose.yml up -d --build

# 状態確認
docker compose -f infra/docker-compose.yml ps

# ログ確認
docker compose -f infra/docker-compose.yml logs -f
docker logs -f reco-ai-service

# 停止（データは残す）
docker compose -f infra/docker-compose.yml down

# 完全リセット（DB データも消す）
docker compose -f infra/docker-compose.yml down -v
""",
        lang_hint="PowerShell",
    )

    _heading(doc, "Python スクリプト", level=2)
    _code(
        doc,
        """\
# アイテム埋め込みを一括登録
python scripts/seed_embeddings.py

# 推薦精度の評価
python scripts/eval_recommendations.py

# このガイドを再生成
python scripts/generate_complete_guide.py
""",
        lang_hint="PowerShell",
    )

    _heading(doc, "Git ワークフロー", level=2)
    _code(
        doc,
        """\
# 最新の main を取得
git checkout main
git pull

# 新しいブランチを作る
git checkout -b RECO-XX-short-name

# 変更を確認
git status
git diff

# コミット
git add ファイル名
git commit -m "feat(area): 何をしたか (RECO-XX)"

# GitHub に push
git push -u origin RECO-XX-short-name

# PR を作る (gh CLI が必要)
gh pr create --title "..." --body "..."
""",
        lang_hint="PowerShell",
    )

    _heading(doc, "DB 直叩き", level=2)
    _code(
        doc,
        """\
# 接続
docker exec -it reco-postgres psql -U reco -d reco

# 接続後 (\\dt で table 一覧、\\q で終了)
\\dt users.*
SELECT * FROM users.users;
\\q
""",
        lang_hint="PowerShell + psql",
    )

    doc.add_page_break()

    # ============================================================
    # 付録 C ファイル構成早見表
    # ============================================================
    _heading(doc, "付録 C  ファイル構成早見表", level=0)
    _code(
        doc,
        """\
RecoForeJP/
├─ frontend/                     画面 (Next.js / TypeScript)
│   ├─ src/app/[lang]/           言語切替対応の各ページ
│   │   ├─ page.tsx              /  ランディング
│   │   ├─ search/page.tsx       /search  意味検索
│   │   ├─ recommendations/page.tsx  /recommendations
│   │   ├─ login/page.tsx        /login
│   │   ├─ me/page.tsx           /me
│   │   └─ admin/items/page.tsx  /admin/items  (ADMIN 限定)
│   ├─ src/app/api/              サーバ側プロキシ (Route Handler)
│   ├─ src/components/           React コンポーネント
│   ├─ src/lib/                  共通ヘルパ (auth.ts 等)
│   ├─ src/i18n/messages/        ja.json / en.json 辞書
│   ├─ src/proxy.ts              locale リダイレクト
│   └─ Dockerfile
├─ api-gateway/                  受付係 (NestJS)
│   ├─ src/auth/                 JWT 発行・検証・ガード
│   ├─ src/me/                   /me/* プロキシ
│   ├─ src/admin/                /admin/* プロキシ + RBAC
│   ├─ src/ai-proxy/             /search /recommend プロキシ
│   └─ Dockerfile
├─ user-service/                 ユーザ管理 (Spring Boot)
│   ├─ src/main/java/.../user/   User / Profile / Preferences
│   ├─ src/main/java/.../auth/   /internal/auth/verify
│   └─ Dockerfile
├─ item-service/                 アイテム管理 (Spring Boot)
│   ├─ src/main/java/.../item/   Item / CRUD
│   ├─ src/main/java/.../catalog/  Category / Tag
│   ├─ src/main/java/.../feedback/ Feedback API
│   └─ Dockerfile
├─ ai-service/                   AI (Python / FastAPI)
│   ├─ src/ai_service/recommend/   scorer / hybrid
│   ├─ src/ai_service/embedding/   encoder / store
│   ├─ src/ai_service/llm/         explain (OpenAI optional)
│   ├─ src/ai_service/eval/        metrics (P / R / NDCG)
│   ├─ tests/                      pytest 66 件
│   └─ Dockerfile
├─ infra/                        インフラ設定
│   ├─ docker-compose.yml          7 サービス定義
│   ├─ .env.example                環境変数サンプル
│   └─ postgres/init/              DB 初期化 SQL
├─ scripts/                      Python 製ツール
│   ├─ seed_embeddings.py          埋め込み投入
│   ├─ eval_recommendations.py     §5.3 評価
│   ├─ generate_dev_guide.py       開発ガイド再生成
│   ├─ generate_project_history.py 開発履歴再生成
│   └─ generate_complete_guide.py  このガイドを再生成
├─ docs/                         ドキュメント
│   ├─ 完全ガイド.docx              ← このファイル
│   ├─ 開発ガイド.docx              リファレンス
│   ├─ 開発履歴.docx                時系列ジャーニー
│   ├─ RecoForeJP.docx              論文目次
│   └─ schema/                     DB スキーマ ER 図
└─ README.md
""",
        lang_hint="tree",
    )

    # ----- フッタ -----
    doc.add_paragraph()
    p = doc.add_paragraph()
    p.alignment = WD_ALIGN_PARAGRAPH.CENTER
    r = p.add_run("ここまで読んでくれてありがとう。\nプロジェクトを楽しんで進めてください。")
    r.italic = True
    _set_jp_font(r, 10)

    OUT_PATH.parent.mkdir(parents=True, exist_ok=True)
    doc.save(OUT_PATH)
    print(f"✅ {OUT_PATH.relative_to(OUT_PATH.parent.parent)} を生成しました")
    print(f"   ({OUT_PATH.stat().st_size:,} bytes)")


if __name__ == "__main__":
    build()
