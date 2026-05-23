package com.recoforejp.userservice.user;

import static org.assertj.core.api.Assertions.assertThat;
import static org.assertj.core.api.Assertions.assertThatThrownBy;
import static org.mockito.ArgumentMatchers.any;
import static org.mockito.Mockito.never;
import static org.mockito.Mockito.verify;
import static org.mockito.Mockito.when;

import com.recoforejp.userservice.user.dto.PreferencesResponse;
import com.recoforejp.userservice.user.dto.UpdatePreferencesRequest;
import java.util.Optional;
import java.util.UUID;
import org.junit.jupiter.api.Test;
import org.junit.jupiter.api.extension.ExtendWith;
import org.mockito.InjectMocks;
import org.mockito.Mock;
import org.mockito.junit.jupiter.MockitoExtension;

@ExtendWith(MockitoExtension.class)
class UserPreferenceServiceTest {

  @Mock UserRepository userRepository;
  @Mock UserPreferenceRepository preferenceRepository;
  @InjectMocks UserPreferenceService service;

  private final UUID userId = UUID.fromString("00000000-0000-0000-0000-000000000001");

  @Test
  void getPreferences_returnsDefaultsWhenMissing() {
    when(userRepository.existsById(userId)).thenReturn(true);
    when(preferenceRepository.findById(userId)).thenReturn(Optional.empty());

    PreferencesResponse res = service.getPreferences(userId);

    assertThat(res.getUserId()).isEqualTo(userId);
    assertThat(res.getPreferredLanguage()).isEqualTo(UserPreferenceService.DEFAULT_LANGUAGE);
    assertThat(res.getNotificationEnabled())
        .isEqualTo(UserPreferenceService.DEFAULT_NOTIFICATIONS);
    verify(preferenceRepository, never()).save(any());
  }

  @Test
  void getPreferences_returnsStoredWhenExists() {
    UserPreference stored =
        UserPreference.builder()
            .userId(userId)
            .preferredLanguage("vi")
            .notificationEnabled(false)
            .build();
    when(userRepository.existsById(userId)).thenReturn(true);
    when(preferenceRepository.findById(userId)).thenReturn(Optional.of(stored));

    PreferencesResponse res = service.getPreferences(userId);

    assertThat(res.getPreferredLanguage()).isEqualTo("vi");
    assertThat(res.getNotificationEnabled()).isFalse();
  }

  @Test
  void getPreferences_throwsWhenUserMissing() {
    when(userRepository.existsById(userId)).thenReturn(false);
    assertThatThrownBy(() -> service.getPreferences(userId))
        .isInstanceOf(UserNotFoundException.class);
  }

  @Test
  void upsert_createsWithDefaultsThenAppliesNonNullFields() {
    when(userRepository.existsById(userId)).thenReturn(true);
    when(preferenceRepository.findById(userId)).thenReturn(Optional.empty());
    when(preferenceRepository.save(any(UserPreference.class)))
        .thenAnswer(inv -> inv.getArgument(0));

    UpdatePreferencesRequest req = new UpdatePreferencesRequest("en", null);

    PreferencesResponse res = service.upsert(userId, req);

    assertThat(res.getPreferredLanguage()).isEqualTo("en");
    // not specified → default
    assertThat(res.getNotificationEnabled())
        .isEqualTo(UserPreferenceService.DEFAULT_NOTIFICATIONS);
  }

  @Test
  void upsert_partialUpdatePreservesExistingValues() {
    UserPreference existing =
        UserPreference.builder()
            .userId(userId)
            .preferredLanguage("vi")
            .notificationEnabled(true)
            .build();
    when(userRepository.existsById(userId)).thenReturn(true);
    when(preferenceRepository.findById(userId)).thenReturn(Optional.of(existing));
    when(preferenceRepository.save(any(UserPreference.class)))
        .thenAnswer(inv -> inv.getArgument(0));

    UpdatePreferencesRequest req = new UpdatePreferencesRequest(null, false);

    PreferencesResponse res = service.upsert(userId, req);

    assertThat(res.getPreferredLanguage()).isEqualTo("vi"); // preserved
    assertThat(res.getNotificationEnabled()).isFalse(); // updated
  }

  @Test
  void upsert_throwsWhenUserMissing() {
    when(userRepository.existsById(userId)).thenReturn(false);
    UpdatePreferencesRequest req = new UpdatePreferencesRequest("ja", true);

    assertThatThrownBy(() -> service.upsert(userId, req))
        .isInstanceOf(UserNotFoundException.class);

    verify(preferenceRepository, never()).save(any());
  }
}
