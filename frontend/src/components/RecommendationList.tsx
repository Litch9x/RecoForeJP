import type { HybridRecommendedItem } from "@/lib/recommend-types";

export function RecommendationList({
  items,
}: {
  items: HybridRecommendedItem[];
}) {
  if (items.length === 0) {
    return (
      <p className="rounded border border-zinc-200 bg-zinc-50 p-4 text-sm text-zinc-600 dark:border-zinc-800 dark:bg-zinc-900 dark:text-zinc-400">
        条件にマッチする推薦がありませんでした。条件を緩めるか、自然言語クエリを変えて試してください。
      </p>
    );
  }

  return (
    <section className="space-y-3">
      <h2 className="text-lg font-semibold">推薦結果 ({items.length} 件)</h2>
      <ul className="space-y-3">
        {items.map((item, idx) => (
          <li
            key={item.item_id}
            className="rounded-lg border border-zinc-200 bg-white p-4 shadow-sm dark:border-zinc-800 dark:bg-zinc-950"
          >
            <div className="flex items-start justify-between gap-4">
              <div className="flex-1 space-y-2">
                <div className="flex items-baseline gap-3">
                  <span className="text-xs font-mono text-zinc-500">
                    #{idx + 1}
                  </span>
                  <h3 className="text-base font-semibold">
                    {item.title ?? "(タイトル未取得)"}
                  </h3>
                </div>

                {item.reasons.length > 0 && (
                  <ul className="space-y-1 text-sm text-zinc-700 dark:text-zinc-300">
                    {item.reasons.map((r) => (
                      <li key={r} className="flex gap-2">
                        <span aria-hidden>•</span>
                        <span>{r}</span>
                      </li>
                    ))}
                  </ul>
                )}

                <p className="font-mono text-xs text-zinc-500">
                  item_id: {item.item_id}
                </p>
              </div>

              <div className="shrink-0 space-y-1 rounded bg-zinc-50 p-3 text-right text-xs dark:bg-zinc-900">
                <div>
                  <span className="text-zinc-500">hybrid</span>{" "}
                  <span className="font-semibold">
                    {item.hybrid_score.toFixed(3)}
                  </span>
                </div>
                <div className="text-zinc-500">
                  content: {item.content_score.toFixed(2)}
                </div>
                <div className="text-zinc-500">
                  semantic: {item.semantic_score.toFixed(2)}
                </div>
              </div>
            </div>
          </li>
        ))}
      </ul>
    </section>
  );
}
