package com.recoforejp.itemservice.feedback;

import jakarta.persistence.Column;
import jakarta.persistence.Entity;
import jakarta.persistence.GeneratedValue;
import jakarta.persistence.GenerationType;
import jakarta.persistence.Id;
import jakarta.persistence.Table;
import java.time.OffsetDateTime;
import java.util.UUID;
import lombok.AllArgsConstructor;
import lombok.Builder;
import lombok.Getter;
import lombok.NoArgsConstructor;
import lombok.Setter;
import org.hibernate.annotations.CreationTimestamp;

/**
 * {@code items.feedbacks}: ユーザーのアイテムに対する行動（view / click / favorite / rating）ログ。
 *
 * <p>{@code user_id} は {@code users.users(id)} への **論理 FK**（schema 跨ぎ）。{@code item_id} は
 * {@code items.items(id)} への物理 FK だが、JPA 上はリレーション化せず UUID 直持ち（軽量化）。
 *
 * <p>DB 側に CHECK 制約: feedbackType=rating の場合のみ rating は 1..5、その他は NULL。
 */
@Entity
@Table(name = "feedbacks")
@Getter
@Setter
@NoArgsConstructor
@AllArgsConstructor
@Builder
public class Feedback {

  @Id
  @GeneratedValue(strategy = GenerationType.IDENTITY)
  private Long id;

  @Column(name = "user_id", nullable = false)
  private UUID userId;

  @Column(name = "item_id", nullable = false)
  private UUID itemId;

  /** {@code view} / {@code click} / {@code favorite} / {@code rating} のいずれか。 */
  @Column(name = "feedback_type", nullable = false, length = 16)
  private String feedbackType;

  /** {@code feedbackType=rating} のとき 1..5。それ以外は null。 */
  @Column
  private Short rating;

  @CreationTimestamp
  @Column(name = "created_at", nullable = false, updatable = false)
  private OffsetDateTime createdAt;
}
