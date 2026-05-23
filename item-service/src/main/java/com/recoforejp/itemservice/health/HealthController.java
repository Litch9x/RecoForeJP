package com.recoforejp.itemservice.health;

import java.time.Instant;
import java.util.Map;
import org.springframework.web.bind.annotation.GetMapping;
import org.springframework.web.bind.annotation.RequestMapping;
import org.springframework.web.bind.annotation.RestController;

/**
 * 軽量ヘルスチェック。他サービス（api-gateway, user-service）と同じレスポンス形式。
 *
 * <p>詳細（DB 接続など）は {@code /actuator/health} を使用。
 */
@RestController
@RequestMapping("/health")
public class HealthController {

  @GetMapping
  public Map<String, Object> check() {
    return Map.of(
        "status", "ok",
        "service", "item-service",
        "timestamp", Instant.now().toString());
  }
}
