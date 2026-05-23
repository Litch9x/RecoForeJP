package com.recoforejp.userservice.config;

import org.springframework.context.annotation.Bean;
import org.springframework.context.annotation.Configuration;
import org.springframework.security.crypto.bcrypt.BCryptPasswordEncoder;
import org.springframework.security.crypto.password.PasswordEncoder;

/**
 * パスワードハッシュ用の {@link PasswordEncoder} を提供する。
 *
 * <p>Spring Security 本体は導入していないため、{@code spring-security-crypto} のみを依存に追加して
 * {@link BCryptPasswordEncoder} を直接 Bean 化する。
 */
@Configuration
public class PasswordEncoderConfig {

  /** strength は強度（コスト）。10 は妥当なデフォルト。 */
  @Bean
  public PasswordEncoder passwordEncoder() {
    return new BCryptPasswordEncoder(10);
  }
}
