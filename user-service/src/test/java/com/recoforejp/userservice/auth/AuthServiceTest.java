package com.recoforejp.userservice.auth;

import static org.assertj.core.api.Assertions.assertThat;
import static org.assertj.core.api.Assertions.assertThatThrownBy;
import static org.mockito.Mockito.never;
import static org.mockito.Mockito.verify;
import static org.mockito.Mockito.when;

import com.recoforejp.userservice.user.User;
import com.recoforejp.userservice.user.UserRepository;
import java.util.Optional;
import java.util.UUID;
import org.junit.jupiter.api.Test;
import org.junit.jupiter.api.extension.ExtendWith;
import org.mockito.InjectMocks;
import org.mockito.Mock;
import org.mockito.junit.jupiter.MockitoExtension;
import org.springframework.security.crypto.password.PasswordEncoder;

/** {@link AuthService} の単体テスト。 */
@ExtendWith(MockitoExtension.class)
class AuthServiceTest {

  @Mock UserRepository userRepository;
  @Mock PasswordEncoder passwordEncoder;
  @InjectMocks AuthService authService;

  @Test
  void verifyCredentials_returnsUser_whenPasswordMatches() {
    UUID id = UUID.randomUUID();
    User user =
        User.builder().id(id).email("alice@example.com").passwordHash("$2b$10$hashed").build();
    when(userRepository.findByEmail("alice@example.com")).thenReturn(Optional.of(user));
    when(passwordEncoder.matches("password123", "$2b$10$hashed")).thenReturn(true);

    User result = authService.verifyCredentials("alice@example.com", "password123");

    assertThat(result.getId()).isEqualTo(id);
    assertThat(result.getEmail()).isEqualTo("alice@example.com");
  }

  @Test
  void verifyCredentials_throws_whenEmailNotFound() {
    when(userRepository.findByEmail("ghost@example.com")).thenReturn(Optional.empty());

    assertThatThrownBy(() -> authService.verifyCredentials("ghost@example.com", "password123"))
        .isInstanceOf(InvalidCredentialsException.class);

    verify(passwordEncoder, never()).matches(org.mockito.ArgumentMatchers.anyString(), org.mockito.ArgumentMatchers.anyString());
  }

  @Test
  void verifyCredentials_throws_whenPasswordMismatch() {
    User user =
        User.builder()
            .id(UUID.randomUUID())
            .email("alice@example.com")
            .passwordHash("$2b$10$hashed")
            .build();
    when(userRepository.findByEmail("alice@example.com")).thenReturn(Optional.of(user));
    when(passwordEncoder.matches("wrong", "$2b$10$hashed")).thenReturn(false);

    assertThatThrownBy(() -> authService.verifyCredentials("alice@example.com", "wrong"))
        .isInstanceOf(InvalidCredentialsException.class);
  }
}
