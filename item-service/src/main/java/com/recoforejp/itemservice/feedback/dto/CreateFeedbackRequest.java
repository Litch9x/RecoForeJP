package com.recoforejp.itemservice.feedback.dto;

import jakarta.validation.constraints.Max;
import jakarta.validation.constraints.Min;
import jakarta.validation.constraints.NotBlank;
import jakarta.validation.constraints.NotNull;
import jakarta.validation.constraints.Pattern;
import java.util.UUID;
import lombok.AllArgsConstructor;
import lombok.Getter;
import lombok.NoArgsConstructor;
import lombok.Setter;

/**
 * フィードバック記録リクエスト DTO。
 *
 * <p>{@code feedbackType=rating} のとき {@code rating} 必須（1〜5）。それ以外は {@code rating}
 * は無視（送られても null として扱う）。
 */
@Getter
@Setter
@NoArgsConstructor
@AllArgsConstructor
public class CreateFeedbackRequest {

  /** ログイン中のユーザー ID（論理 FK → users.users）。 */
  @NotNull private UUID userId;

  /** 対象アイテム ID。存在チェックは Service 側で実施。 */
  @NotNull private UUID itemId;

  @NotBlank
  @Pattern(
      regexp = "^(view|click|favorite|rating)$",
      message = "must be one of view|click|favorite|rating")
  private String feedbackType;

  /** 1〜5。{@code feedbackType=rating} のときのみ意味を持つ。 */
  @Min(value = 1, message = "rating must be 1..5")
  @Max(value = 5, message = "rating must be 1..5")
  private Short rating;
}
