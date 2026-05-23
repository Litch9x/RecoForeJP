package com.recoforejp.userservice.user.dto;

import jakarta.validation.constraints.Email;
import jakarta.validation.constraints.NotBlank;
import jakarta.validation.constraints.Pattern;
import jakarta.validation.constraints.Size;
import lombok.AllArgsConstructor;
import lombok.Getter;
import lombok.NoArgsConstructor;
import lombok.Setter;

/** ユーザー登録リクエスト DTO。 */
@Getter
@Setter
@NoArgsConstructor
@AllArgsConstructor
public class RegisterUserRequest {

  @NotBlank
  @Email
  @Size(max = 255)
  private String email;

  /** bcrypt は最大 72 バイトまでハッシュ可能。8 文字以上を要求。 */
  @NotBlank
  @Size(min = 8, max = 72)
  private String password;

  /** ISO 3166-1 alpha-2（任意） */
  @Pattern(regexp = "^[A-Z]{2}$", message = "must be ISO 3166-1 alpha-2 (e.g. JP, VN)")
  private String nationality;

  /** BCP47 言語コード（任意） */
  @Size(max = 8)
  private String nativeLanguage;
}
