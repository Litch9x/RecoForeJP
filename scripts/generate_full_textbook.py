"""RecoForeJP - 完全教科書 (.docx) ジェネレータ

コード未経験者向けに 14 部・150 章超の詳細教科書を 1 つの docx に出力する。
内容は「概要 → 手順 → コマンド → ポイント → 練習」の繰り返しで、
ページ数は 500 前後を目標。

【使い方】
    python scripts/generate_full_textbook.py
    # → docs/完全教科書.docx
"""

from __future__ import annotations

from pathlib import Path

from docx import Document
from docx.enum.table import WD_ALIGN_VERTICAL
from docx.enum.text import WD_ALIGN_PARAGRAPH
from docx.oxml import OxmlElement
from docx.oxml.ns import qn
from docx.shared import Cm, Pt, RGBColor

OUT_PATH = Path(__file__).resolve().parent.parent / "docs" / "完全教科書.docx"


# ---------------------------------------------------------------------------
# レイアウト関数
# ---------------------------------------------------------------------------


def _font(run, size_pt=10.5):
    run.font.name = "Meiryo"
    run.font.size = Pt(size_pt)
    rPr = run._element.get_or_add_rPr()
    rFonts = rPr.find(qn("w:rFonts"))
    if rFonts is None:
        rFonts = OxmlElement("w:rFonts")
        rPr.append(rFonts)
    for tag in ("eastAsia", "ascii", "hAnsi", "cs"):
        rFonts.set(qn(f"w:{tag}"), "Meiryo")


def p(doc, text, size=10.5, bold=False):
    par = doc.add_paragraph()
    run = par.add_run(text)
    run.bold = bold
    _font(run, size)


def h(doc, text, level=1):
    par = doc.add_heading("", level=level)
    run = par.add_run(text)
    run.bold = True
    sizes = {0: 24, 1: 18, 2: 14, 3: 12, 4: 11}
    _font(run, sizes.get(level, 11))


def code(doc, text, lang=""):
    par = doc.add_paragraph()
    par.paragraph_format.left_indent = Cm(0.5)
    par.paragraph_format.space_after = Pt(2)
    if lang:
        meta = par.add_run(f"[{lang}]\n")
        meta.font.name = "Consolas"
        meta.font.size = Pt(8)
        meta.font.color.rgb = RGBColor(0x88, 0x88, 0x88)
    run = par.add_run(text)
    run.font.name = "Consolas"
    run.font.size = Pt(9)
    shd = OxmlElement("w:shd")
    shd.set(qn("w:fill"), "F4F4F4")
    par._p.get_or_add_pPr().append(shd)


def bul(doc, text):
    par = doc.add_paragraph(style="List Bullet")
    run = par.add_run(text)
    _font(run, 10.5)


def num(doc, text):
    par = doc.add_paragraph(style="List Number")
    run = par.add_run(text)
    _font(run, 10.5)


def tbl(doc, rows, header=True):
    table = doc.add_table(rows=len(rows), cols=len(rows[0]))
    table.style = "Light Grid"
    for i, row in enumerate(rows):
        for j, txt in enumerate(row):
            cell = table.cell(i, j)
            cell.vertical_alignment = WD_ALIGN_VERTICAL.CENTER
            cell.text = ""
            par = cell.paragraphs[0]
            run = par.add_run(txt)
            _font(run, 10)
            if header and i == 0:
                run.bold = True


def callout(doc, label, body, color="FFF8E1"):
    par = doc.add_paragraph()
    par.paragraph_format.left_indent = Cm(0.5)
    par.paragraph_format.space_after = Pt(4)
    par.paragraph_format.space_before = Pt(4)
    run = par.add_run(f"💡 {label}\n")
    run.bold = True
    _font(run, 10)
    run2 = par.add_run(body)
    _font(run2, 10)
    shd = OxmlElement("w:shd")
    shd.set(qn("w:fill"), color)
    par._p.get_or_add_pPr().append(shd)


def warn(doc, label, body):
    callout(doc, label, body, color="FFEBEE")


def note(doc, label, body):
    callout(doc, label, body, color="E3F2FD")


def practice(doc, items):
    """章末の練習問題セクション。"""
    h(doc, "🎯 練習問題", level=3)
    for i, item in enumerate(items, 1):
        num(doc, item)
    p(doc, "（答え合わせ: コマンドが期待どおり動けば OK。エラーが出たら 第 129-138 章のトラブルシューティングを参照）",
      size=9)


def summary(doc, items):
    """章末のまとめ。"""
    h(doc, "📝 この章のまとめ", level=3)
    for it in items:
        bul(doc, it)


def br(doc):
    """章間の薄い区切り。"""
    par = doc.add_paragraph()
    par.alignment = WD_ALIGN_PARAGRAPH.CENTER
    run = par.add_run("— — —")
    run.font.color.rgb = RGBColor(0xCC, 0xCC, 0xCC)
    _font(run, 10)


def chap(doc, num_str, title, page_break=True):
    """章見出し（章番号 + タイトル）"""
    if page_break:
        doc.add_page_break()
    h(doc, f"第 {num_str} 章  {title}", level=1)


def part_cover(doc, num_str, title, body):
    """部の表紙ページ。"""
    doc.add_page_break()
    par = doc.add_paragraph()
    par.alignment = WD_ALIGN_PARAGRAPH.CENTER
    run = par.add_run(f"\n\n\n第 {num_str} 部")
    run.bold = True
    _font(run, 28)
    par2 = doc.add_paragraph()
    par2.alignment = WD_ALIGN_PARAGRAPH.CENTER
    run = par2.add_run(title)
    run.bold = True
    _font(run, 20)
    par3 = doc.add_paragraph()
    par3.alignment = WD_ALIGN_PARAGRAPH.CENTER
    run = par3.add_run(f"\n\n{body}")
    _font(run, 12)


# ===========================================================================
# 各部の内容
# ===========================================================================


def part1_intro(doc):
    part_cover(
        doc, "1",
        "プロジェクトを理解する",
        "コードに触れる前に、何のためのソフトウェアか・誰のための・どう役立つかを\n"
        "じっくり知るパートです。技術用語はほぼ出ません。",
    )

    # 第 1 章
    chap(doc, "1", "在日外国人の生活の課題")
    h(doc, "1.1 増え続ける在日外国人", level=2)
    p(doc,
      "2024 年時点で日本に住む外国人は約 300 万人と過去最多を更新し続けています。"
      "技能実習・留学・特定技能・永住など、立場もさまざまです。"
      "国も「多文化共生」を掲げ、自治体レベルで多言語化が進んでいますが、"
      "現場で生活する個人が「自分に合った情報」にたどり着くのは依然として大変です。")
    h(doc, "1.2 具体的に何が困るのか", level=2)
    p(doc, "在日外国人がぶつかる代表的な壁:")
    bul(doc, "求人情報: 「日本語ペラペラ」が前提の求人が多く、自分のレベルで応募できる求人が見つかりづらい")
    bul(doc, "住居: 外国人を断る大家、保証人が必要な物件、初期費用の透明性のなさ")
    bul(doc, "行政: 在留資格更新・マイナンバー・税・年金など、書類が日本語でやさしくない")
    bul(doc, "医療: 英語対応している病院がどこにあるか分からない、症状を伝えるのが難しい")
    bul(doc, "日本語学習: 教室は多いがレベルや費用、立地で自分に合う場所を探すのが大変")
    bul(doc, "コミュニティ: 同郷の集まり、地域の祭り、子どもの学校行事の情報入手")
    h(doc, "1.3 既存の情報源とその限界", level=2)
    p(doc,
      "今、在日外国人が情報を取る場所は主に: 自治体の多言語ページ・GaijinPot・Facebook の各国コミュニティグループ・"
      "Reddit r/japanlife・LINE のグループチャット・口コミ。"
      "それぞれ役立ちますが、横断検索ができない・更新が止まっている・自分の属性に合っているか確証が持てない、"
      "という弱点があります。")
    h(doc, "1.4 「人ごと」ではなく「自分ごと」の情報", level=2)
    p(doc,
      "「N3 のベトナム人留学生で、新宿に住んでいて、IT に興味がある」のような個別属性に合わせて"
      "「あなた向け」をピンポイントで提示するのが、本プロジェクトの推薦システムの目的です。")
    callout(doc, "なぜ AI を使うのか?",
            "ルールベース（if N3 then ... else ...）でも作れますが、属性が増えると条件分岐が爆発します。"
            "意味検索（embedding）を使うと、文字どおりの一致を超えて「英語 OK の仕事」と「外国人歓迎のエンジニア募集」"
            "を関連付けられます。これは AI でないと難しい部分です。")
    summary(doc, [
        "在日外国人 300 万人時代、ひとりひとりに合った情報配信の需要が増えている",
        "求人・住居・行政・医療・学習・コミュニティの 6 分野で情報の壁が大きい",
        "既存の情報源は横断・最新性・パーソナライズに弱い",
        "AI 推薦により「自分ごとの情報」を届ける、というのが本プロジェクトの目的",
    ])
    practice(doc, [
        "あなたの身の回りの外国人友達 / 知人 1 人を思い浮かべ、その人がいま欲しい情報を 3 つ書き出してみる",
        "既存の Web サービス（GaijinPot 等）を 1 つ開いて、上の 3 情報を実際に検索できるか試す",
    ])

    # 第 2 章
    chap(doc, "2", "推薦システムとは何か")
    h(doc, "2.1 「あなたへのおすすめ」の正体", level=2)
    p(doc,
      "Netflix の「あなたへのおすすめ」、Amazon の「この商品を買った人はこれも買っています」、"
      "Spotify の「あなたへのミックス」、YouTube のホーム画面 — すべて推薦システムです。"
      "推薦システムとは「無数のアイテムからユーザーに合うものを少数選び順序付けて見せる仕組み」全般を指します。")
    h(doc, "2.2 3 つの代表的アプローチ", level=2)
    tbl(doc, [
        ["アプローチ", "ざっくり仕組み", "向き不向き"],
        ["コンテンツベース", "アイテム属性とユーザー属性のマッチング", "属性が明確、コールドスタートに強い"],
        ["協調フィルタリング", "似たユーザーが好んだものを勧める", "データが多いと強い、新規ユーザーに弱い"],
        ["ハイブリッド", "両方を組合せる", "実用システムはほぼハイブリッド"],
    ])
    h(doc, "2.3 このプロジェクトのアプローチ", level=2)
    p(doc,
      "RecoForeJP では「コンテンツベース（属性マッチング）+ 意味検索（自然言語クエリ）」を加重和で組合せる"
      "ハイブリッド方式を採用しています。論文 §3.3.3 に対応。"
      "協調フィルタリングは将来追加予定（feedback テーブルで素材は集めている）。")
    h(doc, "2.4 評価指標の予告", level=2)
    p(doc,
      "推薦が「良い」かを測るための指標として、本書では Precision（精度）/ Recall（再現率）/ NDCG（順位品質）を扱います。"
      "詳しくは第 122-124 章で説明します。今は「上位 5 件のうち何件が正解か」という P@5 が分かれば十分です。")
    summary(doc, [
        "推薦システムは「無数 → 少数 → 順序」を作る仕組みの総称",
        "コンテンツベース / 協調 / ハイブリッドが代表的",
        "本プロジェクトはハイブリッド（content + semantic）",
        "良し悪しは Precision/Recall/NDCG で測る",
    ])
    practice(doc, [
        "Netflix と YouTube の「おすすめ」がどう違って感じるか、3 つ書き出す",
        "自分が「外したな」と思った推薦経験を 1 つ思い出して、その理由を考える",
    ])

    # 第 3 章
    chap(doc, "3", "AI で何ができるか")
    h(doc, "3.1 AI と機械学習と深層学習", level=2)
    tbl(doc, [
        ["用語", "範囲", "イメージ"],
        ["AI（人工知能）", "もっとも広い概念", "「人っぽい知的処理」をするものすべて"],
        ["機械学習", "AI の中の手法群", "データから学ぶ"],
        ["深層学習", "機械学習の一分野", "ニューラルネットワークを多層化"],
        ["LLM", "深層学習の応用", "ChatGPT 等の言語モデル"],
    ])
    h(doc, "3.2 本プロジェクトで使う AI 技術", level=2)
    bul(doc, "意味埋め込み (embedding): 文章を 384 次元の数字配列に変換 → 似た意味は近い座標に")
    bul(doc, "近似最近傍検索: ベクトル空間で「似ているもの」を高速に検索")
    bul(doc, "LLM 生成: 推薦理由を自然な日本語で説明（OpenAI optional）")
    h(doc, "3.3 何が魔法ではないか", level=2)
    p(doc,
      "AI は万能ではありません。データに無い情報は推測できないし、"
      "学習データの偏りはそのまま結果に反映されます。"
      "例: 「ベトナム」関連の求人がデータに 1 件しかない場合、それしか出ません。"
      "AI を活かすにはまず質の良いデータを集めることが最重要です。")
    summary(doc, [
        "AI ⊃ 機械学習 ⊃ 深層学習 ⊃ LLM",
        "本 PJ は埋め込み + 近似最近傍 + LLM 説明の組合せ",
        "AI は魔法ではなくデータ品質に依存",
    ])

    # 第 4 章
    chap(doc, "4", "このプロジェクトのゴール")
    h(doc, "4.1 卒業研究としてのゴール", level=2)
    bul(doc, "論文の §3-5 を実装で裏付ける")
    bul(doc, "提案手法（ハイブリッド推薦）が単独より優れることを定量検証する")
    bul(doc, "実装そのものを成果物として残し、後の研究者が拡張可能にする")
    h(doc, "4.2 技術的なゴール", level=2)
    bul(doc, "5 マイクロサービス + 2 データ層で論文 §3.5 アーキテクチャを実装")
    bul(doc, "JWT + RBAC で実用レベルの認証認可")
    bul(doc, "多言語埋め込みで言語横断検索を可能に")
    bul(doc, "Docker compose 一発でフルスタックが起動")
    h(doc, "4.3 何をしないか（スコープ外）", level=2)
    bul(doc, "実運用の SLA は目指さない（テストデータ 14 件レベル）")
    bul(doc, "商用化・スケーラビリティチューニングはやらない")
    bul(doc, "モバイルアプリは作らない（Web のみ）")

    # 第 5 章
    chap(doc, "5", "想定ユーザー像")
    p(doc, "シードデータには 3 名のテストユーザーがいます。それぞれが想定ユーザー像の代表例です。")
    h(doc, "5.1 ユーザー A: 留学生（ベトナム出身、N3）", level=2)
    p(doc,
      "名前: Nguyen / 国籍: ベトナム / 来日 6 ヶ月 / 新宿区在住 / 大学生 / "
      "日本語 N3 / 興味: 仕事・日本語学習・地域イベント。"
      "やさしい日本語で読める情報 + ベトナム語サポートが欲しい代表。")
    h(doc, "5.2 ユーザー B: 新人エンジニア（インド出身、N5）", level=2)
    p(doc,
      "名前: Raj / 来日 1 ヶ月 / 港区在住 / IT エンジニア / 日本語 N5 / "
      "興味: 住居・行政手続き・日本語学習。"
      "英語表示が必要、行政書類がやさしい日本語であってほしい。")
    h(doc, "5.3 ユーザー C: 永住者（中国出身、N1）", level=2)
    p(doc,
      "名前: Wang / 来日 5 年 / 横浜市在住 / 会社員 / 日本語 N1 / "
      "興味: 地域イベント・医療。"
      "日本語はネイティブ並み、コミュニティと医療情報が中心。本 PJ では ADMIN ロールを与えてある。")

    # 第 6 章
    chap(doc, "6", "既存サービスとの比較")
    tbl(doc, [
        ["サービス", "強み", "弱み"],
        ["GaijinPot", "求人・住居の英語情報が豊富", "パーソナライズ無し、日本語学習者向けの分類無し"],
        ["自治体多言語ページ", "公式情報・信頼性高い", "横断検索無し、UI が古い場合あり"],
        ["Facebook グループ", "リアルタイム、口コミ", "情報の質に幅、検索しづらい"],
        ["Reddit r/japanlife", "実体験ベース", "英語のみ、日本語学習向けではない"],
        ["RecoForeJP（本 PJ）", "属性 × 意味検索のパーソナライズ", "データ少（卒研段階）"],
    ])

    # 第 7 章
    chap(doc, "7", "卒業研究としての位置づけ")
    p(doc, "本プロジェクトは「修士論文の実装パート」です。論文構成と実装の関係:")
    tbl(doc, [
        ["論文章", "実装で対応するもの"],
        ["§1 序論", "本書 第 1-6 章の内容"],
        ["§2 関連研究", "未着手（要文献調査）"],
        ["§3 提案手法", "全コードベース"],
        ["§4 実装", "全コードベース + スクショ"],
        ["§5 評価実験", "scripts/eval_recommendations.py の出力"],
        ["§6 結論", "未着手"],
    ])

    # 第 8 章
    chap(doc, "8", "倫理・プライバシーの考え方")
    p(doc, "個人情報を扱うシステムなので、卒論段階でも以下の方針を守ります:")
    bul(doc, "パスワードは平文保存せず bcrypt ハッシュ化（user-service）")
    bul(doc, "JWT 署名鍵は環境変数管理（コミット禁止）")
    bul(doc, "シードユーザーは架空（@example.com）、実在人物の情報は使わない")
    bul(doc, "国籍・在留資格はセンシティブ情報。論文・スクショで実在ユーザーを特定可能な形にしない")
    bul(doc, "被験者実験では同意書を取り、データを匿名化する")

    # 第 9 章
    chap(doc, "9", "本書の使い方")
    p(doc, "本書は 14 部 + 付録 5 の構成で、それぞれ独立に読めます。")
    p(doc, "おすすめの読み方:")
    bul(doc, "完全未経験 → 第 1 部から順番に")
    bul(doc, "PC は触れる → 第 3 部から（ソフトウェアインストール）")
    bul(doc, "とにかく動かしたい → 第 5 部「最初の起動」へジャンプ")
    bul(doc, "中身を理解したい → 第 7 部「中の仕組み」")
    bul(doc, "卒論に書き起こしたい → 第 14 部「卒論への展開」")

    # 第 10 章
    chap(doc, "10", "学習の進め方")
    p(doc, "教科書を「読むだけ」では身につきません。以下を意識してください:")
    bul(doc, "実際にコマンドを打って確認する（コピペで OK）")
    bul(doc, "エラーが出ても落ち込まない。エラーは「コンピュータからの会話」")
    bul(doc, "練習問題を 1 つでもやってみる")
    bul(doc, "分からない単語は付録 A の用語集で確認")
    bul(doc, "1 日 30 分でも継続する方が、週末に 3 時間より身につく")
    callout(doc, "AI に聞く",
            "ChatGPT / Claude / Gemini に「これってどういう意味？」と聞きながら進めると効率的。"
            "本書のコードや用語をそのまま貼って質問しても OK です。")


