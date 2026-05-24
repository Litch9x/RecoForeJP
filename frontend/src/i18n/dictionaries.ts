import "server-only";

import { type Locale } from "./config";
import enMessages from "./messages/en.json";
import jaMessages from "./messages/ja.json";

export type Dictionary = typeof jaMessages;

const dictionaries: Record<Locale, Dictionary> = {
  ja: jaMessages,
  en: enMessages,
};

/**
 * 静的 import を使う（dict は数 KB なので bundle 影響なし）。
 * server-only マーカーでクライアント漏出を防ぐ。
 */
export function getDictionary(locale: Locale): Dictionary {
  return dictionaries[locale];
}
