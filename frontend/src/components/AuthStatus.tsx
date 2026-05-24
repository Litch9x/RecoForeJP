"use client";

import Link from "next/link";
import { useRouter } from "next/navigation";

import type { Locale } from "@/i18n/config";
import type { Dictionary } from "@/i18n/dictionaries";
import { clearAuth } from "@/lib/auth";
import { notifyAuthChange, useAuth } from "@/lib/use-auth";

interface Props {
  lang: Locale;
  dict: Dictionary["auth"];
}

/**
 * ヘッダ右の認証状態表示。useAuth が SSR では null を返すので、
 * hydrate 前後で「ログイン」リンク → ログイン中表示、と差し替わる。
 */
export function AuthStatus({ lang, dict }: Props) {
  const auth = useAuth();
  const router = useRouter();

  if (!auth) {
    return (
      <Link
        href={`/${lang}/login`}
        className="rounded border border-zinc-300 px-2 py-0.5 text-xs text-zinc-700 hover:bg-zinc-100 dark:border-zinc-700 dark:text-zinc-300 dark:hover:bg-zinc-800"
      >
        {dict.loginLink}
      </Link>
    );
  }

  return (
    <div className="flex items-center gap-2 text-xs">
      <span className="text-zinc-500">
        {dict.loggedInAs}:{" "}
        <span className="text-zinc-700 dark:text-zinc-300">{auth.email}</span>
      </span>
      <button
        type="button"
        onClick={() => {
          clearAuth();
          notifyAuthChange();
          router.push(`/${lang}`);
          router.refresh();
        }}
        className="rounded border border-zinc-300 px-2 py-0.5 text-zinc-700 hover:bg-zinc-100 dark:border-zinc-700 dark:text-zinc-300 dark:hover:bg-zinc-800"
      >
        {dict.logout}
      </button>
    </div>
  );
}