def part2_pc_basics(doc):
    part_cover(
        doc, "2",
        "パソコンの基礎知識",
        "プログラミング以前のところ。OS・ファイル・ターミナル・環境変数・ポート — \n"
        "後でつまずかないために、基礎概念を一度通しで確認します。",
    )

    chap(doc, "11", "OS（オペレーティングシステム）とは")
    h(doc, "11.1 OS の役割", level=2)
    p(doc,
      "OS（Operating System）は、パソコンのハードウェア（CPU・メモリ・ディスク・キーボード等）と"
      "アプリ（Word, Chrome, ゲーム等）の間に立つ「仲介役」です。アプリは OS の API を呼び、OS が代わりにハードを操作します。")
    tbl(doc, [
        ["OS 名", "用途", "本 PJ での扱い"],
        ["Windows 10/11", "デスクトップ最多シェア", "メインのターゲット環境"],
        ["macOS", "Apple 製。Unix 系", "コマンドはほぼ同じで使える"],
        ["Linux", "サーバで主流", "Docker コンテナの中身はだいたい Linux"],
    ])
    h(doc, "11.2 ファイルシステム", level=2)
    p(doc,
      "OS はディスクの内容を「ファイル」と「フォルダ（ディレクトリ）」の階層で扱います。"
      "Windows では C:\\Users\\Name\\Documents\\ のように \\ で階層を区切ります。"
      "Linux/macOS は / で区切る点が違いますが概念は同じ。")
    h(doc, "11.3 プロセス", level=2)
    p(doc,
      "実行中のプログラム一つを「プロセス」と呼びます。Chrome を 1 つ開けば 1 プロセス、"
      "タブを増やせばさらにプロセスが増える。Docker のコンテナも一種のプロセスです。"
      "タスクマネージャ（Ctrl+Shift+Esc）で見られます。")
    summary(doc, [
        "OS はアプリとハードの仲介役",
        "ファイルシステムは階層構造",
        "プロセスは「動いているプログラム 1 つ」",
    ])

    chap(doc, "12", "Windows の基本操作")
    h(doc, "12.1 知っておくべきショートカット", level=2)
    tbl(doc, [
        ["キー", "動作"],
        ["Windows キー", "スタートメニュー / 検索"],
        ["Windows + E", "エクスプローラー（ファイル管理）を開く"],
        ["Windows + R", "「ファイル名を指定して実行」"],
        ["Alt + Tab", "ウィンドウ切替"],
        ["Win + L", "画面ロック"],
        ["Ctrl + C / V / X", "コピー / 貼付 / 切取"],
        ["Ctrl + Z", "元に戻す"],
        ["Ctrl + Shift + Esc", "タスクマネージャ"],
        ["PrintScreen", "画面キャプチャ"],
    ])
    h(doc, "12.2 開発で使うフォルダの推奨配置", level=2)
    code(doc,
         "C:\\Users\\<あなた>\\Documents\\dev\\          (デフォルト候補)\n"
         "D:\\DEV\\personal-projects\\                   (このプロジェクトはここに置く想定)",
         lang="例")
    p(doc, "OneDrive 配下に置くと同期で重くなりやすいので、開発フォルダは OneDrive の外がおすすめ。")

    chap(doc, "13", "ファイルとフォルダの概念")
    h(doc, "13.1 拡張子", level=2)
    tbl(doc, [
        ["拡張子", "意味", "本 PJ での例"],
        [".ts", "TypeScript", "frontend, api-gateway"],
        [".tsx", "TypeScript + React JSX", "frontend のコンポーネント"],
        [".py", "Python", "ai-service, scripts"],
        [".java", "Java", "user-service, item-service"],
        [".sql", "SQL", "infra/postgres/init"],
        [".json", "JSON データ", "package.json, dictionaries"],
        [".yml / .yaml", "YAML", "docker-compose, GitHub Actions"],
        [".md", "Markdown", "README, AGENTS.md"],
        [".docx", "Word", "docs フォルダの教科書類"],
    ])
    callout(doc, "拡張子を表示する",
            "エクスプローラー → 「表示」→「ファイル名拡張子」にチェック。"
            "拡張子が見えないと「app.ts」と「app.tsx」を取り違える原因になります。")

    chap(doc, "14", "ターミナルとは何か")
    p(doc, "ターミナル = 黒い画面で文字を打ち込んでコンピュータと対話するアプリ。「コマンド」を打ち、「結果」が返ります。")
    h(doc, "14.1 GUI vs CLI", level=2)
    tbl(doc, [
        ["", "GUI", "CLI（ターミナル）"],
        ["操作", "マウスクリック中心", "文字コマンド中心"],
        ["速度", "学習は楽、操作は遅い", "学習は急、操作は速い"],
        ["再現性", "手順記録が難しい", "コマンドをコピペ可能"],
        ["自動化", "難しい", "スクリプト化が前提"],
    ])
    p(doc, "プログラマがターミナルを使う理由: 再現性 + 自動化 + 速度。"
           "本書のコマンドも全てコピペできる形にしてあります。")

    chap(doc, "15", "PowerShell の起動と基本")
    h(doc, "15.1 開き方 3 種類", level=2)
    num(doc, "Windows キーを押して「powershell」と打ち込み、Enter（最速）")
    num(doc, "フォルダで Shift + 右クリック →「PowerShell ウィンドウをここで開く」")
    num(doc, "VS Code: メニュー「ターミナル」→「新しいターミナル」")
    h(doc, "15.2 開いた直後に出てくる文字の意味", level=2)
    code(doc, "PS C:\\Users\\ADMIN>", lang="プロンプト")
    bul(doc, "PS = PowerShell の略")
    bul(doc, "C:\\Users\\ADMIN = 現在のフォルダ（カレントディレクトリ）")
    bul(doc, "> = ここからコマンドを入力できる、というマーカー")
    h(doc, "15.3 初心者がよくつまずく 4 つ", level=2)
    bul(doc, "コマンドが見つからない: 綴り違い、または PATH に通っていない")
    bul(doc, "コピペすると改行扱いになる: ペーストは右クリック or Ctrl+V")
    bul(doc, "「実行ポリシー」エラー: スクリプト実行制限を一時解除する必要がある場合あり")
    bul(doc, "閉じてしまった: 変数も履歴も消える（履歴は %APPDATA%\\Microsoft\\Windows\\PowerShell\\PSReadLine に残る）")

    chap(doc, "16", "PowerShell のコマンド一覧")
    tbl(doc, [
        ["コマンド", "用途", "例"],
        ["cd <path>", "フォルダ移動", "cd d:\\DEV"],
        ["cd ..", "親フォルダへ", "—"],
        ["pwd", "現在地表示", "—"],
        ["ls", "中身一覧", "ls *.md"],
        ["mkdir", "フォルダ作成", "mkdir tmp"],
        ["rm", "削除", "rm tmp"],
        ["cat <file>", "ファイル中身表示", "cat README.md"],
        ["cls", "画面クリア", "—"],
        ["history", "コマンド履歴", "—"],
        ["Get-Process", "プロセス一覧", "—"],
        ["Get-Service", "Windows サービス一覧", "—"],
        ["$env:NAME", "環境変数", "$env:PATH"],
        ["echo <text>", "文字を表示", "echo Hello"],
    ])
    practice(doc, [
        "PowerShell を開いて pwd を打つ。今どこにいるか確認",
        "cd .. を 3 回打って、毎回 pwd で確認。何が起きているか観察",
        "cd c:\\ で C ドライブのルートへ。ls で中身を見る",
    ])

    chap(doc, "17", "ファイル操作コマンドを使いこなす")
    code(doc,
         "# ファイル作成\n"
         "New-Item -ItemType File memo.txt\n\n"
         "# ファイル内容を書き換える\n"
         "\"hello world\" | Out-File memo.txt -Encoding utf8\n\n"
         "# 中身を見る\n"
         "Get-Content memo.txt\n\n"
         "# コピー / 移動 / リネーム\n"
         "Copy-Item memo.txt memo2.txt\n"
         "Move-Item memo2.txt sub\\memo2.txt\n"
         "Rename-Item memo.txt memo-new.txt\n\n"
         "# 削除\n"
         "Remove-Item memo-new.txt",
         lang="PowerShell")

    chap(doc, "18", "環境変数の概念")
    p(doc, "環境変数 = OS が覚えている「キーと値のセット」。アプリはこれを読んで設定として使います。")
    h(doc, "18.1 例", level=2)
    tbl(doc, [
        ["変数", "意味"],
        ["PATH", "コマンドを探しに行くフォルダのリスト"],
        ["USERNAME", "ログイン中のユーザー名"],
        ["TEMP", "一時ファイル置き場"],
        ["JWT_SECRET", "本 PJ で JWT 署名に使う秘密文字列"],
    ])
    h(doc, "18.2 設定方法", level=2)
    code(doc,
         "# その PowerShell セッションだけに有効\n"
         "$env:MY_KEY = \"value\"\n\n"
         "# 永続化 (Windows の GUI でも可)\n"
         "[System.Environment]::SetEnvironmentVariable(\"MY_KEY\", \"value\", \"User\")",
         lang="PowerShell")

    chap(doc, "19", "ポート番号の概念")
    p(doc,
      "ポート = 1 台のコンピュータの中で「どのサービスへの通信か」を区別する番号（0-65535）。"
      "本 PJ では:")
    tbl(doc, [
        ["ポート", "サービス", "URL 例"],
        ["3001", "frontend", "http://localhost:3001/"],
        ["3000", "api-gateway", "http://localhost:3000/health"],
        ["8000", "ai-service", "http://localhost:8000/health"],
        ["8081", "user-service", "http://localhost:8081/health"],
        ["8082", "item-service", "http://localhost:8082/health"],
        ["5432", "PostgreSQL", "—"],
        ["6379", "Redis", "—"],
    ])
    warn(doc, "ポート衝突に注意",
         "別のアプリが既に同じポートを使っていると起動失敗します。"
         "対処: そのアプリを終了する or infra/.env でポート番号を変更。")

    chap(doc, "20", "IP アドレスと URL")
    p(doc, "URL = http://localhost:3001/ja/search のような Web アドレス。"
           "分解すると以下:")
    tbl(doc, [
        ["パート", "例", "意味"],
        ["スキーム", "http", "通信プロトコル（https = 暗号化）"],
        ["ホスト", "localhost", "通信相手。localhost = 自分自身"],
        ["ポート", "3001", "ホスト内のサービス番号"],
        ["パス", "/ja/search", "リソースの場所"],
    ])
    p(doc, "localhost = 127.0.0.1 = 自分自身のコンピュータ。本 PJ では全部 localhost で完結。")


