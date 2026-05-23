package com.recoforejp.userservice.user.dto;

import com.recoforejp.userservice.user.User;
import java.time.OffsetDateTime;
import java.util.UUID;
import lombok.AllArgsConstructor;
import lombok.Builder;
import lombok.Getter;

/**
 * ユーザー API のレスポンス DTO。{@link User} エンティティから、機微な情報（passwordHash）を除外して
 * 構築する。
 */
@Getter
@Builder
@AllArgsConstructor
public class UserResponse {

  private final UUID id;
  private final String email;
  private final String nationality;
  private final String nativeLanguage;
  private final OffsetDateTime createdAt;

  public static UserResponse from(User user) {
    return UserResponse.builder()
        .id(user.getId())
        .email(user.getEmail())
        .nationality(user.getNationality())
        .nativeLanguage(user.getNativeLanguage())
        .createdAt(user.getCreatedAt())
        .build();
  }
}
