import {
  CanActivate,
  ExecutionContext,
  ForbiddenException,
  Injectable,
} from "@nestjs/common";
import { Reflector } from "@nestjs/core";
import type { AuthUser } from "./auth-user";
import { Roles } from "./roles.decorator";

/**
 * {@link Roles} デコレータで宣言された権限のいずれかを {@code req.user.role} が
 * 持つことを要求する。デコレータが無いハンドラは素通り（JwtAuthGuard だけで判定）。
 *
 * 必ず JwtAuthGuard と組み合わせて使う:
 *   {@code ＠UseGuards(JwtAuthGuard, RolesGuard)} の順序が必要。
 */
@Injectable()
export class RolesGuard implements CanActivate {
  constructor(private readonly reflector: Reflector) {}

  canActivate(context: ExecutionContext): boolean {
    const required = this.reflector.getAllAndOverride(Roles, [
      context.getHandler(),
      context.getClass(),
    ]);
    if (!required || required.length === 0) return true;

    const req = context.switchToHttp().getRequest<{ user?: AuthUser }>();
    const user = req.user;
    if (!user) {
      // JwtAuthGuard が先に走っていればここには来ないが、防御的に
      throw new ForbiddenException("No authenticated user");
    }
    if (!required.includes(user.role)) {
      throw new ForbiddenException(
        `Required role: ${required.join(",")}; user has: ${user.role}`,
      );
    }
    return true;
  }
}
