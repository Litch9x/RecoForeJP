// /api/recommendations
// Browser からのリクエストをサーバー側で受け、ai-service の /recommend/hybrid に転送する。
// 利点:
//   - CORS を気にしなくて済む（同一オリジン）
//   - AI_SERVICE_URL を環境変数で差し替えやすい
//   - 必要なら今後ここに認証・レート制限・キャッシュを足せる

import { aiServiceUrl } from "@/lib/config";

export async function POST(request: Request) {
  const body = await request.text();

  let upstream: Response;
  try {
    upstream = await fetch(`${aiServiceUrl()}/recommend/hybrid`, {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body,
      cache: "no-store",
    });
  } catch (err) {
    return Response.json(
      {
        error: "AI_SERVICE_UNAVAILABLE",
        message: err instanceof Error ? err.message : String(err),
      },
      { status: 502 },
    );
  }

  const data = await upstream.text();
  return new Response(data, {
    status: upstream.status,
    headers: { "Content-Type": "application/json" },
  });
}
