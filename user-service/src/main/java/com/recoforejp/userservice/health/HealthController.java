package com.recoforejp.userservice.health;

import java.time.Instant;
import java.util.Map;
import org.springframework.web.bind.annotation.GetMapping;
import org.springframework.web.bind.annotation.RequestMapping;
import org.springframework.web.bind.annotation.RestController;

/**
 * 軽量ヘルスチェック。api-gateway の /health とレスポンス形式を揃える。
 *
 * <p>詳細な依存（DB 接続等）のチェックは Spring Boot Actuator が提供する
 * /actuator/health を使用すること。
 */
@RestController
@RequestMapping("/health")
public class HealthController {

    @GetMapping
    public Map<String, Object> check() {
        return Map.of(
                "status", "ok",
                "service", "user-service",
                "timestamp", Instant.now().toString());
    }
}
