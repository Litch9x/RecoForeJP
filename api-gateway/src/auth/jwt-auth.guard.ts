import {
  CanActivate,
  ExecutionContext,
  Injectable,
  UnauthorizedException,
} from "@nestjs/common";
import { JwtService } from "@nestjs/jwt";
import { Request } from "express";
import { AuthUser, Role } from "./auth-user";

interface JwtPayload {
  sub: string;
  email: string;
  role?: Role;
  iat?: number;
  exp?: number;
}

/**
 * Authorization: Bearer &lt;jwt&gt; を検証し、{@code req.user} に {@link AuthUser} を詰める。
 * 検証失敗（ヘッダ欠落 / 形式違反 / 署名不一致 / 期限切れ）はすべて 401。
 *
 * 旧 JWT（role クレームを持たない）は USER として扱う（後方互換）。
 */
@Injectable()
export class JwtAuthGuard implements CanActivate {
  constructor(private readonly jwt: JwtService) {}

  async canActivate(context: ExecutionContext): Promise<boolean> {
    const req = context.switchToHttp().getRequest<Request & { user?: AuthUser }>();
    const header = req.headers.authorization;
    if (!header || !header.startsWith("Bearer ")) {
      throw new UnauthorizedException("Missing Bearer token");
    }
    const token = header.slice("Bearer ".length).trim();
    if (!token) {
      throw new UnauthorizedException("Empty Bearer token");
    }
    let payload: JwtPayload;
    try {
      payload = await this.jwt.verifyAsync<JwtPayload>(token);
    } catch {
      throw new UnauthorizedException("Invalid or expired token");
    }
    if (!payload.sub || !payload.email) {
      throw new UnauthorizedException("Malformed token payload");
    }
    req.user = {
      userId: payload.sub,
      email: payload.email,
      role: payload.role ?? "USER",
    };
    return true;
  }
}
