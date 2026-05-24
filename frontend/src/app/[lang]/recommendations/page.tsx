import { RecommendationForm } from "@/components/RecommendationForm";

export const metadata = {
  title: "推薦 | RecoForeJP",
};

export default function RecommendationsPage() {
  return (
    <div className="flex flex-1 flex-col bg-zinc-50 dark:bg-black">
      <main className="mx-auto w-full max-w-3xl space-y-6 px-6 py-12 sm:px-10">
        <header className="space-y-2">
          <p className="text-xs uppercase tracking-widest text-zinc-500">
            RecoForeJP
          </p>
          <h1 className="text-2xl font-semibold tracking-tight">
            ハイブリッド推薦（content × semantic）
          </h1>
          <p className="text-sm text-zinc-600 dark:text-zinc-400">
            ユーザー属性に基づくコンテンツベース推薦と、自然言語クエリによる意味検索を
            重み付きで統合した結果を返します（論文 3.3.3）。
          </p>
        </header>

        <RecommendationForm />
      </main>
    </div>
  );
}
