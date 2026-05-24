package com.recoforejp.userservice.auth;

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

/** {@code POST /internal/auth/verify} のエンドツーエンドテスト。 */
@SpringBootTest(webEnvironment = SpringBootTest.WebEnvironment.RANDOM_PORT)
@Testcontainers
@Tag("integration")
class AuthControllerIT {

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

  private String registerUser(String email, String password) throws Exception {
    var req =
        new java.util.HashMap<String, String>() {
          {
            put("email", email);
            put("password", password);
          }
        };
    HttpResponse<String> res = postJson("/users", req);
    assertThat(res.statusCode()).isEqualTo(201);
    return objectMapper.readTree(res.body()).get("id").asText();
  }

  @Test
  void verify_returnsOkAndUserId_whenCredentialsMatch() throws Exception {
    String userId = registerUser("auth-ok@example.com", "password123");

    var req =
        new java.util.HashMap<String, String>() {
          {
            put("email", "auth-ok@example.com");
            put("password", "password123");
          }
        };
    HttpResponse<String> res = postJson("/internal/auth/verify", req);

    assertThat(res.statusCode()).isEqualTo(200);
    JsonNode body = objectMapper.readTree(res.body());
    assertThat(body.get("userId").asText()).isEqualTo(userId);
    assertThat(body.get("email").asText()).isEqualTo("auth-ok@example.com");
    // 新規登録ユーザーは USER ロール（DEFAULT）
    assertThat(body.get("role").asText()).isEqualTo("USER");
    // passwordHash を含めない
    assertThat(body.has("passwordHash")).isFalse();
  }

  @Test
  void verify_returnsUnauthorized_whenPasswordMismatch() throws Exception {
    registerUser("auth-bad-pw@example.com", "password123");

    var req =
        new java.util.HashMap<String, String>() {
          {
            put("email", "auth-bad-pw@example.com");
            put("password", "wrong-password");
          }
        };
    HttpResponse<String> res = postJson("/internal/auth/verify", req);

    assertThat(res.statusCode()).isEqualTo(401);
    JsonNode body = objectMapper.readTree(res.body());
    assertThat(body.get("code").asText()).isEqualTo("INVALID_CREDENTIALS");
  }

  @Test
  void verify_returnsUnauthorized_whenEmailNotFound() throws Exception {
    var req =
        new java.util.HashMap<String, String>() {
          {
            put("email", "ghost@example.com");
            put("password", "password123");
          }
        };
    HttpResponse<String> res = postJson("/internal/auth/verify", req);

    assertThat(res.statusCode()).isEqualTo(401);
    JsonNode body = objectMapper.readTree(res.body());
    assertThat(body.get("code").asText()).isEqualTo("INVALID_CREDENTIALS");
  }

  @Test
  void verify_returnsBadRequest_whenEmailInvalid() throws Exception {
    var req =
        new java.util.HashMap<String, String>() {
          {
            put("email", "not-an-email");
            put("password", "password123");
          }
        };
    HttpResponse<String> res = postJson("/internal/auth/verify", req);

    assertThat(res.statusCode()).isEqualTo(400);
    JsonNode body = objectMapper.readTree(res.body());
    assertThat(body.get("code").asText()).isEqualTo("VALIDATION_ERROR");
  }
}
