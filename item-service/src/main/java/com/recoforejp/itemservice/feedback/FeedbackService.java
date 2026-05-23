package com.recoforejp.itemservice.feedback;

import com.recoforejp.itemservice.feedback.dto.CreateFeedbackRequest;
import com.recoforejp.itemservice.item.ItemNotFoundException;
import com.recoforejp.itemservice.item.ItemRepository;
import java.util.List;
import java.util.UUID;
import lombok.RequiredArgsConstructor;
import org.springframework.stereotype.Service;
import org.springframework.transaction.annotation.Transactional;

/**
 * フィードバック記録・参照のビジネスロジック。
 *
 * <p>{@code feedbackType=rating} のときは {@code rating} 必須（1〜5）。それ以外の type で {@code
 * rating} が来た場合は無視（null 化）して保存する。
 */
@Service
@RequiredArgsConstructor
public class FeedbackService {

  private static final String TYPE_RATING = "rating";

  private final FeedbackRepository feedbackRepository;
  private final ItemRepository itemRepository;

  @Transactional
  public Feedback record(CreateFeedbackRequest req) {
    if (!itemRepository.existsById(req.getItemId())) {
      throw new ItemNotFoundException(req.getItemId());
    }
    Short rating = normalizeRating(req.getFeedbackType(), req.getRating());

    Feedback fb =
        Feedback.builder()
            .userId(req.getUserId())
            .itemId(req.getItemId())
            .feedbackType(req.getFeedbackType())
            .rating(rating)
            .build();
    return feedbackRepository.save(fb);
  }

  @Transactional(readOnly = true)
  public List<Feedback> listByUser(UUID userId) {
    return feedbackRepository.findByUserIdOrderByCreatedAtDesc(userId);
  }

  @Transactional(readOnly = true)
  public List<Feedback> listByItem(UUID itemId) {
    if (!itemRepository.existsById(itemId)) {
      throw new ItemNotFoundException(itemId);
    }
    return feedbackRepository.findByItemIdOrderByCreatedAtDesc(itemId);
  }

  /**
   * type が rating の場合 1〜5 必須。それ以外の type で rating が来たら null にクランプ（DB CHECK 制約と整合）。
   */
  private Short normalizeRating(String type, Short rating) {
    if (TYPE_RATING.equals(type)) {
      if (rating == null) {
        throw new InvalidFeedbackException("rating is required when feedbackType=rating");
      }
      if (rating < 1 || rating > 5) {
        throw new InvalidFeedbackException("rating must be between 1 and 5");
      }
      return rating;
    }
    return null;
  }
}
