package com.recoforejp.userservice.user;

import com.recoforejp.userservice.user.dto.PreferencesResponse;
import com.recoforejp.userservice.user.dto.UpdatePreferencesRequest;
import java.util.UUID;
import lombok.RequiredArgsConstructor;
import org.springframework.stereotype.Service;
import org.springframework.transaction.annotation.Transactional;

/** ユーザー設定（{@link UserPreference}）のビジネスロジック。 */
@Service
@RequiredArgsConstructor
public class UserPreferenceService {

  /** 初期値（行が無い場合に返す／作る際の既定値）。 */
  public static final String DEFAULT_LANGUAGE = "ja";

  public static final boolean DEFAULT_NOTIFICATIONS = true;

  private final UserRepository userRepository;
  private final UserPreferenceRepository preferenceRepository;

  /** 取得：行が無ければ既定値の {@link PreferencesResponse} を返す（DB 書き込みはしない）。 */
  @Transactional(readOnly = true)
  public PreferencesResponse getPreferences(UUID userId) {
    requireUserExists(userId);
    return preferenceRepository
        .findById(userId)
        .map(PreferencesResponse::from)
        .orElseGet(
            () ->
                PreferencesResponse.builder()
                    .userId(userId)
                    .preferredLanguage(DEFAULT_LANGUAGE)
                    .notificationEnabled(DEFAULT_NOTIFICATIONS)
                    .build());
  }

  /**
   * 部分更新：null フィールドは変更しない（新規作成時は既定値）。
   *
   * @throws UserNotFoundException ユーザーが存在しない場合
   */
  @Transactional
  public PreferencesResponse upsert(UUID userId, UpdatePreferencesRequest req) {
    requireUserExists(userId);

    UserPreference pref =
        preferenceRepository
            .findById(userId)
            .orElseGet(
                () ->
                    UserPreference.builder()
                        .userId(userId)
                        .preferredLanguage(DEFAULT_LANGUAGE)
                        .notificationEnabled(DEFAULT_NOTIFICATIONS)
                        .build());

    if (req.getPreferredLanguage() != null) {
      pref.setPreferredLanguage(req.getPreferredLanguage());
    }
    if (req.getNotificationEnabled() != null) {
      pref.setNotificationEnabled(req.getNotificationEnabled());
    }

    UserPreference saved = preferenceRepository.save(pref);
    return PreferencesResponse.from(saved);
  }

  private void requireUserExists(UUID userId) {
    if (!userRepository.existsById(userId)) {
      throw new UserNotFoundException(userId);
    }
  }
}
