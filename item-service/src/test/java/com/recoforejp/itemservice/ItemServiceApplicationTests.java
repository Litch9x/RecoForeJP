package com.recoforejp.itemservice;

import com.recoforejp.itemservice.catalog.CategoryRepository;
import com.recoforejp.itemservice.catalog.TagRepository;
import com.recoforejp.itemservice.feedback.FeedbackRepository;
import com.recoforejp.itemservice.item.ItemRepository;
import org.junit.jupiter.api.Test;
import org.springframework.boot.test.context.SpringBootTest;
import org.springframework.test.context.ActiveProfiles;
import org.springframework.test.context.bean.override.mockito.MockitoBean;

/**
 * 最小コンテキストロードテスト。"no-db" profile で DB 関連 autoconfig を除外。
 *
 * <p>JPA リポジトリは autoconfig 除外で生成されないため、{@link MockitoBean} で配線を成立させる。
 */
@SpringBootTest
@ActiveProfiles("no-db")
class ItemServiceApplicationTests {

  @MockitoBean CategoryRepository categoryRepository;
  @MockitoBean TagRepository tagRepository;
  @MockitoBean ItemRepository itemRepository;
  @MockitoBean FeedbackRepository feedbackRepository;

  @Test
  void contextLoads() {}
}
