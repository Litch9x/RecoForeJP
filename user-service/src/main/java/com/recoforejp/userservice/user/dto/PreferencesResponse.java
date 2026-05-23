package com.recoforejp.userservice.user.dto;

import com.recoforejp.userservice.user.UserPreference;
import java.time.OffsetDateTime;
import java.util.UUID;
import lombok.AllArgsConstructor;
import lombok.Builder;
import lombok.Getter;

@Getter
@Builder
@AllArgsConstructor
public class PreferencesResponse {

  private final UUID userId;
  private final String preferredLanguage;
  private final Boolean notificationEnabled;
  private final OffsetDateTime updatedAt;

  public static PreferencesResponse from(UserPreference p) {
    return PreferencesResponse.builder()
        .userId(p.getUserId())
        .preferredLanguage(p.getPreferredLanguage())
        .notificationEnabled(p.getNotificationEnabled())
        .updatedAt(p.getUpdatedAt())
        .build();
  }
}
