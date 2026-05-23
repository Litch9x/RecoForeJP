package com.recoforejp.userservice.common;

import java.time.OffsetDateTime;
import java.util.List;
import lombok.AllArgsConstructor;
import lombok.Builder;
import lombok.Getter;

/** API エラーレスポンスの共通形式。 */
@Getter
@Builder
@AllArgsConstructor
public class ErrorResponse {

  /** プログラム判定用のエラーコード（例: {@code EMAIL_ALREADY_EXISTS}） */
  private final String code;

  /** 人間向けメッセージ */
  private final String message;

  /** バリデーションエラー等の詳細（任意） */
  private final List<String> details;

  /** エラー発生時刻 */
  private final OffsetDateTime timestamp;
}
