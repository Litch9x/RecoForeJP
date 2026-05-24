import { NextResponse, type NextRequest } from "next/server";

import { defaultLocale, locales, type Locale } from "@/i18n/config";

/**
 * Accept-Language ヘッダから優先 locale を粗く推定する。
 * 厳密な BCP47 マッチングは @formatjs/intl-localematcher を別途導入する想定だが、
 * 現在は ja/en の 2 つだけなので "en" を含むかどうかで判定する。
 */
function detectLocale(request: NextRequest): Locale {
  const header = request.headers.get("accept-language") ?? "";
  const primary = header.split(",")[0]?.toLowerCase() ?? "";
  if (primary.startsWith("en")) return "en";
  return defaultLocale;
}

/**
 * Next.js 16 の proxy.ts（旧 middleware）。
 * locale プレフィックス（/ja, /en）が無いパスへのアクセスは、
 * Accept-Language から推定した locale を付けてリダイレクトする。
 */
export function proxy(request: NextRequest) {
  const { pathname } = request.nextUrl;

  const hasLocale = locales.some(
    (l) => pathname === `/${l}` || pathname.startsWith(`/${l}/`),
  );
  if (hasLocale) return;

  const locale = detectLocale(request);
  const url = request.nextUrl.clone();
  url.pathname = pathname === "/" ? `/${locale}` : `/${locale}${pathname}`;
  return NextResponse.redirect(url);
}

export const config = {
  // /api と Next.js 内部資産は除外する
  matcher: ["/((?!api|_next/static|_next/image|favicon.ico).*)"],
};
