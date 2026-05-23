package com.recoforejp.itemservice.feedback;

import static org.assertj.core.api.Assertions.assertThat;
import static org.assertj.core.api.Assertions.assertThatThrownBy;
import static org.mockito.ArgumentMatchers.any;
import static org.mockito.Mockito.never;
import static org.mockito.Mockito.verify;
import static org.mockito.Mockito.when;

import com.recoforejp.itemservice.feedback.dto.CreateFeedbackRequest;
import com.recoforejp.itemservice.item.ItemNotFoundException;
import com.recoforejp.itemservice.item.ItemRepository;
import java.util.UUID;
import org.junit.jupiter.api.Test;
import org.junit.jupiter.api.extension.ExtendWith;
import org.mockito.InjectMocks;
import org.mockito.Mock;
import org.mockito.junit.jupiter.MockitoExtension;

@ExtendWith(MockitoExtension.class)
class FeedbackServiceTest {

  @Mock FeedbackRepository feedbackRepository;
  @Mock ItemRepository itemRepository;
  @InjectMocks FeedbackService feedbackService;

  private final UUID userId = UUID.fromString("00000000-0000-0000-0000-000000000001");
  private final UUID itemId = UUID.fromString("10000000-0000-0000-0000-000000000001");

  @Test
  void record_view_savesWithNullRating() {
    when(itemRepository.existsById(itemId)).thenReturn(true);
    when(feedbackRepository.save(any(Feedback.class))).thenAnswer(inv -> inv.getArgument(0));

    Feedback saved =
        feedbackService.record(new CreateFeedbackRequest(userId, itemId, "view", null));

    assertThat(saved.getFeedbackType()).isEqualTo("view");
    assertThat(saved.getRating()).isNull();
  }

  @Test
  void record_view_dropsRatingIfSent() {
    when(itemRepository.existsById(itemId)).thenReturn(true);
    when(feedbackRepository.save(any(Feedback.class))).thenAnswer(inv -> inv.getArgument(0));

    Feedback saved =
        feedbackService.record(
            new CreateFeedbackRequest(userId, itemId, "click", (short) 4)); // rating ignored

    assertThat(saved.getRating()).isNull();
  }

  @Test
  void record_rating_requiresRatingValue() {
    when(itemRepository.existsById(itemId)).thenReturn(true);

    assertThatThrownBy(
            () -> feedbackService.record(new CreateFeedbackRequest(userId, itemId, "rating", null)))
        .isInstanceOf(InvalidFeedbackException.class)
        .hasMessageContaining("required");
    verify(feedbackRepository, never()).save(any());
  }

  @Test
  void record_rating_savesWhenInRange() {
    when(itemRepository.existsById(itemId)).thenReturn(true);
    when(feedbackRepository.save(any(Feedback.class))).thenAnswer(inv -> inv.getArgument(0));

    Feedback saved =
        feedbackService.record(new CreateFeedbackRequest(userId, itemId, "rating", (short) 5));

    assertThat(saved.getRating()).isEqualTo((short) 5);
  }

  @Test
  void record_404WhenItemMissing() {
    when(itemRepository.existsById(itemId)).thenReturn(false);

    assertThatThrownBy(
            () -> feedbackService.record(new CreateFeedbackRequest(userId, itemId, "view", null)))
        .isInstanceOf(ItemNotFoundException.class);
    verify(feedbackRepository, never()).save(any());
  }

  @Test
  void listByItem_throwsWhenItemMissing() {
    when(itemRepository.existsById(itemId)).thenReturn(false);
    assertThatThrownBy(() -> feedbackService.listByItem(itemId))
        .isInstanceOf(ItemNotFoundException.class);
  }
}
