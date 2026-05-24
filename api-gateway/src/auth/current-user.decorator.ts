import { ExecutionContext, createParamDecorator } from "@nestjs/common";
import { AuthUser } from "./auth-user";

/**
 * {@code JwtAuthGuard} が詰めた認証済みユーザーをハンドラ引数に注入する。
 *
 * @example
 *   ＠Get("profile")
 *   getMine(＠CurrentUser() user: AuthUser) { ... }
 */
export const CurrentUser = createParamDecorator(
  (_: unknown, ctx: ExecutionContext): AuthUser => {
    const req = ctx.switchToHttp().getRequest<{ user: AuthUser }>();
    return req.user;
  },
);
