package com.recoforejp.userservice.auth;

import com.recoforejp.userservice.user.User;
import com.recoforejp.userservice.user.UserRepository;
import lombok.RequiredArgsConstructor;
import org.springframework.security.crypto.password.PasswordEncoder;
import org.springframework.stereotype.Service;
import org.springframework.transaction.annotation.Transactional;

/**
 * 内部向け認証ロジック。email + password を検証し、一致すれば {@link User} を返す。
 *
 * <p>呼び出し元は同じネットワーク内の信頼できるサービス（api-gateway）。 ここでは JWT を発行せず、認証結果のみを返す。
 */
@Service
@RequiredArgsConstructor
public class AuthService {

  private final UserRepository userRepository;
  private final PasswordEncoder passwordEncoder;

  /**
   * 認証検証。email 未存在 / password 不一致のいずれでも {@link InvalidCredentialsException} をスローする
   * （エラーメッセージを共通化して、email の存在有無を漏らさない）。
   */
  @Transactional(readOnly = true)
  public User verifyCredentials(String email, String rawPassword) {
    User user =
        userRepository.findByEmail(email).orElseThrow(InvalidCredentialsException::new);
    if (!passwordEncoder.matches(rawPassword, user.getPasswordHash())) {
      throw new InvalidCredentialsException();
    }
    return user;
  }
}
