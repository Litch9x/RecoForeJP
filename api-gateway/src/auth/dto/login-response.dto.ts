/**
 * ログイン成功時のレスポンス。
 * - accessToken: 署名済み JWT (subject = userId)
 * - tokenType: 常に "Bearer"
 * - expiresIn: 秒単位の有効期限
 */
export interface LoginResponse {
  accessToken: string;
  tokenType: "Bearer";
  expiresIn: number;
  userId: string;
  email: string;
}
