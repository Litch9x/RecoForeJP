package com.recoforejp.userservice.auth;

/**
 * 認証検証で email が未存在、または password が一致しない場合にスローされる。
 *
 * <p>セキュリティ上、{@code email 未存在} と {@code password 不一致} を区別せず、 どちらも HTTP 401
 * にマップする（{@code GlobalExceptionHandler}）。
 */
public class InvalidCredentialsException extends RuntimeException {

  public InvalidCredentialsException() {
    super("Invalid email or password");
  }
}
