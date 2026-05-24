/** JWT 検証成功後に req に詰める認証済みユーザー情報。 */
export interface AuthUser {
  userId: string;
  email: string;
}
