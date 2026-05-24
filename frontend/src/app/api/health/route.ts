// ヘルスチェック用 Route Handler。他サービス（api-gateway, user-service, item-service, ai-service）
// と同じレスポンス形式を返す。
//
// ref: node_modules/next/dist/docs/01-app/01-getting-started/15-route-handlers.md

export function GET() {
  return Response.json({
    status: "ok",
    service: "frontend",
    timestamp: new Date().toISOString(),
  });
}
