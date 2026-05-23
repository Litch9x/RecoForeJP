package com.recoforejp.itemservice.item;

import java.util.UUID;

/** Item が見つからない場合 → HTTP 404。 */
public class ItemNotFoundException extends RuntimeException {

  public ItemNotFoundException(UUID id) {
    super("Item not found: " + id);
  }
}
