package com.recoforejp.itemservice.item.dto;

import jakarta.validation.constraints.NotBlank;
import jakarta.validation.constraints.Pattern;
import jakarta.validation.constraints.Size;
import java.time.OffsetDateTime;
import java.util.HashMap;
import java.util.Map;
import java.util.Set;
import lombok.AllArgsConstructor;
import lombok.Builder;
import lombok.Getter;
import lombok.NoArgsConstructor;
import lombok.Setter;

/** アイテム作成リクエスト DTO。 */
@Getter
@Setter
@NoArgsConstructor
@AllArgsConstructor
@Builder
public class CreateItemRequest {

  /** 既存のカテゴリ slug（例: {@code job-fulltime}）。存在しないと 400。 */
  @NotBlank
  @Size(max = 64)
  private String categorySlug;

  @NotBlank
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

  /** カテゴリ固有の自由項目（JSONB）。null は空 {} として扱う。 */
  @Builder.Default private Map<String, Object> metadata = new HashMap<>();

  private OffsetDateTime publishedAt;

  private OffsetDateTime expiresAt;

  /** 既存タグの名前（例: {@code "foreigner-welcome"}）。未知の名前は 400。 */
  private Set<String> tags;

  /** BCP47 言語コード（例: {@code "ja"}, {@code "en"}）。 */
  private Set<String> languages;
}
