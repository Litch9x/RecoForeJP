import type { SearchResultItem } from "@/lib/search-types";

export function SearchResultList({
  query,
  results,
}: {
  query: string;
  results: SearchResultItem[];
}) {
  if (results.length === 0) {
    return (
      <div className="space-y-2">
        <p className="text-sm text-zinc-600 dark:text-zinc-400">
          「{query}」に対する検索結果がありませんでした。
        </p>
        <p className="text-xs text-zinc-500">
          ヒント: 意味検索は事前に <code>POST /embeddings/items/{`{id}`}</code>
          でアイテム埋め込みを登録しておく必要があります（RECO-23）。
          まだ何も登録されていない場合は 0 件が返ります。
        </p>
      </div>
    );
  }

  return (
    <section className="space-y-3">
      <h2 className="text-lg font-semibold">
        検索結果 ({results.length} 件) — クエリ「{query}」
      </h2>
      <ul className="space-y-3">
        {results.map((item, idx) => (
          <li
            key={item.item_id}
            className="rounded-lg border border-zinc-200 bg-white p-4 shadow-sm dark:border-zinc-800 dark:bg-zinc-950"
          >
            <div className="flex items-start justify-between gap-4">
              <div className="flex-1 space-y-1">
                <div className="flex items-baseline gap-3">
                  <span className="text-xs font-mono text-zinc-500">
                    #{idx + 1}
                  </span>
                  <h3 className="text-base font-semibold">
                    {item.title ?? "(タイトル未取得)"}
                  </h3>
                </div>
                <p className="font-mono text-xs text-zinc-500">
                  item_id: {item.item_id}
                </p>
              </div>
              <div className="shrink-0 rounded bg-zinc-50 p-3 text-right text-xs dark:bg-zinc-900">
                <div className="text-zinc-500">similarity</div>
                <div className="font-semibold">
                  {item.similarity.toFixed(3)}
                </div>
              </div>
            </div>
          </li>
        ))}
      </ul>
    </section>
  );
}
