package com.recoforejp.itemservice.item;

import static org.assertj.core.api.Assertions.assertThat;

import com.recoforejp.itemservice.catalog.Category;
import com.recoforejp.itemservice.catalog.CategoryRepository;
import com.recoforejp.itemservice.catalog.Tag;
import com.recoforejp.itemservice.catalog.TagRepository;
import com.recoforejp.itemservice.feedback.Feedback;
import com.recoforejp.itemservice.feedback.FeedbackRepository;
import java.nio.file.Paths;
import java.util.HashMap;
import java.util.HashSet;
import java.util.List;
import java.util.Map;
import java.util.Set;
import java.util.UUID;
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
 * Item / Category / Tag / Feedback リポジトリの実 PostgreSQL 連携テスト。
 *
 * <p>{@code infra/postgres/init/*.sql} のうち items schema 関連 + seed をマウントして検証。
 */
@SpringBootTest
@Testcontainers
@org.junit.jupiter.api.Tag("integration")
class ItemRepositoryIT {

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
                  Paths.get("../infra/postgres/init/04-items-schema.sql").toAbsolutePath()),
              "/docker-entrypoint-initdb.d/04-items-schema.sql")
          .withCopyFileToContainer(
              MountableFile.forHostPath(
                  Paths.get("../infra/postgres/init/10-seed-categories.sql").toAbsolutePath()),
              "/docker-entrypoint-initdb.d/10-seed-categories.sql")
          .withCopyFileToContainer(
              MountableFile.forHostPath(
                  Paths.get("../infra/postgres/init/11-seed-tags.sql").toAbsolutePath()),
              "/docker-entrypoint-initdb.d/11-seed-tags.sql");

  @Autowired CategoryRepository categoryRepository;
  @Autowired TagRepository tagRepository;
  @Autowired ItemRepository itemRepository;
  @Autowired FeedbackRepository feedbackRepository;

  @Test
  void seedCategories_areAvailableViaRepository() {
    assertThat(categoryRepository.findBySlug("job")).isPresent();
    assertThat(categoryRepository.findBySlug("housing")).isPresent();
    assertThat(categoryRepository.findBySlug("job-fulltime"))
        .hasValueSatisfying(c -> assertThat(c.getParent()).isNotNull());
  }

  @Test
  void seedTags_areAvailableViaRepository() {
    assertThat(tagRepository.findByName("foreigner-welcome")).isPresent();
    assertThat(tagRepository.findByName("vietnamese-ok")).isPresent();
  }

  @Test
  void saveItem_withCategoryTagsLanguagesAndJsonbMetadata() {
    Category job =
        categoryRepository
            .findBySlug("job-parttime")
            .orElseThrow(() -> new AssertionError("seed missing"));
    Tag foreignerWelcome =
        tagRepository
            .findByName("foreigner-welcome")
            .orElseThrow(() -> new AssertionError("seed missing"));
    Tag vietnameseOk =
        tagRepository
            .findByName("vietnamese-ok")
            .orElseThrow(() -> new AssertionError("seed missing"));

    Map<String, Object> meta = new HashMap<>();
    meta.put("hourly_wage", 1500);
    meta.put("shifts", List.of("morning", "afternoon"));

    Item item =
        Item.builder()
            .category(job)
            .title("ベトナム語話者向けカスタマーサポート（テスト）")
            .description("テストデータ")
            .region("東京都-渋谷区")
            .source("company-direct")
            .minJapaneseLevel("N4")
            .metadata(meta)
            .tags(new HashSet<>(Set.of(foreignerWelcome, vietnameseOk)))
            .languages(new HashSet<>(Set.of("ja", "vi")))
            .build();

    Item saved = itemRepository.save(item);
    assertThat(saved.getId()).isNotNull();
    assertThat(saved.getCreatedAt()).isNotNull();

    Item reloaded =
        itemRepository
            .findById(saved.getId())
            .orElseThrow(() -> new AssertionError("not found"));
    assertThat(reloaded.getCategory().getSlug()).isEqualTo("job-parttime");
    assertThat(reloaded.getTags()).hasSize(2);
    assertThat(reloaded.getLanguages()).containsExactlyInAnyOrder("ja", "vi");
    assertThat(reloaded.getMetadata()).containsEntry("hourly_wage", 1500);
  }

  @Test
  void findByCategoryAndRegion_workOnPersistedItems() {
    Category housing =
        categoryRepository
            .findBySlug("housing-apartment")
            .orElseThrow(() -> new AssertionError("seed missing"));

    Item item =
        Item.builder()
            .category(housing)
            .title("テスト物件（渋谷）")
            .region("東京都-渋谷区")
            .metadata(new HashMap<>(Map.of("rent", 75000)))
            .build();
    itemRepository.save(item);

    assertThat(itemRepository.findByCategoryId(housing.getId()))
        .anyMatch(i -> i.getTitle().equals("テスト物件（渋谷）"));
    assertThat(itemRepository.findByRegion("東京都-渋谷区"))
        .anyMatch(i -> i.getTitle().equals("テスト物件（渋谷）"));
  }

  @Test
  void saveFeedback_andFindByUser() {
    Category job =
        categoryRepository
            .findBySlug("job-parttime")
            .orElseThrow(() -> new AssertionError("seed missing"));
    Item item =
        itemRepository.save(
            Item.builder()
                .category(job)
                .title("フィードバックテスト用アイテム")
                .metadata(new HashMap<>())
                .build());

    UUID userId = UUID.randomUUID();
    feedbackRepository.save(
        Feedback.builder()
            .userId(userId)
            .itemId(item.getId())
            .feedbackType("favorite")
            .build());
    feedbackRepository.save(
        Feedback.builder()
            .userId(userId)
            .itemId(item.getId())
            .feedbackType("rating")
            .rating((short) 5)
            .build());

    List<Feedback> byUser = feedbackRepository.findByUserIdOrderByCreatedAtDesc(userId);
    assertThat(byUser).hasSize(2);
    List<Feedback> byItem = feedbackRepository.findByItemIdOrderByCreatedAtDesc(item.getId());
    assertThat(byItem).hasSize(2);
  }
}
