package com.recoforejp.userservice.user;

import jakarta.persistence.Column;
import jakarta.persistence.Entity;
import jakarta.persistence.Id;
import jakarta.persistence.Table;
import java.time.OffsetDateTime;
import java.util.UUID;
import lombok.AllArgsConstructor;
import lombok.Builder;
import lombok.Getter;
import lombok.NoArgsConstructor;
import lombok.Setter;
import org.hibernate.annotations.UpdateTimestamp;

/**
 * {@code users.user_preferences} に対応するユーザー設定（{@link User} と 1:1）。
 *
 * <p>schema 跨ぎでないので主キーは UUID 単体。{@link User} との関係は論理 FK（{@code user_id}
 * は users.users.id を指すが、JPA 上はリレーション化しない）。
 */
@Entity
@Table(name = "user_preferences")
@Getter
@Setter
@NoArgsConstructor
@AllArgsConstructor
@Builder
public class UserPreference {

  @Id
  @Column(name = "user_id")
  private UUID userId;

  /** 表示言語（BCP47）。{@link UserPreferenceService#DEFAULT_LANGUAGE} を既定とする。 */
  @Column(name = "preferred_language", nullable = false, length = 8)
  private String preferredLanguage;

  /** 通知の有効/無効。 */
  @Column(name = "notification_enabled", nullable = false)
  private Boolean notificationEnabled;

  @UpdateTimestamp
  @Column(name = "updated_at", nullable = false)
  private OffsetDateTime updatedAt;
}
