package com.recoforejp.itemservice.common;

import com.recoforejp.itemservice.feedback.InvalidFeedbackException;
import com.recoforejp.itemservice.item.InvalidReferenceException;
import com.recoforejp.itemservice.item.ItemNotFoundException;
import java.time.OffsetDateTime;
import java.util.List;
import org.springframework.http.HttpStatus;
import org.springframework.http.ResponseEntity;
import org.springframework.web.bind.MethodArgumentNotValidException;
import org.springframework.web.bind.annotation.ExceptionHandler;
import org.springframework.web.bind.annotation.RestControllerAdvice;

/** 例外を HTTP レスポンスにマップする共通ハンドラ。 */
@RestControllerAdvice
public class GlobalExceptionHandler {

  /** Item 未存在 → 404 */
  @ExceptionHandler(ItemNotFoundException.class)
  public ResponseEntity<ErrorResponse> handleItemNotFound(ItemNotFoundException e) {
    return ResponseEntity.status(HttpStatus.NOT_FOUND)
        .body(
            ErrorResponse.builder()
                .code("ITEM_NOT_FOUND")
                .message(e.getMessage())
                .timestamp(OffsetDateTime.now())
                .build());
  }

  /** 不正な参照（未知の categorySlug や tag 名など） → 400 */
  @ExceptionHandler(InvalidReferenceException.class)
  public ResponseEntity<ErrorResponse> handleInvalidReference(InvalidReferenceException e) {
    return ResponseEntity.status(HttpStatus.BAD_REQUEST)
        .body(
            ErrorResponse.builder()
                .code("INVALID_REFERENCE")
                .message(e.getMessage())
                .timestamp(OffsetDateTime.now())
                .build());
  }

  /** フィードバックの type/rating 組み合わせが不正 → 400 */
  @ExceptionHandler(InvalidFeedbackException.class)
  public ResponseEntity<ErrorResponse> handleInvalidFeedback(InvalidFeedbackException e) {
    return ResponseEntity.status(HttpStatus.BAD_REQUEST)
        .body(
            ErrorResponse.builder()
                .code("INVALID_FEEDBACK")
                .message(e.getMessage())
                .timestamp(OffsetDateTime.now())
                .build());
  }

  /** {@code @Valid} バリデーション失敗 → 400 */
  @ExceptionHandler(MethodArgumentNotValidException.class)
  public ResponseEntity<ErrorResponse> handleValidation(MethodArgumentNotValidException e) {
    List<String> details =
        e.getBindingResult().getFieldErrors().stream()
            .map(err -> err.getField() + ": " + err.getDefaultMessage())
            .toList();
    return ResponseEntity.status(HttpStatus.BAD_REQUEST)
        .body(
            ErrorResponse.builder()
                .code("VALIDATION_ERROR")
                .message("Request validation failed")
                .details(details)
                .timestamp(OffsetDateTime.now())
                .build());
  }
}
