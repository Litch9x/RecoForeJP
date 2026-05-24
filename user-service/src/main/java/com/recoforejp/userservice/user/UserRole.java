package com.recoforejp.userservice.user;

/**
 * ユーザーの権限ロール。DB の {@code users.users.role} と一致する。
 * 文字列としてシリアライズされる（{@link Enum#name()}）。
 */
public enum UserRole {
  USER,
  ADMIN,
}
