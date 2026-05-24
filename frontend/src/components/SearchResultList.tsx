import type { Dictionary } from "@/i18n/dictionaries";
import type { SearchResultItem } from "@/lib/search-types";

interface Props {
  dict: Dictionary["search"]["results"];
  query: string;
  results: SearchResultItem[];
}

export function SearchResultList({ dict, query, results }: Props) {
  if (results.length === 0) {
    return (
      <div className="space-y-2">
        <p className="text-sm text-zinc-600 dark:text-zinc-400">
          「{query}」 — {dict.emptyTitle}
        </p>
        <p className="text-xs text-zinc-500">{dict.emptyHint}</p>
      </div>
    );
  }

  return (
    <section className="space-y-3">
      <h2 className="text-lg font-semibold">
        {dict.heading} ({results.length} {dict.countSuffix}) — {dict.querySuffix}「{query}」
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
                    {item.title ?? dict.missingTitle}
                  </h3>
                </div>
                <p className="font-mono text-xs text-zinc-500">
                  item_id: {item.item_id}
                </p>
              </div>
              <div className="shrink-0 rounded bg-zinc-50 p-3 text-right text-xs dark:bg-zinc-900">
                <div className="text-zinc-500">{dict.similarityLabel}</div>
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
