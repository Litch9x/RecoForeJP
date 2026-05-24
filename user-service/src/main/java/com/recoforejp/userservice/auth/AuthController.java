package com.recoforejp.userservice.auth;

import com.recoforejp.userservice.auth.dto.VerifyCredentialsRequest;
import com.recoforejp.userservice.auth.dto.VerifyCredentialsResponse;
import jakarta.validation.Valid;
import lombok.RequiredArgsConstructor;
import org.springframework.web.bind.annotation.PostMapping;
import org.springframework.web.bind.annotation.RequestBody;
import org.springframework.web.bind.annotation.RequestMapping;
import org.springframework.web.bind.annotation.RestController;

/**
 * 内部認証エンドポイント。{@code /internal/...} 以下は同一ネットワーク内サービス間通信のみを想定し、
 * 外部公開しない（api-gateway もしくはサービスメッシュ側でルーティング制限する）。
 */
@RestController
@RequestMapping("/internal/auth")
@RequiredArgsConstructor
public class AuthController {

  private final AuthService authService;

  /** email + password 検証。成功時 200 + userId、失敗時 401。 */
  @PostMapping("/verify")
  public VerifyCredentialsResponse verify(@Valid @RequestBody VerifyCredentialsRequest request) {
    return VerifyCredentialsResponse.from(
        authService.verifyCredentials(request.getEmail(), request.getPassword()));
  }
}
