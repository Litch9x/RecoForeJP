import {
  Injectable,
  InternalServerErrorException,
  Logger,
  UnauthorizedException,
} from "@nestjs/common";
import { ConfigService } from "@nestjs/config";
import { JwtService } from "@nestjs/jwt";
import { LoginResponse } from "./dto/login-response.dto";

interface VerifyCredentialsResponse {
  userId: string;
  email: string;
}

/**
 * ログイン処理。user-service の内部認証エンドポイントへ問い合わせ、
 * 検証成功時に JWT を発行する。
 *
 * JWT 仕様:
 *   - subject (sub) = userId
 *   - email クレーム
 *   - 署名アルゴリズム HS256（共有 secret）
 */
@Injectable()
export class AuthService {
  private readonly logger = new Logger(AuthService.name);

  constructor(
    private readonly jwt: JwtService,
    private readonly config: ConfigService,
  ) {}

  async login(email: string, password: string): Promise<LoginResponse> {
    const userServiceUrl =
      this.config.get<string>("USER_SERVICE_URL") ?? "http://localhost:8081";
    const expiresInSec = Number(
      this.config.get<string>("JWT_EXPIRES_IN_SECONDS") ?? "3600",
    );

    const verifyUrl = `${userServiceUrl}/internal/auth/verify`;
    let res: Response;
    try {
      res = await fetch(verifyUrl, {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({ email, password }),
      });
    } catch (e) {
      this.logger.error(`user-service へ到達できません: ${verifyUrl}`, e as Error);
      throw new InternalServerErrorException("user-service unreachable");
    }

    if (res.status === 401) {
      // 同じメッセージで email 未存在 / password 不一致を区別しない
      throw new UnauthorizedException("Invalid email or password");
    }
    if (!res.ok) {
      this.logger.error(`user-service 異常応答 status=${res.status}`);
      throw new InternalServerErrorException("user-service error");
    }

    const verified = (await res.json()) as VerifyCredentialsResponse;
    const accessToken = await this.jwt.signAsync(
      { email: verified.email },
      { subject: verified.userId, expiresIn: expiresInSec },
    );
    return {
      accessToken,
      tokenType: "Bearer",
      expiresIn: expiresInSec,
      userId: verified.userId,
      email: verified.email,
    };
  }
}
