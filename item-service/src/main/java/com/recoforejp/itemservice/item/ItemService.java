package com.recoforejp.itemservice.item;

import com.recoforejp.itemservice.catalog.Category;
import com.recoforejp.itemservice.catalog.CategoryRepository;
import com.recoforejp.itemservice.catalog.Tag;
import com.recoforejp.itemservice.catalog.TagRepository;
import com.recoforejp.itemservice.item.dto.CreateItemRequest;
import com.recoforejp.itemservice.item.dto.UpdateItemRequest;
import java.util.HashMap;
import java.util.HashSet;
import java.util.List;
import java.util.Set;
import java.util.UUID;
import java.util.stream.Collectors;
import lombok.RequiredArgsConstructor;
import org.springframework.stereotype.Service;
import org.springframework.transaction.annotation.Transactional;

/** アイテム CRUD のビジネスロジック。 */
@Service
@RequiredArgsConstructor
public class ItemService {

  private final ItemRepository itemRepository;
  private final CategoryRepository categoryRepository;
  private final TagRepository tagRepository;

  /** 新規作成。category/tags の参照整合性を検証。 */
  @Transactional
  public Item create(CreateItemRequest req) {
    Category category = resolveCategory(req.getCategorySlug());
    Set<Tag> tags = resolveTags(req.getTags());

    Item item =
        Item.builder()
            .category(category)
            .title(req.getTitle())
            .description(req.getDescription())
            .url(req.getUrl())
            .region(req.getRegion())
            .source(req.getSource())
            .minJapaneseLevel(req.getMinJapaneseLevel())
            .metadata(req.getMetadata() != null ? req.getMetadata() : new HashMap<>())
            .publishedAt(req.getPublishedAt())
            .expiresAt(req.getExpiresAt())
            .tags(tags)
            .languages(req.getLanguages() != null ? new HashSet<>(req.getLanguages()) : new HashSet<>())
            .build();
    return itemRepository.save(item);
  }

  @Transactional(readOnly = true)
  public Item get(UUID id) {
    return itemRepository.findById(id).orElseThrow(() -> new ItemNotFoundException(id));
  }

  /**
   * フィルタ付き一覧取得。category と region は任意。両方指定の場合 AND。
   *
   * <p>MVP につきページングなし。データ規模が育ったら Pageable 化する。
   */
  @Transactional(readOnly = true)
  public List<Item> list(String categorySlug, String region) {
    List<Item> base;
    if (categorySlug != null) {
      Category c = resolveCategory(categorySlug);
      base = itemRepository.findByCategoryId(c.getId());
    } else if (region != null) {
      base = itemRepository.findByRegion(region);
    } else {
      base = itemRepository.findAll();
    }
    if (region != null && categorySlug != null) {
      return base.stream().filter(i -> region.equals(i.getRegion())).toList();
    }
    return base;
  }

  /** 部分更新。null フィールドは変更しない。{@code tags/languages} は {@code []} で全削除。 */
  @Transactional
  public Item update(UUID id, UpdateItemRequest req) {
    Item item = get(id);

    if (req.getCategorySlug() != null) {
      item.setCategory(resolveCategory(req.getCategorySlug()));
    }
    if (req.getTitle() != null) item.setTitle(req.getTitle());
    if (req.getDescription() != null) item.setDescription(req.getDescription());
    if (req.getUrl() != null) item.setUrl(req.getUrl());
    if (req.getRegion() != null) item.setRegion(req.getRegion());
    if (req.getSource() != null) item.setSource(req.getSource());
    if (req.getMinJapaneseLevel() != null) item.setMinJapaneseLevel(req.getMinJapaneseLevel());
    if (req.getMetadata() != null) item.setMetadata(req.getMetadata());
    if (req.getPublishedAt() != null) item.setPublishedAt(req.getPublishedAt());
    if (req.getExpiresAt() != null) item.setExpiresAt(req.getExpiresAt());
    if (req.getTags() != null) item.setTags(resolveTags(req.getTags()));
    if (req.getLanguages() != null) item.setLanguages(new HashSet<>(req.getLanguages()));

    return itemRepository.save(item);
  }

  @Transactional
  public void delete(UUID id) {
    if (!itemRepository.existsById(id)) {
      throw new ItemNotFoundException(id);
    }
    itemRepository.deleteById(id);
  }

  // ---- helpers ----

  private Category resolveCategory(String slug) {
    return categoryRepository
        .findBySlug(slug)
        .orElseThrow(() -> new InvalidReferenceException("Unknown category slug: " + slug));
  }

  private Set<Tag> resolveTags(Set<String> names) {
    if (names == null || names.isEmpty()) return new HashSet<>();
    Set<Tag> resolved = new HashSet<>();
    Set<String> missing = new HashSet<>();
    for (String name : names) {
      tagRepository.findByName(name).ifPresentOrElse(resolved::add, () -> missing.add(name));
    }
    if (!missing.isEmpty()) {
      String list = missing.stream().sorted().collect(Collectors.joining(", "));
      throw new InvalidReferenceException("Unknown tag names: " + list);
    }
    return resolved;
  }
}
