package com.recoforejp.itemservice.item;

import com.recoforejp.itemservice.item.dto.CreateItemRequest;
import com.recoforejp.itemservice.item.dto.ItemResponse;
import com.recoforejp.itemservice.item.dto.UpdateItemRequest;
import jakarta.validation.Valid;
import java.util.List;
import java.util.UUID;
import lombok.RequiredArgsConstructor;
import org.springframework.http.HttpStatus;
import org.springframework.web.bind.annotation.DeleteMapping;
import org.springframework.web.bind.annotation.GetMapping;
import org.springframework.web.bind.annotation.PathVariable;
import org.springframework.web.bind.annotation.PostMapping;
import org.springframework.web.bind.annotation.PutMapping;
import org.springframework.web.bind.annotation.RequestBody;
import org.springframework.web.bind.annotation.RequestMapping;
import org.springframework.web.bind.annotation.RequestParam;
import org.springframework.web.bind.annotation.ResponseStatus;
import org.springframework.web.bind.annotation.RestController;

/** アイテム CRUD REST エンドポイント。 */
@RestController
@RequestMapping("/items")
@RequiredArgsConstructor
public class ItemController {

  private final ItemService itemService;

  /** 新規アイテム作成。201 Created。 */
  @PostMapping
  @ResponseStatus(HttpStatus.CREATED)
  public ItemResponse create(@Valid @RequestBody CreateItemRequest request) {
    return ItemResponse.from(itemService.create(request));
  }

  /** 単一取得。 */
  @GetMapping("/{id}")
  public ItemResponse get(@PathVariable UUID id) {
    return ItemResponse.from(itemService.get(id));
  }

  /** 一覧取得（フィルタ任意）。 */
  @GetMapping
  public List<ItemResponse> list(
      @RequestParam(required = false) String category,
      @RequestParam(required = false) String region) {
    return itemService.list(category, region).stream().map(ItemResponse::from).toList();
  }

  /** 部分更新（null フィールドは保持）。 */
  @PutMapping("/{id}")
  public ItemResponse update(
      @PathVariable UUID id, @Valid @RequestBody UpdateItemRequest request) {
    return ItemResponse.from(itemService.update(id, request));
  }

  /** 削除。204 No Content。 */
  @DeleteMapping("/{id}")
  @ResponseStatus(HttpStatus.NO_CONTENT)
  public void delete(@PathVariable UUID id) {
    itemService.delete(id);
  }
}
