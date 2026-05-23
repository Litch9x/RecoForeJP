package com.recoforejp.userservice.user;

import jakarta.persistence.Column;
import jakarta.persistence.Entity;
import jakarta.persistence.IdClass;
import jakarta.persistence.Table;
import java.io.Serializable;
import java.util.Objects;
import java.util.UUID;
import lombok.AllArgsConstructor;
import lombok.Builder;
import lombok.Getter;
import lombok.NoArgsConstructor;
import lombok.Setter;

/**
 * {@code users.user_interests} に対応する興味分野エントリ。複合主キー {@code (user_id, interest)}。
 *
 * <p>ユーザーは複数の興味カテゴリ（例: {@code "japanese-learning"}, {@code "job"}, {@code
 * "housing"}）を持てる。
 */
@Entity
@Table(name = "user_interests")
@IdClass(UserInterest.Id.class)
@Getter
@Setter
@NoArgsConstructor
@AllArgsConstructor
@Builder
public class UserInterest {

  @jakarta.persistence.Id
  @Column(name = "user_id")
  private UUID userId;

  @jakarta.persistence.Id
  @Column(length = 64)
  private String interest;

  /** {@link IdClass} 用の複合主キー型。 */
  @Getter
  @Setter
  @NoArgsConstructor
  @AllArgsConstructor
  public static class Id implements Serializable {
    private UUID userId;
    private String interest;

    @Override
    public boolean equals(Object o) {
      if (this == o) return true;
      if (!(o instanceof Id other)) return false;
      return Objects.equals(userId, other.userId) && Objects.equals(interest, other.interest);
    }

    @Override
    public int hashCode() {
      return Objects.hash(userId, interest);
    }
  }
}
