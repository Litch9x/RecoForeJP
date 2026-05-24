import { notFound } from "next/navigation";

import { hasLocale } from "@/i18n/config";
import { getDictionary } from "@/i18n/dictionaries";

export default async function Home({ params }: PageProps<"/[lang]">) {
  const { lang } = await params;
  if (!hasLocale(lang)) notFound();
  const dict = getDictionary(lang);

  return (
    <div className="flex flex-1 flex-col items-center justify-center bg-zinc-50 font-sans dark:bg-black">
      <main className="flex w-full max-w-3xl flex-1 flex-col gap-10 px-8 py-24 sm:px-16">
        <header className="space-y-2">
          <p className="text-xs uppercase tracking-widest text-zinc-500">
            {dict.common.appName}
          </p>
          <h1 className="text-3xl font-semibold leading-tight tracking-tight text-black dark:text-zinc-50 sm:text-4xl">
            {dict.home.tagline}
          </h1>
          <p className="text-base text-zinc-600 dark:text-zinc-400">
            {dict.home.description}
          </p>
        </header>

        <section className="space-y-3">
          <h2 className="text-xl font-semibold">{dict.home.servicesHeading}</h2>
          <ul className="space-y-1 text-sm text-zinc-700 dark:text-zinc-300">
            <li>
              <span className="font-mono">frontend</span> —{" "}
              {dict.home.services.frontend}
            </li>
            <li>
              <span className="font-mono">api-gateway</span> —{" "}
              {dict.home.services.apiGateway}
            </li>
            <li>
              <span className="font-mono">user-service</span> —{" "}
              {dict.home.services.userService}
            </li>
            <li>
              <span className="font-mono">item-service</span> —{" "}
              {dict.home.services.itemService}
            </li>
            <li>
              <span className="font-mono">ai-service</span> —{" "}
              {dict.home.services.aiService}
            </li>
          </ul>
        </section>

        <section className="space-y-3">
          <h2 className="text-xl font-semibold">{dict.home.screensHeading}</h2>
          <ul className="space-y-1 text-sm">
            <li>
              <a
                href={`/${lang}/recommendations`}
                className="font-medium text-zinc-950 underline-offset-4 hover:underline dark:text-zinc-50"
              >
                /{lang}/recommendations
              </a>{" "}
              — {dict.home.screens.recommendations}
            </li>
            <li>
              <a
                href={`/${lang}/search`}
                className="font-medium text-zinc-950 underline-offset-4 hover:underline dark:text-zinc-50"
              >
                /{lang}/search
              </a>{" "}
              — {dict.home.screens.search}
            </li>
            <li>
              <a
                href="/api/health"
                className="font-medium text-zinc-950 underline-offset-4 hover:underline dark:text-zinc-50"
              >
                /api/health
              </a>{" "}
              — {dict.home.screens.health}
            </li>
          </ul>
        </section>
      </main>
    </div>
  );
}
