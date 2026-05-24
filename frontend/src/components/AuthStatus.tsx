"use client";

import Link from "next/link";
import { useRouter } from "next/navigation";
import { useEffect, useState } from "react";

import type { Locale } from "@/i18n/config";
import type { Dictionary } from "@/i18n/dictionaries";
import { clearAuth, readAuth } from "@/lib/auth";

interface Props {
  lang: Locale;
  dict: Dictionary["auth"];
}

/**
 * ヘッダ右の認証状態表示。SSR 時は何も描画せず、マウント後に localStorage を読む。
 * （SSR と最初の hydrate で同じ DOM になるよう、初期値は常に未認証扱い）
 */
export function AuthStatus({ lang, dict }: Props) {
  const [email, setEmail] = useState<string | null>(null);
  const [mounted, setMounted] = useState(false);
  const router = useRouter();

  useEffect(() => {
    setMounted(true);
    const auth = readAuth();
    setEmail(auth?.email ?? null);
  }, []);

  if (!mounted) return null;

  if (!email) {
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
        {dict.loggedInAs}: <span className="text-zinc-700 dark:text-zinc-300">{email}</span>
      </span>
      <button
        type="button"
        onClick={() => {
          clearAuth();
          setEmail(null);
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
