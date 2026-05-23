package com.recoforejp.itemservice.item;

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

/** Item CRUD エンドポイントのエンドツーエンドテスト。 */
@SpringBootTest(webEnvironment = SpringBootTest.WebEnvironment.RANDOM_PORT)
@Testcontainers
@org.junit.jupiter.api.Tag("integration")
class ItemControllerIT {

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
          case "PUT" -> rb.PUT(HttpRequest.BodyPublishers.ofString(json)).build();
          case "DELETE" -> rb.DELETE().build();
          default -> throw new IllegalArgumentException(method);
        };
    return http.send(req, HttpResponse.BodyHandlers.ofString());
  }

  private Map<String, Object> baseCreateBody() {
    Map<String, Object> body = new LinkedHashMap<>();
    body.put("categorySlug", "job-fulltime");
    body.put("title", "外国人向け IT エンジニア");
    body.put("description", "テスト案件");
    body.put("region", "東京都-港区");
    body.put("source", "company-direct");
    body.put("minJapaneseLevel", "N5");
    body.put("metadata", Map.of("salary_min", 4000000, "remote_ok", true));
    body.put("tags", List.of("foreigner-welcome", "english-ok"));
    body.put("languages", List.of("ja", "en"));
    return body;
  }

  @Test
  void create_returnsCreatedAndFullItem() throws Exception {
    HttpResponse<String> res = send("POST", "/items", baseCreateBody());
    assertThat(res.statusCode()).isEqualTo(201);

    JsonNode body = objectMapper.readTree(res.body());
    assertThat(body.get("id").asText()).isNotEmpty();
    assertThat(body.get("categorySlug").asText()).isEqualTo("job-fulltime");
    assertThat(body.get("title").asText()).isEqualTo("外国人向け IT エンジニア");
    assertThat(body.get("tags").size()).isEqualTo(2);
    assertThat(body.get("languages").get(0).asText()).isEqualTo("en"); // sorted
    assertThat(body.get("metadata").get("salary_min").asInt()).isEqualTo(4000000);
  }

  @Test
  void create_returns400WhenCategoryUnknown() throws Exception {
    Map<String, Object> body = baseCreateBody();
    body.put("categorySlug", "no-such-category");

    HttpResponse<String> res = send("POST", "/items", body);
    assertThat(res.statusCode()).isEqualTo(400);
    assertThat(objectMapper.readTree(res.body()).get("code").asText())
        .isEqualTo("INVALID_REFERENCE");
  }

  @Test
  void create_returns400WhenTagUnknown() throws Exception {
    Map<String, Object> body = baseCreateBody();
    body.put("tags", List.of("foreigner-welcome", "this-tag-does-not-exist"));

    HttpResponse<String> res = send("POST", "/items", body);
    assertThat(res.statusCode()).isEqualTo(400);
  }

  @Test
  void create_returns400OnValidationFailure() throws Exception {
    Map<String, Object> body = baseCreateBody();
    body.remove("title"); // required

    HttpResponse<String> res = send("POST", "/items", body);
    assertThat(res.statusCode()).isEqualTo(400);
    assertThat(objectMapper.readTree(res.body()).get("code").asText())
        .isEqualTo("VALIDATION_ERROR");
  }

  @Test
  void get_returnsItemThen404AfterDelete() throws Exception {
    String id = create();

    HttpResponse<String> got = send("GET", "/items/" + id, null);
    assertThat(got.statusCode()).isEqualTo(200);

    HttpResponse<String> del = send("DELETE", "/items/" + id, null);
    assertThat(del.statusCode()).isEqualTo(204);

    HttpResponse<String> after = send("GET", "/items/" + id, null);
    assertThat(after.statusCode()).isEqualTo(404);
    assertThat(objectMapper.readTree(after.body()).get("code").asText())
        .isEqualTo("ITEM_NOT_FOUND");
  }

  @Test
  void update_partialKeepsExistingFields() throws Exception {
    String id = create();

    Map<String, Object> patch = new LinkedHashMap<>();
    patch.put("title", "更新後タイトル");
    patch.put("tags", List.of("foreigner-welcome")); // 一つに置換

    HttpResponse<String> res = send("PUT", "/items/" + id, patch);
    assertThat(res.statusCode()).isEqualTo(200);
    JsonNode body = objectMapper.readTree(res.body());
    assertThat(body.get("title").asText()).isEqualTo("更新後タイトル");
    assertThat(body.get("tags").size()).isEqualTo(1);
    // description は変更してないので元のまま
    assertThat(body.get("description").asText()).isEqualTo("テスト案件");
  }

  @Test
  void list_filtersByCategoryAndRegion() throws Exception {
    create(); // job-fulltime / 東京都-港区
    HttpResponse<String> byCategory = send("GET", "/items?category=job-fulltime", null);
    assertThat(byCategory.statusCode()).isEqualTo(200);
    assertThat(objectMapper.readTree(byCategory.body()).isArray()).isTrue();
    assertThat(objectMapper.readTree(byCategory.body()).size()).isGreaterThanOrEqualTo(1);

    HttpResponse<String> byRegion = send("GET", "/items?region=東京都-港区", null);
    assertThat(byRegion.statusCode()).isEqualTo(200);
    assertThat(objectMapper.readTree(byRegion.body()).size()).isGreaterThanOrEqualTo(1);
  }

  private String create() throws Exception {
    HttpResponse<String> res = send("POST", "/items", baseCreateBody());
    assertThat(res.statusCode()).isEqualTo(201);
    return objectMapper.readTree(res.body()).get("id").asText();
  }
}
