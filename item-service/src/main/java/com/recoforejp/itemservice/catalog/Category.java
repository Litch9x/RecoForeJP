package com.recoforejp.itemservice.catalog;

import jakarta.persistence.Column;
import jakarta.persistence.Entity;
import jakarta.persistence.FetchType;
import jakarta.persistence.GeneratedValue;
import jakarta.persistence.GenerationType;
import jakarta.persistence.Id;
import jakarta.persistence.JoinColumn;
import jakarta.persistence.ManyToOne;
import jakarta.persistence.Table;
import lombok.AllArgsConstructor;
import lombok.Builder;
import lombok.Getter;
import lombok.NoArgsConstructor;
import lombok.Setter;

/**
 * {@code items.categories} に対応するカテゴリ階層。
 *
 * <p>{@link #parent} で自己参照（トップレベルは {@code null}）。slug は {@code "job"} / {@code
 * "housing"} / {@code "admin"} などの内部識別子。
 */
@Entity
@Table(name = "categories")
@Getter
@Setter
@NoArgsConstructor
@AllArgsConstructor
@Builder
public class Category {

  @Id
  @GeneratedValue(strategy = GenerationType.IDENTITY)
  private Integer id;

  @Column(nullable = false, unique = true, length = 64)
  private String slug;

  @Column(name = "name_ja", nullable = false, length = 128)
  private String nameJa;

  @Column(name = "name_en", length = 128)
  private String nameEn;

  @ManyToOne(fetch = FetchType.LAZY)
  @JoinColumn(name = "parent_id")
  private Category parent;
}
