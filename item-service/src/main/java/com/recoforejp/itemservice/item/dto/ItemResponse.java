package com.recoforejp.itemservice.item.dto;

import com.recoforejp.itemservice.catalog.Tag;
import com.recoforejp.itemservice.item.Item;
import java.time.OffsetDateTime;
import java.util.Comparator;
import java.util.List;
import java.util.Map;
import java.util.UUID;
import lombok.AllArgsConstructor;
import lombok.Builder;
import lombok.Getter;

/** アイテム応答 DTO。 */
@Getter
@Builder
@AllArgsConstructor
public class ItemResponse {

  private final UUID id;
  private final String categorySlug;
  private final String categoryNameJa;
  private final String title;
  private final String description;
  private final String url;
  private final String region;
  private final String source;
  private final String minJapaneseLevel;
  private final Map<String, Object> metadata;
  private final OffsetDateTime publishedAt;
  private final OffsetDateTime expiresAt;
  private final OffsetDateTime createdAt;
  private final OffsetDateTime updatedAt;
  private final List<String> tags;
  private final List<String> languages;

  public static ItemResponse from(Item item) {
    return ItemResponse.builder()
        .id(item.getId())
        .categorySlug(item.getCategory().getSlug())
        .categoryNameJa(item.getCategory().getNameJa())
        .title(item.getTitle())
        .description(item.getDescription())
        .url(item.getUrl())
        .region(item.getRegion())
        .source(item.getSource())
        .minJapaneseLevel(item.getMinJapaneseLevel())
        .metadata(item.getMetadata())
        .publishedAt(item.getPublishedAt())
        .expiresAt(item.getExpiresAt())
        .createdAt(item.getCreatedAt())
        .updatedAt(item.getUpdatedAt())
        .tags(item.getTags().stream().map(Tag::getName).sorted().toList())
        .languages(item.getLanguages().stream().sorted(Comparator.naturalOrder()).toList())
        .build();
  }
}
