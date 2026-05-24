"use client";

import Link from "next/link";
import { useCallback, useEffect, useState, type FormEvent } from "react";

import type { Locale } from "@/i18n/config";
import type { Dictionary } from "@/i18n/dictionaries";
import { clearAuth, readAuth, type StoredAuth } from "@/lib/auth";
import { notifyAuthChange } from "@/lib/use-auth";

interface Item {
  id: string;
  title: string;
  categorySlug?: string;
  categoryNameJa?: string;
  region?: string;
  tags?: string[];
}

interface Props {
  dict: Dictionary["admin"]["items"];
  lang: Locale;
}

type State =
  | { kind: "loading" }
  | { kind: "unauthenticated" }
  | { kind: "forbidden" }
  | { kind: "ready"; items: Item[] }
  | { kind: "error"; message: string };

function csvToList(csv: string): string[] {
  return csv
    .split(",")
    .map((s) => s.trim())
    .filter((s) => s.length > 0);
}

export function AdminItemsView({ dict, lang }: Props) {
  const [state, setState] = useState<State>({ kind: "loading" });
  const [auth, setAuth] = useState<StoredAuth | null>(null);
  const [submitting, setSubmitting] = useState(false);
  const [formError, setFormError] = useState<string | null>(null);

  // form fields
  const [categorySlug, setCategorySlug] = useState("");
  const [title, setTitle] = useState("");
  const [description, setDescription] = useState("");
  const [url, setUrl] = useState("");
  const [region, setRegion] = useState("");
  const [source, setSource] = useState("manual");
  const [minJapaneseLevel, setMinJapaneseLevel] = useState("");
  const [languages, setLanguages] = useState("ja");
  const [tags, setTags] = useState("");

  const fetchItems = useCallback(async (a: StoredAuth) => {
    try {
      const res = await fetch("/api/admin/items", {
        headers: { Authorization: `${a.tokenType} ${a.accessToken}` },
      });
      if (res.status === 401) {
        clearAuth();
        notifyAuthChange();
        return { kind: "unauthenticated" } as State;
      }
      if (res.status === 403) {
        return { kind: "forbidden" } as State;
      }
      if (!res.ok) {
        return { kind: "error", message: `${res.status}` } as State;
      }
      const items = (await res.json()) as Item[];
      return { kind: "ready", items } as State;
    } catch (e) {
      return {
        kind: "error",
        message: e instanceof Error ? e.message : String(e),
      } as State;
    }
  }, []);

  useEffect(() => {
    let cancelled = false;
    void (async () => {
      const a = readAuth();
      if (!a) {
        if (!cancelled) setState({ kind: "unauthenticated" });
        return;
      }
      if (a.role !== "ADMIN") {
        if (!cancelled) setState({ kind: "forbidden" });
        return;
      }
      setAuth(a);
      const next = await fetchItems(a);
      if (!cancelled) setState(next);
    })();
    return () => {
      cancelled = true;
    };
  }, [fetchItems]);

  async function handleAdd(e: FormEvent<HTMLFormElement>) {
    e.preventDefault();
    setFormError(null);
    if (!title.trim()) {
      setFormError(dict.errors.emptyTitle);
      return;
    }
    if (!categorySlug.trim()) {
      setFormError(dict.errors.emptyCategory);
      return;
    }
    if (!auth) return;
    setSubmitting(true);
    try {
      const body: Record<string, unknown> = {
        categorySlug: categorySlug.trim(),
        title: title.trim(),
      };
      if (description.trim()) body.description = description.trim();
      if (url.trim()) body.url = url.trim();
      if (region.trim()) body.region = region.trim();
      if (source.trim()) body.source = source.trim();
      if (minJapaneseLevel.trim()) body.minJapaneseLevel = minJapaneseLevel.trim();
      const langs = csvToList(languages);
      if (langs.length > 0) body.languages = langs;
      const tagList = csvToList(tags);
      if (tagList.length > 0) body.tags = tagList;

      const res = await fetch("/api/admin/items", {
        method: "POST",
        headers: {
          "Content-Type": "application/json",
          Authorization: `${auth.tokenType} ${auth.accessToken}`,
        },
        body: JSON.stringify(body),
      });
      if (!res.ok) {
        const text = await res.text();
        setFormError(`${dict.errors.addFailed} (${res.status}): ${text.slice(0, 200)}`);
        return;
      }
      // reset form + reload list
      setCategorySlug("");
      setTitle("");
      setDescription("");
      setUrl("");
      setRegion("");
      setMinJapaneseLevel("");
      setTags("");
      const next = await fetchItems(auth);
      setState(next);
    } finally {
      setSubmitting(false);
    }
  }

  async function handleDelete(id: string) {
    if (!auth) return;
    if (!window.confirm(dict.deleteConfirm)) return;
    try {
      const res = await fetch(`/api/admin/items/${id}`, {
        method: "DELETE",
        headers: { Authorization: `${auth.tokenType} ${auth.accessToken}` },
      });
      if (!res.ok && res.status !== 204) {
        alert(`${dict.errors.deleteFailed} (${res.status})`);
        return;
      }
      const next = await fetchItems(auth);
      setState(next);
    } catch (e) {
      alert(`${dict.errors.deleteFailed}: ${e instanceof Error ? e.message : e}`);
    }
  }

  if (state.kind === "loading") {
    return <p className="text-sm text-zinc-500">{dict.loading}</p>;
  }
  if (state.kind === "unauthenticated") {
    return (
      <div className="space-y-3 rounded border border-amber-300 bg-amber-50 p-4 text-sm text-amber-900 dark:border-amber-800 dark:bg-amber-950 dark:text-amber-200">
        <Link
          href={`/${lang}/login`}
          className="inline-block rounded bg-amber-900 px-3 py-1 text-white hover:bg-amber-800 dark:bg-amber-200 dark:text-amber-950 dark:hover:bg-amber-100"
        >
          {dict.needAdmin}
        </Link>
      </div>
    );
  }
  if (state.kind === "forbidden") {
    return (
      <p className="rounded border border-red-200 bg-red-50 p-3 text-sm text-red-800 dark:border-red-900 dark:bg-red-950 dark:text-red-300">
        {dict.needAdmin}
      </p>
    );
  }
  if (state.kind === "error") {
    return (
      <p className="rounded border border-red-200 bg-red-50 p-3 text-sm text-red-800 dark:border-red-900 dark:bg-red-950 dark:text-red-300">
        {state.message}
      </p>
    );
  }

  return (
    <div className="space-y-10">
      <section>
        <table className="w-full text-sm">
          <thead className="border-b border-zinc-300 text-left dark:border-zinc-700">
            <tr>
              <th className="py-2 pr-2">{dict.table.title}</th>
              <th className="py-2 pr-2">{dict.table.category}</th>
              <th className="py-2 pr-2">{dict.table.region}</th>
              <th className="py-2 pr-2">{dict.table.tags}</th>
              <th className="py-2 pr-2">{dict.table.actions}</th>
            </tr>
          </thead>
          <tbody>
            {state.items.map((item) => (
              <tr
                key={item.id}
                className="border-b border-zinc-200 dark:border-zinc-800"
              >
                <td className="py-2 pr-2 font-medium">{item.title}</td>
                <td className="py-2 pr-2 text-zinc-600 dark:text-zinc-400">
                  {item.categoryNameJa ?? item.categorySlug ?? "—"}
                </td>
                <td className="py-2 pr-2 text-zinc-600 dark:text-zinc-400">
                  {item.region ?? "—"}
                </td>
                <td className="py-2 pr-2 text-zinc-600 dark:text-zinc-400">
                  {item.tags && item.tags.length > 0 ? item.tags.join(", ") : "—"}
                </td>
                <td className="py-2 pr-2">
                  <button
                    type="button"
                    onClick={() => handleDelete(item.id)}
                    className="rounded border border-red-300 px-2 py-0.5 text-xs text-red-700 hover:bg-red-50 dark:border-red-800 dark:text-red-300 dark:hover:bg-red-950"
                  >
                    {dict.delete}
                  </button>
                </td>
              </tr>
            ))}
          </tbody>
        </table>
      </section>

      <section>
        <h2 className="mb-3 text-lg font-semibold">{dict.addHeading}</h2>
        <form
          onSubmit={handleAdd}
          className="grid gap-3 rounded-lg border border-zinc-200 bg-white p-6 sm:grid-cols-2 dark:border-zinc-800 dark:bg-zinc-950"
        >
          <label className="block sm:col-span-1">
            <span className="text-xs font-medium">{dict.form.categorySlug} *</span>
            <input
              type="text"
              value={categorySlug}
              onChange={(e) => setCategorySlug(e.target.value)}
              className="mt-1 block w-full rounded border border-zinc-300 bg-white px-2 py-1 text-sm dark:border-zinc-700 dark:bg-zinc-900"
            />
            <span className="text-xs text-zinc-500">{dict.form.categoryHint}</span>
          </label>

          <label className="block sm:col-span-1">
            <span className="text-xs font-medium">{dict.form.title} *</span>
            <input
              type="text"
              value={title}
              onChange={(e) => setTitle(e.target.value)}
              className="mt-1 block w-full rounded border border-zinc-300 bg-white px-2 py-1 text-sm dark:border-zinc-700 dark:bg-zinc-900"
            />
          </label>

          <label className="block sm:col-span-2">
            <span className="text-xs font-medium">{dict.form.description}</span>
            <textarea
              value={description}
              onChange={(e) => setDescription(e.target.value)}
              rows={3}
              className="mt-1 block w-full rounded border border-zinc-300 bg-white px-2 py-1 text-sm dark:border-zinc-700 dark:bg-zinc-900"
            />
          </label>

          <label className="block">
            <span className="text-xs font-medium">{dict.form.url}</span>
            <input
              type="url"
              value={url}
              onChange={(e) => setUrl(e.target.value)}
              className="mt-1 block w-full rounded border border-zinc-300 bg-white px-2 py-1 text-sm dark:border-zinc-700 dark:bg-zinc-900"
            />
          </label>

          <label className="block">
            <span className="text-xs font-medium">{dict.form.region}</span>
            <input
              type="text"
              value={region}
              onChange={(e) => setRegion(e.target.value)}
              className="mt-1 block w-full rounded border border-zinc-300 bg-white px-2 py-1 text-sm dark:border-zinc-700 dark:bg-zinc-900"
            />
          </label>

          <label className="block">
            <span className="text-xs font-medium">{dict.form.source}</span>
            <input
              type="text"
              value={source}
              onChange={(e) => setSource(e.target.value)}
              className="mt-1 block w-full rounded border border-zinc-300 bg-white px-2 py-1 text-sm dark:border-zinc-700 dark:bg-zinc-900"
            />
          </label>

          <label className="block">
            <span className="text-xs font-medium">{dict.form.minJapaneseLevel}</span>
            <select
              value={minJapaneseLevel}
              onChange={(e) => setMinJapaneseLevel(e.target.value)}
              className="mt-1 block w-full rounded border border-zinc-300 bg-white px-2 py-1 text-sm dark:border-zinc-700 dark:bg-zinc-900"
            >
              <option value="">—</option>
              <option value="N5">N5</option>
              <option value="N4">N4</option>
              <option value="N3">N3</option>
              <option value="N2">N2</option>
              <option value="N1">N1</option>
            </select>
          </label>

          <label className="block">
            <span className="text-xs font-medium">{dict.form.languages}</span>
            <input
              type="text"
              value={languages}
              onChange={(e) => setLanguages(e.target.value)}
              className="mt-1 block w-full rounded border border-zinc-300 bg-white px-2 py-1 text-sm dark:border-zinc-700 dark:bg-zinc-900"
            />
            <span className="text-xs text-zinc-500">{dict.form.languagesHint}</span>
          </label>

          <label className="block sm:col-span-2">
            <span className="text-xs font-medium">{dict.form.tags}</span>
            <input
              type="text"
              value={tags}
              onChange={(e) => setTags(e.target.value)}
              className="mt-1 block w-full rounded border border-zinc-300 bg-white px-2 py-1 text-sm dark:border-zinc-700 dark:bg-zinc-900"
            />
            <span className="text-xs text-zinc-500">{dict.form.tagsHint}</span>
          </label>

          <div className="sm:col-span-2">
            <button
              type="submit"
              disabled={submitting}
              className="rounded bg-black px-4 py-2 text-sm font-medium text-white hover:opacity-90 disabled:opacity-50 dark:bg-white dark:text-black"
            >
              {submitting ? dict.form.submitting : dict.form.submit}
            </button>
          </div>

          {formError && (
            <p className="sm:col-span-2 rounded border border-red-200 bg-red-50 p-3 text-sm text-red-800 dark:border-red-900 dark:bg-red-950 dark:text-red-300">
              {formError}
            </p>
          )}
        </form>
      </section>
    </div>
  );
}
