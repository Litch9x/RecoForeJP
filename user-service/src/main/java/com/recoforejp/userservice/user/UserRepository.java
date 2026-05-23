package com.recoforejp.userservice.user;

import java.util.Optional;
import java.util.UUID;
import org.springframework.data.jpa.repository.JpaRepository;

/**
 * {@link User} の Spring Data JPA リポジトリ。
 *
 * <p>{@code findByEmail} で、メールアドレスからユーザーを取得（ログイン時等で使用）。
 */
public interface UserRepository extends JpaRepository<User, UUID> {

  Optional<User> findByEmail(String email);

  boolean existsByEmail(String email);
}
