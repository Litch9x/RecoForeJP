import type { Metadata } from "next";
import { Geist, Geist_Mono } from "next/font/google";
import { notFound } from "next/navigation";

import { LanguageSwitcher } from "@/components/LanguageSwitcher";
import { hasLocale } from "@/i18n/config";
import { getDictionary } from "@/i18n/dictionaries";
import "../globals.css";

const geistSans = Geist({
  variable: "--font-geist-sans",
  subsets: ["latin"],
});

const geistMono = Geist_Mono({
  variable: "--font-geist-mono",
  subsets: ["latin"],
});

export const metadata: Metadata = {
  title: "RecoForeJP",
  description:
    "AI-powered personalized recommendation system for foreigners in Japan.",
};

export default async function LocalizedRootLayout({
  children,
  params,
}: LayoutProps<"/[lang]">) {
  const { lang } = await params;
  if (!hasLocale(lang)) notFound();
  const dict = getDictionary(lang);

  return (
    <html
      lang={lang}
      className={`${geistSans.variable} ${geistMono.variable} h-full antialiased`}
    >
      <body className="min-h-full flex flex-col">
        <header className="flex items-center justify-between border-b border-zinc-200 bg-white px-6 py-3 text-sm dark:border-zinc-800 dark:bg-zinc-950">
          <span className="font-mono text-xs uppercase tracking-widest text-zinc-500">
            {dict.common.appName}
          </span>
          <LanguageSwitcher current={lang} label={dict.common.languageLabel} />
        </header>
        {children}
      </body>
    </html>
  );
}
