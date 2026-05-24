import {
  Body,
  Controller,
  Get,
  Put,
  UseGuards,
} from "@nestjs/common";
import type { AuthUser } from "../auth/auth-user";
import { CurrentUser } from "../auth/current-user.decorator";
import { JwtAuthGuard } from "../auth/jwt-auth.guard";
import { MeService } from "./me.service";

/**
 * 認証済みユーザー自身のリソース。JWT の subject から userId を取り、
 * user-service の {@code /users/{userId}/...} にプロキシする。
 *
 * クライアントは自分の userId を知る必要がなく、{@code /me} だけ覚えればよい。
 */
@Controller("me")
@UseGuards(JwtAuthGuard)
export class MeController {
  constructor(private readonly meService: MeService) {}

  @Get("profile")
  getProfile(@CurrentUser() user: AuthUser): Promise<unknown> {
    return this.meService.getProfile(user.userId);
  }

  @Put("profile")
  putProfile(
    @CurrentUser() user: AuthUser,
    @Body() body: Record<string, unknown>,
  ): Promise<unknown> {
    return this.meService.putProfile(user.userId, body);
  }

  @Get("preferences")
  getPreferences(@CurrentUser() user: AuthUser): Promise<unknown> {
    return this.meService.getPreferences(user.userId);
  }

  @Put("preferences")
  putPreferences(
    @CurrentUser() user: AuthUser,
    @Body() body: Record<string, unknown>,
  ): Promise<unknown> {
    return this.meService.putPreferences(user.userId, body);
  }
}
