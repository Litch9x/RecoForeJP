package com.recoforejp.userservice.user;

import com.recoforejp.userservice.user.dto.ProfileResponse;
import com.recoforejp.userservice.user.dto.RegisterUserRequest;
import com.recoforejp.userservice.user.dto.UpdateProfileRequest;
import com.recoforejp.userservice.user.dto.UserResponse;
import jakarta.validation.Valid;
import java.util.UUID;
import lombok.RequiredArgsConstructor;
import org.springframework.http.HttpStatus;
import org.springframework.web.bind.annotation.GetMapping;
import org.springframework.web.bind.annotation.PathVariable;
import org.springframework.web.bind.annotation.PostMapping;
import org.springframework.web.bind.annotation.PutMapping;
import org.springframework.web.bind.annotation.RequestBody;
import org.springframework.web.bind.annotation.RequestMapping;
import org.springframework.web.bind.annotation.ResponseStatus;
import org.springframework.web.bind.annotation.RestController;

/** ユーザー関連 REST エンドポイント。 */
@RestController
@RequestMapping("/users")
@RequiredArgsConstructor
public class UserController {

  private final UserService userService;
  private final UserProfileService profileService;
  private final UserRepository userRepository;

  /** ユーザー新規登録。成功時 201 Created を返す。 */
  @PostMapping
  @ResponseStatus(HttpStatus.CREATED)
  public UserResponse register(@Valid @RequestBody RegisterUserRequest request) {
    return UserResponse.from(userService.register(request));
  }

  /** 単一ユーザーの基本情報。 */
  @GetMapping("/{id}")
  public UserResponse getUser(@PathVariable UUID id) {
    return userRepository
        .findById(id)
        .map(UserResponse::from)
        .orElseThrow(() -> new UserNotFoundException(id));
  }

  /** ユーザーのプロフィール + 興味分野を取得。プロフィール未設定でも 200。 */
  @GetMapping("/{id}/profile")
  public ProfileResponse getProfile(@PathVariable UUID id) {
    return profileService.getProfile(id);
  }

  /** プロフィール upsert（存在しなければ作成、あれば更新）。興味も置き換え可能。 */
  @PutMapping("/{id}/profile")
  public ProfileResponse upsertProfile(
      @PathVariable UUID id, @Valid @RequestBody UpdateProfileRequest request) {
    return profileService.upsertProfile(id, request);
  }
}
