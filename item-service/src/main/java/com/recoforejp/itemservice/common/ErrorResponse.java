package com.recoforejp.itemservice.common;

import java.time.OffsetDateTime;
import java.util.List;
import lombok.AllArgsConstructor;
import lombok.Builder;
import lombok.Getter;

/** API エラーレスポンスの共通形式（user-service と同形）。 */
@Getter
@Builder
@AllArgsConstructor
public class ErrorResponse {

  private final String code;
  private final String message;
  private final List<String> details;
  private final OffsetDateTime timestamp;
}
