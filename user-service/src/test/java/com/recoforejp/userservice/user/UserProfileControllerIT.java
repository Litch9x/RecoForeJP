package com.recoforejp.userservice.user;

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
import org.junit.jupiter.api.Tag;
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

/** プロフィール関連エンドポイント（GET/PUT {@code /users/{id}/profile}）の統合テスト。 */
@SpringBootTest(webEnvironment = SpringBootTest.WebEnvironment.RANDOM_PORT)
@Testcontainers
@Tag("integration")
class UserProfileControllerIT {

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
    HttpRequest.Builder rb =
        HttpRequest.newBuilder(URI.create(baseUrl + path))
            .header("Content-Type", "application/json");
    String json = body == null ? "" : objectMapper.writeValueAsString(body);
    HttpRequest req =
        switch (method) {
          case "GET" -> rb.GET().build();
          case "POST" -> rb.POST(HttpRequest.BodyPublishers.ofString(json)).build();
          case "PUT" -> rb.PUT(HttpRequest.BodyPublishers.ofString(json)).build();
          default -> throw new IllegalArgumentException(method);
        };
    return http.send(req, HttpResponse.BodyHandlers.ofString());
  }

  /** 登録 → ID 抽出 のヘルパ。 */
  String registerAndGetId(String email) throws Exception {
    Map<String, String> req = new LinkedHashMap<>();
    req.put("email", email);
    req.put("password", "password123");
    HttpResponse<String> res = send("POST", "/users", req);
    assertThat(res.statusCode()).isEqualTo(201);
    return objectMapper.readTree(res.body()).get("id").asText();
  }

  @Test
  void getProfile_returnsEmptyShapeWhenProfileNotSet() throws Exception {
    String id = registerAndGetId("get-empty@example.com");

    HttpResponse<String> res = send("GET", "/users/" + id + "/profile", null);

    assertThat(res.statusCode()).isEqualTo(200);
    JsonNode body = objectMapper.readTree(res.body());
    assertThat(body.get("userId").asText()).isEqualTo(id);
    assertThat(body.get("japaneseLevel").isNull()).isTrue();
    assertThat(body.get("interests").isArray()).isTrue();
    assertThat(body.get("interests").size()).isZero();
  }

  @Test
  void getProfile_returns404WhenUserMissing() throws Exception {
    HttpResponse<String> res =
        send("GET", "/users/00000000-1111-2222-3333-444444444444/profile", null);
    assertThat(res.statusCode()).isEqualTo(404);
    JsonNode body = objectMapper.readTree(res.body());
    assertThat(body.get("code").asText()).isEqualTo("USER_NOT_FOUND");
  }

  @Test
  void upsertProfile_createsAndUpdatesIncludingInterests() throws Exception {
    String id = registerAndGetId("upsert@example.com");

    // ----- 1st PUT: create -----
    Map<String, Object> body1 = new LinkedHashMap<>();
    body1.put("japaneseLevel", "N3");
    body1.put("residencyStatus", "student");
    body1.put("occupation", "大学生");
    body1.put("region", "東京都-新宿区");
    body1.put("arrivalDate", "2025-11-15");
    body1.put("lifeStage", "settled");
    body1.put("interests", List.of("japanese-learning", "job"));

    HttpResponse<String> res1 = send("PUT", "/users/" + id + "/profile", body1);
    assertThat(res1.statusCode()).isEqualTo(200);
    JsonNode r1 = objectMapper.readTree(res1.body());
    assertThat(r1.get("japaneseLevel").asText()).isEqualTo("N3");
    assertThat(r1.get("lifeStage").asText()).isEqualTo("settled");
    // sorted
    assertThat(r1.get("interests").get(0).asText()).isEqualTo("japanese-learning");
    assertThat(r1.get("interests").get(1).asText()).isEqualTo("job");

    // ----- 2nd PUT: update, replace interests -----
    Map<String, Object> body2 = new LinkedHashMap<>();
    body2.put("japaneseLevel", "N2");
    body2.put("interests", List.of("housing"));

    HttpResponse<String> res2 = send("PUT", "/users/" + id + "/profile", body2);
    assertThat(res2.statusCode()).isEqualTo(200);
    JsonNode r2 = objectMapper.readTree(res2.body());
    assertThat(r2.get("japaneseLevel").asText()).isEqualTo("N2");
    assertThat(r2.get("residencyStatus").isNull()).isTrue(); // cleared
    assertThat(r2.get("interests").size()).isEqualTo(1);
    assertThat(r2.get("interests").get(0).asText()).isEqualTo("housing");
  }

  @Test
  void upsertProfile_rejectsInvalidJapaneseLevel() throws Exception {
    String id = registerAndGetId("invalid-level@example.com");

    Map<String, Object> body = new LinkedHashMap<>();
    body.put("japaneseLevel", "N0"); // invalid

    HttpResponse<String> res = send("PUT", "/users/" + id + "/profile", body);
    assertThat(res.statusCode()).isEqualTo(400);
    JsonNode r = objectMapper.readTree(res.body());
    assertThat(r.get("code").asText()).isEqualTo("VALIDATION_ERROR");
  }

  @Test
  void getUser_returnsBasicInfo() throws Exception {
    String id = registerAndGetId("basic@example.com");

    HttpResponse<String> res = send("GET", "/users/" + id, null);
    assertThat(res.statusCode()).isEqualTo(200);
    JsonNode body = objectMapper.readTree(res.body());
    assertThat(body.get("email").asText()).isEqualTo("basic@example.com");
    assertThat(body.has("passwordHash")).isFalse();
  }
}