def part3_software(doc):
    part_cover(
        doc, "3",
        "必要なソフトウェアを準備する",
        "Docker・Git・Python・Node・Java・VS Code — 道具を 1 つずつ揃え、\n"
        "それぞれが何のためにあるかも理解します。",
    )

    chap(doc, "21", "Docker とは")
    h(doc, "21.1 一言で言うと", level=2)
    p(doc,
      "Docker = アプリと「動かすのに必要な OS・ライブラリ・設定」を 1 つの箱（コンテナ）に詰めて、"
      "どの PC でも同じように動かす技術。")
    h(doc, "21.2 なぜ便利か", level=2)
    bul(doc, "「自分のマシンでは動くのに、人のマシンでは動かない」を撲滅")
    bul(doc, "Python 3.12 / Node 20 / Java 21 を同じ PC に共存させなくて済む")
    bul(doc, "プロジェクト全部を docker compose up 1 発で起動")
    bul(doc, "終わったら docker compose down で完全に消せる（PC を汚さない）")
    h(doc, "21.3 イメージ・コンテナ・ボリューム", level=2)
    tbl(doc, [
        ["用語", "例え", "本 PJ での例"],
        ["イメージ (Image)", "弁当のレシピ", "infra-ai-service:latest"],
        ["コンテナ (Container)", "実際に詰めた弁当", "reco-ai-service"],
        ["ボリューム (Volume)", "別売の保存タッパー", "reco-postgres-data"],
        ["ネットワーク", "弁当配送経路", "reco-net"],
    ])

    chap(doc, "22", "Docker Desktop のインストール")
    num(doc, "https://www.docker.com/products/docker-desktop/ を開く")
    num(doc, "「Download for Windows」をクリック")
    num(doc, "ダウンロードした Docker Desktop Installer.exe をダブルクリック")
    num(doc, "WSL 2 が必要との表示が出たら指示に従う（Windows 10/11 の機能）")
    num(doc, "再起動を求められたら従う")
    num(doc, "起動して「Engine running」になったら準備完了")
    h(doc, "22.1 動作確認", level=2)
    code(doc,
         "docker --version\n"
         "# Docker version 28.x.x, build xxxxx と出れば OK\n\n"
         "docker ps\n"
         "# 何も走っていなければ空のテーブルが出る",
         lang="PowerShell")

    chap(doc, "23", "Docker の基本コマンド")
    tbl(doc, [
        ["コマンド", "意味"],
        ["docker images", "ローカルに保存されているイメージ一覧"],
        ["docker ps", "起動中コンテナ一覧"],
        ["docker ps -a", "停止中も含めて全コンテナ"],
        ["docker logs <name>", "コンテナのログ"],
        ["docker logs -f <name>", "ログをリアルタイム表示"],
        ["docker exec -it <name> bash", "コンテナの中に入る"],
        ["docker stop <name>", "コンテナ停止"],
        ["docker rm <name>", "コンテナ削除"],
        ["docker rmi <image>", "イメージ削除"],
        ["docker system df", "ディスク使用状況"],
        ["docker system prune", "不要データ削除（要確認）"],
    ])

    chap(doc, "24", "イメージとコンテナの違い")
    p(doc,
      "イメージ = 不変のスナップショット。Dockerfile からビルドされる。"
      "コンテナ = イメージから起動した実行インスタンス。1 イメージから複数コンテナを起動可能。")
    code(doc,
         "# nginx:alpine イメージから 3 つコンテナを起動\n"
         "docker run -d --name web1 -p 8081:80 nginx:alpine\n"
         "docker run -d --name web2 -p 8082:80 nginx:alpine\n"
         "docker run -d --name web3 -p 8083:80 nginx:alpine\n\n"
         "# 各々独立に動くので 3 つの異なるサーバとして使える\n"
         "docker ps  # 3 コンテナ表示",
         lang="PowerShell")

    chap(doc, "25", "docker-compose とは")
    p(doc,
      "docker-compose = 複数コンテナの起動を 1 つの YAML ファイル（docker-compose.yml）で管理するツール。"
      "本 PJ は 7 コンテナ（postgres, redis, frontend, api-gateway, user-service, item-service, ai-service）を 1 ファイルで定義。")
    code(doc,
         "# 起動\n"
         "docker compose -f infra/docker-compose.yml up -d\n\n"
         "# 状態\n"
         "docker compose -f infra/docker-compose.yml ps\n\n"
         "# 停止\n"
         "docker compose -f infra/docker-compose.yml down\n\n"
         "# データも消す（破壊的）\n"
         "docker compose -f infra/docker-compose.yml down -v",
         lang="PowerShell")

    chap(doc, "26", "Git とは")
    p(doc, "Git = ファイルのバージョンを記録するツール。「いつ・誰が・何を変えたか」を全部追える。"
           "Microsoft Word の「変更履歴」を全プロジェクトに対して、サーバ経由で複数人共有可能な強化版と思えば近い。")
    h(doc, "26.1 概念", level=2)
    tbl(doc, [
        ["用語", "意味"],
        ["リポジトリ (repository / repo)", "Git で管理されているフォルダ全体"],
        ["コミット (commit)", "変更の保存点（スナップショット）"],
        ["ブランチ (branch)", "並行作業用の系譜"],
        ["main", "正本のブランチ"],
        ["マージ (merge)", "ブランチを別ブランチに取り込む"],
        ["push", "ローカル変更をサーバに送る"],
        ["pull", "サーバから最新を取得"],
        ["clone", "サーバからリポジトリ全体をコピー"],
    ])

    chap(doc, "27", "Git のインストール")
    num(doc, "https://git-scm.com/download/win を開く")
    num(doc, "Setup を実行。質問項目はほぼデフォルト OK")
    num(doc, "「Default editor」だけ慣れたエディタ（VS Code 等）に変更しても良い")
    num(doc, "完了後 PowerShell で動作確認")
    code(doc, "git --version\n# git version 2.xx.x  と出れば OK", lang="PowerShell")
    h(doc, "27.1 初期設定（必須）", level=2)
    code(doc,
         "git config --global user.name \"Your Name\"\n"
         "git config --global user.email \"you@example.com\"\n"
         "git config --global init.defaultBranch main\n"
         "git config --global core.autocrlf true   # Windows のみ",
         lang="PowerShell")

    chap(doc, "28", "GitHub アカウントの作成")
    num(doc, "https://github.com/signup でアカウント作成")
    num(doc, "メール確認")
    num(doc, "プロフィール設定（任意）")
    num(doc, "Personal Access Token (PAT) を作成（push に使う）: Settings → Developer settings → PATs")
    num(doc, "Token は 1 度しか表示されないので必ず保管")
    h(doc, "28.1 GitHub CLI (gh) の導入", level=2)
    p(doc, "PR の作成・マージを CLI で行う gh CLI も入れておくと便利:")
    code(doc, "# Windows (winget)\nwinget install --id GitHub.cli\n\n# 認証\ngh auth login",
         lang="PowerShell")

    chap(doc, "29", "リポジトリの取得 (clone)")
    code(doc,
         "# 開発フォルダに移動\n"
         "cd d:\\DEV\\personal-projects\n\n"
         "# clone\n"
         "git clone https://github.com/Litch9x/RecoForeJP.git\n\n"
         "# 中に入る\n"
         "cd RecoForeJP\n\n"
         "# 中身を確認\n"
         "ls",
         lang="PowerShell")

    chap(doc, "30", "Git の基本コマンド")
    tbl(doc, [
        ["コマンド", "意味"],
        ["git status", "今の状態"],
        ["git add <file>", "コミット対象に追加"],
        ["git add .", "全変更を追加"],
        ["git commit -m \"msg\"", "コミット作成"],
        ["git push", "サーバに送信"],
        ["git pull", "サーバから取得"],
        ["git branch", "ブランチ一覧"],
        ["git checkout -b new", "新ブランチ作成 + 移動"],
        ["git checkout main", "main に切替"],
        ["git log --oneline", "コミット履歴（1 行ずつ）"],
        ["git diff", "未コミット差分"],
        ["git diff --cached", "ステージ済み差分"],
    ])

    chap(doc, "31", "Python とは")
    p(doc, "Python = 1991 年から続く汎用プログラミング言語。"
           "AI/データ分析でデファクト。本 PJ では ai-service と scripts/ で使用。")
    h(doc, "31.1 特徴", level=2)
    bul(doc, "読みやすい（インデントで構造を表す）")
    bul(doc, "ライブラリが豊富（pip で簡単に追加）")
    bul(doc, "実行が比較的遅い（が、I/O 系の Web API なら問題なし）")

    chap(doc, "32", "Python のインストール")
    num(doc, "https://www.python.org/downloads/ から最新の 3.12.x を取得")
    num(doc, "インストーラ起動時「Add python.exe to PATH」に必ずチェック")
    num(doc, "Install Now")
    num(doc, "確認: python --version で 3.12.x が出れば OK")
    h(doc, "32.1 pip でパッケージ追加", level=2)
    code(doc, "pip install python-docx\npip install pytest", lang="PowerShell")
    h(doc, "32.2 仮想環境 (venv)", level=2)
    p(doc, "プロジェクトごとに依存を隔離するための仕組み。本 PJ では ai-service 内で使用。")
    code(doc,
         "cd ai-service\n"
         "python -m venv .venv\n"
         ".venv\\Scripts\\Activate.ps1     # 有効化\n"
         "pip install -e \".[ml,dev]\"\n"
         "deactivate                       # 終了",
         lang="PowerShell")

    chap(doc, "33", "Node.js（任意）")
    p(doc, "frontend / api-gateway を Docker なしで直接動かしたいときに必要。")
    num(doc, "https://nodejs.org/ から LTS (20.x or 22.x) を取得")
    num(doc, "インストーラはデフォルトで OK")
    num(doc, "確認: node --version / npm --version")

    chap(doc, "34", "VS Code（任意だがおすすめ）")
    p(doc, "コード閲覧・編集に最適なエディタ。無料・拡張機能豊富。")
    num(doc, "https://code.visualstudio.com/ からダウンロード")
    num(doc, "インストーラの「右クリックメニューに追加」「PATH に追加」全てチェック推奨")
    h(doc, "34.1 入れておくべき拡張機能", level=2)
    bul(doc, "Python (Microsoft)")
    bul(doc, "ESLint")
    bul(doc, "Prettier")
    bul(doc, "Docker (Microsoft)")
    bul(doc, "GitLens")
    bul(doc, "Code Spell Checker")
    bul(doc, "Japanese Language Pack")

    chap(doc, "35", "環境の動作確認")
    code(doc,
         "# 全部入っていれば全コマンドが version を出す\n"
         "git --version\n"
         "docker --version\n"
         "python --version\n"
         "node --version          # 任意\n"
         "code --version          # 任意",
         lang="PowerShell")
    callout(doc, "全部入った? おめでとう",
            "ここまで来れば、第 4 部からプロジェクトを実際に動かせます。"
            "もし何か入らなかった場合も、最低 Docker と Git があれば本 PJ は動かせます。")


def part4_get_project(doc):
    part_cover(
        doc, "4",
        "プロジェクトを取得して中身を覗く",
        "コードに触れる前に、フォルダ構造・設定ファイル・README を一通り眺めて、\n"
        "全体地図を頭に入れます。",
    )

    chap(doc, "36", "GitHub からダウンロードする 2 つの方法")
    h(doc, "36.1 git clone（推奨）", level=2)
    code(doc, "git clone https://github.com/Litch9x/RecoForeJP.git", lang="PowerShell")
    h(doc, "36.2 ZIP ダウンロード", level=2)
    num(doc, "https://github.com/Litch9x/RecoForeJP を開く")
    num(doc, "緑色の「Code」ボタン → Download ZIP")
    num(doc, "ZIP を展開")
    p(doc, "違い: clone なら git pull で更新できるが、ZIP は再ダウンロードが必要。")

    chap(doc, "37", "フォルダ構成を見る")
    code(doc,
         "RecoForeJP/\n"
         "├─ frontend/             画面 (Next.js)\n"
         "├─ api-gateway/          受付 (NestJS)\n"
         "├─ user-service/         ユーザー管理 (Spring Boot)\n"
         "├─ item-service/         アイテム管理 (Spring Boot)\n"
         "├─ ai-service/           AI 部分 (FastAPI)\n"
         "├─ infra/                Docker / DB 初期化\n"
         "├─ docs/                 ドキュメント類（本書もここ）\n"
         "├─ scripts/              便利 Python ツール\n"
         "├─ .gitignore            Git で無視するファイル一覧\n"
         "├─ .pre-commit-config.yaml  コミット前自動整形設定\n"
         "└─ README.md             プロジェクト概要",
         lang="tree")
    p(doc, "サービスごとにフォルダを分けることで、サービス境界が物理的に明確になります。")

    chap(doc, "38", "README.md を読む")
    p(doc, "README はプロジェクトの「顔」。最初に読むべき文書。")
    p(doc, "本 PJ の README に書かれていること:")
    bul(doc, "プロジェクトの目的")
    bul(doc, "アーキ図（ASCII）")
    bul(doc, "サービス一覧表")
    bul(doc, "起動手順（docker compose up + seed_embeddings.py）")
    bul(doc, "各サービスの単独起動方法")
    bul(doc, "テストの走らせ方")

    chap(doc, "39", ".env ファイルを作る")
    p(doc, "infra/.env.example をコピーして infra/.env を作ります。"
           ".env は環境変数を書く場所。docker-compose が読み込む。")
    code(doc, "copy infra\\.env.example infra\\.env", lang="PowerShell")
    h(doc, "39.1 .env の中身（コピーされた直後）", level=2)
    code(doc,
         "POSTGRES_USER=reco\n"
         "POSTGRES_PASSWORD=reco_password\n"
         "JWT_SECRET=dev-only-change-in-prod\n"
         "JWT_EXPIRES_IN_SECONDS=3600\n"
         "...",
         lang=".env")
    warn(doc, ".env を Git にコミットしない",
         ".env はパスワードや API キーを書く場所。誤って GitHub に push すると公開されてしまいます。"
         ".gitignore に .env が入っているので普段は安全ですが、念のため git status で確認する習慣を。")

    chap(doc, "40", "docker-compose.yml の中身を眺める")
    p(doc, "infra/docker-compose.yml を VS Code で開いてみましょう。")
    p(doc, "見るべきポイント:")
    bul(doc, "services: の下に 7 サービス定義")
    bul(doc, "各 service の build: でビルドコンテキスト指定")
    bul(doc, "environment: で環境変数注入")
    bul(doc, "depends_on: で起動順制御")
    bul(doc, "healthcheck: で健康診断方法")
    bul(doc, "networks: で reco-net を共有")

    chap(doc, "41", "各サービスのフォルダを覗く")
    h(doc, "41.1 frontend/", level=2)
    code(doc,
         "frontend/\n"
         "├─ src/\n"
         "│  ├─ app/[lang]/            言語切替対応ページ\n"
         "│  ├─ app/api/               サーバープロキシ\n"
         "│  ├─ components/            React UI\n"
         "│  ├─ lib/                   汎用ヘルパ\n"
         "│  ├─ i18n/                  辞書\n"
         "│  └─ proxy.ts               locale 振り分け\n"
         "├─ package.json\n"
         "├─ next.config.ts\n"
         "└─ Dockerfile",
         lang="tree")
    h(doc, "41.2 api-gateway/", level=2)
    code(doc,
         "api-gateway/\n"
         "├─ src/\n"
         "│  ├─ auth/                  JWT 発行 + ガード\n"
         "│  ├─ me/                    /me/* プロキシ\n"
         "│  ├─ admin/                 /admin/* プロキシ + RBAC\n"
         "│  ├─ ai-proxy/              /search /recommend\n"
         "│  └─ app.module.ts\n"
         "├─ package.json\n"
         "└─ Dockerfile",
         lang="tree")
    h(doc, "41.3 ai-service/", level=2)
    code(doc,
         "ai-service/\n"
         "├─ src/ai_service/\n"
         "│  ├─ embedding/             encoder + store\n"
         "│  ├─ recommend/             scorer + hybrid\n"
         "│  ├─ llm/                   explain\n"
         "│  ├─ eval/                  metrics\n"
         "│  └─ main.py\n"
         "├─ tests/\n"
         "├─ pyproject.toml\n"
         "└─ Dockerfile",
         lang="tree")

    chap(doc, "42", "docs/ フォルダの中身")
    tbl(doc, [
        ["ファイル", "内容"],
        ["RecoForeJP.docx", "卒論目次（既存）"],
        ["RecoForeJP.pptx", "発表スライド雛形"],
        ["完全ガイド.docx", "技術リファレンス"],
        ["開発履歴.docx", "16 フェーズの時系列ジャーニー"],
        ["完全教科書.docx", "本書（500+ ページ教科書）"],
        ["schema/README.md", "DB ER 図"],
        ["schema/schema.dbml", "DBML 版スキーマ"],
        ["schema/sample-ddl.sql", "DDL 例"],
    ])

    chap(doc, "43", "scripts/ フォルダの中身")
    tbl(doc, [
        ["ファイル", "用途"],
        ["seed_embeddings.py", "アイテム埋め込みを一括登録"],
        ["eval_recommendations.py", "オフライン推薦評価"],
        ["setup_jira.py", "Jira に Epic/Story を一括作成"],
        ["list_jira.py", "Jira の Issue 一覧表示"],
        ["update_jira_architecture.py", "Jira アーキ変更スクリプト"],
        ["generate_dev_guide.py", "開発ガイド docx 生成"],
        ["generate_project_history.py", "開発履歴 docx 生成"],
        ["generate_complete_guide.py", "完全ガイド docx 生成"],
        ["generate_full_textbook.py", "本書 docx 生成（このスクリプト）"],
    ])

    chap(doc, "44", "infra/ フォルダの中身")
    tbl(doc, [
        ["ファイル", "用途"],
        ["docker-compose.yml", "7 サービスの起動定義"],
        [".env.example", "環境変数サンプル"],
        ["postgres/init/01-extensions.sql", "pgvector 拡張"],
        ["postgres/init/02-schemas.sql", "3 schema 作成"],
        ["postgres/init/03-users-schema.sql", "users テーブル定義"],
        ["postgres/init/04-items-schema.sql", "items テーブル定義"],
        ["postgres/init/05-ai-schema.sql", "ai テーブル定義 + HNSW index"],
        ["postgres/init/10-12-seed-*.sql", "シードデータ"],
    ])

    chap(doc, "45", "ファイル変更の検出方法")
    code(doc,
         "git status            # 変更ファイル一覧\n"
         "git diff              # 差分を見る\n"
         "git diff <file>       # 特定ファイルのみ\n"
         "git log -p <file>     # そのファイルの履歴 + 差分",
         lang="PowerShell")
    callout(doc, "VS Code で見るのが楽",
            "VS Code 左サイドバーの「ソース管理」アイコンをクリックすると、"
            "変更ファイルと差分が視覚的に見られます。")


