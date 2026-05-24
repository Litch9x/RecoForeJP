package com.recoforejp.userservice.user;

import jakarta.persistence.Column;
import jakarta.persistence.Entity;
import jakarta.persistence.EnumType;
import jakarta.persistence.Enumerated;
import jakarta.persistence.Id;
import jakarta.persistence.OneToOne;
import jakarta.persistence.Table;
import java.time.OffsetDateTime;
import java.util.UUID;
import lombok.AllArgsConstructor;
import lombok.Builder;
import lombok.Getter;
import lombok.NoArgsConstructor;
import lombok.Setter;
import org.hibernate.annotations.CreationTimestamp;
import org.hibernate.annotations.UpdateTimestamp;
import org.hibernate.annotations.UuidGenerator;

/**
 * {@code users.users} テーブルに対応するエンティティ。
 *
 * <p>schema は {@code spring.jpa.properties.hibernate.default_schema=users} で
 * 設定済みのため、{@code @Table} で明示しない。
 */
@Entity
@Table(name = "users")
@Getter
@Setter
@NoArgsConstructor
@AllArgsConstructor
@Builder
public class User {

  @Id @UuidGenerator private UUID id;

  @Column(nullable = false, unique = true, length = 255)
  private String email;

  @Column(name = "password_hash", nullable = false, length = 255)
  private String passwordHash;

  /** ISO 3166-1 alpha-2 (例: {@code JP}, {@code VN}) */
  @Column(length = 2)
  private String nationality;

  /** BCP47 言語コード (例: {@code ja}, {@code vi}, {@code zh-CN}) */
  @Column(name = "native_language", length = 8)
  private String nativeLanguage;

  /**
   * 権限ロール。新規登録時は DB の DEFAULT 'USER' に任せる（{@code @Builder.Default} で
   * Java 側でも USER を初期値とする）。
   */
  @Enumerated(EnumType.STRING)
  @Column(nullable = false, length = 16)
  @lombok.Builder.Default
  private UserRole role = UserRole.USER;

  @CreationTimestamp
  @Column(name = "created_at", nullable = false, updatable = false)
  private OffsetDateTime createdAt;

  @UpdateTimestamp
  @Column(name = "updated_at", nullable = false)
  private OffsetDateTime updatedAt;

  /** 1:1 で UserProfile を保持（任意）。 */
  @OneToOne(mappedBy = "user", optional = true)
  private UserProfile profile;
}
