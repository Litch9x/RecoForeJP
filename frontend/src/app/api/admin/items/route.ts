// /api/admin/items
// Browser → Next API → api-gateway /admin/items (GET, POST) の薄い proxy。
// Authorization: Bearer ヘッダをそのまま転送。

import { apiGatewayUrl } from "@/lib/config";

async function proxy(method: "GET" | "POST", request: Request): Promise<Response> {
  const authorization = request.headers.get("authorization");
  if (!authorization) {
    return Response.json({ error: "MISSING_AUTHORIZATION" }, { status: 401 });
  }

  const init: RequestInit = {
    method,
    headers: { Authorization: authorization },
    cache: "no-store",
  };
  if (method === "POST") {
    init.headers = {
      ...init.headers,
      "Content-Type": "application/json",
    } as HeadersInit;
    init.body = await request.text();
  }

  let upstream: Response;
  try {
    upstream = await fetch(`${apiGatewayUrl()}/admin/items`, init);
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
  const noBody = upstream.status === 204 || upstream.status === 205 || upstream.status === 304;
  return new Response(noBody || text.length === 0 ? null : text, {
    status: upstream.status,
    headers: noBody ? undefined : { "Content-Type": "application/json" },
  });
}

export const GET = (req: Request) => proxy("GET", req);
export const POST = (req: Request) => proxy("POST", req);
