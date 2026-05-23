package com.recoforejp.userservice.user;

import static org.assertj.core.api.Assertions.assertThat;

import java.nio.file.Paths;
import java.time.LocalDate;
import java.util.Optional;
import org.junit.jupiter.api.Tag;
import org.junit.jupiter.api.Test;
import org.springframework.beans.factory.annotation.Autowired;
import org.springframework.boot.test.context.SpringBootTest;
import org.springframework.boot.testcontainers.service.connection.ServiceConnection;
import org.testcontainers.containers.PostgreSQLContainer;
import org.testcontainers.junit.jupiter.Container;
import org.testcontainers.junit.jupiter.Testcontainers;
import org.testcontainers.utility.DockerImageName;
import org.testcontainers.utility.MountableFile;

/**
 * {@link UserRepository} の DB 連携を実 PostgreSQL（Testcontainers）で確認する統合テスト。
 *
 * <p>{@code infra/postgres/init/*.sql} を必要な分だけコンテナの {@code
 * /docker-entrypoint-initdb.d/} にコピーし、本番と同じ DDL でテーブルを作成する。
 *
 * <p>Docker が動いていない環境ではこのテストは失敗する（{@code testcontainers.reuse.enable=true}
 * 設定で高速化可能）。
 */
@SpringBootTest
@Testcontainers
@Tag("integration")
class UserRepositoryIT {

  @Container @ServiceConnection
  static PostgreSQLContainer<?> postgres =
      new PostgreSQLContainer<>(
              DockerImageName.parse("pgvector/pgvector:pg16").asCompatibleSubstituteFor("postgres"))
          .withDatabaseName("reco")
          .withUsername("reco")
          .withPassword("reco_password")
          .withCopyFileToContainer(
              MountableFile.forHostPath(
                  Paths.get("../infra/postgres/init/01-extensions.sql").toAbsolutePath()),
              "/docker-entrypoint-initdb.d/01-extensions.sql")
          .withCopyFileToContainer(
              MountableFile.forHostPath(
                  Paths.get("../infra/postgres/init/02-schemas.sql").toAbsolutePath()),
              "/docker-entrypoint-initdb.d/02-schemas.sql")
          .withCopyFileToContainer(
              MountableFile.forHostPath(
                  Paths.get("../infra/postgres/init/03-users-schema.sql").toAbsolutePath()),
              "/docker-entrypoint-initdb.d/03-users-schema.sql");

  @Autowired UserRepository userRepository;

  @Test
  void saveAndFindByEmail_minimalUser() {
    User user =
        User.builder()
            .email("alice@example.com")
            .passwordHash("$2b$10$placeholder-not-a-real-hash")
            .nationality("VN")
            .nativeLanguage("vi")
            .build();

    User saved = userRepository.save(user);
    assertThat(saved.getId()).isNotNull();
    assertThat(saved.getCreatedAt()).isNotNull();
    assertThat(saved.getUpdatedAt()).isNotNull();

    Optional<User> found = userRepository.findByEmail("alice@example.com");
    assertThat(found).isPresent();
    assertThat(found.get().getNativeLanguage()).isEqualTo("vi");
    assertThat(found.get().getNationality()).isEqualTo("VN");
  }

  @Test
  void saveUserWithProfile_sharedPrimaryKey() {
    User user =
        User.builder()
            .email("bob@example.com")
            .passwordHash("$2b$10$placeholder-not-a-real-hash")
            .nationality("IN")
            .nativeLanguage("en")
            .build();

    UserProfile profile =
        UserProfile.builder()
            .user(user)
            .japaneseLevel("N5")
            .residencyStatus("engineer")
            .occupation("Software Engineer")
            .region("東京都-港区")
            .arrivalDate(LocalDate.of(2026, 4, 20))
            .lifeStage("arrival")
            .build();
    user.setProfile(profile);

    userRepository.save(user); // cascade なしなので、Profile は別途保存する必要あり
    // ※ 次の Story（API 実装）で UserProfileRepository を追加し、save 順を明確化する

    Optional<User> found = userRepository.findByEmail("bob@example.com");
    assertThat(found).isPresent();
    assertThat(found.get().getId()).isEqualTo(user.getId());
  }

  @Test
  void existsByEmail_returnsTrueWhenExists() {
    User user =
        User.builder()
            .email("charlie@example.com")
            .passwordHash("$2b$10$placeholder")
            .build();
    userRepository.save(user);

    assertThat(userRepository.existsByEmail("charlie@example.com")).isTrue();
    assertThat(userRepository.existsByEmail("nobody@example.com")).isFalse();
  }
}
