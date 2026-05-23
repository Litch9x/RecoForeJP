package com.recoforejp.itemservice.item;

/** 存在しないカテゴリ slug やタグ名を参照した場合 → HTTP 400。 */
public class InvalidReferenceException extends RuntimeException {

  public InvalidReferenceException(String message) {
    super(message);
  }
}
