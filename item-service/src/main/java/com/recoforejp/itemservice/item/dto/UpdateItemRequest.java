package com.recoforejp.itemservice.item.dto;

import jakarta.validation.constraints.Pattern;
import jakarta.validation.constraints.Size;
import java.time.OffsetDateTime;
import java.util.Map;
import java.util.Set;
import lombok.AllArgsConstructor;
import lombok.Builder;
import lombok.Getter;
import lombok.NoArgsConstructor;
import lombok.Setter;

/**
 * アイテム部分更新リクエスト DTO。
 *
 * <p>各フィールド {@code null} は「変更しない」。{@code tags}/{@code languages} は {@code []} で全削除。
 */
@Getter
@Setter
@NoArgsConstructor
@AllArgsConstructor
@Builder
public class UpdateItemRequest {

  @Size(max = 64)
  private String categorySlug;

  @Size(max = 255)
  private String title;

  private String description;

  @Size(max = 1024)
  private String url;

  @Size(max = 64)
  private String region;

  @Size(max = 64)
  private String source;

  @Pattern(regexp = "^(N1|N2|N3|N4|N5)$", message = "must be one of N1..N5")
  private String minJapaneseLevel;

  private Map<String, Object> metadata;

  private OffsetDateTime publishedAt;

  private OffsetDateTime expiresAt;

  private Set<String> tags;

  private Set<String> languages;
}
