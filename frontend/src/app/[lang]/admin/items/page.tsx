import { notFound } from "next/navigation";

import { AdminItemsView } from "@/components/AdminItemsView";
import { hasLocale } from "@/i18n/config";
import { getDictionary } from "@/i18n/dictionaries";

export default async function AdminItemsPage({ params }: PageProps<"/[lang]">) {
  const { lang } = await params;
  if (!hasLocale(lang)) notFound();
  const dict = getDictionary(lang);

  return (
    <div className="flex flex-1 flex-col bg-zinc-50 dark:bg-black">
      <main className="mx-auto w-full max-w-5xl space-y-6 px-6 py-12 sm:px-10">
        <header className="space-y-2">
          <p className="text-xs uppercase tracking-widest text-zinc-500">
            {dict.common.appName} / Admin
          </p>
          <h1 className="text-2xl font-semibold tracking-tight">
            {dict.admin.items.title}
          </h1>
          <p className="text-sm text-zinc-600 dark:text-zinc-400">
            {dict.admin.items.description}
          </p>
        </header>
        <AdminItemsView dict={dict.admin.items} lang={lang} />
      </main>
    </div>
  );
}
