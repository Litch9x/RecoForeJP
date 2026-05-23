package com.recoforejp.userservice.user;

import com.recoforejp.userservice.user.dto.ProfileResponse;
import com.recoforejp.userservice.user.dto.UpdateProfileRequest;
import java.util.Comparator;
import java.util.List;
import java.util.UUID;
import lombok.RequiredArgsConstructor;
import org.springframework.stereotype.Service;
import org.springframework.transaction.annotation.Transactional;

/** プロフィール（{@link UserProfile} + {@link UserInterest}）のビジネスロジック。 */
@Service
@RequiredArgsConstructor
public class UserProfileService {

  private final UserRepository userRepository;
  private final UserProfileRepository profileRepository;
  private final UserInterestRepository interestRepository;

  /** 指定ユーザーのプロフィール + 興味を返す。プロフィール未設定でも 404 にはせず、空フィールドで返す。 */
  @Transactional(readOnly = true)
  public ProfileResponse getProfile(UUID userId) {
    requireUserExists(userId);
    UserProfile profile = profileRepository.findById(userId).orElse(null);
    List<String> interests = readSortedInterests(userId);
    return ProfileResponse.from(userId, profile, interests);
  }

  /**
   * プロフィールを upsert する。interests が {@code null} 以外なら、興味リストも置き換える（{@code []}
   * で全削除）。
   */
  @Transactional
  public ProfileResponse upsertProfile(UUID userId, UpdateProfileRequest req) {
    User user =
        userRepository.findById(userId).orElseThrow(() -> new UserNotFoundException(userId));

    UserProfile profile =
        profileRepository
            .findById(userId)
            .orElseGet(
                () -> {
                  UserProfile p = new UserProfile();
                  p.setUser(user);
                  return p;
                });
    profile.setJapaneseLevel(req.getJapaneseLevel());
    profile.setResidencyStatus(req.getResidencyStatus());
    profile.setOccupation(req.getOccupation());
    profile.setRegion(req.getRegion());
    profile.setArrivalDate(req.getArrivalDate());
    profile.setLifeStage(req.getLifeStage());
    profileRepository.save(profile);

    if (req.getInterests() != null) {
      interestRepository.deleteByUserId(userId);
      List<UserInterest> newInterests =
          req.getInterests().stream()
              .distinct()
              .map(i -> UserInterest.builder().userId(userId).interest(i).build())
              .toList();
      if (!newInterests.isEmpty()) {
        interestRepository.saveAll(newInterests);
      }
    }

    return ProfileResponse.from(userId, profile, readSortedInterests(userId));
  }

  private void requireUserExists(UUID userId) {
    if (!userRepository.existsById(userId)) {
      throw new UserNotFoundException(userId);
    }
  }

  private List<String> readSortedInterests(UUID userId) {
    return interestRepository.findByUserId(userId).stream()
        .map(UserInterest::getInterest)
        .sorted(Comparator.naturalOrder())
        .toList();
  }
}
