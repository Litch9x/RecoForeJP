package com.recoforejp.userservice.common;

import com.recoforejp.userservice.user.EmailAlreadyExistsException;
import com.recoforejp.userservice.user.UserNotFoundException;
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

  /** ユーザー未存在 → 404 Not Found */
  @ExceptionHandler(UserNotFoundException.class)
  public ResponseEntity<ErrorResponse> handleUserNotFound(UserNotFoundException e) {
    ErrorResponse body =
        ErrorResponse.builder()
            .code("USER_NOT_FOUND")
            .message(e.getMessage())
            .timestamp(OffsetDateTime.now())
            .build();
    return ResponseEntity.status(HttpStatus.NOT_FOUND).body(body);
  }

  /** メールアドレス重複 → 409 Conflict */
  @ExceptionHandler(EmailAlreadyExistsException.class)
  public ResponseEntity<ErrorResponse> handleEmailExists(EmailAlreadyExistsException e) {
    ErrorResponse body =
        ErrorResponse.builder()
            .code("EMAIL_ALREADY_EXISTS")
            .message(e.getMessage())
            .timestamp(OffsetDateTime.now())
            .build();
    return ResponseEntity.status(HttpStatus.CONFLICT).body(body);
  }

  /** {@code @Valid} のバリデーション失敗 → 400 Bad Request */
  @ExceptionHandler(MethodArgumentNotValidException.class)
  public ResponseEntity<ErrorResponse> handleValidation(MethodArgumentNotValidException e) {
    List<String> details =
        e.getBindingResult().getFieldErrors().stream()
            .map(err -> err.getField() + ": " + err.getDefaultMessage())
            .toList();
    ErrorResponse body =
        ErrorResponse.builder()
            .code("VALIDATION_ERROR")
            .message("Request validation failed")
            .details(details)
            .timestamp(OffsetDateTime.now())
            .build();
    return ResponseEntity.status(HttpStatus.BAD_REQUEST).body(body);
  }
}
