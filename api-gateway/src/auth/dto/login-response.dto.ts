import type { Role } from "../auth-user";

/**
 * ログイン成功時のレスポンス。
 * - accessToken: 署名済み JWT (subject = userId, role クレーム入り)
 * - tokenType: 常に "Bearer"
 * - expiresIn: 秒単位の有効期限
 * - role: フロントが UI 切替に使う（admin メニュー表示等）
 */
export interface LoginResponse {
  accessToken: string;
  tokenType: "Bearer";
  expiresIn: number;
  userId: string;
  email: string;
  role: Role;
}
