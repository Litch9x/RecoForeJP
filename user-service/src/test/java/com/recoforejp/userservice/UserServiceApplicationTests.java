package com.recoforejp.userservice;

import com.recoforejp.userservice.user.UserRepository;
import org.junit.jupiter.api.Test;
import org.springframework.boot.test.context.SpringBootTest;
import org.springframework.test.context.ActiveProfiles;
import org.springframework.test.context.bean.override.mockito.MockitoBean;

/**
 * 最小コンテキストロードテスト。DB を必要としないため "no-db" profile を有効化し、 DataSource / JPA
 * の autoconfig を除外する。
 *
 * <p>{@link UserRepository} は JPA リポジトリ（autoconfig 除外で生成されない）のため、 {@link
 * MockitoBean} でモック化してアプリケーション全体の Bean 配線が成立することを確認する。
 *
 * <p>実 DB を伴う検証は {@code UserControllerIT} / {@code UserRepositoryIT} を参照。
 */
@SpringBootTest
@ActiveProfiles("no-db")
class UserServiceApplicationTests {

  @MockitoBean UserRepository userRepository;

  @Test
  void contextLoads() {}
}
