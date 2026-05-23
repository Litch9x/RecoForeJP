package com.recoforejp.itemservice.feedback;

import java.util.List;
import java.util.UUID;
import org.springframework.data.jpa.repository.JpaRepository;

public interface FeedbackRepository extends JpaRepository<Feedback, Long> {

  List<Feedback> findByUserIdOrderByCreatedAtDesc(UUID userId);

  List<Feedback> findByItemIdOrderByCreatedAtDesc(UUID itemId);
}
