package com.recoforejp.itemservice.feedback;

import com.recoforejp.itemservice.feedback.dto.CreateFeedbackRequest;
import com.recoforejp.itemservice.feedback.dto.FeedbackResponse;
import jakarta.validation.Valid;
import java.util.List;
import java.util.UUID;
import lombok.RequiredArgsConstructor;
import org.springframework.http.HttpStatus;
import org.springframework.web.bind.annotation.GetMapping;
import org.springframework.web.bind.annotation.PathVariable;
import org.springframework.web.bind.annotation.PostMapping;
import org.springframework.web.bind.annotation.RequestBody;
import org.springframework.web.bind.annotation.RequestMapping;
import org.springframework.web.bind.annotation.ResponseStatus;
import org.springframework.web.bind.annotation.RestController;

/** フィードバック関連 REST エンドポイント。 */
@RestController
@RequestMapping("/feedbacks")
@RequiredArgsConstructor
public class FeedbackController {

  private final FeedbackService feedbackService;

  /** フィードバック記録（view/click/favorite/rating）。201 を返す。 */
  @PostMapping
  @ResponseStatus(HttpStatus.CREATED)
  public FeedbackResponse record(@Valid @RequestBody CreateFeedbackRequest request) {
    return FeedbackResponse.from(feedbackService.record(request));
  }

  /** 指定ユーザーのフィードバック履歴（最新順）。 */
  @GetMapping("/by-user/{userId}")
  public List<FeedbackResponse> listByUser(@PathVariable UUID userId) {
    return feedbackService.listByUser(userId).stream().map(FeedbackResponse::from).toList();
  }

  /** 指定アイテムへのフィードバック一覧（最新順）。 */
  @GetMapping("/by-item/{itemId}")
  public List<FeedbackResponse> listByItem(@PathVariable UUID itemId) {
    return feedbackService.listByItem(itemId).stream().map(FeedbackResponse::from).toList();
  }
}
