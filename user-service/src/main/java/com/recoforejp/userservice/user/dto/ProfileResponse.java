package com.recoforejp.userservice.user.dto;

import com.recoforejp.userservice.user.UserProfile;
import java.time.LocalDate;
import java.util.List;
import java.util.UUID;
import lombok.AllArgsConstructor;
import lombok.Builder;
import lombok.Getter;

/** プロフィール取得・更新のレスポンス DTO。 */
@Getter
@Builder
@AllArgsConstructor
public class ProfileResponse {

  private final UUID userId;
  private final String japaneseLevel;
  private final String residencyStatus;
  private final String occupation;
  private final String region;
  private final LocalDate arrivalDate;
  private final String lifeStage;
  private final List<String> interests;

  /** プロフィール未設定でも空 DTO を返せるよう、{@code profile} は nullable。 */
  public static ProfileResponse from(UUID userId, UserProfile profile, List<String> interests) {
    ProfileResponseBuilder b = ProfileResponse.builder().userId(userId).interests(interests);
    if (profile != null) {
      b.japaneseLevel(profile.getJapaneseLevel())
          .residencyStatus(profile.getResidencyStatus())
          .occupation(profile.getOccupation())
          .region(profile.getRegion())
          .arrivalDate(profile.getArrivalDate())
          .lifeStage(profile.getLifeStage());
    }
    return b.build();
  }
}
