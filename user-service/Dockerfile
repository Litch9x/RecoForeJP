# ============================================================
# user-service - Multi-stage Dockerfile
# ============================================================

# ---- Stage 1: build ----
FROM eclipse-temurin:21-jdk-alpine AS builder

WORKDIR /app

# Gradle Wrapper をコピーし、実行権限を付与（Windows host からだと欠落するため）
COPY gradlew ./
COPY gradle gradle
RUN chmod +x gradlew

# 依存定義をコピーして wrapper を初期化（依存キャッシュ目的）
COPY settings.gradle build.gradle ./
RUN ./gradlew --no-daemon dependencies > /dev/null 2>&1 || true

# ソースをコピーしてビルド（テストはスキップ：Docker ビルドの高速化）
COPY src src
RUN ./gradlew --no-daemon bootJar -x test

# ---- Stage 2: runtime ----
FROM eclipse-temurin:21-jre-alpine

WORKDIR /app

ENV PORT=8081

# wget は alpine の busybox に内蔵（HEALTHCHECK で使用）

COPY --from=builder /app/build/libs/*.jar app.jar

# 非 root ユーザーで実行
RUN addgroup -g 1000 spring && adduser -u 1000 -G spring -s /bin/sh -D spring
USER spring:spring

EXPOSE 8081

HEALTHCHECK --interval=30s --timeout=5s --start-period=60s --retries=3 \
    CMD wget --quiet --tries=1 --spider http://localhost:8081/health || exit 1

ENTRYPOINT ["java", "-jar", "app.jar"]
