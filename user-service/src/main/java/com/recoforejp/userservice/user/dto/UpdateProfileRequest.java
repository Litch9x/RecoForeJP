package com.recoforejp.userservice.user.dto;

import jakarta.validation.constraints.Pattern;
import jakarta.validation.constraints.Size;
import java.time.LocalDate;
import java.util.List;
import lombok.AllArgsConstructor;
import lombok.Getter;
import lombok.NoArgsConstructor;
import lombok.Setter;

/**
 * プロフィール更新リクエスト DTO。全フィールド任意（null は「変更しない」ではなく「未設定にする」を表す
 * upsert 仕様）。
 */
@Getter
@Setter
@NoArgsConstructor
@AllArgsConstructor
public class UpdateProfileRequest {

  /** N1〜N5 のいずれか、または null */
  @Pattern(regexp = "^(N1|N2|N3|N4|N5)$", message = "must be one of N1..N5")
  private String japaneseLevel;

  /** 在留資格スラグ（例: {@code student}, {@code engineer}, {@code permanent}） */
  @Size(max = 32)
  private String residencyStatus;

  @Size(max = 64)
  private String occupation;

  @Size(max = 64)
  private String region;

  private LocalDate arrivalDate;

  @Pattern(
      regexp = "^(arrival|settled|established)$",
      message = "must be one of arrival|settled|established")
  private String lifeStage;

  /** 興味分野リスト。{@code null} の場合は変更しない。空リストの場合は全削除。 */
  private List<@Size(min = 1, max = 64) String> interests;
}
