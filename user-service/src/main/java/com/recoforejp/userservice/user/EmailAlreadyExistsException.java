package com.recoforejp.userservice.user;

/**
 * ユーザー登録時、すでに同じメールアドレスが存在する場合にスローされる。 HTTP 409 にマップする（{@code
 * GlobalExceptionHandler}）。
 */
public class EmailAlreadyExistsException extends RuntimeException {

  public EmailAlreadyExistsException(String email) {
    super("Email already registered: " + email);
  }
}