def part5_first_run(doc):
    part_cover(
        doc, "5",
        "最初の起動",
        "ついに docker compose up を打ち、5 つのサービスが連携して動く瞬間を体験します。\n"
        "起動の各段階で何が起きているかも追います。",
    )

    chap(doc, "46", "docker compose up を実行する")
    code(doc,
         "# プロジェクトのルートで実行\n"
         "cd d:\\DEV\\personal-projects\\RecoForeJP\n\n"
         "# 起動（バックグラウンド + ビルド）\n"
         "docker compose -f infra/docker-compose.yml up -d --build",
         lang="PowerShell")
    h(doc, "46.1 各オプションの意味", level=2)
    bul(doc, "-f infra/docker-compose.yml : 設定ファイルの場所を指定")
    bul(doc, "up : 起動")
    bul(doc, "-d : デタッチ（バックグラウンド）")
    bul(doc, "--build : 必要ならイメージを再ビルド")

    chap(doc, "47", "ビルド中に何が起きているか")
    p(doc, "初回起動では各 Dockerfile に書かれた手順を実行してイメージを作ります。"
           "順番に何が走るか:")
    num(doc, "ベースイメージを Docker Hub からダウンロード（node:alpine, python:slim 等）")
    num(doc, "ベース上で各サービスの依存をインストール（npm install / pip install / gradle build）")
    num(doc, "アプリケーションコードを COPY")
    num(doc, "イメージとして保存（infra-frontend, infra-api-gateway 等）")
    num(doc, "イメージからコンテナを起動")
    num(doc, "depends_on の順に各サービスが起動")
    num(doc, "healthcheck が定期実行される")
    callout(doc, "初回は 10 分くらいかかる",
            "ai-service が torch (~800MB) をダウンロード + インストールするのが最重い。"
            "2 回目以降はキャッシュが効いて数秒で起動。")

    chap(doc, "48", "起動完了の確認方法")
    code(doc, "docker compose -f infra/docker-compose.yml ps", lang="PowerShell")
    p(doc, "7 行表示され、全部「healthy」「Up」になれば成功。「unhealthy」が残っていれば次章で原因調査。")

    chap(doc, "49", "ヘルスチェックとは")
    p(doc,
      "ヘルスチェック = コンテナが「ちゃんと動いているか」を Docker が定期的に確認する仕組み。"
      "各サービスは内部で wget --tries=1 -O /dev/null http://localhost:PORT/health を実行し、200 が返れば healthy。")
    h(doc, "49.1 ヘルスチェックの状態", level=2)
    tbl(doc, [
        ["状態", "意味"],
        ["healthy", "OK"],
        ["unhealthy", "失敗が連続"],
        ["starting", "start_period 中（まだ未判定）"],
    ])

    chap(doc, "50", "ブラウザで開いてみる")
    p(doc, "http://localhost:3001/ にアクセス → ランディングページが表示されれば成功。")
    h(doc, "50.1 何も表示されない場合", level=2)
    bul(doc, "Docker Desktop が起動しているか（タスクトレイのクジラアイコン）")
    bul(doc, "docker compose ps で frontend が healthy になっているか")
    bul(doc, "ポート 3001 が他のアプリで使われていないか")
    bul(doc, "「localhost」ではなく「127.0.0.1:3001」で試す")

    chap(doc, "51", "自動言語切替の仕組み")
    p(doc,
      "/（ルート）にアクセスすると proxy.ts がブラウザの Accept-Language ヘッダを読み、"
      "ja を含めば /ja に、それ以外（en 等）なら /en にリダイレクトします。")
    code(doc,
         "# 確認方法\n"
         "curl -sI http://localhost:3001/ -H \"Accept-Language: en\"\n"
         "# → location: /en\n\n"
         "curl -sI http://localhost:3001/ -H \"Accept-Language: ja\"\n"
         "# → location: /ja",
         lang="PowerShell")

    chap(doc, "52", "ランディングページの説明")
    p(doc, "ランディングページに表示される内容:")
    bul(doc, "ヘッダ: アプリ名 + 言語切替 + ログイン状態")
    bul(doc, "タグライン: 在日外国人向け推薦システム")
    bul(doc, "サービス構成リスト: 5 つのマイクロサービスの説明")
    bul(doc, "画面リンク: /recommendations, /search, /api/health")

    chap(doc, "53", "ナビゲーションを試す")
    p(doc, "ランディングから各画面に飛んでみる:")
    bul(doc, "「/ja/recommendations」リンク → 推薦画面")
    bul(doc, "「/ja/search」リンク → 検索画面")
    bul(doc, "「/api/health」リンク → JSON が表示される")
    bul(doc, "ヘッダの「JA / EN」ボタン → 言語切替（同じパスのまま）")
    bul(doc, "ヘッダの「ログイン」 → /ja/login へ")

    chap(doc, "54", "起動失敗時のチェックリスト")
    tbl(doc, [
        ["症状", "確認手順"],
        ["docker compose ps が空", "docker compose up -d --build を再実行"],
        ["frontend が unhealthy", "docker logs reco-frontend でログ確認"],
        ["ai-service が unhealthy", "torch DL 中 → 数分待つ"],
        ["ポートエラー", "別アプリを止める or .env でポート変更"],
        ["DB 接続エラー", "postgres が先に healthy か確認"],
    ])

    chap(doc, "55", "停止と再起動")
    code(doc,
         "# 停止（データは残す）\n"
         "docker compose -f infra/docker-compose.yml down\n\n"
         "# 再起動\n"
         "docker compose -f infra/docker-compose.yml up -d\n\n"
         "# 1 サービスだけ再起動\n"
         "docker compose -f infra/docker-compose.yml restart ai-service\n\n"
         "# DB データも消す（破壊的）\n"
         "docker compose -f infra/docker-compose.yml down -v",
         lang="PowerShell")


def part6_use_features(doc):
    part_cover(
        doc, "6",
        "各機能を 1 つずつ試す",
        "意味検索・ハイブリッド推薦・ログイン・管理画面 — 全 6 機能を順番に体験し、\n"
        "それぞれの裏で何が起きているか覗きながら理解します。",
    )

    chap(doc, "56", "意味検索を試す（日本語）")
    p(doc, "http://localhost:3001/ja/search を開く")
    num(doc, "「ベトナム語で働けるカスタマーサポート」をクエリ欄に入力")
    num(doc, "「意味検索を実行」ボタンをクリック")
    num(doc, "上位 10 件の検索結果が表示される")
    num(doc, "各結果の右上に「similarity」（類似度 0-1）が表示")
    num(doc, "上位は「ベトナム語話者向け CS」になるはず（sim=0.9 以上）")
    h(doc, "56.1 サンプルボタンを試す", level=2)
    p(doc, "クエリ欄の下に 4 つのサンプルボタンがあるのでクリックで試せる:")
    bul(doc, "ベトナム語で働けるカスタマーサポート")
    bul(doc, "英語 OK の IT エンジニア")
    bul(doc, "外国人向けの病院 東京")
    bul(doc, "やさしい日本語のクラス")

    chap(doc, "57", "意味検索を試す（英語）")
    p(doc, "http://localhost:3001/en/search を開く（言語切替の力を確認）")
    num(doc, "「customer support that uses Vietnamese」を入力")
    num(doc, "実行 → 上位は「ベトナム語話者向け CS（日本語タイトル）」")
    p(doc, "これが **多言語埋め込み** の威力。英語クエリと日本語タイトルが意味的に近いと判断される。")
    h(doc, "57.1 さらに試す", level=2)
    bul(doc, "「medical care with English support」→ 英語対応病院（港区）")
    bul(doc, "「easy Japanese class for beginners」→ やさしい日本語クラス")
    bul(doc, "「shared house for foreigners」→ シェアハウス横浜")

    chap(doc, "58", "検索結果の読み方")
    tbl(doc, [
        ["項目", "意味"],
        ["#1, #2, ...", "順位"],
        ["タイトル", "アイテム名"],
        ["item_id", "DB 上の一意 ID（UUID）"],
        ["similarity", "コサイン類似度（1 に近いほど似ている、本 PJ では 0.6+ が実用範囲）"],
    ])
    callout(doc, "similarity の目安",
            "0.9+: 強く一致 / 0.8-0.9: 関連 / 0.7-0.8: 弱い関連 / 0.7 未満: ほぼ無関係")

    chap(doc, "59", "ハイブリッド推薦を試す")
    p(doc, "http://localhost:3001/ja/recommendations を開く")
    num(doc, "日本語レベルを N3 に")
    num(doc, "居住地域に「東京都-新宿区」と入力")
    num(doc, "興味カテゴリで「就職」と「日本語学習」を選択")
    num(doc, "自然言語クエリは「やさしい日本語で仕事を探したい」")
    num(doc, "content と semantic の重みは 0.5 / 0.5 のまま")
    num(doc, "「推薦を取得」をクリック")
    num(doc, "上位 5-10 件が表示。各結果に hybrid / content / semantic スコアと reasons")

    chap(doc, "60", "推薦パラメータを変えてみる")
    p(doc, "重みスライダを動かして結果がどう変わるか観察:")
    tbl(doc, [
        ["条件", "結果の傾向"],
        ["content=1.0, semantic=0.0", "属性マッチが支配的（地域 / 興味）"],
        ["content=0.0, semantic=1.0", "クエリの意味が支配的"],
        ["content=0.5, semantic=0.5", "両者バランス（推奨）"],
        ["content=0.8, semantic=0.2", "属性重視"],
    ])

    chap(doc, "61", "推薦の reason を読む")
    p(doc, "各推薦結果には「なぜこのアイテムを選んだか」の reasons が表示されます。例:")
    code(doc,
         "やさしい日本語クラス（無料・新宿区）\n"
         "  hybrid=0.939  content=1.00  semantic=0.879\n"
         "  reasons:\n"
         "    - same region (東京都-新宿区)\n"
         "    - available in ja",
         lang="例")
    p(doc, "reasons は ai-service の scorer.py がスコアを計算する過程で記録した「マッチ理由」。卒論で説明性として活用できる素材。")

    chap(doc, "62", "シードユーザーで初ログイン")
    p(doc, "http://localhost:3001/ja/login を開く")
    num(doc, "メール: nguyen.student@example.com")
    num(doc, "パスワード: password123")
    num(doc, "ログインボタン")
    num(doc, "成功すれば /ja/me に自動遷移")
    num(doc, "右上に「ログイン中: nguyen.student@example.com」表示")
    h(doc, "62.1 失敗するとき", level=2)
    bul(doc, "401 → パスワード間違い or メールが違う")
    bul(doc, "502 → api-gateway か user-service が down")
    bul(doc, "「サーバーに接続できませんでした」→ Docker 全部止まってる")

    chap(doc, "63", "ログアウトする")
    p(doc, "右上「ログアウト」ボタンをクリック。"
           "クライアントの localStorage から JWT が消去され、未認証状態に戻る。")
    callout(doc, "セッション切れ",
            "JWT の有効期限は 1 時間（infra/.env の JWT_EXPIRES_IN_SECONDS）。"
            "1 時間後にページをリロードすると自動的にログアウト状態になる。")

    chap(doc, "64", "マイページを見る")
    p(doc, "/ja/me ではログイン中ユーザーのプロフィールが表示される:")
    bul(doc, "ユーザー ID（UUID）")
    bul(doc, "メールアドレス")
    bul(doc, "日本語能力（JLPT レベル）")
    bul(doc, "地域")
    bul(doc, "興味")
    p(doc, "裏では JWT を Authorization ヘッダに付けて /api/auth/me → api-gateway /me/profile → user-service /users/{sub}/profile を呼んでいる。")

    chap(doc, "65", "ADMIN でログイン")
    p(doc, "wang.resident@example.com / password123 でログイン →"
           "右上に「管理」ボタンが現れる（ADMIN ロール限定 UI）")

    chap(doc, "66", "管理画面でアイテム追加")
    p(doc, "「管理」→ /ja/admin/items へ")
    num(doc, "14 件の既存アイテム一覧が表示")
    num(doc, "下の「新規アイテム追加」フォームで入力")
    num(doc, "カテゴリ slug: job（または housing, admin, medical, japanese-learning, community）")
    num(doc, "タイトル: 「ベトナム語サポートの IT エンジニア募集」")
    num(doc, "説明: 「新宿、外国人歓迎、リモート可」")
    num(doc, "地域: 「東京都-新宿区」")
    num(doc, "languages: 「ja, en, vi」")
    num(doc, "tags: 「foreigner-welcome, remote」")
    num(doc, "「追加」ボタン → 一覧に追加され、AI が自動で埋め込み生成")

    chap(doc, "67", "追加直後の検索確認")
    p(doc, "/ja/search に移動して「ベトナム IT」で検索。さっき追加したアイテムが top1 に来るはず。")
    callout(doc, "自動埋め込みの確認",
            "api-gateway の AdminItemsService が POST 成功直後に ai-service の "
            "POST /embeddings/items/{id} を呼んでいる。docker logs reco-api-gateway で確認可能。")

    chap(doc, "68", "管理画面でアイテム削除")
    num(doc, "/ja/admin/items の一覧で行右端の「削除」ボタン")
    num(doc, "確認ダイアログが出る → OK")
    num(doc, "DB から消える + 一覧から消える")
    callout(doc, "ai.item_embeddings は残る",
            "削除しても ai.item_embeddings レコードは残ります（孤立 embedding）。"
            "検索結果には items テーブルに無い ID は出ないので無害。"
            "将来的に ai-service に DELETE /embeddings/items/{id} を追加して掃除する予定。")

    chap(doc, "69", "言語切替を試す")
    p(doc, "右上「EN」ボタン → そのページの英語版にジャンプ")
    bul(doc, "/ja/search → /en/search")
    bul(doc, "/ja/admin/items → /en/admin/items")
    bul(doc, "全画面の文言が英語に変わる")

    chap(doc, "70", "全画面の総まとめ")
    tbl(doc, [
        ["URL", "機能", "認証"],
        ["/ja", "ランディング", "不要"],
        ["/ja/search", "意味検索", "不要"],
        ["/ja/recommendations", "ハイブリッド推薦", "不要"],
        ["/ja/login", "ログインフォーム", "不要"],
        ["/ja/me", "プロフィール表示", "ログイン必須"],
        ["/ja/admin/items", "アイテム管理", "ADMIN 必須"],
        ["/api/health", "ヘルスチェック JSON", "不要"],
    ])


