/**
 * 環境変数の取得ヘルパ（server-side / Route Handler 専用）。
 *
 * Docker Compose 内ではコンテナ名、ローカル開発では localhost。
 */

export function aiServiceUrl(): string {
  return process.env.AI_SERVICE_URL ?? "http://localhost:8000";
}

export function apiGatewayUrl(): string {
  return process.env.API_GATEWAY_URL ?? "http://localhost:3000";
}
