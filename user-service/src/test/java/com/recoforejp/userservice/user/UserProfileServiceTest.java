package com.recoforejp.userservice.user;

import static org.assertj.core.api.Assertions.assertThat;
import static org.assertj.core.api.Assertions.assertThatThrownBy;
import static org.mockito.ArgumentMatchers.any;
import static org.mockito.ArgumentMatchers.eq;
import static org.mockito.Mockito.never;
import static org.mockito.Mockito.times;
import static org.mockito.Mockito.verify;
import static org.mockito.Mockito.when;

import com.recoforejp.userservice.user.dto.ProfileResponse;
import com.recoforejp.userservice.user.dto.UpdateProfileRequest;
import java.time.LocalDate;
import java.util.List;
import java.util.Optional;
import java.util.UUID;
import org.junit.jupiter.api.Test;
import org.junit.jupiter.api.extension.ExtendWith;
import org.mockito.InjectMocks;
import org.mockito.Mock;
import org.mockito.junit.jupiter.MockitoExtension;

@ExtendWith(MockitoExtension.class)
class UserProfileServiceTest {

  @Mock UserRepository userRepository;
  @Mock UserProfileRepository profileRepository;
  @Mock UserInterestRepository interestRepository;
  @InjectMocks UserProfileService userProfileService;

  private final UUID userId = UUID.fromString("00000000-0000-0000-0000-000000000001");

  @Test
  void getProfile_returnsEmptyResponseWhenProfileMissing() {
    when(userRepository.existsById(userId)).thenReturn(true);
    when(profileRepository.findById(userId)).thenReturn(Optional.empty());
    when(interestRepository.findByUserId(userId)).thenReturn(List.of());

    ProfileResponse res = userProfileService.getProfile(userId);

    assertThat(res.getUserId()).isEqualTo(userId);
    assertThat(res.getJapaneseLevel()).isNull();
    assertThat(res.getInterests()).isEmpty();
  }

  @Test
  void getProfile_throwsWhenUserMissing() {
    when(userRepository.existsById(userId)).thenReturn(false);

    assertThatThrownBy(() -> userProfileService.getProfile(userId))
        .isInstanceOf(UserNotFoundException.class);
  }

  @Test
  void upsertProfile_createsProfileAndReplacesInterests() {
    User user = User.builder().email("a@example.com").passwordHash("h").build();
    user.setId(userId);
    when(userRepository.findById(userId)).thenReturn(Optional.of(user));
    when(profileRepository.findById(userId)).thenReturn(Optional.empty());
    when(profileRepository.save(any(UserProfile.class))).thenAnswer(inv -> inv.getArgument(0));
    when(interestRepository.findByUserId(userId))
        .thenReturn(
            List.of(
                UserInterest.builder().userId(userId).interest("job").build(),
                UserInterest.builder().userId(userId).interest("housing").build()));

    UpdateProfileRequest req =
        new UpdateProfileRequest(
            "N3",
            "student",
            "大学生",
            "東京都-新宿区",
            LocalDate.of(2025, 11, 15),
            "settled",
            List.of("job", "housing"));

    ProfileResponse res = userProfileService.upsertProfile(userId, req);

    assertThat(res.getJapaneseLevel()).isEqualTo("N3");
    assertThat(res.getLifeStage()).isEqualTo("settled");
    assertThat(res.getInterests()).containsExactly("housing", "job"); // sorted
    verify(interestRepository).deleteByUserId(userId);
    verify(interestRepository, times(1)).saveAll(any());
  }

  @Test
  void upsertProfile_doesNotTouchInterestsWhenNull() {
    User user = User.builder().email("a@example.com").passwordHash("h").build();
    user.setId(userId);
    when(userRepository.findById(userId)).thenReturn(Optional.of(user));
    when(profileRepository.findById(userId)).thenReturn(Optional.empty());
    when(profileRepository.save(any(UserProfile.class))).thenAnswer(inv -> inv.getArgument(0));
    when(interestRepository.findByUserId(userId)).thenReturn(List.of());

    UpdateProfileRequest req =
        new UpdateProfileRequest("N5", null, null, null, null, null, null);

    userProfileService.upsertProfile(userId, req);

    verify(interestRepository, never()).deleteByUserId(eq(userId));
    verify(interestRepository, never()).saveAll(any());
  }

  @Test
  void upsertProfile_throwsWhenUserMissing() {
    when(userRepository.findById(userId)).thenReturn(Optional.empty());
    UpdateProfileRequest req =
        new UpdateProfileRequest(null, null, null, null, null, null, null);

    assertThatThrownBy(() -> userProfileService.upsertProfile(userId, req))
        .isInstanceOf(UserNotFoundException.class);

    verify(profileRepository, never()).save(any());
  }
}
