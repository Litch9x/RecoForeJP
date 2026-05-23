package com.recoforejp.userservice.user;

import static org.assertj.core.api.Assertions.assertThat;
import static org.assertj.core.api.Assertions.assertThatThrownBy;
import static org.mockito.ArgumentMatchers.any;
import static org.mockito.Mockito.never;
import static org.mockito.Mockito.verify;
import static org.mockito.Mockito.when;

import com.recoforejp.userservice.user.dto.RegisterUserRequest;
import org.junit.jupiter.api.Test;
import org.junit.jupiter.api.extension.ExtendWith;
import org.mockito.InjectMocks;
import org.mockito.Mock;
import org.mockito.junit.jupiter.MockitoExtension;
import org.springframework.security.crypto.password.PasswordEncoder;

/** {@link UserService} の単体テスト。Spring context は起動しない（Mockito のみ）。 */
@ExtendWith(MockitoExtension.class)
class UserServiceTest {

  @Mock UserRepository userRepository;
  @Mock PasswordEncoder passwordEncoder;
  @InjectMocks UserService userService;

  @Test
  void register_savesUserWithHashedPassword() {
    RegisterUserRequest req =
        new RegisterUserRequest("alice@example.com", "password123", "VN", "vi");
    when(userRepository.existsByEmail("alice@example.com")).thenReturn(false);
    when(passwordEncoder.encode("password123")).thenReturn("$2b$10$hashed");
    when(userRepository.save(any(User.class))).thenAnswer(inv -> inv.getArgument(0));

    User saved = userService.register(req);

    assertThat(saved.getEmail()).isEqualTo("alice@example.com");
    assertThat(saved.getPasswordHash()).isEqualTo("$2b$10$hashed");
    assertThat(saved.getNationality()).isEqualTo("VN");
    assertThat(saved.getNativeLanguage()).isEqualTo("vi");
    verify(userRepository).save(any(User.class));
  }

  @Test
  void register_throwsWhenEmailExists() {
    RegisterUserRequest req =
        new RegisterUserRequest("dup@example.com", "password123", null, null);
    when(userRepository.existsByEmail("dup@example.com")).thenReturn(true);

    assertThatThrownBy(() -> userService.register(req))
        .isInstanceOf(EmailAlreadyExistsException.class)
        .hasMessageContaining("dup@example.com");

    verify(userRepository, never()).save(any());
    verify(passwordEncoder, never()).encode(any());
  }
}
