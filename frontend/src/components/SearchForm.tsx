"use client";

import { useState, type FormEvent } from "react";

import type { Dictionary } from "@/i18n/dictionaries";
import type {
  SemanticSearchRequest,
  SemanticSearchResponse,
} from "@/lib/search-types";
import { SearchResultList } from "./SearchResultList";

interface Props {
  dict: Dictionary["search"];
}

export function SearchForm({ dict }: Props) {
  const [query, setQuery] = useState("");
  const [limit, setLimit] = useState(10);

  const [loading, setLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);
  const [results, setResults] = useState<SemanticSearchResponse | null>(null);

  async function handleSubmit(event: FormEvent<HTMLFormElement>) {
    event.preventDefault();
    if (!query.trim()) {
      setError(dict.form.emptyQueryError);
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
        setError(`${dict.form.errorPrefix} (${response.status}): ${text}`);
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
          <span className="text-sm font-medium">{dict.form.queryLabel}</span>
          <input
            type="text"
            value={query}
            onChange={(e) => setQuery(e.target.value)}
            placeholder={dict.form.queryPlaceholder}
            autoFocus
            className="mt-1 block w-full rounded border border-zinc-300 bg-white px-3 py-2 text-sm dark:border-zinc-700 dark:bg-zinc-900"
          />
        </label>

        <div className="flex flex-wrap gap-2">
          <span className="text-xs text-zinc-500">{dict.form.samplesLabel}</span>
          {dict.samples.map((ex) => (
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
          <span className="text-sm font-medium">
            {dict.form.limitLabel}: {limit}
          </span>
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
          {loading ? dict.form.submitting : dict.form.submit}
        </button>

        {error && (
          <p className="rounded border border-red-200 bg-red-50 p-3 text-sm text-red-800 dark:border-red-900 dark:bg-red-950 dark:text-red-300">
            {error}
          </p>
        )}
      </form>

      {results && (
        <SearchResultList
          dict={dict.results}
          query={results.query}
          results={results.results}
        />
      )}
    </div>
  );
}
