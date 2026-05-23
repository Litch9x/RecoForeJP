package com.recoforejp.userservice.user;

import java.util.List;
import java.util.UUID;
import org.springframework.data.jpa.repository.JpaRepository;
import org.springframework.data.jpa.repository.Modifying;
import org.springframework.data.jpa.repository.Query;
import org.springframework.transaction.annotation.Transactional;

public interface UserInterestRepository extends JpaRepository<UserInterest, UserInterest.Id> {

  List<UserInterest> findByUserId(UUID userId);

  @Modifying
  @Transactional
  @Query("DELETE FROM UserInterest ui WHERE ui.userId = :userId")
  int deleteByUserId(UUID userId);
}
