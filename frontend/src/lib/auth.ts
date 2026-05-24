/**
 * クライアント側の JWT トークン管理（localStorage）。
 *
 * NOTE: XSS 耐性は localStorage より httpOnly Cookie のほうが高いが、
 * MVP では実装のシンプルさを優先。次ステップで httpOnly Cookie へ移行可能。
 */

const STORAGE_KEY = "recoforejp.auth";

export type Role = "USER" | "ADMIN";

export interface StoredAuth {
  accessToken: string;
  tokenType: "Bearer";
  expiresAt: number; // epoch ms
  userId: string;
  email: string;
  role: Role;
}

export function readAuth(): StoredAuth | null {
  if (typeof window === "undefined") return null;
  const raw = window.localStorage.getItem(STORAGE_KEY);
  if (!raw) return null;
  try {
    const parsed = JSON.parse(raw) as Partial<StoredAuth>;
    if (!parsed.accessToken || !parsed.expiresAt) return null;
    if (parsed.expiresAt < Date.now()) {
      clearAuth();
      return null;
    }
    // role が無い旧データは USER として扱う（後方互換）
    return { ...parsed, role: parsed.role ?? "USER" } as StoredAuth;
  } catch {
    return null;
  }
}

export function writeAuth(auth: StoredAuth): void {
  if (typeof window === "undefined") return;
  window.localStorage.setItem(STORAGE_KEY, JSON.stringify(auth));
}

export function clearAuth(): void {
  if (typeof window === "undefined") return;
  window.localStorage.removeItem(STORAGE_KEY);
}

/** {@code expiresIn}（秒） + 現在時刻から expiresAt を計算する。 */
export function computeExpiresAt(expiresInSec: number): number {
  return Date.now() + expiresInSec * 1000;
}
