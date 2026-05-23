package com.recoforejp.itemservice.feedback;

/** フィードバックの type と rating の組み合わせが不正な場合 → HTTP 400。 */
public class InvalidFeedbackException extends RuntimeException {

  public InvalidFeedbackException(String message) {
    super(message);
  }
}
