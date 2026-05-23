package com.recoforejp.itemservice.item;

import com.recoforejp.itemservice.catalog.Category;
import com.recoforejp.itemservice.catalog.Tag;
import jakarta.persistence.CollectionTable;
import jakarta.persistence.Column;
import jakarta.persistence.ElementCollection;
import jakarta.persistence.Entity;
import jakarta.persistence.FetchType;
import jakarta.persistence.Id;
import jakarta.persistence.JoinColumn;
import jakarta.persistence.JoinTable;
import jakarta.persistence.ManyToMany;
import jakarta.persistence.ManyToOne;
import jakarta.persistence.Table;
import java.time.OffsetDateTime;
import java.util.HashMap;
import java.util.HashSet;
import java.util.Map;
import java.util.Set;
import java.util.UUID;
import lombok.AllArgsConstructor;
import lombok.Builder;
import lombok.Getter;
import lombok.NoArgsConstructor;
import lombok.Setter;
import org.hibernate.annotations.CreationTimestamp;
import org.hibernate.annotations.JdbcTypeCode;
import org.hibernate.annotations.UpdateTimestamp;
import org.hibernate.annotations.UuidGenerator;
import org.hibernate.type.SqlTypes;

/**
 * {@code items.items} に対応する推薦対象アイテム。
 *
 * <p>関連:
 *
 * <ul>
 *   <li>{@link Category} と多対一（必須）
 *   <li>{@link Tag} と多対多（{@code item_tags} 経由）
 *   <li>対応言語は {@code item_languages} の文字列集合
 * </ul>
 *
 * <p>{@code metadata} はカテゴリ固有のフィールドを格納する JSONB（Hibernate 6 ネイティブ {@code
 * JdbcTypeCode(SqlTypes.JSON)}）。
 */
@Entity
@Table(name = "items")
@Getter
@Setter
@NoArgsConstructor
@AllArgsConstructor
@Builder
public class Item {

  @Id @UuidGenerator private UUID id;

  @ManyToOne(fetch = FetchType.LAZY, optional = false)
  @JoinColumn(name = "category_id", nullable = false)
  private Category category;

  @Column(nullable = false, length = 255)
  private String title;

  @Column(columnDefinition = "TEXT")
  private String description;

  @Column(length = 1024)
  private String url;

  @Column(length = 64)
  private String region;

  @Column(length = 64)
  private String source;

  @Column(name = "min_japanese_level", length = 4)
  private String minJapaneseLevel;

  /** カテゴリごとに異なる構造（求人なら時給、住居なら家賃など）を格納する自由項目。 */
  @JdbcTypeCode(SqlTypes.JSON)
  @Column(columnDefinition = "jsonb", nullable = false)
  @Builder.Default
  private Map<String, Object> metadata = new HashMap<>();

  @Column(name = "published_at")
  private OffsetDateTime publishedAt;

  @Column(name = "expires_at")
  private OffsetDateTime expiresAt;

  @CreationTimestamp
  @Column(name = "created_at", nullable = false, updatable = false)
  private OffsetDateTime createdAt;

  @UpdateTimestamp
  @Column(name = "updated_at", nullable = false)
  private OffsetDateTime updatedAt;

  @ManyToMany
  @JoinTable(
      name = "item_tags",
      joinColumns = @JoinColumn(name = "item_id"),
      inverseJoinColumns = @JoinColumn(name = "tag_id"))
  @Builder.Default
  private Set<Tag> tags = new HashSet<>();

  @ElementCollection
  @CollectionTable(name = "item_languages", joinColumns = @JoinColumn(name = "item_id"))
  @Column(name = "language", length = 8)
  @Builder.Default
  private Set<String> languages = new HashSet<>();
}
