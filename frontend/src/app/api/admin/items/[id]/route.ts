// /api/admin/items/[id]
// Browser → Next API → api-gateway /admin/items/{id} (GET, PUT, DELETE) の薄い proxy。

import { apiGatewayUrl } from "@/lib/config";

interface Params {
  params: Promise<{ id: string }>;
}

async function proxy(
  method: "GET" | "PUT" | "DELETE",
  request: Request,
  ctx: Params,
): Promise<Response> {
  const authorization = request.headers.get("authorization");
  if (!authorization) {
    return Response.json({ error: "MISSING_AUTHORIZATION" }, { status: 401 });
  }
  const { id } = await ctx.params;

  const init: RequestInit = {
    method,
    headers: { Authorization: authorization },
    cache: "no-store",
  };
  if (method === "PUT") {
    init.headers = {
      ...init.headers,
      "Content-Type": "application/json",
    } as HeadersInit;
    init.body = await request.text();
  }

  let upstream: Response;
  try {
    upstream = await fetch(`${apiGatewayUrl()}/admin/items/${id}`, init);
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
  // 204 / 205 / 304 は body 不可（Response constructor が TypeError を投げる）
  const noBody = upstream.status === 204 || upstream.status === 205 || upstream.status === 304;
  return new Response(noBody || text.length === 0 ? null : text, {
    status: upstream.status,
    headers: noBody ? undefined : { "Content-Type": "application/json" },
  });
}

export const GET = (req: Request, ctx: Params) => proxy("GET", req, ctx);
export const PUT = (req: Request, ctx: Params) => proxy("PUT", req, ctx);
export const DELETE = (req: Request, ctx: Params) => proxy("DELETE", req, ctx);
