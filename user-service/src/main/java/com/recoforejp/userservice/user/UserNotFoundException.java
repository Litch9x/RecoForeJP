package com.recoforejp.userservice.user;

import java.util.UUID;

/** ユーザーが見つからない場合にスローされる。HTTP 404 にマップ。 */
public class UserNotFoundException extends RuntimeException {

  public UserNotFoundException(UUID userId) {
    super("User not found: " + userId);
  }
}
