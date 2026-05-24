"use client";

import Link from "next/link";
import { usePathname } from "next/navigation";

import { locales, type Locale } from "@/i18n/config";

interface Props {
  current: Locale;
  label: string;
}

/**
 * 現在のパスから locale セグメント（先頭の {@code /ja} or {@code /en}）を抜き、
 * 各 locale の同じパスへのリンクを並べる。
 */
export function LanguageSwitcher({ current, label }: Props) {
  const pathname = usePathname();
  // /ja/search → /search、/en → ""
  const stripped = pathname.replace(/^\/(ja|en)(?=\/|$)/, "") || "";

  return (
    <nav aria-label={label} className="flex items-center gap-2 text-xs">
      <span className="text-zinc-500">{label}:</span>
      {locales.map((locale) => {
        const href = stripped ? `/${locale}${stripped}` : `/${locale}`;
        const active = locale === current;
        return (
          <Link
            key={locale}
            href={href}
            aria-current={active ? "true" : undefined}
            className={
              active
                ? "rounded bg-zinc-900 px-2 py-0.5 text-zinc-50 dark:bg-zinc-50 dark:text-zinc-900"
                : "rounded border border-zinc-300 px-2 py-0.5 text-zinc-700 hover:bg-zinc-100 dark:border-zinc-700 dark:text-zinc-300 dark:hover:bg-zinc-800"
            }
          >
            {locale.toUpperCase()}
          </Link>
        );
      })}
    </nav>
  );
}
