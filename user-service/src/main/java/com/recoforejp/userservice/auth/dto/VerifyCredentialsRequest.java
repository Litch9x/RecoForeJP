package com.recoforejp.userservice.auth.dto;

import jakarta.validation.constraints.Email;
import jakarta.validation.constraints.NotBlank;
import jakarta.validation.constraints.Size;
import lombok.AllArgsConstructor;
import lombok.Getter;
import lombok.NoArgsConstructor;
import lombok.Setter;

/** 内部認証検証リクエスト DTO。api-gateway がログイン時に user-service を呼び出すために使う。 */
@Getter
@Setter
@NoArgsConstructor
@AllArgsConstructor
public class VerifyCredentialsRequest {

  @NotBlank
  @Email
  @Size(max = 255)
  private String email;

  @NotBlank
  @Size(min = 1, max = 72)
  private String password;
}
