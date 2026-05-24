"use client";

import { useRouter } from "next/navigation";
import { useState, type FormEvent } from "react";

import type { Locale } from "@/i18n/config";
import type { Dictionary } from "@/i18n/dictionaries";
import { computeExpiresAt, writeAuth } from "@/lib/auth";
import { notifyAuthChange } from "@/lib/use-auth";

interface LoginResponse {
  accessToken: string;
  tokenType: "Bearer";
  expiresIn: number;
  userId: string;
  email: string;
}

interface Props {
  dict: Dictionary["login"];
  lang: Locale;
}

export function LoginForm({ dict, lang }: Props) {
  const router = useRouter();
  const [email, setEmail] = useState("");
  const [password, setPassword] = useState("");
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);

  async function handleSubmit(event: FormEvent<HTMLFormElement>) {
    event.preventDefault();
    setError(null);
    if (!email.trim() || !password) {
      setError(dict.errors.emptyFields);
      return;
    }
    setLoading(true);
    try {
      const res = await fetch("/api/auth/login", {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({ email: email.trim(), password }),
      });
      if (res.status === 401) {
        setError(dict.errors.unauthorized);
        return;
      }
      if (res.status === 502) {
        setError(dict.errors.unavailable);
        return;
      }
      if (!res.ok) {
        setError(`${dict.errors.unknown} (${res.status})`);
        return;
      }
      const data = (await res.json()) as LoginResponse;
      writeAuth({
        accessToken: data.accessToken,
        tokenType: data.tokenType,
        expiresAt: computeExpiresAt(data.expiresIn),
        userId: data.userId,
        email: data.email,
      });
      notifyAuthChange();
      router.push(`/${lang}/me`);
      router.refresh();
    } catch (err) {
      setError(err instanceof Error ? err.message : String(err));
    } finally {
      setLoading(false);
    }
  }

  return (
    <form
      onSubmit={handleSubmit}
      className="space-y-4 rounded-lg border border-zinc-200 bg-white p-6 dark:border-zinc-800 dark:bg-zinc-950"
    >
      <label className="block">
        <span className="text-sm font-medium">{dict.emailLabel}</span>
        <input
          type="email"
          value={email}
          onChange={(e) => setEmail(e.target.value)}
          autoComplete="email"
          autoFocus
          className="mt-1 block w-full rounded border border-zinc-300 bg-white px-3 py-2 text-sm dark:border-zinc-700 dark:bg-zinc-900"
        />
      </label>

      <label className="block">
        <span className="text-sm font-medium">{dict.passwordLabel}</span>
        <input
          type="password"
          value={password}
          onChange={(e) => setPassword(e.target.value)}
          autoComplete="current-password"
          className="mt-1 block w-full rounded border border-zinc-300 bg-white px-3 py-2 text-sm dark:border-zinc-700 dark:bg-zinc-900"
        />
      </label>

      <button
        type="submit"
        disabled={loading}
        className="w-full rounded bg-black px-4 py-2 text-sm font-medium text-white transition-opacity hover:opacity-90 disabled:opacity-50 dark:bg-white dark:text-black sm:w-auto"
      >
        {loading ? dict.submitting : dict.submit}
      </button>

      {error && (
        <p className="rounded border border-red-200 bg-red-50 p-3 text-sm text-red-800 dark:border-red-900 dark:bg-red-950 dark:text-red-300">
          {error}
        </p>
      )}
    </form>
  );
}
