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

/** GET/PUT {@code /users/{id}/preferences} の統合テスト。 */
@SpringBootTest(webEnvironment = SpringBootTest.WebEnvironment.RANDOM_PORT)
@Testcontainers
@Tag("integration")
class UserPreferenceControllerIT {

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
    String json = body == null ? "" : objectMapper.writeValueAsString(body);
    HttpRequest req =
        switch (method) {
          case "GET" ->
              HttpRequest.newBuilder(URI.create(baseUrl + path))
                  .header("Content-Type", "application/json")
                  .GET()
                  .build();
          case "POST" ->
              HttpRequest.newBuilder(URI.create(baseUrl + path))
                  .header("Content-Type", "application/json")
                  .POST(HttpRequest.BodyPublishers.ofString(json))
                  .build();
          case "PUT" ->
              HttpRequest.newBuilder(URI.create(baseUrl + path))
                  .header("Content-Type", "application/json")
                  .PUT(HttpRequest.BodyPublishers.ofString(json))
                  .build();
          default -> throw new IllegalArgumentException(method);
        };
    return http.send(req, HttpResponse.BodyHandlers.ofString());
  }

  String registerAndGetId(String email) throws Exception {
    Map<String, String> req = new LinkedHashMap<>();
    req.put("email", email);
    req.put("password", "password123");
    HttpResponse<String> res = send("POST", "/users", req);
    assertThat(res.statusCode()).isEqualTo(201);
    return objectMapper.readTree(res.body()).get("id").asText();
  }

  @Test
  void getPreferences_returnsDefaultsWhenNotSet() throws Exception {
    String id = registerAndGetId("pref-default@example.com");
    HttpResponse<String> res = send("GET", "/users/" + id + "/preferences", null);

    assertThat(res.statusCode()).isEqualTo(200);
    JsonNode body = objectMapper.readTree(res.body());
    assertThat(body.get("userId").asText()).isEqualTo(id);
    assertThat(body.get("preferredLanguage").asText()).isEqualTo("ja");
    assertThat(body.get("notificationEnabled").asBoolean()).isTrue();
  }

  @Test
  void getPreferences_returns404WhenUserMissing() throws Exception {
    HttpResponse<String> res =
        send("GET", "/users/00000000-1111-2222-3333-444444444444/preferences", null);
    assertThat(res.statusCode()).isEqualTo(404);
  }

  @Test
  void upsertPreferences_createsThenPartialUpdates() throws Exception {
    String id = registerAndGetId("pref-upsert@example.com");

    // 1st PUT: set language to "vi"
    Map<String, Object> body1 = new LinkedHashMap<>();
    body1.put("preferredLanguage", "vi");
    HttpResponse<String> res1 = send("PUT", "/users/" + id + "/preferences", body1);
    assertThat(res1.statusCode()).isEqualTo(200);
    JsonNode r1 = objectMapper.readTree(res1.body());
    assertThat(r1.get("preferredLanguage").asText()).isEqualTo("vi");
    assertThat(r1.get("notificationEnabled").asBoolean()).isTrue(); // default

    // 2nd PUT: only flip notifications; language preserved
    Map<String, Object> body2 = new LinkedHashMap<>();
    body2.put("notificationEnabled", false);
    HttpResponse<String> res2 = send("PUT", "/users/" + id + "/preferences", body2);
    assertThat(res2.statusCode()).isEqualTo(200);
    JsonNode r2 = objectMapper.readTree(res2.body());
    assertThat(r2.get("preferredLanguage").asText()).isEqualTo("vi"); // preserved
    assertThat(r2.get("notificationEnabled").asBoolean()).isFalse();
  }

  @Test
  void upsertPreferences_rejectsInvalidLanguage() throws Exception {
    String id = registerAndGetId("pref-invalid@example.com");

    Map<String, Object> body = new LinkedHashMap<>();
    body.put("preferredLanguage", "JAPANESE"); // invalid BCP47

    HttpResponse<String> res = send("PUT", "/users/" + id + "/preferences", body);
    assertThat(res.statusCode()).isEqualTo(400);
    JsonNode r = objectMapper.readTree(res.body());
    assertThat(r.get("code").asText()).isEqualTo("VALIDATION_ERROR");
  }
}
