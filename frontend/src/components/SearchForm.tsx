"use client";

import { useState, type FormEvent } from "react";

import type {
  SemanticSearchRequest,
  SemanticSearchResponse,
} from "@/lib/search-types";
import { SearchResultList } from "./SearchResultList";

const EXAMPLES = [
  "ベトナム語で働けるカスタマーサポート",
  "英語 OK の IT エンジニア",
  "外国人向けの病院 東京",
  "やさしい日本語のクラス",
];

export function SearchForm() {
  const [query, setQuery] = useState("");
  const [limit, setLimit] = useState(10);

  const [loading, setLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);
  const [results, setResults] = useState<SemanticSearchResponse | null>(null);

  async function handleSubmit(event: FormEvent<HTMLFormElement>) {
    event.preventDefault();
    if (!query.trim()) {
      setError("クエリを入力してください");
      return;
    }
    setLoading(true);
    setError(null);
    setResults(null);

    const payload: SemanticSearchRequest = { query: query.trim(), limit };

    try {
      const response = await fetch("/api/search", {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify(payload),
      });
      if (!response.ok) {
        const text = await response.text();
        setError(`エラー (${response.status}): ${text}`);
        return;
      }
      const data = (await response.json()) as SemanticSearchResponse;
      setResults(data);
    } catch (err) {
      setError(err instanceof Error ? err.message : String(err));
    } finally {
      setLoading(false);
    }
  }

  return (
    <div className="space-y-8">
      <form
        onSubmit={handleSubmit}
        className="space-y-4 rounded-lg border border-zinc-200 bg-white p-6 dark:border-zinc-800 dark:bg-zinc-950"
      >
        <label className="block">
          <span className="text-sm font-medium">検索クエリ（自然言語）</span>
          <input
            type="text"
            value={query}
            onChange={(e) => setQuery(e.target.value)}
            placeholder="例: ベトナム語で働ける仕事"
            autoFocus
            className="mt-1 block w-full rounded border border-zinc-300 bg-white px-3 py-2 text-sm dark:border-zinc-700 dark:bg-zinc-900"
          />
        </label>

        <div className="flex flex-wrap gap-2">
          <span className="text-xs text-zinc-500">サンプル:</span>
          {EXAMPLES.map((ex) => (
            <button
              type="button"
              key={ex}
              onClick={() => setQuery(ex)}
              className="rounded-full border border-zinc-300 px-2 py-0.5 text-xs text-zinc-700 hover:bg-zinc-50 dark:border-zinc-700 dark:text-zinc-300 dark:hover:bg-zinc-800"
            >
              {ex}
            </button>
          ))}
        </div>

        <label className="block">
          <span className="text-sm font-medium">取得件数: {limit}</span>
          <input
            type="range"
            min={1}
            max={50}
            step={1}
            value={limit}
            onChange={(e) => setLimit(Number(e.target.value))}
            className="mt-1 block w-full"
          />
        </label>

        <button
          type="submit"
          disabled={loading}
          className="w-full rounded bg-black px-4 py-2 text-sm font-medium text-white transition-opacity hover:opacity-90 disabled:opacity-50 dark:bg-white dark:text-black sm:w-auto"
        >
          {loading ? "検索中..." : "意味検索を実行"}
        </button>

        {error && (
          <p className="rounded border border-red-200 bg-red-50 p-3 text-sm text-red-800 dark:border-red-900 dark:bg-red-950 dark:text-red-300">
            {error}
          </p>
        )}
      </form>

      {results && (
        <SearchResultList query={results.query} results={results.results} />
      )}
    </div>
  );
}
