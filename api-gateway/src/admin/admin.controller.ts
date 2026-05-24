import { Controller, Get, UseGuards } from "@nestjs/common";

import type { AuthUser } from "../auth/auth-user";
import { CurrentUser } from "../auth/current-user.decorator";
import { JwtAuthGuard } from "../auth/jwt-auth.guard";
import { Roles } from "../auth/roles.decorator";
import { RolesGuard } from "../auth/roles.guard";

/**
 * 管理者専用エンドポイント。次回 PR で /admin/items を追加する予定。
 * 今回は RBAC が機能していることを確認するための {@code /admin/ping} のみ。
 */
@Controller("admin")
@UseGuards(JwtAuthGuard, RolesGuard)
@Roles(["ADMIN"])
export class AdminController {
  @Get("ping")
  ping(@CurrentUser() user: AuthUser): { ok: true; role: string; email: string } {
    return { ok: true, role: user.role, email: user.email };
  }
}
