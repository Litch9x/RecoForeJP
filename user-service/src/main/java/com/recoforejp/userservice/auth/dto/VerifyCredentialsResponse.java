package com.recoforejp.userservice.auth.dto;

import com.recoforejp.userservice.user.User;
import com.recoforejp.userservice.user.UserRole;
import java.util.UUID;
import lombok.AllArgsConstructor;
import lombok.Builder;
import lombok.Getter;
import lombok.NoArgsConstructor;
import lombok.Setter;

/**
 * 検証成功時に返す最小ペイロード。api-gateway はこの {@code userId} を JWT の subject に詰め、
 * {@code role} を権限クレームとして含める。
 */
@Getter
@Setter
@NoArgsConstructor
@AllArgsConstructor
@Builder
public class VerifyCredentialsResponse {

  private UUID userId;
  private String email;
  private UserRole role;

  public static VerifyCredentialsResponse from(User user) {
    return VerifyCredentialsResponse.builder()
        .userId(user.getId())
        .email(user.getEmail())
        .role(user.getRole())
        .build();
  }
}