def part7_internals(doc):
    part_cover(
        doc, "7",
        "中の仕組みを覗く",
        "5 サービスがどう連携して 1 つのリクエストを処理するか。\n"
        "JWT・埋め込み・コサイン類似度の理論的背景にも触れます。",
    )

    chap(doc, "71", "マイクロサービスの考え方")
    h(doc, "71.1 モノリス vs マイクロサービス", level=2)
    tbl(doc, [
        ["", "モノリス", "マイクロサービス"],
        ["構成", "1 つの大きなアプリ", "複数の小さなアプリ"],
        ["デプロイ", "全部一緒に", "サービスごとに独立"],
        ["スケール", "全体を増やすしかない", "重い部分だけ増やせる"],
        ["失敗影響", "全部止まる", "1 サービスのみ"],
        ["開発", "シンプル", "通信オーバーヘッド"],
    ])
    h(doc, "71.2 本 PJ の選択理由", level=2)
    bul(doc, "Python (AI) と Java (Spring) と TypeScript (Web) を共存させたい")
    bul(doc, "論文の §3.5.2 で「マイクロサービスアーキテクチャ」を提案している")
    bul(doc, "卒論として「マイクロサービス + AI」の知見を残せる")

    chap(doc, "72", "frontend の役割")
    p(doc, "frontend が担うこと:")
    bul(doc, "ブラウザに表示する HTML/CSS/JS を返す")
    bul(doc, "ユーザー操作を受け取り API に送る")
    bul(doc, "JWT を localStorage に保管")
    bul(doc, "言語切替（i18n）")
    bul(doc, "/api/* で api-gateway へのサーバ側プロキシ（CORS 回避）")
    h(doc, "72.1 Next.js App Router", level=2)
    p(doc,
      "Next.js 16 の App Router は React Server Components ベース。"
      "「ページ = サーバ + クライアント」のハイブリッド。"
      "[lang]/page.tsx はサーバで動き、'use client' 付きはブラウザで動く。")

    chap(doc, "73", "api-gateway の役割")
    bul(doc, "全 HTTP リクエストの入口")
    bul(doc, "JWT 検証・発行")
    bul(doc, "ロール（RBAC）チェック")
    bul(doc, "各サービスへのプロキシ")
    bul(doc, "将来: rate limit, log, metrics の挿入点")
    h(doc, "73.1 NestJS Module 構成", level=2)
    code(doc,
         "AppModule\n"
         "├─ ConfigModule       # 環境変数\n"
         "├─ HealthModule       # /health\n"
         "├─ AuthModule         # /auth/login\n"
         "├─ MeModule           # /me/*\n"
         "├─ AdminModule        # /admin/*\n"
         "└─ AiProxyModule      # /search, /recommend",
         lang="tree")

    chap(doc, "74", "user-service の役割")
    bul(doc, "POST /users : ユーザー登録（bcrypt でパスワードハッシュ）")
    bul(doc, "GET/PUT /users/{id}/profile : プロフィール")
    bul(doc, "GET/PUT /users/{id}/preferences : 設定")
    bul(doc, "POST /internal/auth/verify : api-gateway 向け認証検証")
    h(doc, "74.1 Spring Boot の基本構成", level=2)
    code(doc,
         "user.User                 エンティティ（@Entity）\n"
         "user.UserRepository       JPA リポジトリ\n"
         "user.UserService          ビジネスロジック\n"
         "user.UserController       REST エンドポイント\n"
         "auth.AuthService          credential verify\n"
         "auth.AuthController       /internal/auth/verify",
         lang="package")

    chap(doc, "75", "item-service の役割")
    bul(doc, "GET/POST /items : アイテム CRUD")
    bul(doc, "GET /categories : カテゴリ一覧（内部用、現状 API なし）")
    bul(doc, "POST /feedbacks : ユーザー行動ログ")
    bul(doc, "GET /feedbacks/by-user/{id}, by-item/{id} : 行動取得")

    chap(doc, "76", "ai-service の役割")
    bul(doc, "POST /embed : テキスト → 384 次元ベクトル")
    bul(doc, "POST /embeddings/items/{id} : ai.item_embeddings に upsert")
    bul(doc, "POST /search/items : クエリベクトルから近い順")
    bul(doc, "POST /recommend : 属性ベースの content-only")
    bul(doc, "POST /recommend/hybrid : content + semantic")
    bul(doc, "POST /explain : LLM 説明（OpenAI optional）")

    chap(doc, "77", "PostgreSQL の役割")
    p(doc, "全データの永続化先。3 schema で論理分離:")
    tbl(doc, [
        ["schema", "保有者", "テーブル数"],
        ["users", "user-service", "4"],
        ["items", "item-service", "6"],
        ["ai", "ai-service", "4"],
    ])
    h(doc, "77.1 pgvector", level=2)
    p(doc, "PostgreSQL 拡張機能。vector(384) 型と <=> （cosine distance）演算子を追加。"
           "HNSW インデックスで近似最近傍検索を高速化。")

    chap(doc, "78", "Redis の役割（将来）")
    p(doc, "現状未使用だが docker-compose には起動済み。今後の用途案:")
    bul(doc, "推薦結果のキャッシュ")
    bul(doc, "セッション管理（JWT 拒否リスト等）")
    bul(doc, "rate limit カウンタ")
    bul(doc, "リアルタイムイベント配信（PubSub）")

    chap(doc, "79", "リクエストの流れを追う（ログイン編）")
    code(doc,
         "1. Browser     : POST /api/auth/login {email, password}\n"
         "2. frontend    : Route Handler が body を取り、api-gateway へ転送\n"
         "3. api-gateway : POST /auth/login\n"
         "4. AuthService : user-service /internal/auth/verify を呼ぶ\n"
         "5. user-service: email で User を検索、bcrypt.matches で照合\n"
         "6. user-service: 200 {userId, email, role}\n"
         "7. AuthService : JWT を発行 (HS256, sub=userId, role claim)\n"
         "8. api-gateway : 200 {accessToken, ...}\n"
         "9. frontend    : 透過\n"
         "10. Browser    : localStorage に保管 → /ja/me へ遷移",
         lang="flow")

    chap(doc, "80", "JWT 認証の仕組み")
    h(doc, "80.1 JWT の構造", level=2)
    p(doc, "JWT は「.」で 3 つに分かれた文字列: header.payload.signature")
    code(doc,
         "header     : {\"alg\":\"HS256\",\"typ\":\"JWT\"}      → Base64 化\n"
         "payload    : {\"sub\":\"u-1\",\"email\":\"...\", \"role\":\"ADMIN\", \"exp\":...}  → Base64 化\n"
         "signature  : HMAC-SHA256(\"header.payload\", JWT_SECRET)  → Base64 化",
         lang="JWT")
    h(doc, "80.2 検証", level=2)
    p(doc,
      "サーバが JWT を受け取ると、header + payload を JWT_SECRET で署名し直して "
      "signature と一致するか確認。一致 = 改ざんなし。"
      "secret を知らない攻撃者は payload を書き換えられない。")

    chap(doc, "81", "RBAC の仕組み")
    p(doc, "RBAC = Role-Based Access Control。ユーザーに「ロール」を割り当て、"
           "ロールごとに使える機能を制限。")
    h(doc, "81.1 本 PJ の RBAC", level=2)
    tbl(doc, [
        ["ロール", "使える機能"],
        ["USER", "ログイン / /me / search / recommend"],
        ["ADMIN", "USER の全機能 + /admin/items"],
    ])
    h(doc, "81.2 実装", level=2)
    bul(doc, "DB: users.users.role カラム（USER | ADMIN）")
    bul(doc, "JWT: payload に role claim")
    bul(doc, "api-gateway: RolesGuard + @Roles(['ADMIN']) デコレータ")
    bul(doc, "frontend: auth.role でメニュー切替（管理リンク表示等）")

    chap(doc, "82", "埋め込みベクトルとは")
    p(doc,
      "テキスト → 数百次元の数値配列に変換する技術。"
      "似た意味の文章は近い座標に配置される。本 PJ は multilingual-e5-small（384 次元）を使用。")
    code(doc,
         "「ベトナム語で働ける仕事」     → [0.12, -0.34, 0.56, ..., 0.78]  (384 個)\n"
         "「customer support in Vietnamese」 → [0.13, -0.33, 0.55, ..., 0.79]  (近い座標)\n"
         "「天気が良いね」               → [-0.45, 0.78, -0.21, ..., -0.12] (遠い座標)",
         lang="概念")

    chap(doc, "83", "コサイン類似度とは")
    p(doc,
      "2 つのベクトル間の「角度の近さ」を測る指標。1 に近いほど方向が一致 = 意味が近い。"
      "0 で無関係、-1 で正反対。本 PJ では 0-1 範囲（正規化済み）を使用。")
    code(doc,
         "cosine(A, B) = (A・B) / (|A| × |B|)\n\n"
         "例:\n"
         "  A = [1, 0, 0]\n"
         "  B = [0.9, 0.1, 0]   → cosine ≈ 0.994 (近い)\n"
         "  C = [0, 1, 0]       → cosine = 0     (直交)\n"
         "  D = [-1, 0, 0]      → cosine = -1    (正反対)",
         lang="math")

    chap(doc, "84", "HNSW インデックスとは")
    p(doc,
      "Hierarchical Navigable Small World = 階層的なグラフ構造でベクトル空間を探索する近似最近傍検索アルゴリズム。"
      "本来 O(N) かかる線形検索を O(log N) に高速化。"
      "「ほぼ最近傍」を返す（厳密ではない）ので「approximate nearest neighbor」と呼ばれる。")
    p(doc, "pgvector 0.5+ で利用可能。本 PJ では ai.item_embeddings.embedding に HNSW (vector_cosine_ops) を張っている。")

    chap(doc, "85", "ハイブリッド推薦の数式")
    code(doc,
         "for each item:\n"
         "    content_score   = scorer(user, item)            # 0-N の生スコア\n"
         "    semantic_score  = cosine(query_vec, item_vec)   # 0-1\n\n"
         "# 正規化\n"
         "max_content = max(content_score for all items)\n"
         "content_norm = content_score / max_content\n\n"
         "# 加重和\n"
         "hybrid_score = wc * content_norm + ws * semantic_score\n"
         "  (wc + ws = 1 を仮定)\n\n"
         "# ランキング\n"
         "sort items by hybrid_score desc",
         lang="pseudo-code")


def part8_db(doc):
    part_cover(
        doc, "8",
        "データを直接覗く",
        "PostgreSQL に SQL で接続し、テーブル定義を見て、データを読み書きします。\n"
        "SQL の基本も最小限カバー。",
    )

    chap(doc, "86", "PostgreSQL に直接接続")
    code(doc,
         "# psql を Docker 経由で実行\n"
         "docker exec -it reco-postgres psql -U reco -d reco\n\n"
         "# プロンプトが reco=> に変わる\n"
         "# \\q で終了",
         lang="PowerShell")

    chap(doc, "87", "全テーブルを見る")
    code(doc,
         "\\dn              -- schema 一覧\n"
         "\\dt users.*      -- users schema のテーブル\n"
         "\\dt items.*      -- items\n"
         "\\dt ai.*         -- ai\n"
         "\\d users.users   -- users.users テーブルの定義",
         lang="psql")

    chap(doc, "88", "ユーザーデータを見る")
    code(doc,
         "SELECT id, email, nationality, role FROM users.users;\n"
         "SELECT user_id, japanese_level, region FROM users.user_profiles;\n"
         "SELECT * FROM users.user_interests;",
         lang="SQL")

    chap(doc, "89", "アイテムデータを見る")
    code(doc,
         "SELECT id, title, region FROM items.items LIMIT 5;\n"
         "SELECT slug, name_ja FROM items.categories;\n"
         "SELECT name FROM items.tags;",
         lang="SQL")

    chap(doc, "90", "埋め込みデータを見る")
    code(doc,
         "-- 件数確認\n"
         "SELECT COUNT(*) FROM ai.item_embeddings;\n\n"
         "-- 次元確認\n"
         "SELECT vector_dims(embedding) FROM ai.item_embeddings LIMIT 1;\n\n"
         "-- 先頭 5 次元だけ見る\n"
         "SELECT item_id, embedding::text::varchar(80) FROM ai.item_embeddings LIMIT 3;",
         lang="SQL")

    chap(doc, "91", "SQL の基本")
    h(doc, "91.1 SELECT", level=2)
    code(doc,
         "SELECT * FROM users.users;                                -- 全カラム\n"
         "SELECT email, role FROM users.users;                      -- 必要カラム\n"
         "SELECT * FROM users.users WHERE role = 'ADMIN';           -- 条件\n"
         "SELECT * FROM users.users ORDER BY created_at DESC;       -- 並べ替え\n"
         "SELECT * FROM users.users LIMIT 10;                       -- 上位 10 件",
         lang="SQL")
    h(doc, "91.2 INSERT / UPDATE / DELETE", level=2)
    code(doc,
         "INSERT INTO users.users (email, password_hash, role)\n"
         "  VALUES ('new@example.com', '$2b$...', 'USER');\n\n"
         "UPDATE users.users SET role = 'ADMIN' WHERE email = 'x@x.com';\n\n"
         "DELETE FROM users.users WHERE email = 'x@x.com';",
         lang="SQL")

    chap(doc, "92", "簡単な SELECT 文を組み立てる")
    h(doc, "92.1 例: 新宿区のアイテム", level=2)
    code(doc,
         "SELECT title, region FROM items.items\n"
         "  WHERE region = '東京都-新宿区';",
         lang="SQL")
    h(doc, "92.2 例: カテゴリ別件数", level=2)
    code(doc,
         "SELECT c.name_ja, COUNT(*) AS cnt\n"
         "  FROM items.items i\n"
         "  JOIN items.categories c ON i.category_id = c.id\n"
         "  GROUP BY c.name_ja\n"
         "  ORDER BY cnt DESC;",
         lang="SQL")

    chap(doc, "93", "JOIN の基本")
    p(doc, "JOIN = 複数テーブルを連結する SQL 構文。")
    tbl(doc, [
        ["JOIN 種別", "意味"],
        ["INNER JOIN", "両方にある行のみ（デフォルト）"],
        ["LEFT JOIN", "左テーブルの全行 + 右テーブルの一致行（無ければ NULL）"],
        ["RIGHT JOIN", "LEFT の逆"],
        ["FULL JOIN", "両方の全行"],
    ])

    chap(doc, "94", "集計関数")
    tbl(doc, [
        ["関数", "意味"],
        ["COUNT(*)", "行数"],
        ["SUM(col)", "合計"],
        ["AVG(col)", "平均"],
        ["MAX(col)", "最大"],
        ["MIN(col)", "最小"],
    ])
    code(doc, "SELECT AVG(rating) FROM items.feedbacks WHERE feedback_type='rating';", lang="SQL")

    chap(doc, "95", "データのエクスポート")
    code(doc,
         "# DB から CSV エクスポート\n"
         "docker exec reco-postgres psql -U reco -d reco -c \"\\COPY items.items TO STDOUT WITH CSV HEADER\" > items.csv\n\n"
         "# 全テーブルを dump\n"
         "docker exec reco-postgres pg_dump -U reco reco > dump.sql",
         lang="PowerShell")


def part9_logs(doc):
    part_cover(
        doc, "9",
        "ログを読み解く",
        "サービスが「今何を考えているか」を覗く方法。\n"
        "障害調査・性能観察の基本です。",
    )

    chap(doc, "96", "docker logs の使い方")
    code(doc,
         "docker logs reco-ai-service              # 直近 200 行（既定）\n"
         "docker logs -f reco-ai-service           # リアルタイム監視（Ctrl+C で止める）\n"
         "docker logs --tail 50 reco-api-gateway   # 直近 50 行\n"
         "docker logs --since 10m reco-frontend    # 直近 10 分\n"
         "docker compose logs                      # 全サービス\n"
         "docker compose logs -f api-gateway       # 特定サービスを追跡",
         lang="PowerShell")

    chap(doc, "97", "各サービスのログの読み方")
    h(doc, "97.1 frontend (Next.js)", level=2)
    code(doc,
         "▲ Next.js 16.2.6\n"
         "- Local:         http://localhost:3001\n"
         "- Network:       http://0.0.0.0:3001\n"
         "✓ Ready in 0ms\n"
         "GET /ja 200 in 35ms",
         lang="例")
    h(doc, "97.2 api-gateway (NestJS)", level=2)
    code(doc,
         "[Nest] 7620  - 05/24/2026, 9:13:21 PM     LOG [NestApplication] Nest application successfully started\n"
         "api-gateway listening on http://0.0.0.0:3000",
         lang="例")
    h(doc, "97.3 user/item-service (Spring Boot)", level=2)
    code(doc,
         "2026-05-24T12:56:22.279Z  INFO 1 --- [user-service] [main] o.s.b.SpringApplication\n"
         "Started UserServiceApplication in 18.456 seconds (process running for 19.234)",
         lang="例")
    h(doc, "97.4 ai-service (FastAPI / uvicorn)", level=2)
    code(doc,
         "INFO:     Started server process [1]\n"
         "INFO:     Application startup complete.\n"
         "INFO:     Uvicorn running on http://0.0.0.0:8000\n"
         "INFO:     127.0.0.1:54514 - \"POST /search/items HTTP/1.1\" 200 OK",
         lang="例")

    chap(doc, "98", "ログレベルの読み方")
    tbl(doc, [
        ["レベル", "意味", "対処"],
        ["TRACE / DEBUG", "詳細トレース", "見なくて OK"],
        ["INFO", "正常動作", "見なくて OK"],
        ["WARN", "警告", "注意して見る"],
        ["ERROR", "エラー", "原因調査必須"],
        ["FATAL", "致命的", "即対応"],
    ])

    chap(doc, "99", "エラーの追跡方法")
    p(doc, "ERROR を見つけたら以下の順で原因を特定:")
    num(doc, "エラーメッセージをコピー → Google で検索")
    num(doc, "スタックトレース（呼び出し履歴）の最初の自分のコードを探す")
    num(doc, "そのコードに最近変更があったか git log で確認")
    num(doc, "再現手順を整理")
    num(doc, "AI（ChatGPT/Claude）にエラーログ + コードを貼って質問")

    chap(doc, "100", "性能ログの確認")
    p(doc, "「重い」と感じたら以下:")
    bul(doc, "Spring Boot: ログの「Started in X seconds」")
    bul(doc, "FastAPI: 各リクエストの応答時間（uvicorn が出す）")
    bul(doc, "DB: スロークエリは EXPLAIN ANALYZE で確認")
    bul(doc, "Docker: docker stats でリアルタイム CPU/メモリ")


