/**
 * Client / Server / Middleware 共通の i18n 定数。
 * 辞書本体（メッセージ JSON）は {@link "./dictionaries"} を参照（server-only）。
 */
export const locales = ["ja", "en"] as const;
export type Locale = (typeof locales)[number];
export const defaultLocale: Locale = "ja";

export function hasLocale(value: string): value is Locale {
  return (locales as readonly string[]).includes(value);
}
