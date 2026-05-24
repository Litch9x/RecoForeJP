/**
 * 環境変数の取得ヘルパ。
 *
 * `AI_SERVICE_URL` は server-side（Route Handler）でのみ参照する。
 * Docker Compose 内では `http://ai-service:8000`、ローカル開発では `http://localhost:8000`。
 */

export function aiServiceUrl(): string {
  return process.env.AI_SERVICE_URL ?? "http://localhost:8000";
}
