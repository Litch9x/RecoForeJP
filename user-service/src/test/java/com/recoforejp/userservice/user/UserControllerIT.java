package com.recoforejp.userservice.user;

import static org.assertj.core.api.Assertions.assertThat;

import com.fasterxml.jackson.databind.JsonNode;
import com.fasterxml.jackson.databind.ObjectMapper;
import java.net.URI;
import java.net.http.HttpClient;
import java.net.http.HttpRequest;
import java.net.http.HttpResponse;
import java.nio.file.Paths;
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

/**
 * {@code POST /users}（ユーザー登録）のエンドツーエンドテスト。
 *
 * <p>RANDOM_PORT で実サーバーを起動し、Java 標準の {@link HttpClient} で叩く（{@code
 * TestRestTemplate} 等の追加依存を避けるため）。
 */
@SpringBootTest(webEnvironment = SpringBootTest.WebEnvironment.RANDOM_PORT)
@Testcontainers
@Tag("integration")
class UserControllerIT {

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

  HttpResponse<String> postJson(String path, Object body) throws Exception {
    HttpRequest req =
        HttpRequest.newBuilder(URI.create(baseUrl + path))
            .header("Content-Type", "application/json")
            .POST(HttpRequest.BodyPublishers.ofString(objectMapper.writeValueAsString(body)))
            .build();
    return http.send(req, HttpResponse.BodyHandlers.ofString());
  }

  @Test
  void register_returnsCreatedAndUserResponse() throws Exception {
    var req =
        new java.util.HashMap<String, String>() {
          {
            put("email", "new@example.com");
            put("password", "password123");
            put("nationality", "JP");
            put("nativeLanguage", "ja");
          }
        };

    HttpResponse<String> response = postJson("/users", req);

    assertThat(response.statusCode()).isEqualTo(201);
    JsonNode body = objectMapper.readTree(response.body());
    assertThat(body.get("id").asText()).isNotEmpty();
    assertThat(body.get("email").asText()).isEqualTo("new@example.com");
    assertThat(body.get("nationality").asText()).isEqualTo("JP");
    assertThat(body.get("createdAt").asText()).isNotEmpty();
    // passwordHash は絶対に出さない
    assertThat(body.has("passwordHash")).isFalse();
  }

  @Test
  void register_returnsConflictWhenEmailDuplicate() throws Exception {
    var first =
        new java.util.HashMap<String, String>() {
          {
            put("email", "dup@example.com");
            put("password", "password123");
          }
        };
    postJson("/users", first);

    var second =
        new java.util.HashMap<String, String>() {
          {
            put("email", "dup@example.com");
            put("password", "password456");
          }
        };
    HttpResponse<String> response = postJson("/users", second);

    assertThat(response.statusCode()).isEqualTo(409);
    JsonNode body = objectMapper.readTree(response.body());
    assertThat(body.get("code").asText()).isEqualTo("EMAIL_ALREADY_EXISTS");
  }

  @Test
  void register_returnsBadRequestWhenValidationFails() throws Exception {
    var invalid =
        new java.util.HashMap<String, String>() {
          {
            put("email", "not-an-email");
            put("password", "short"); // 8 文字未満
            put("nationality", "japan"); // 2 文字大文字 ISO 違反
          }
        };

    HttpResponse<String> response = postJson("/users", invalid);

    assertThat(response.statusCode()).isEqualTo(400);
    JsonNode body = objectMapper.readTree(response.body());
    assertThat(body.get("code").asText()).isEqualTo("VALIDATION_ERROR");
    assertThat(body.get("details").isArray()).isTrue();
    assertThat(body.get("details").size()).isGreaterThan(0);
  }
}
