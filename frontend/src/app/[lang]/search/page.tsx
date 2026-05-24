import { SearchForm } from "@/components/SearchForm";

export const metadata = {
  title: "意味検索 | RecoForeJP",
};

export default function SearchPage() {
  return (
    <div className="flex flex-1 flex-col bg-zinc-50 dark:bg-black">
      <main className="mx-auto w-full max-w-3xl space-y-6 px-6 py-12 sm:px-10">
        <header className="space-y-2">
          <p className="text-xs uppercase tracking-widest text-zinc-500">
            RecoForeJP
          </p>
          <h1 className="text-2xl font-semibold tracking-tight">
            意味検索（multilingual-e5 × pgvector）
          </h1>
          <p className="text-sm text-zinc-600 dark:text-zinc-400">
            自然言語クエリを 384
            次元ベクトルに変換し、事前に登録されたアイテム埋め込みに対して
            cosine 類似度で近似最近傍検索（HNSW）を行います（論文 2.3.3 /
            3.4.4）。
          </p>
        </header>

        <SearchForm />
      </main>
    </div>
  );
}
