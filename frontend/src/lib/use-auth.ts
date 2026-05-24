"use client";

import { useSyncExternalStore } from "react";

import { readAuth, type StoredAuth } from "./auth";

/**
 * localStorage の StoredAuth を React に同期して購読する hook。
 * - SSR では常に null（クライアント実行値とのミスマッチを避ける）
 * - 別タブで localStorage が変わった場合も storage イベントで反映
 * - 同タブ内の login/logout もカスタムイベントで反映
 *
 * useEffect 内で setState せず useSyncExternalStore を使うことで、
 * react-hooks/set-state-in-effect ルールを満たす。
 */
export function useAuth(): StoredAuth | null {
  return useSyncExternalStore(subscribe, getSnapshot, getServerSnapshot);
}

const AUTH_CHANGE_EVENT = "recoforejp:auth-change";

function subscribe(callback: () => void): () => void {
  window.addEventListener("storage", callback);
  window.addEventListener(AUTH_CHANGE_EVENT, callback);
  return () => {
    window.removeEventListener("storage", callback);
    window.removeEventListener(AUTH_CHANGE_EVENT, callback);
  };
}

let cachedSnapshot: StoredAuth | null = null;
let cachedRaw: string | null | undefined = undefined;

/**
 * useSyncExternalStore は getSnapshot が毎回同じオブジェクト参照を返すことを要求する。
 * localStorage の生 JSON 文字列をキャッシュキーにし、変わったときだけ再 parse する。
 */
function getSnapshot(): StoredAuth | null {
  const raw = window.localStorage.getItem("recoforejp.auth");
  if (raw === cachedRaw) return cachedSnapshot;
  cachedRaw = raw;
  cachedSnapshot = readAuth();
  return cachedSnapshot;
}

function getServerSnapshot(): StoredAuth | null {
  return null;
}

/** 同タブ内で localStorage を書き換えた直後に呼ぶ。 */
export function notifyAuthChange(): void {
  if (typeof window === "undefined") return;
  window.dispatchEvent(new Event(AUTH_CHANGE_EVENT));
}
