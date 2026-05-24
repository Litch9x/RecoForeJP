export default function Home() {
  return (
    <div className="flex flex-1 flex-col items-center justify-center bg-zinc-50 font-sans dark:bg-black">
      <main className="flex w-full max-w-3xl flex-1 flex-col gap-10 px-8 py-24 sm:px-16">
        <header className="space-y-2">
          <p className="text-xs uppercase tracking-widest text-zinc-500">
            RecoForeJP
          </p>
          <h1 className="text-3xl font-semibold leading-tight tracking-tight text-black dark:text-zinc-50 sm:text-4xl">
            在日外国人向け AI パーソナライズ推薦システム
          </h1>
          <p className="text-base text-zinc-600 dark:text-zinc-400">
            日本語能力・在留資格・興味・行動履歴に基づき、就職・住居・行政手続き・
            日本語学習・地域イベントなどの生活情報を推薦するマイクロサービス
            アプリケーションの管理用 UI。
          </p>
        </header>

        <section className="space-y-3">
          <h2 className="text-xl font-semibold">サービス構成</h2>
          <ul className="space-y-1 text-sm text-zinc-700 dark:text-zinc-300">
            <li>
              <span className="font-mono">frontend</span> — Next.js (この
              UI、ポート 3001)
            </li>
            <li>
              <span className="font-mono">api-gateway</span> — NestJS (3000) -
              認証・ルーティング
            </li>
            <li>
              <span className="font-mono">user-service</span> — Spring Boot
              (8081) - ユーザー・プロフィール・設定
            </li>
            <li>
              <span className="font-mono">item-service</span> — Spring Boot
              (8082) - アイテム・カテゴリ・フィードバック
            </li>
            <li>
              <span className="font-mono">ai-service</span> — FastAPI (8000) -
              推薦・埋め込み・LLM・意味検索
            </li>
          </ul>
        </section>

        <section className="space-y-3">
          <h2 className="text-xl font-semibold">画面</h2>
          <ul className="space-y-1 text-sm">
            <li>
              <a
                href="/recommendations"
                className="font-medium text-zinc-950 underline-offset-4 hover:underline dark:text-zinc-50"
              >
                /recommendations
              </a>{" "}
              — ハイブリッド推薦（content × semantic）の動作確認
            </li>
            <li>
              <a
                href="/search"
                className="font-medium text-zinc-950 underline-offset-4 hover:underline dark:text-zinc-50"
              >
                /search
              </a>{" "}
              — 自然言語クエリでの意味検索（埋め込み × pgvector）
            </li>
            <li>
              <a
                href="/api/health"
                className="font-medium text-zinc-950 underline-offset-4 hover:underline dark:text-zinc-50"
              >
                /api/health
              </a>{" "}
              — ヘルスチェック JSON
            </li>
          </ul>
        </section>
      </main>
    </div>
  );
}