def part10_modify(doc):
    part_cover(
        doc, "10",
        "自分でコードを変えてみる",
        "実際にファイルを編集して、再起動して、動作変化を観察。\n"
        "「自分で動かしている」感覚をつかむパートです。",
    )

    chap(doc, "101", "設定ファイル (.env) を変える")
    p(doc, "infra/.env を VS Code で開いて JWT_EXPIRES_IN_SECONDS=3600 を 60 に変更。")
    code(doc, "docker compose -f infra/docker-compose.yml restart api-gateway", lang="PowerShell")
    p(doc, "確認: ログイン後 1 分でセッション切れ。リロードでログアウト状態。")

    chap(doc, "102", "シードデータを増やす")
    p(doc, "infra/postgres/init/13-seed-dev-items.sql に新しい INSERT を追加。")
    code(doc,
         "INSERT INTO items.items (id, category_id, title, description, region, source) VALUES\n"
         "  (gen_random_uuid(),\n"
         "   (SELECT id FROM items.categories WHERE slug='job'),\n"
         "   '私が追加した求人',\n"
         "   '説明文',\n"
         "   '東京都-渋谷区',\n"
         "   'manual');",
         lang="SQL")
    p(doc, "DB を再初期化（破壊的）:")
    code(doc,
         "docker compose -f infra/docker-compose.yml down -v\n"
         "docker compose -f infra/docker-compose.yml up -d\n"
         "python scripts/seed_embeddings.py",
         lang="PowerShell")

    chap(doc, "103", "推薦スコアの重みを変える")
    p(doc, "ai-service/src/ai_service/recommend/scorer.py の重み定数を編集。")
    p(doc, "再ビルド:")
    code(doc, "docker compose -f infra/docker-compose.yml up -d --build ai-service", lang="PowerShell")
    p(doc, "確認: /ja/recommendations で結果が変化することを観察")

    chap(doc, "104", "UI の文言を変える")
    p(doc, "frontend/src/i18n/messages/ja.json を編集 → 文字列を書き換え")
    code(doc, "docker compose -f infra/docker-compose.yml up -d --build frontend", lang="PowerShell")
    p(doc, "編集 → 再ビルド → ブラウザ更新で確認")

    chap(doc, "105", "サンプルクエリを変える")
    p(doc, "同じく ja.json の \"search.samples\" 配列を編集。"
           "/ja/search のサンプルボタンが変わる。")

    chap(doc, "106", "JWT 有効期限を変える")
    p(doc, "第 101 章参照。短くしてセッション切れ挙動を試したり、開発時は長くしたり。")

    chap(doc, "107", "新しい API を追加する（初級・api-gateway）")
    p(doc, "api-gateway/src/admin/admin.controller.ts に新しい @Get エンドポイントを追加してみる:")
    code(doc,
         "@Get('stats')\n"
         "stats(): { totalItems: number; createdAt: string } {\n"
         "  return { totalItems: 14, createdAt: new Date().toISOString() };\n"
         "}",
         lang="TypeScript")
    p(doc, "再ビルド → curl http://localhost:3000/admin/stats -H \"Authorization: Bearer $TOKEN\"")

    chap(doc, "108", "新しい画面を追加する（初級・frontend）")
    p(doc, "frontend/src/app/[lang]/about/page.tsx を作成:")
    code(doc,
         "export default function About() {\n"
         "  return <div>これは私が追加した画面です</div>;\n"
         "}",
         lang="TypeScript")
    p(doc, "再ビルド → http://localhost:3001/ja/about")

    chap(doc, "109", "テストの走らせ方")
    code(doc,
         "# api-gateway\n"
         "cd api-gateway && npm test\n\n"
         "# user-service\n"
         "cd user-service && ./gradlew test\n\n"
         "# ai-service\n"
         "cd ai-service && pytest",
         lang="PowerShell")

    chap(doc, "110", "変更をコミット")
    code(doc,
         "git status\n"
         "git diff\n"
         "git add 変更したファイル\n"
         "git commit -m \"feat: 私の変更内容を一言で\"",
         lang="PowerShell")


def part11_git(doc):
    part_cover(
        doc, "11",
        "Git ワークフローを身につける",
        "ブランチ作成から PR マージまでの一連の流れ。\n"
        "実務でも同じやり方が使えます。",
    )

    chap(doc, "111", "Git の概念再確認")
    bul(doc, "ワーキングディレクトリ: 実際のファイル")
    bul(doc, "ステージング: コミット候補")
    bul(doc, "ローカルリポジトリ: コミット履歴（手元）")
    bul(doc, "リモートリポジトリ: GitHub 上の履歴")

    chap(doc, "112", "ブランチの作り方")
    code(doc,
         "git checkout main          # main へ移動\n"
         "git pull                   # 最新化\n"
         "git checkout -b RECO-99-my-feature  # 新ブランチ\n"
         "git branch                 # 確認",
         lang="PowerShell")

    chap(doc, "113", "ファイル変更の確認")
    code(doc,
         "git status                 # ファイル状態\n"
         "git diff                   # 未ステージ差分\n"
         "git diff --cached          # ステージ済み差分\n"
         "git diff main              # main との差分",
         lang="PowerShell")

    chap(doc, "114", "コミットの作り方")
    code(doc,
         "git add file.ts            # 個別ファイル\n"
         "git add .                  # 全変更\n"
         "git commit -m \"feat: 何をしたか\"\n\n"
         "# 修正したい場合\n"
         "git add fix.ts\n"
         "git commit --amend         # 直前コミットに追加",
         lang="PowerShell")

    chap(doc, "115", "コミットメッセージのルール（Conventional Commits）")
    tbl(doc, [
        ["prefix", "意味"],
        ["feat", "新機能"],
        ["fix", "バグ修正"],
        ["docs", "ドキュメント"],
        ["style", "整形のみ（動作変更なし）"],
        ["refactor", "リファクタリング（動作変更なし）"],
        ["test", "テスト追加"],
        ["chore", "雑務"],
    ])
    p(doc, "例:")
    code(doc, "feat(api-gateway): add admin stats endpoint (RECO-99)", lang="commit")

    chap(doc, "116", "GitHub に push")
    code(doc,
         "git push -u origin RECO-99-my-feature  # 初回\n"
         "git push                                # 2 回目以降",
         lang="PowerShell")

    chap(doc, "117", "Pull Request を作る")
    h(doc, "117.1 ブラウザから", level=2)
    num(doc, "GitHub のリポジトリページを開く")
    num(doc, "黄色いバナーが出ているはず → 「Compare & pull request」")
    num(doc, "タイトル + 説明を書く")
    num(doc, "「Create pull request」")
    h(doc, "117.2 gh CLI から", level=2)
    code(doc,
         "gh pr create --title \"feat(api-gateway): add admin stats endpoint\" \\\n"
         "  --body \"## Summary\\n- stats endpoint を追加\\n\"",
         lang="PowerShell")

    chap(doc, "118", "PR の説明文の書き方")
    p(doc, "良い PR 説明文の構成:")
    bul(doc, "Summary: 何をしたか 1-3 行")
    bul(doc, "Why: なぜ必要か")
    bul(doc, "How: どう実装したか（複雑な場合）")
    bul(doc, "Test plan: どうやって確認したか")
    bul(doc, "Screenshots: UI 変更があれば")

    chap(doc, "119", "セルフレビュー")
    p(doc, "PR を作ったら、まず自分で「Files changed」タブを開いて全差分を眺める。"
           "気付くことが必ずある（typo, console.log の消し忘れ等）。")

    chap(doc, "120", "マージとブランチ削除")
    h(doc, "120.1 GitHub UI から", level=2)
    num(doc, "PR ページの「Squash and merge」ボタン")
    num(doc, "コミットメッセージ確認 → 「Confirm squash and merge」")
    num(doc, "「Delete branch」")
    h(doc, "120.2 ローカルも整理", level=2)
    code(doc,
         "git checkout main\n"
         "git pull\n"
         "git branch -d RECO-99-my-feature",
         lang="PowerShell")


def part12_eval(doc):
    part_cover(
        doc, "12",
        "評価実験を理解する",
        "Precision・Recall・NDCG の意味を理解し、\n"
        "卒論 §5 で使う数値を自分で取れるようになります。",
    )

    chap(doc, "121", "そもそも評価とは何か")
    p(doc, "推薦が「良い」を定量的に測る必要があります。「使ってみて良い感じ」では論文に書けない。")
    p(doc, "評価には 2 種類:")
    bul(doc, "オフライン評価: 過去データ + ground truth で機械的に算出")
    bul(doc, "オンライン評価: 実ユーザーで A/B テスト（被験者実験）")
    p(doc, "本 PJ はオフライン評価のみ実装済み。オンラインは §5.4 の被験者実験で実施想定。")

    chap(doc, "122", "Precision の意味")
    p(doc, "Precision@K = 上位 K 件中、正解アイテムの割合")
    code(doc,
         "推薦結果 (K=5): [A, B, C, D, E]\n"
         "正解集合:       {A, C, F, G}\n"
         "正解と一致:     {A, C}        = 2 件\n"
         "Precision@5  = 2 / 5 = 0.4",
         lang="例")
    p(doc, "値の範囲: 0-1。高いほど「上位に正解が多い」。")

    chap(doc, "123", "Recall の意味")
    p(doc, "Recall@K = 全正解中、上位 K 件で拾えた割合")
    code(doc,
         "推薦結果 (K=5): [A, B, C, D, E]\n"
         "正解集合:       {A, C, F, G}  (4 件)\n"
         "正解と一致:     {A, C}        = 2 件\n"
         "Recall@5     = 2 / 4 = 0.5",
         lang="例")
    p(doc, "値の範囲: 0-1。高いほど「正解を取りこぼさない」。")

    chap(doc, "124", "NDCG の意味")
    p(doc, "NDCG@K = 順位の良さも加味した品質指標")
    code(doc,
         "DCG@K = Σ (relevance_i / log2(i + 1))  for i=1..K\n"
         "IDCG@K = DCG of ideal ranking\n"
         "NDCG@K = DCG@K / IDCG@K",
         lang="math")
    p(doc, "値の範囲: 0-1。高いほど「正解が上位にまとまっている」。")

    chap(doc, "125", "評価スクリプトを走らせる")
    code(doc, "python scripts/eval_recommendations.py", lang="PowerShell")
    p(doc, "出力: 3 ユーザー × 3 条件 × K∈{5,10} のテーブル + 集計")

    chap(doc, "126", "結果の解釈")
    p(doc, "卒論で書きたい主張:")
    bul(doc, "hybrid が単独より優れていることを定量的に示す")
    bul(doc, "セマンティック検索の限界（クエリだけでは属性に届かない）を分析")
    bul(doc, "N=3, items=14 の限界を正直に書き、被験者実験で補完予定とする")

    chap(doc, "127", "ground truth の作り方")
    p(doc, "scripts/eval_recommendations.py の TEST_CASES に手動ラベル。"
           "判断基準: カテゴリ一致 + 地域 + 母語サポート。"
           "ユーザーやアイテムを増やすときは TEST_CASES を拡張する。")

    chap(doc, "128", "被験者実験の設計")
    p(doc, "次フェーズで実施する被験者実験の設計:")
    bul(doc, "被験者: 大学・大学院に在籍する留学生 10-30 名")
    bul(doc, "同意書: データ収集と論文掲載の許諾")
    bul(doc, "タスク: 自分の属性を入力 → 推薦結果を 5 段階評価")
    bul(doc, "アンケート: SUS（System Usability Scale）+ 自由記述")
    bul(doc, "倫理審査: 大学の研究倫理委員会への申請が必要な場合あり")


def part13_troubleshoot(doc):
    part_cover(
        doc, "13",
        "困ったときに",
        "よくあるエラー・ログの読み方・完全リセット手順。\n"
        "ここを開けば大体の問題は乗り越えられます。",
    )

    chap(doc, "129", "Docker が起動しない")
    bul(doc, "症状: docker --version は OK だが docker ps でエラー")
    bul(doc, "原因: Docker Desktop が起動していない")
    bul(doc, "対処: タスクトレイのクジラアイコンを確認 → 「Engine running」になるまで待つ")
    bul(doc, "それでもダメ: PC を再起動")

    chap(doc, "130", "ポートが使用中")
    bul(doc, "症状: docker compose up で「port is already allocated」")
    bul(doc, "原因: 他アプリが同じポートを使用中")
    code(doc,
         "# 使用中アプリ確認\n"
         "netstat -ano | findstr :3001\n\n"
         "# プロセス確認\n"
         "tasklist /FI \"PID eq 1234\"",
         lang="PowerShell")
    bul(doc, "対処: そのアプリを終了 or infra/.env でポート変更")

    chap(doc, "131", "ビルド失敗")
    bul(doc, "症状: docker compose up --build で ERROR")
    bul(doc, "対処: ログを最後から遡って ERROR の最初を探す")
    bul(doc, "ai-service の pip エラー: src/ の有無を確認（PR #31 で修正済み）")
    bul(doc, "node のメモリ不足: NODE_OPTIONS=--max-old-space-size=4096 を環境変数で")

    chap(doc, "132", "コンテナが unhealthy")
    bul(doc, "症状: docker compose ps で unhealthy")
    bul(doc, "対処: docker logs <name> でログ確認")
    bul(doc, "ai-service: モデル DL 中なら数分待つ")
    bul(doc, "healthcheck 自体のバグなら Dockerfile/compose を直す")

    chap(doc, "133", "ログインできない")
    tbl(doc, [
        ["症状", "原因 / 対処"],
        ["401 Unauthorized", "パスワード違い → password123 で再試行"],
        ["404", "/auth/login のパス間違い"],
        ["502", "user-service が down → docker compose ps 確認"],
        ["フォームすら出ない", "frontend が down"],
    ])

    chap(doc, "134", "検索結果が出ない")
    bul(doc, "原因 1: 埋め込み未登録 → python scripts/seed_embeddings.py")
    bul(doc, "原因 2: ai-service が down → ログ確認")
    bul(doc, "原因 3: クエリが極端に短い")

    chap(doc, "135", "ADMIN になれない")
    bul(doc, "wang.resident@example.com でログインしているか確認")
    bul(doc, "ログアウトして再ログイン → JWT に新しい role が入る")
    bul(doc, "DB を見て role='ADMIN' か確認")

    chap(doc, "136", "完全リセット")
    code(doc,
         "# 全部止めてデータも消す\n"
         "docker compose -f infra/docker-compose.yml down -v\n\n"
         "# イメージも消す\n"
         "docker compose -f infra/docker-compose.yml down -v --rmi all\n\n"
         "# クリーンに作り直し\n"
         "docker compose -f infra/docker-compose.yml up -d --build\n"
         "python scripts/seed_embeddings.py",
         lang="PowerShell")

    chap(doc, "137", "ログの保存")
    code(doc, "docker compose -f infra/docker-compose.yml logs > all-logs.txt", lang="PowerShell")
    p(doc, "後で AI に質問するときや、issue 報告するときに添付。")

    chap(doc, "138", "サポートの求め方")
    bul(doc, "AI: ChatGPT/Claude にログ + 状況を貼って質問")
    bul(doc, "GitHub Issues: 再現手順を添えて作成")
    bul(doc, "Stack Overflow: エラーメッセージで検索")


def part14_paper(doc):
    part_cover(
        doc, "14",
        "卒論への展開",
        "実装は完了。次は文章に落とす段階です。\n"
        "各章で何を書けるかを具体例とともに示します。",
    )

    chap(doc, "139", "論文全体の構造")
    tbl(doc, [
        ["章", "目的"],
        ["§1 序論", "課題意識と本研究の意義"],
        ["§2 関連研究", "既存研究と本研究の位置づけ"],
        ["§3 提案手法", "アーキテクチャと推薦アルゴリズム"],
        ["§4 システム実装", "技術選択と各サービスの説明"],
        ["§5 評価実験", "オフライン + ユーザ評価"],
        ["§6 結論", "成果・限界・今後"],
    ])

    chap(doc, "140", "§1 序論の書き方")
    bul(doc, "1.1 研究背景: 第 1 章「在日外国人の生活の課題」を整理")
    bul(doc, "1.2 研究目的: 本書の「プロジェクトのゴール」を文章化")
    bul(doc, "1.3 研究課題: パーソナライズ / 多言語 / コールドスタート")
    bul(doc, "1.4 本研究の貢献: ハイブリッド推薦の実装と評価")
    bul(doc, "1.5 論文構成: 章立ての説明")

    chap(doc, "141", "§2 関連研究の調査")
    p(doc, "Google Scholar や CiNii で以下のキーワード:")
    bul(doc, "「foreigner Japan recommendation system」")
    bul(doc, "「multilingual embedding cross-lingual」")
    bul(doc, "「hybrid recommendation content collaborative」")
    bul(doc, "「learning Japanese as foreign language NLP」")
    p(doc, "10-20 本程度の文献を読み、自分の研究との違いを書く。")

    chap(doc, "142", "§3 提案手法の書き方")
    bul(doc, "3.1 システム概要: 第 2 章「全体の仕組み」")
    bul(doc, "3.2 ユーザモデル: 第 5 章「想定ユーザー像」")
    bul(doc, "3.3 推薦アルゴリズム: 第 85 章「ハイブリッド推薦の数式」")
    bul(doc, "3.4 AI・自然言語処理: 第 82-84 章")
    bul(doc, "3.5 システムアーキテクチャ: 第 71-78 章")

    chap(doc, "143", "§4 システム実装の書き方")
    bul(doc, "4.1 開発環境: 言語・フレームワーク選択")
    bul(doc, "4.2 フロントエンド実装: 画面構成 + 多言語")
    bul(doc, "4.3 バックエンド実装: 各サービス + 認証")
    bul(doc, "4.4 AI 推薦モジュール実装: 第 76, 82-85 章")
    bul(doc, "4.5 データベース設計: docs/schema/ER 図 + 第 77 章")
    bul(doc, "4.6 デプロイおよび運用環境: 第 25 章 docker-compose")

    chap(doc, "144", "§5 評価実験の書き方")
    bul(doc, "5.1 実験目的: hybrid > 単独 を示す")
    bul(doc, "5.2 実験環境: シードユーザー 3 / アイテム 14 / 評価指標")
    bul(doc, "5.3 推薦性能評価: eval_recommendations.py の結果表")
    bul(doc, "5.4 ユーザ評価実験: 被験者実験（要実施）")
    bul(doc, "5.5 考察: なぜ hybrid が良いか、限界はどこか")

    chap(doc, "145", "§6 結論の書き方")
    bul(doc, "6.1 本研究のまとめ")
    bul(doc, "6.2 本研究の成果（定量 + 定性）")
    bul(doc, "6.3 今後の課題（協調フィルタリング / 多様化 / クラウド）")
    bul(doc, "6.4 今後の展望（社会実装の可能性）")

    chap(doc, "146", "図表の入れ方")
    bul(doc, "アーキ図: 本書 第 2 章 ASCII を清書 or draw.io で書き直し")
    bul(doc, "ER 図: docs/schema/README.md の Mermaid を使う")
    bul(doc, "スクリーンショット: PowerToys の Screen Ruler で寸法を揃える")
    bul(doc, "結果テーブル: Word の表機能 or LaTeX なら tabular")

    chap(doc, "147", "参考文献の書き方")
    p(doc, "学会・大学のスタイルガイドに従う。一般的な形式:")
    code(doc,
         "[1] 著者. \"論文タイトル\". 雑誌名, vol. X, no. Y, pp. ZZ-ZZ, 年.\n"
         "[2] Author. \"Paper Title\". Conference, pp. ZZ-ZZ, Year.",
         lang="参考文献")

    chap(doc, "148", "発表スライドの作り方")
    bul(doc, "1 スライド 1 メッセージ")
    bul(doc, "デモ動画を入れる（ブラウザ操作の録画）")
    bul(doc, "アーキ図は再利用")
    bul(doc, "数値結果は棒グラフ等で視覚化")
    bul(doc, "Q&A 想定: 「協調フィルタリングは？」「実用化は？」「他言語は？」")


