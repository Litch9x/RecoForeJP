package com.recoforejp.itemservice.feedback;

import static org.assertj.core.api.Assertions.assertThat;

import com.fasterxml.jackson.databind.JsonNode;
import com.fasterxml.jackson.databind.ObjectMapper;
import java.net.URI;
import java.net.http.HttpClient;
import java.net.http.HttpRequest;
import java.net.http.HttpResponse;
import java.nio.file.Paths;
import java.util.LinkedHashMap;
import java.util.List;
import java.util.Map;
import java.util.UUID;
import org.junit.jupiter.api.BeforeEach;
import org.junit.jupiter.api.Test;
import org.springframework.beans.factory.annotation.Autowired;
import org.springframework.boot.test.context.SpringBootTest;
import org.springframework.boot.test.web.server.LocalServerPort;
import org.springframework.boot.testcontainers.service.connection.ServiceConnection;
import org.testcontainers.containers.PostgreSQLContainer;
import org.testcontainers.junit.jupiter.Container;
import org.testcontainers.junit.jupiter.Testcontainers;
import org.testcontainers.utility.DockerImageName;
import org.testcontainers.utility.MountableFile;

/** {@code POST /feedbacks} および GET の統合テスト。 */
@SpringBootTest(webEnvironment = SpringBootTest.WebEnvironment.RANDOM_PORT)
@Testcontainers
@org.junit.jupiter.api.Tag("integration")
class FeedbackControllerIT {

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

  @LocalServerPort int port;
  @Autowired ObjectMapper objectMapper;

  HttpClient http;
  String baseUrl;

  @BeforeEach
  void setUp() {
    http = HttpClient.newHttpClient();
    baseUrl = "http://localhost:" + port;
  }

  HttpResponse<String> send(String method, String path, Object body) throws Exception {
    String json = body == null ? "" : objectMapper.writeValueAsString(body);
    HttpRequest.Builder rb =
        HttpRequest.newBuilder(URI.create(baseUrl + path))
            .header("Content-Type", "application/json");
    HttpRequest req =
        switch (method) {
          case "GET" -> rb.GET().build();
          case "POST" -> rb.POST(HttpRequest.BodyPublishers.ofString(json)).build();
          default -> throw new IllegalArgumentException(method);
        };
    return http.send(req, HttpResponse.BodyHandlers.ofString());
  }

  /** 既存カテゴリ・タグを使って 1 件アイテムを作成し ID を返す。 */
  private String createItem() throws Exception {
    Map<String, Object> body = new LinkedHashMap<>();
    body.put("categorySlug", "job-fulltime");
    body.put("title", "フィードバック検証用");
    body.put("region", "東京都-港区");
    body.put("metadata", Map.of());
    body.put("tags", List.of("foreigner-welcome"));
    body.put("languages", List.of("ja"));

    HttpResponse<String> res = send("POST", "/items", body);
    assertThat(res.statusCode()).isEqualTo(201);
    return objectMapper.readTree(res.body()).get("id").asText();
  }

  @Test
  void record_view_returnsCreatedWithNullRating() throws Exception {
    String itemId = createItem();
    Map<String, Object> body = new LinkedHashMap<>();
    body.put("userId", UUID.randomUUID().toString());
    body.put("itemId", itemId);
    body.put("feedbackType", "view");

    HttpResponse<String> res = send("POST", "/feedbacks", body);
    assertThat(res.statusCode()).isEqualTo(201);
    JsonNode r = objectMapper.readTree(res.body());
    assertThat(r.get("id").asLong()).isPositive();
    assertThat(r.get("feedbackType").asText()).isEqualTo("view");
    assertThat(r.get("rating").isNull()).isTrue();
  }

  @Test
  void record_rating_savesRatingValue() throws Exception {
    String itemId = createItem();
    Map<String, Object> body = new LinkedHashMap<>();
    body.put("userId", UUID.randomUUID().toString());
    body.put("itemId", itemId);
    body.put("feedbackType", "rating");
    body.put("rating", 5);

    HttpResponse<String> res = send("POST", "/feedbacks", body);
    assertThat(res.statusCode()).isEqualTo(201);
    assertThat(objectMapper.readTree(res.body()).get("rating").asInt()).isEqualTo(5);
  }

  @Test
  void record_rating_400WhenRatingMissing() throws Exception {
    String itemId = createItem();
    Map<String, Object> body = new LinkedHashMap<>();
    body.put("userId", UUID.randomUUID().toString());
    body.put("itemId", itemId);
    body.put("feedbackType", "rating");
    // no rating

    HttpResponse<String> res = send("POST", "/feedbacks", body);
    assertThat(res.statusCode()).isEqualTo(400);
    assertThat(objectMapper.readTree(res.body()).get("code").asText())
        .isEqualTo("INVALID_FEEDBACK");
  }

  @Test
  void record_404WhenItemMissing() throws Exception {
    Map<String, Object> body = new LinkedHashMap<>();
    body.put("userId", UUID.randomUUID().toString());
    body.put("itemId", "00000000-1111-2222-3333-444444444444");
    body.put("feedbackType", "click");

    HttpResponse<String> res = send("POST", "/feedbacks", body);
    assertThat(res.statusCode()).isEqualTo(404);
    assertThat(objectMapper.readTree(res.body()).get("code").asText())
        .isEqualTo("ITEM_NOT_FOUND");
  }

  @Test
  void record_400WhenFeedbackTypeUnknown() throws Exception {
    String itemId = createItem();
    Map<String, Object> body = new LinkedHashMap<>();
    body.put("userId", UUID.randomUUID().toString());
    body.put("itemId", itemId);
    body.put("feedbackType", "love"); // not allowed

    HttpResponse<String> res = send("POST", "/feedbacks", body);
    assertThat(res.statusCode()).isEqualTo(400);
    assertThat(objectMapper.readTree(res.body()).get("code").asText())
        .isEqualTo("VALIDATION_ERROR");
  }

  @Test
  void listByUserAndByItem_returnFeedbacks() throws Exception {
    String itemId = createItem();
    String userId = UUID.randomUUID().toString();

    for (String type : List.of("view", "click", "favorite")) {
      Map<String, Object> body = new LinkedHashMap<>();
      body.put("userId", userId);
      body.put("itemId", itemId);
      body.put("feedbackType", type);
      assertThat(send("POST", "/feedbacks", body).statusCode()).isEqualTo(201);
    }

    HttpResponse<String> byUser = send("GET", "/feedbacks/by-user/" + userId, null);
    assertThat(byUser.statusCode()).isEqualTo(200);
    assertThat(objectMapper.readTree(byUser.body()).size()).isEqualTo(3);

    HttpResponse<String> byItem = send("GET", "/feedbacks/by-item/" + itemId, null);
    assertThat(byItem.statusCode()).isEqualTo(200);
    assertThat(objectMapper.readTree(byItem.body()).size()).isEqualTo(3);
  }
}
