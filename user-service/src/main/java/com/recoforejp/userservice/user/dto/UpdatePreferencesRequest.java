package com.recoforejp.userservice.user.dto;

import jakarta.validation.constraints.Pattern;
import jakarta.validation.constraints.Size;
import lombok.AllArgsConstructor;
import lombok.Getter;
import lombok.NoArgsConstructor;
import lombok.Setter;

/**
 * ユーザー設定の更新リクエスト DTO。
 *
 * <p>各フィールド null は「変更しない」を意味する（partial update）。
 */
@Getter
@Setter
@NoArgsConstructor
@AllArgsConstructor
public class UpdatePreferencesRequest {

  /** BCP47 言語コード（例: {@code ja}, {@code en}, {@code vi}, {@code zh-CN}） */
  @Pattern(
      regexp = "^[a-z]{2}(-[A-Z]{2})?$",
      message = "must be BCP47 (e.g. ja, en, vi, zh-CN)")
  @Size(max = 8)
  private String preferredLanguage;

  private Boolean notificationEnabled;
}
