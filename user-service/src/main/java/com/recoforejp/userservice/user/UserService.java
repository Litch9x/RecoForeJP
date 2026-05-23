package com.recoforejp.userservice.user;

import com.recoforejp.userservice.user.dto.RegisterUserRequest;
import lombok.RequiredArgsConstructor;
import org.springframework.security.crypto.password.PasswordEncoder;
import org.springframework.stereotype.Service;
import org.springframework.transaction.annotation.Transactional;

/** ユーザー関連のビジネスロジック。 */
@Service
@RequiredArgsConstructor
public class UserService {

  private final UserRepository userRepository;
  private final PasswordEncoder passwordEncoder;

  /**
   * 新規ユーザーを登録する。
   *
   * @throws EmailAlreadyExistsException email が既に登録済みの場合
   */
  @Transactional
  public User register(RegisterUserRequest req) {
    if (userRepository.existsByEmail(req.getEmail())) {
      throw new EmailAlreadyExistsException(req.getEmail());
    }
    User user =
        User.builder()
            .email(req.getEmail())
            .passwordHash(passwordEncoder.encode(req.getPassword()))
            .nationality(req.getNationality())
            .nativeLanguage(req.getNativeLanguage())
            .build();
    return userRepository.save(user);
  }
}
