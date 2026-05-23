package com.recoforejp.itemservice.feedback.dto;

import com.recoforejp.itemservice.feedback.Feedback;
import java.time.OffsetDateTime;
import java.util.UUID;
import lombok.AllArgsConstructor;
import lombok.Builder;
import lombok.Getter;

@Getter
@Builder
@AllArgsConstructor
public class FeedbackResponse {

  private final Long id;
  private final UUID userId;
  private final UUID itemId;
  private final String feedbackType;
  private final Short rating;
  private final OffsetDateTime createdAt;

  public static FeedbackResponse from(Feedback f) {
    return FeedbackResponse.builder()
        .id(f.getId())
        .userId(f.getUserId())
        .itemId(f.getItemId())
        .feedbackType(f.getFeedbackType())
        .rating(f.getRating())
        .createdAt(f.getCreatedAt())
        .build();
  }
}
