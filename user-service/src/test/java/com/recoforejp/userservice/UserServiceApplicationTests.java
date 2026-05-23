package com.recoforejp.userservice;

import org.junit.jupiter.api.Test;
import org.springframework.boot.test.context.SpringBootTest;
import org.springframework.test.context.ActiveProfiles;

/**
 * 最小コンテキストロードテスト。DB を必要としないため "no-db" profile を有効化し、
 * DataSource / JPA の autoconfig を除外する（src/test/resources/application-no-db.properties）。
 *
 * <p>DB を実際に触る確認は {@code com.recoforejp.userservice.user.UserRepositoryIT} を参照。
 */
@SpringBootTest
@ActiveProfiles("no-db")
class UserServiceApplicationTests {

  @Test
  void contextLoads() {}
}
