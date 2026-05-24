// /api/search
// Browser からの意味検索リクエストを ai-service /search/items に server-side で転送。
// /api/recommendations と同じパターン（CORS 回避、env で接続先差し替え）。

import { aiServiceUrl } from "@/lib/config";

export async function POST(request: Request) {
  const body = await request.text();

  let upstream: Response;
  try {
    upstream = await fetch(`${aiServiceUrl()}/search/items`, {
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
