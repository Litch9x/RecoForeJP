// /api/auth/login
// Browser → Next API → api-gateway /auth/login の薄いプロキシ。
// CORS 回避と API_GATEWAY_URL 隠蔽が目的。

import { apiGatewayUrl } from "@/lib/config";

export async function POST(request: Request) {
  const body = await request.text();

  let upstream: Response;
  try {
    upstream = await fetch(`${apiGatewayUrl()}/auth/login`, {
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

  const text = await upstream.text();
  return new Response(text, {
    status: upstream.status,
    headers: { "Content-Type": "application/json" },
  });
}
