// /api/search
// Browser → Next API → api-gateway /search/items → ai-service へ。
// 当初は ai-service 直結だったが、全トラフィックを gateway 経由に統一するため切替済み。

import { apiGatewayUrl } from "@/lib/config";

export async function POST(request: Request) {
  const body = await request.text();

  let upstream: Response;
  try {
    upstream = await fetch(`${apiGatewayUrl()}/search/items`, {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body,
      cache: "no-store",
    });
  } catch (err) {
    return Response.json(
      {
        error: "API_GATEWAY_UNAVAILABLE",
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
