package com.recoforejp.userservice.user;

import jakarta.persistence.Column;
import jakarta.persistence.Entity;
import jakarta.persistence.Id;
import jakarta.persistence.JoinColumn;
import jakarta.persistence.MapsId;
import jakarta.persistence.OneToOne;
import jakarta.persistence.Table;
import java.time.LocalDate;
import java.time.OffsetDateTime;
import java.util.UUID;
import lombok.AllArgsConstructor;
import lombok.Builder;
import lombok.Getter;
import lombok.NoArgsConstructor;
import lombok.Setter;
import org.hibernate.annotations.CreationTimestamp;
import org.hibernate.annotations.UpdateTimestamp;

/**
 * {@code users.user_profiles} テーブルに対応する詳細プロフィール（{@link User} と 1:1）。
 *
 * <p>{@link MapsId} により {@code user_id} を主キーかつ {@link User} への FK として共有する
 * （共有主キー方式）。
 */
@Entity
@Table(name = "user_profiles")
@Getter
@Setter
@NoArgsConstructor
@AllArgsConstructor
@Builder
public class UserProfile {

  @Id
  @Column(name = "user_id")
  private UUID userId;

  @MapsId
  @OneToOne
  @JoinColumn(name = "user_id")
  private User user;

  /** N1..N5 のいずれか、または null */
  @Column(name = "japanese_level", length = 4)
  private String japaneseLevel;

  /** 在留資格（例: student, technical-intern, engineer, highly-skilled, permanent） */
  @Column(name = "residency_status", length = 32)
  private String residencyStatus;

  @Column(length = 64)
  private String occupation;

  /** 都道府県-市区町村 形式（例: {@code 東京都-新宿区}） */
  @Column(length = 64)
  private String region;

  @Column(name = "arrival_date")
  private LocalDate arrivalDate;

  /** {@code arrival} / {@code settled} / {@code established} */
  @Column(name = "life_stage", length = 16)
  private String lifeStage;

  @CreationTimestamp
  @Column(name = "created_at", nullable = false, updatable = false)
  private OffsetDateTime createdAt;

  @UpdateTimestamp
  @Column(name = "updated_at", nullable = false)
  private OffsetDateTime updatedAt;
}
