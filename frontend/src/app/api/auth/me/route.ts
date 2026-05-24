// /api/auth/me
// Browser → Next API → api-gateway /me/profile の薄いプロキシ。
// クライアントの Authorization: Bearer ヘッダをそのまま上流に転送する。

import { apiGatewayUrl } from "@/lib/config";

export async function GET(request: Request) {
  const authorization = request.headers.get("authorization");
  if (!authorization) {
    return Response.json(
      { error: "MISSING_AUTHORIZATION" },
      { status: 401 },
    );
  }

  let upstream: Response;
  try {
    upstream = await fetch(`${apiGatewayUrl()}/me/profile`, {
      method: "GET",
      headers: { Authorization: authorization },
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
