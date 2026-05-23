package com.recoforejp.userservice.user;

import com.recoforejp.userservice.user.dto.RegisterUserRequest;
import com.recoforejp.userservice.user.dto.UserResponse;
import jakarta.validation.Valid;
import lombok.RequiredArgsConstructor;
import org.springframework.http.HttpStatus;
import org.springframework.web.bind.annotation.PostMapping;
import org.springframework.web.bind.annotation.RequestBody;
import org.springframework.web.bind.annotation.RequestMapping;
import org.springframework.web.bind.annotation.ResponseStatus;
import org.springframework.web.bind.annotation.RestController;

/** ユーザー関連 REST エンドポイント。 */
@RestController
@RequestMapping("/users")
@RequiredArgsConstructor
public class UserController {

  private final UserService userService;

  /** ユーザー新規登録。成功時 201 Created を返す。 */
  @PostMapping
  @ResponseStatus(HttpStatus.CREATED)
  public UserResponse register(@Valid @RequestBody RegisterUserRequest request) {
    return UserResponse.from(userService.register(request));
  }
}
