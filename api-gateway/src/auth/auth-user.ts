/** RBAC ロール。user-service の {@code UserRole} と一致。 */
export type Role = "USER" | "ADMIN";

/** JWT 検証成功後に req に詰める認証済みユーザー情報。 */
export interface AuthUser {
  userId: string;
  email: string;
  role: Role;
}
