package com.recoforejp.itemservice;

import org.junit.jupiter.api.Test;
import org.springframework.boot.test.context.SpringBootTest;
import org.springframework.test.context.ActiveProfiles;

/**
 * 最小コンテキストロードテスト。"no-db" profile で DB 関連 autoconfig を除外。 実 DB を伴う検証は
 * {@code @Tag("integration")} の IT テストを別途追加する。
 */
@SpringBootTest
@ActiveProfiles("no-db")
class ItemServiceApplicationTests {

  @Test
  void contextLoads() {}
}
