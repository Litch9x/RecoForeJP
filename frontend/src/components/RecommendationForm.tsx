"use client";

import { useState, type FormEvent } from "react";

import type { Dictionary } from "@/i18n/dictionaries";
import type {
  HybridRecommendRequest,
  HybridRecommendResponse,
  JapaneseLevel,
} from "@/lib/recommend-types";
import { RecommendationList } from "./RecommendationList";

interface Props {
  dict: Dictionary["recommend"];
}

// 既知のシードカテゴリ slug（infra/postgres/init/10-seed-categories.sql 参照）。
// 表示ラベルは dict から引く（後方互換: japaneseLearning ↔ japanese-learning など）。
const INTEREST_SLUGS = [
  "job",
  "housing",
  "admin",
  "medical",
  "japanese-learning",
  "community-event",
] as const;

type InterestSlug = (typeof INTEREST_SLUGS)[number];

const INTEREST_DICT_KEY: Record<InterestSlug, keyof Dictionary["recommend"]["form"]["interests"]> = {
  job: "job",
  housing: "housing",
  admin: "admin",
  medical: "medical",
  "japanese-learning": "japaneseLearning",
  "community-event": "communityEvent",
};

const LANGUAGES = [
  { code: "ja", label: "日本語" },
  { code: "en", label: "English" },
  { code: "vi", label: "Tiếng Việt" },
  { code: "zh-CN", label: "中文" },
];

export function RecommendationForm({ dict }: Props) {
  const [japaneseLevel, setJapaneseLevel] = useState<JapaneseLevel | "">("N3");
  const [region, setRegion] = useState("");
  const [preferredLanguage, setPreferredLanguage] = useState("ja");
  const [interests, setInterests] = useState<string[]>(["job"]);
  const [query, setQuery] = useState("");
  const [weightContent, setWeightContent] = useState(0.5);
  const [weightSemantic, setWeightSemantic] = useState(0.5);

  const [loading, setLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);
  const [results, setResults] = useState<HybridRecommendResponse | null>(null);

  function toggleInterest(slug: string) {
    setInterests((current) =>
      current.includes(slug)
        ? current.filter((s) => s !== slug)
        : [...current, slug],
    );
  }

  async function handleSubmit(event: FormEvent<HTMLFormElement>) {
    event.preventDefault();
    setLoading(true);
    setError(null);
    setResults(null);

    const payload: HybridRecommendRequest = {
      user: {
        japanese_level: japaneseLevel || null,
        region: region.trim() || null,
        preferred_language: preferredLanguage,
        interest_categories: interests,
      },
      query: query.trim() || null,
      region: null,
      limit: 10,
      weight_content: weightContent,
      weight_semantic: weightSemantic,
    };

    try {
      const response = await fetch("/api/recommendations", {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify(payload),
      });

      if (!response.ok) {
        const text = await response.text();
        setError(`${dict.form.errorPrefix} (${response.status}): ${text}`);
        return;
      }

      const data = (await response.json()) as HybridRecommendResponse;
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
        className="space-y-6 rounded-lg border border-zinc-200 bg-white p-6 dark:border-zinc-800 dark:bg-zinc-950"
      >
        <div className="grid gap-4 sm:grid-cols-2">
          <label className="block">
            <span className="text-sm font-medium">{dict.form.jlptLabel}</span>
            <select
              value={japaneseLevel}
              onChange={(e) =>
                setJapaneseLevel(e.target.value as JapaneseLevel | "")
              }
              className="mt-1 block w-full rounded border border-zinc-300 bg-white px-3 py-2 text-sm dark:border-zinc-700 dark:bg-zinc-900"
            >
              <option value="">{dict.form.jlptUnspecified}</option>
              <option value="N5">N5 ({dict.form.jlptN5Hint})</option>
              <option value="N4">N4</option>
              <option value="N3">N3</option>
              <option value="N2">N2</option>
              <option value="N1">N1 ({dict.form.jlptN1Hint})</option>
            </select>
          </label>

          <label className="block">
            <span className="text-sm font-medium">
              {dict.form.preferredLanguageLabel}
            </span>
            <select
              value={preferredLanguage}
              onChange={(e) => setPreferredLanguage(e.target.value)}
              className="mt-1 block w-full rounded border border-zinc-300 bg-white px-3 py-2 text-sm dark:border-zinc-700 dark:bg-zinc-900"
            >
              {LANGUAGES.map((l) => (
                <option key={l.code} value={l.code}>
                  {l.label} ({l.code})
                </option>
              ))}
            </select>
          </label>

          <label className="block sm:col-span-2">
            <span className="text-sm font-medium">{dict.form.regionLabel}</span>
            <input
              type="text"
              value={region}
              onChange={(e) => setRegion(e.target.value)}
              placeholder={dict.form.regionPlaceholder}
              className="mt-1 block w-full rounded border border-zinc-300 bg-white px-3 py-2 text-sm dark:border-zinc-700 dark:bg-zinc-900"
            />
          </label>
        </div>

        <fieldset>
          <legend className="text-sm font-medium">
            {dict.form.interestsLegend}
          </legend>
          <div className="mt-2 flex flex-wrap gap-2">
            {INTEREST_SLUGS.map((slug) => {
              const selected = interests.includes(slug);
              const label = dict.form.interests[INTEREST_DICT_KEY[slug]];
              return (
                <button
                  type="button"
                  key={slug}
                  onClick={() => toggleInterest(slug)}
                  className={`rounded-full border px-3 py-1 text-sm transition-colors ${
                    selected
                      ? "border-zinc-900 bg-zinc-900 text-white dark:border-zinc-100 dark:bg-zinc-100 dark:text-black"
                      : "border-zinc-300 bg-white text-zinc-700 hover:bg-zinc-50 dark:border-zinc-700 dark:bg-zinc-900 dark:text-zinc-300 dark:hover:bg-zinc-800"
                  }`}
                >
                  {label}
                </button>
              );
            })}
          </div>
        </fieldset>

        <label className="block">
          <span className="text-sm font-medium">{dict.form.queryLabel}</span>
          <input
            type="text"
            value={query}
            onChange={(e) => setQuery(e.target.value)}
            placeholder={dict.form.queryPlaceholder}
            className="mt-1 block w-full rounded border border-zinc-300 bg-white px-3 py-2 text-sm dark:border-zinc-700 dark:bg-zinc-900"
          />
          <span className="mt-1 block text-xs text-zinc-500">
            {dict.form.queryHint}
          </span>
        </label>

        <div className="grid gap-4 sm:grid-cols-2">
          <label className="block">
            <span className="text-sm font-medium">
              {dict.form.contentWeightLabel}: {weightContent.toFixed(2)}
            </span>
            <input
              type="range"
              min={0}
              max={1}
              step={0.1}
              value={weightContent}
              onChange={(e) => setWeightContent(Number(e.target.value))}
              className="mt-1 block w-full"
            />
          </label>

          <label className="block">
            <span className="text-sm font-medium">
              {dict.form.semanticWeightLabel}: {weightSemantic.toFixed(2)}
            </span>
            <input
              type="range"
              min={0}
              max={1}
              step={0.1}
              value={weightSemantic}
              onChange={(e) => setWeightSemantic(Number(e.target.value))}
              className="mt-1 block w-full"
            />
          </label>
        </div>

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

      {results && <RecommendationList dict={dict.results} items={results.items} />}
    </div>
  );
}
