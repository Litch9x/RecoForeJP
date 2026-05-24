"use client";

import Link from "next/link";
import { useEffect, useState } from "react";

import type { Locale } from "@/i18n/config";
import type { Dictionary } from "@/i18n/dictionaries";
import { clearAuth, readAuth } from "@/lib/auth";

interface ProfilePayload {
  jlpt?: string | null;
  region?: string | null;
  interests?: string[] | null;
}

interface Props {
  dict: Dictionary["me"];
  lang: Locale;
}

type State =
  | { kind: "loading" }
  | { kind: "unauthenticated" }
  | { kind: "ready"; email: string; userId: string; profile: ProfilePayload | null }
  | { kind: "error"; message: string };

export function MeView({ dict, lang }: Props) {
  const [state, setState] = useState<State>({ kind: "loading" });

  useEffect(() => {
    const auth = readAuth();
    if (!auth) {
      setState({ kind: "unauthenticated" });
      return;
    }
    let cancelled = false;
    (async () => {
      try {
        const res = await fetch("/api/auth/me", {
          headers: { Authorization: `${auth.tokenType} ${auth.accessToken}` },
        });
        if (cancelled) return;
        if (res.status === 401) {
          clearAuth();
          setState({ kind: "unauthenticated" });
          return;
        }
        if (res.status === 404) {
          // user-service: プロフィール未設定でも 200 で空が返るので 404 はまれ
          setState({
            kind: "ready",
            email: auth.email,
            userId: auth.userId,
            profile: null,
          });
          return;
        }
        if (!res.ok) {
          setState({ kind: "error", message: `${res.status}` });
          return;
        }
        const profile = (await res.json()) as ProfilePayload;
        setState({
          kind: "ready",
          email: auth.email,
          userId: auth.userId,
          profile,
        });
      } catch (e) {
        if (cancelled) return;
        setState({
          kind: "error",
          message: e instanceof Error ? e.message : String(e),
        });
      }
    })();
    return () => {
      cancelled = true;
    };
  }, []);

  if (state.kind === "loading") {
    return <p className="text-sm text-zinc-500">{dict.loading}</p>;
  }
  if (state.kind === "unauthenticated") {
    return (
      <div className="space-y-3 rounded border border-amber-300 bg-amber-50 p-4 text-sm text-amber-900 dark:border-amber-800 dark:bg-amber-950 dark:text-amber-200">
        <p>{dict.needLogin}</p>
        <Link
          href={`/${lang}/login`}
          className="inline-block rounded bg-amber-900 px-3 py-1 text-white hover:bg-amber-800 dark:bg-amber-200 dark:text-amber-950 dark:hover:bg-amber-100"
        >
          {dict.goLogin}
        </Link>
      </div>
    );
  }
  if (state.kind === "error") {
    return (
      <p className="rounded border border-red-200 bg-red-50 p-3 text-sm text-red-800 dark:border-red-900 dark:bg-red-950 dark:text-red-300">
        {state.message}
      </p>
    );
  }

  const { profile } = state;
  return (
    <dl className="grid grid-cols-3 gap-x-4 gap-y-2 rounded-lg border border-zinc-200 bg-white p-6 text-sm dark:border-zinc-800 dark:bg-zinc-950">
      <dt className="text-zinc-500">{dict.userId}</dt>
      <dd className="col-span-2 font-mono">{state.userId}</dd>

      <dt className="text-zinc-500">{dict.email}</dt>
      <dd className="col-span-2">{state.email}</dd>

      {profile === null ? (
        <>
          <dt className="text-zinc-500">{dict.jlpt}</dt>
          <dd className="col-span-2 text-zinc-400">{dict.noProfile}</dd>
        </>
      ) : (
        <>
          <dt className="text-zinc-500">{dict.jlpt}</dt>
          <dd className="col-span-2">{profile.jlpt ?? "—"}</dd>
          <dt className="text-zinc-500">{dict.region}</dt>
          <dd className="col-span-2">{profile.region ?? "—"}</dd>
          <dt className="text-zinc-500">{dict.interests}</dt>
          <dd className="col-span-2">
            {profile.interests && profile.interests.length > 0
              ? profile.interests.join(", ")
              : "—"}
          </dd>
        </>
      )}
    </dl>
  );
}