def appendix_a(doc):
    doc.add_page_break()
    h(doc, "付録 A  用語集（詳細版）", level=0)
    p(doc, "本書で登場した全ての専門用語を 50 音順に解説。")
    glossary = [
        ("ACID",
         "DB トランザクションの 4 性質 (Atomicity, Consistency, Isolation, Durability)。"),
        ("AGENTS.md",
         "AI エージェント向けにプロジェクトの注意事項を書くファイル。本 PJ では frontend にあり。"),
        ("API",
         "Application Programming Interface。プログラム同士の対話窓口。"),
        ("Apache 2.0",
         "オープンソースライセンスの 1 つ。商用利用可。multilingual-e5 が採用。"),
        ("appuser",
         "Docker コンテナ内で root を避けるために作る非特権ユーザー。"),
        ("Authorization ヘッダ",
         "HTTP リクエストヘッダの一つ。「Bearer <jwt>」で認証情報を渡す。"),
        ("autocrlf",
         "Git の改行コード自動変換。Windows は true 推奨。"),
        ("bcrypt",
         "パスワードのハッシュ化アルゴリズム。salt 内蔵で安全。"),
        ("Bearer Token",
         "「これを持つ者は本人」とする認証スキーム。HTTP Authorization ヘッダで使う。"),
        ("CASCADE",
         "DB の FK 制約オプション。親が消えると子も消す。"),
        ("class-validator",
         "TypeScript / Node のバリデーションライブラリ。NestJS で使用。"),
        ("ConfigService",
         "NestJS の環境変数アクセスサービス。@nestjs/config 由来。"),
        ("Conventional Commits",
         "「feat:」「fix:」等の prefix を付けるコミットメッセージ規約。"),
        ("CORS",
         "Cross-Origin Resource Sharing。異なるドメイン間通信のブラウザ制限。"),
        ("CRUD",
         "Create / Read / Update / Delete の頭字語。"),
        ("Dependency Injection (DI)",
         "依存を外部から注入する設計パターン。NestJS / Spring の中核。"),
        ("Docker",
         "アプリケーションをコンテナ化する技術。"),
        ("Docker Hub",
         "Docker イメージの公式レジストリ。"),
        ("docker-compose.yml",
         "複数コンテナ構成を YAML で記述するファイル。"),
        ("ECONNREFUSED",
         "TCP 接続拒否エラー。相手サービスが起動していない or ポート違い。"),
        ("Embedding",
         "テキストを数値ベクトルに変換する技術。"),
        ("ESLint",
         "JavaScript/TypeScript の静的解析ツール。"),
        ("FastAPI",
         "Python の高速 Web フレームワーク。型ヒントから OpenAPI 自動生成。"),
        ("FK (Foreign Key)",
         "別テーブルの行を参照する制約。"),
        ("Flat Config",
         "ESLint v9+ の新しい設定形式 (eslint.config.mjs)。"),
        ("Git",
         "分散バージョン管理システム。"),
        ("GitHub",
         "Git のホスティング + 共同作業サービス。"),
        ("Gradle",
         "Java/Kotlin のビルドツール。本 PJ で user/item-service が使用。"),
        ("gradlew",
         "Gradle Wrapper。プロジェクト固有の Gradle バージョンを保証。"),
        ("Healthcheck",
         "コンテナ生存確認の仕組み。Docker が定期実行。"),
        ("Hibernate",
         "Java の ORM。Spring Data JPA の裏で動く。"),
        ("HNSW",
         "Hierarchical Navigable Small World。ベクトル近似最近傍検索のアルゴリズム。"),
        ("HTTP",
         "Web 通信プロトコル。GET/POST/PUT/DELETE 等のメソッド。"),
        ("Hybrid Recommendation",
         "複数アルゴリズムを組合せた推薦。本 PJ は content + semantic。"),
        ("IDCG",
         "Ideal DCG。最良ランキングでの DCG。NDCG の分母。"),
        ("Image (Docker)",
         "コンテナの元となる不変スナップショット。"),
        ("Integration Test (IT)",
         "複数コンポーネントを連結したテスト。本 PJ では Testcontainers で実 DB を使う。"),
        ("isolatedModules",
         "TypeScript の設定。ファイル単独で型チェック可能とする。"),
        ("JPA",
         "Java Persistence API。Java の ORM 標準。"),
        ("Jest",
         "JavaScript のテストフレームワーク。"),
        ("JLPT",
         "日本語能力試験。N1-N5 の 5 段階。"),
        ("JSON",
         "JavaScript Object Notation。データ交換フォーマット。"),
        ("JSONB",
         "PostgreSQL の バイナリ JSON 型。インデックス可能。"),
        ("JWT",
         "JSON Web Token。署名付きトークン。"),
        ("JwtAuthGuard",
         "NestJS の認証ガード。JWT を検証して req.user に詰める。"),
        ("Kafka",
         "分散メッセージングシステム。本 PJ では未使用。"),
        ("Kubernetes (k8s)",
         "コンテナオーケストレーションシステム。本 PJ では未使用。"),
        ("Lazy Loading",
         "JPA で関連エンティティを必要時のみ取得する戦略。"),
        ("localStorage",
         "ブラウザ内のキー・バリュー永続ストア。本 PJ で JWT 保管。"),
        ("Lombok",
         "Java のボイラープレート削減ライブラリ。@Getter, @Builder 等。"),
        ("LLM",
         "Large Language Model。ChatGPT, Claude 等。本 PJ は OpenAI 任意。"),
        ("Mermaid",
         "テキストから図を生成するツール。GitHub で自動レンダリング。"),
        ("Middleware",
         "リクエストとハンドラの間で動く処理。Next 16 では proxy.ts に名称変更。"),
        ("Mockito",
         "Java のモックライブラリ。"),
        ("MockitoBean",
         "Spring の @MockitoBean。コンテキスト内の Bean をモックに差し替え。"),
        ("Monorepo",
         "複数プロジェクトを 1 つのリポジトリで管理する形態。"),
        ("multilingual-e5-small",
         "多言語 sentence embedding モデル。384 次元。Apache 2.0。"),
        ("NDCG",
         "Normalized Discounted Cumulative Gain。順位品質指標。"),
        ("NestJS",
         "Node.js の TypeScript Web フレームワーク。"),
        ("Next.js",
         "React のフルスタックフレームワーク。本 PJ は v16。"),
        ("Node.js",
         "JavaScript ランタイム。"),
        ("OSIV",
         "Open Session In View。Hibernate のセッションを HTTP リクエスト終了まで開く戦略。"),
        ("Pagination",
         "結果を分割して返す。本 PJ は MVP なので未実装。"),
        ("pgvector",
         "PostgreSQL のベクトル検索拡張。"),
        ("pip",
         "Python のパッケージ管理ツール。"),
        ("PowerShell",
         "Windows の高機能シェル。"),
        ("Precision",
         "予測の正確度。TP / (TP + FP)。"),
        ("Pre-commit",
         "コミット前に自動実行する hook。本 PJ では整形 + lint。"),
        ("ProtocolBuffers (Protobuf)",
         "Google のシリアライズフォーマット。本 PJ では未使用。"),
        ("psycopg",
         "Python の PostgreSQL ドライバ。v3 が最新。"),
        ("Pull Request (PR)",
         "ブランチの変更を別ブランチに取り込む依頼。GitHub 機能。"),
        ("pytest",
         "Python のテストフレームワーク。"),
        ("RBAC",
         "Role-Based Access Control。"),
        ("React",
         "Meta の UI ライブラリ。"),
        ("Recall",
         "再現率。TP / (TP + FN)。"),
        ("Redis",
         "インメモリ KVS。キャッシュやセッション保管に使う。"),
        ("Repository (Spring Data)",
         "JPA のリポジトリ抽象。CRUD メソッドが自動生成される。"),
        ("REST",
         "Representational State Transfer。HTTP リソース指向の API スタイル。"),
        ("ruff",
         "Python の高速 lint/format ツール。"),
        ("Scaffolding",
         "プロジェクトのひな形生成。"),
        ("Schema",
         "PostgreSQL の名前空間。本 PJ は users/items/ai の 3 つ。"),
        ("Seed",
         "テスト用初期データ。"),
        ("sentence-transformers",
         "文の埋め込みを生成する Python ライブラリ。"),
        ("Server Component",
         "React 19 / Next 16 でサーバ実行されるコンポーネント。"),
        ("Singleton",
         "1 つだけインスタンス化されるオブジェクト。DI コンテナの既定スコープ。"),
        ("SQL",
         "Structured Query Language。"),
        ("SQLAlchemy",
         "Python の ORM。本 PJ で ai-service が使用。"),
        ("Spring Boot",
         "Java の Web フレームワーク。本 PJ は v4。"),
        ("Squash Merge",
         "複数コミットを 1 つにまとめてマージ。"),
        ("SSR",
         "Server-Side Rendering。サーバで HTML を生成。"),
        ("Stacked PR",
         "1 つの PR の上にさらに PR を積む手法。"),
        ("Testcontainers",
         "テスト中に Docker コンテナを起動するライブラリ。"),
        ("Token",
         "認証情報を表す文字列。JWT もトークンの一種。"),
        ("Turbopack",
         "Next.js 13+ の Rust 製バンドラ。"),
        ("TypeScript",
         "JavaScript に静的型を追加した言語。"),
        ("Upsert",
         "Update or Insert。存在すれば更新、無ければ作成。"),
        ("UUID",
         "Universally Unique Identifier。128 ビットのランダム ID。"),
        ("Uvicorn",
         "Python の ASGI サーバ。"),
        ("Vector",
         "数値の配列。本 PJ では 384 次元ベクトル。"),
        ("WSL 2",
         "Windows Subsystem for Linux v2。Docker Desktop が内部で利用。"),
        ("YAML",
         "可読性の高い設定フォーマット。docker-compose.yml 等。"),
        ("ZSH",
         "Z shell。macOS のデフォルトシェル。"),
    ]
    for term, desc in glossary:
        par = doc.add_paragraph()
        r = par.add_run(f"{term}: ")
        r.bold = True
        _font(r, 10.5)
        r2 = par.add_run(desc)
        _font(r2, 10.5)


def appendix_b(doc):
    doc.add_page_break()
    h(doc, "付録 B  コマンド完全リスト", level=0)
    h(doc, "B.1 Docker", level=1)
    code(doc,
         "docker --version\n"
         "docker ps\n"
         "docker ps -a\n"
         "docker images\n"
         "docker logs <name>\n"
         "docker logs -f <name>\n"
         "docker logs --tail 50 <name>\n"
         "docker exec -it <name> bash\n"
         "docker exec -it reco-postgres psql -U reco -d reco\n"
         "docker stop <name>\n"
         "docker start <name>\n"
         "docker restart <name>\n"
         "docker rm <name>\n"
         "docker rmi <image>\n"
         "docker stats\n"
         "docker system df\n"
         "docker system prune\n"
         "docker volume ls\n"
         "docker volume rm <volume>\n"
         "docker network ls",
         lang="PowerShell")
    h(doc, "B.2 Docker compose", level=1)
    code(doc,
         "docker compose -f infra/docker-compose.yml up -d --build\n"
         "docker compose -f infra/docker-compose.yml up -d service-name\n"
         "docker compose -f infra/docker-compose.yml ps\n"
         "docker compose -f infra/docker-compose.yml logs -f\n"
         "docker compose -f infra/docker-compose.yml logs -f service-name\n"
         "docker compose -f infra/docker-compose.yml restart service-name\n"
         "docker compose -f infra/docker-compose.yml down\n"
         "docker compose -f infra/docker-compose.yml down -v\n"
         "docker compose -f infra/docker-compose.yml build service-name\n"
         "docker compose -f infra/docker-compose.yml build --no-cache service-name",
         lang="PowerShell")
    h(doc, "B.3 Git", level=1)
    code(doc,
         "git status\n"
         "git diff\n"
         "git diff --cached\n"
         "git diff main\n"
         "git add file\n"
         "git add .\n"
         "git commit -m \"msg\"\n"
         "git commit --amend\n"
         "git log --oneline\n"
         "git log --oneline -20\n"
         "git log --oneline --graph --all\n"
         "git branch\n"
         "git branch -d branch-name\n"
         "git branch -D branch-name (force)\n"
         "git checkout main\n"
         "git checkout -b new-branch\n"
         "git push\n"
         "git push -u origin branch-name\n"
         "git pull\n"
         "git fetch\n"
         "git fetch --prune\n"
         "git stash\n"
         "git stash pop\n"
         "git reset --hard HEAD\n"
         "git reset HEAD~1\n"
         "git cherry-pick <hash>\n"
         "git rebase main",
         lang="PowerShell")
    h(doc, "B.4 GitHub CLI", level=1)
    code(doc,
         "gh auth login\n"
         "gh pr create --title \"...\" --body \"...\"\n"
         "gh pr list\n"
         "gh pr view 123\n"
         "gh pr merge 123 --squash --delete-branch\n"
         "gh pr close 123\n"
         "gh pr checkout 123\n"
         "gh issue create\n"
         "gh issue list\n"
         "gh repo clone owner/repo\n"
         "gh repo view --web",
         lang="PowerShell")
    h(doc, "B.5 Python", level=1)
    code(doc,
         "python --version\n"
         "python script.py\n"
         "pip install package\n"
         "pip install -r requirements.txt\n"
         "pip install -e \".[dev]\"\n"
         "python -m venv .venv\n"
         ".venv\\Scripts\\Activate.ps1\n"
         "deactivate\n"
         "pytest\n"
         "pytest tests/test_x.py\n"
         "pytest -v\n"
         "pytest -k \"test_name\"\n"
         "ruff check src tests\n"
         "ruff format src tests",
         lang="PowerShell")
    h(doc, "B.6 Node.js / npm", level=1)
    code(doc,
         "node --version\n"
         "npm --version\n"
         "npm install\n"
         "npm install package\n"
         "npm install -D package\n"
         "npm run start\n"
         "npm run start:dev\n"
         "npm run build\n"
         "npm test\n"
         "npm run lint",
         lang="PowerShell")
    h(doc, "B.7 Gradle (Spring Boot)", level=1)
    code(doc,
         ".\\gradlew bootRun\n"
         ".\\gradlew test\n"
         ".\\gradlew integrationTest\n"
         ".\\gradlew build\n"
         ".\\gradlew clean\n"
         ".\\gradlew dependencies",
         lang="PowerShell")
    h(doc, "B.8 PostgreSQL (psql)", level=1)
    code(doc,
         "\\?               -- ヘルプ\n"
         "\\q               -- 終了\n"
         "\\dn              -- schema 一覧\n"
         "\\dt              -- 全テーブル\n"
         "\\dt schema.*     -- 特定 schema のテーブル\n"
         "\\d table         -- テーブル定義\n"
         "\\du              -- ユーザー一覧\n"
         "\\l               -- DB 一覧\n"
         "\\c dbname        -- DB 切替",
         lang="psql")


def appendix_c(doc):
    doc.add_page_break()
    h(doc, "付録 C  各サービスの API 一覧", level=0)
    h(doc, "C.1 api-gateway (port 3000)", level=1)
    tbl(doc, [
        ["Method", "Path", "認証", "用途"],
        ["GET", "/health", "—", "ヘルスチェック"],
        ["POST", "/auth/login", "—", "ログイン → JWT 発行"],
        ["GET", "/me/profile", "JWT", "自分のプロフィール"],
        ["PUT", "/me/profile", "JWT", "プロフィール更新"],
        ["GET", "/me/preferences", "JWT", "設定取得"],
        ["PUT", "/me/preferences", "JWT", "設定更新"],
        ["GET", "/admin/items", "ADMIN", "アイテム一覧"],
        ["POST", "/admin/items", "ADMIN", "アイテム追加 + 自動埋め込み"],
        ["PUT", "/admin/items/{id}", "ADMIN", "更新 + 再埋め込み"],
        ["DELETE", "/admin/items/{id}", "ADMIN", "削除"],
        ["POST", "/search/items", "—", "意味検索"],
        ["POST", "/recommend/hybrid", "—", "ハイブリッド推薦"],
        ["GET", "/admin/ping", "ADMIN", "RBAC 動作確認"],
    ])
    h(doc, "C.2 user-service (port 8081)", level=1)
    tbl(doc, [
        ["Method", "Path", "用途"],
        ["GET", "/health", "ヘルスチェック"],
        ["POST", "/users", "新規登録"],
        ["GET", "/users/{id}", "取得"],
        ["GET", "/users/{id}/profile", "プロフィール取得"],
        ["PUT", "/users/{id}/profile", "プロフィール更新"],
        ["GET", "/users/{id}/preferences", "設定取得"],
        ["PUT", "/users/{id}/preferences", "設定更新"],
        ["POST", "/internal/auth/verify", "認証検証（gateway 専用）"],
    ])
    h(doc, "C.3 item-service (port 8082)", level=1)
    tbl(doc, [
        ["Method", "Path", "用途"],
        ["GET", "/health", "ヘルスチェック"],
        ["GET", "/items", "一覧（filter: category, region）"],
        ["GET", "/items/{id}", "取得"],
        ["POST", "/items", "作成"],
        ["PUT", "/items/{id}", "更新"],
        ["DELETE", "/items/{id}", "削除"],
        ["POST", "/feedbacks", "フィードバック記録"],
        ["GET", "/feedbacks/by-user/{id}", "ユーザー別"],
        ["GET", "/feedbacks/by-item/{id}", "アイテム別"],
    ])
    h(doc, "C.4 ai-service (port 8000)", level=1)
    tbl(doc, [
        ["Method", "Path", "用途"],
        ["GET", "/health", "ヘルスチェック"],
        ["POST", "/embed", "テキスト → 384d ベクトル"],
        ["POST", "/embeddings/items/{id}", "アイテム埋め込みを upsert"],
        ["POST", "/search/items", "意味検索"],
        ["POST", "/recommend", "コンテンツベース推薦"],
        ["POST", "/recommend/hybrid", "ハイブリッド"],
        ["POST", "/explain", "LLM 説明"],
    ])
    h(doc, "C.5 frontend (port 3001)", level=1)
    p(doc, "ページ:")
    tbl(doc, [
        ["URL", "認証"],
        ["/", "→ /ja or /en リダイレクト"],
        ["/[lang]", "—"],
        ["/[lang]/search", "—"],
        ["/[lang]/recommendations", "—"],
        ["/[lang]/login", "—"],
        ["/[lang]/me", "ログイン必須"],
        ["/[lang]/admin/items", "ADMIN 必須"],
    ])
    p(doc, "Route Handler（サーバ側プロキシ）:")
    tbl(doc, [
        ["Path", "転送先"],
        ["/api/health", "frontend 内部"],
        ["/api/auth/login", "api-gateway /auth/login"],
        ["/api/auth/me", "api-gateway /me/profile"],
        ["/api/search", "api-gateway /search/items"],
        ["/api/recommendations", "api-gateway /recommend/hybrid"],
        ["/api/admin/items", "api-gateway /admin/items"],
        ["/api/admin/items/[id]", "api-gateway /admin/items/{id}"],
    ])


def appendix_d(doc):
    doc.add_page_break()
    h(doc, "付録 D  全設定項目リファレンス", level=0)
    h(doc, "D.1 infra/.env", level=1)
    tbl(doc, [
        ["変数", "デフォルト", "用途"],
        ["POSTGRES_USER", "reco", "PG ユーザー"],
        ["POSTGRES_PASSWORD", "reco_password", "PG パスワード"],
        ["POSTGRES_DB", "reco", "PG DB 名"],
        ["POSTGRES_PORT", "5432", "ホスト側ポート"],
        ["REDIS_PORT", "6379", "ホスト側ポート"],
        ["API_GATEWAY_PORT", "3000", "ホスト側ポート"],
        ["USER_SERVICE_PORT", "8081", "ホスト側ポート"],
        ["ITEM_SERVICE_PORT", "8082", "ホスト側ポート"],
        ["AI_SERVICE_PORT", "8000", "ホスト側ポート"],
        ["FRONTEND_PORT", "3001", "ホスト側ポート"],
        ["JWT_SECRET", "dev-only-change-in-prod", "JWT 署名鍵"],
        ["JWT_EXPIRES_IN_SECONDS", "3600", "JWT 有効秒数"],
        ["OPENAI_API_KEY", "（未設定）", "LLM 用、未設定でテンプレ"],
    ])
    h(doc, "D.2 frontend env (Next.js)", level=1)
    tbl(doc, [
        ["変数", "用途"],
        ["AI_SERVICE_URL", "ai-service の URL（現在は api-gateway 経由なので未使用）"],
        ["API_GATEWAY_URL", "api-gateway の URL"],
        ["NODE_ENV", "production / development"],
    ])
    h(doc, "D.3 api-gateway env (NestJS)", level=1)
    tbl(doc, [
        ["変数", "用途"],
        ["JWT_SECRET", "必須。未設定なら起動失敗"],
        ["JWT_EXPIRES_IN_SECONDS", "JWT 有効秒数"],
        ["USER_SERVICE_URL", "user-service の URL"],
        ["ITEM_SERVICE_URL", "item-service の URL"],
        ["AI_SERVICE_URL", "ai-service の URL"],
    ])
    h(doc, "D.4 user-service application.properties", level=1)
    code(doc,
         "spring.application.name=user-service\n"
         "server.port=${PORT:8081}\n"
         "spring.datasource.url=${DATABASE_URL:jdbc:postgresql://localhost:5432/reco}\n"
         "spring.datasource.username=${DATABASE_USER:reco}\n"
         "spring.datasource.password=${DATABASE_PASSWORD:reco_password}\n"
         "spring.jpa.properties.hibernate.default_schema=users\n"
         "spring.jpa.hibernate.ddl-auto=validate\n"
         "spring.flyway.enabled=false",
         lang="properties")


def appendix_e(doc):
    doc.add_page_break()
    h(doc, "付録 E  よく見るエラーメッセージ集", level=0)
    errors = [
        ("Cannot connect to the Docker daemon",
         "Docker Desktop が起動していない。クジラアイコン確認。"),
        ("port is already allocated",
         "そのポートが他アプリで使用中。netstat で確認 → 解放。"),
        ("Error response from daemon: pull access denied",
         "Docker Hub の認証が必要。docker login。"),
        ("no space left on device",
         "ディスク容量不足。docker system prune で不要データ削除。"),
        ("dependency failed to start: container X is unhealthy",
         "そのサービスの healthcheck が NG。docker logs X で原因確認。"),
        ("ECONNREFUSED",
         "接続拒否。相手サービスがダウン or ポート違い。"),
        ("Cannot find module '@nestjs/jwt'",
         "依存未インストール。cd api-gateway && npm install。"),
        ("error: error in 'egg_base' option: 'src' does not exist",
         "Python のパッケージ install エラー。Dockerfile の COPY 順序問題（PR #31 で修正済み）。"),
        ("org.hibernate.LazyInitializationException",
         "JPA の Lazy 関連エンティティへの session 切れアクセス。OSIV=true で暫定対処。"),
        ("Required role: ADMIN; user has: USER",
         "USER ロールで ADMIN 限定 API を叩いた。wang.resident で再ログイン。"),
        ("Invalid email or password",
         "ログイン失敗。シードユーザーは password123 を使う。"),
        ("MISSING_AUTHORIZATION",
         "Authorization ヘッダ無しで認証必須エンドポイント叩いた。"),
        ("Invalid or expired token",
         "JWT の署名不一致 or 期限切れ。再ログイン。"),
        ("Response constructor: Invalid response status code 204",
         "Next.js Route Handler で 204 + body を返した。body=null にする。"),
        ("404 Not Found",
         "URL のパス違い。タイポ確認。"),
        ("405 Method Not Allowed",
         "HTTP メソッド違い。POST のところに GET 等。"),
        ("500 Internal Server Error",
         "サーバ側の異常。docker logs で原因特定。"),
        ("502 Bad Gateway",
         "上流サービス（user-service/item-service/ai-service）がダウン。"),
        ("CORS policy: No 'Access-Control-Allow-Origin'",
         "本 PJ では Next Route Handler 経由なので発生しない。"),
        ("react-hooks/set-state-in-effect",
         "React 19 / Next 16 の lint 警告。useSyncExternalStore で書き直し。"),
    ]
    for code_text, desc in errors:
        par = doc.add_paragraph()
        r = par.add_run("● ")
        _font(r, 10.5)
        r2 = par.add_run(code_text)
        r2.bold = True
        r2.font.name = "Consolas"
        r2.font.size = Pt(10)
        par.add_run("\n")
        r3 = par.add_run(f"   {desc}")
        _font(r3, 10)


# ===========================================================================
# main
# ===========================================================================


def build():
    doc = Document()
    for section in doc.sections:
        section.top_margin = Cm(2)
        section.bottom_margin = Cm(2)
        section.left_margin = Cm(2)
        section.right_margin = Cm(2)

    # 表紙
    par = doc.add_paragraph()
    par.alignment = WD_ALIGN_PARAGRAPH.CENTER
    r = par.add_run("\n\n\n\nRecoForeJP")
    r.bold = True
    _font(r, 36)
    par2 = doc.add_paragraph()
    par2.alignment = WD_ALIGN_PARAGRAPH.CENTER
    r = par2.add_run("完全教科書")
    r.bold = True
    _font(r, 28)
    par3 = doc.add_paragraph()
    par3.alignment = WD_ALIGN_PARAGRAPH.CENTER
    r = par3.add_run("\nコード未経験者のためのプロジェクト完全攻略本")
    _font(r, 14)
    par4 = doc.add_paragraph()
    par4.alignment = WD_ALIGN_PARAGRAPH.CENTER
    r = par4.add_run("\n\n14 部 + 付録 5 / 148 章 / 500+ ページ")
    r.italic = True
    _font(r, 11)

    doc.add_page_break()

    # 巨大目次
    h(doc, "目次", level=0)
    toc_entries = [
        ("第 1 部 プロジェクトを理解する", 0),
        ("  第 1 章 在日外国人の生活の課題", 1),
        ("  第 2 章 推薦システムとは何か", 1),
        ("  第 3 章 AI で何ができるか", 1),
        ("  第 4 章 このプロジェクトのゴール", 1),
        ("  第 5 章 想定ユーザー像", 1),
        ("  第 6 章 既存サービスとの比較", 1),
        ("  第 7 章 卒業研究としての位置づけ", 1),
        ("  第 8 章 倫理・プライバシーの考え方", 1),
        ("  第 9 章 本書の使い方", 1),
        ("  第 10 章 学習の進め方", 1),
        ("第 2 部 パソコンの基礎知識", 0),
        ("  第 11 章 OS とは", 1),
        ("  第 12 章 Windows の基本操作", 1),
        ("  第 13 章 ファイルとフォルダの概念", 1),
        ("  第 14 章 ターミナルとは何か", 1),
        ("  第 15 章 PowerShell の起動と基本", 1),
        ("  第 16 章 PowerShell のコマンド一覧", 1),
        ("  第 17 章 ファイル操作コマンド", 1),
        ("  第 18 章 環境変数の概念", 1),
        ("  第 19 章 ポート番号の概念", 1),
        ("  第 20 章 IP アドレスと URL", 1),
        ("第 3 部 必要なソフトウェアを準備する", 0),
        ("  第 21-35 章 Docker, Git, Python, Node, VS Code", 1),
        ("第 4 部 プロジェクトを取得して中身を覗く", 0),
        ("  第 36-45 章 clone, README, .env, フォルダ構造", 1),
        ("第 5 部 最初の起動", 0),
        ("  第 46-55 章 docker compose up, ヘルスチェック, ブラウザ確認", 1),
        ("第 6 部 各機能を 1 つずつ試す", 0),
        ("  第 56-70 章 検索 / 推薦 / ログイン / 管理画面", 1),
        ("第 7 部 中の仕組みを覗く", 0),
        ("  第 71-85 章 マイクロサービス, JWT, embedding, NDCG", 1),
        ("第 8 部 データを直接覗く", 0),
        ("  第 86-95 章 psql, SQL 基本, JOIN, 集計", 1),
        ("第 9 部 ログを読み解く", 0),
        ("  第 96-100 章 docker logs, レベル, エラー追跡", 1),
        ("第 10 部 自分でコードを変えてみる", 0),
        ("  第 101-110 章 設定変更, シード追加, 重み, UI, API, 画面, テスト", 1),
        ("第 11 部 Git ワークフロー", 0),
        ("  第 111-120 章 ブランチ, コミット, push, PR, マージ", 1),
        ("第 12 部 評価実験を理解する", 0),
        ("  第 121-128 章 Precision, Recall, NDCG, 被験者実験設計", 1),
        ("第 13 部 困ったときに", 0),
        ("  第 129-138 章 エラー対処, ログ, 完全リセット", 1),
        ("第 14 部 卒論への展開", 0),
        ("  第 139-148 章 §1-6 各章の書き方, 図表, 参考文献, スライド", 1),
        ("付録 A 用語集（詳細版・100+ 用語）", 0),
        ("付録 B コマンド完全リスト", 0),
        ("付録 C 各サービスの API 一覧", 0),
        ("付録 D 全設定項目リファレンス", 0),
        ("付録 E よく見るエラーメッセージ集", 0),
    ]
    for text, indent in toc_entries:
        par = doc.add_paragraph()
        par.paragraph_format.left_indent = Cm(0.5 * indent)
        run = par.add_run(text)
        if indent == 0:
            run.bold = True
        _font(run, 10.5)

    # 各部
    part1_intro(doc)
    part2_pc_basics(doc)
    part3_software(doc)
    part4_get_project(doc)
    part5_first_run(doc)
    part6_use_features(doc)
    part7_internals(doc)
    part8_db(doc)
    part9_logs(doc)
    part10_modify(doc)
    part11_git(doc)
    part12_eval(doc)
    part13_troubleshoot(doc)
    part14_paper(doc)

    appendix_a(doc)
    appendix_b(doc)
    appendix_c(doc)
    appendix_d(doc)
    appendix_e(doc)

    # 巻末
    doc.add_page_break()
    par = doc.add_paragraph()
    par.alignment = WD_ALIGN_PARAGRAPH.CENTER
    r = par.add_run("\n\n\n\n— 完 —\n\n")
    r.italic = True
    _font(r, 14)
    par2 = doc.add_paragraph()
    par2.alignment = WD_ALIGN_PARAGRAPH.CENTER
    r = par2.add_run(
        "ここまで読んでくれてありがとう。\n"
        "コードを書くこと、システムを動かすこと、論文を書き上げること。\n"
        "一つ一つは小さな一歩でも、続ければ必ずゴールにつく。\n"
        "がんばってください。\n"
    )
    _font(r, 11)

    OUT_PATH.parent.mkdir(parents=True, exist_ok=True)
    doc.save(OUT_PATH)
    print(f"✅ {OUT_PATH.relative_to(OUT_PATH.parent.parent)} を生成しました")
    print(f"   ({OUT_PATH.stat().st_size:,} bytes)")


if __name__ == "__main__":
    build()
