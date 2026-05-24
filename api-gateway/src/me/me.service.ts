import {
  HttpException,
  Injectable,
  InternalServerErrorException,
  Logger,
} from "@nestjs/common";
import { ConfigService } from "@nestjs/config";

type ProxyBody = Record<string, unknown> | undefined;

/**
 * user-service への薄いプロキシ。JwtAuthGuard で抽出した userId を path に挿入し、
 * 上流のレスポンス JSON とステータスをそのままクライアントに返す。
 *
 * このゲートウェイ層では body 構造を再検証しない（user-service の DTO が唯一の真実）。
 * 上流のエラーレスポンスをそのまま透過させることで、エラーコードの一意性を保つ。
 */
@Injectable()
export class MeService {
  private readonly logger = new Logger(MeService.name);

  constructor(private readonly config: ConfigService) {}

  private baseUrl(): string {
    return this.config.get<string>("USER_SERVICE_URL") ?? "http://localhost:8081";
  }

  async getProfile(userId: string): Promise<unknown> {
    return this.proxy("GET", `/users/${userId}/profile`);
  }

  async putProfile(userId: string, body: ProxyBody): Promise<unknown> {
    return this.proxy("PUT", `/users/${userId}/profile`, body);
  }

  async getPreferences(userId: string): Promise<unknown> {
    return this.proxy("GET", `/users/${userId}/preferences`);
  }

  async putPreferences(userId: string, body: ProxyBody): Promise<unknown> {
    return this.proxy("PUT", `/users/${userId}/preferences`, body);
  }

  private async proxy(
    method: "GET" | "PUT",
    path: string,
    body?: ProxyBody,
  ): Promise<unknown> {
    const url = `${this.baseUrl()}${path}`;
    let res: Response;
    try {
      res = await fetch(url, {
        method,
        headers: body ? { "Content-Type": "application/json" } : undefined,
        body: body ? JSON.stringify(body) : undefined,
      });
    } catch (e) {
      this.logger.error(`user-service unreachable: ${method} ${url}`, e as Error);
      throw new InternalServerErrorException("user-service unreachable");
    }
    const text = await res.text();
    const json: unknown = text ? JSON.parse(text) : undefined;
    if (!res.ok) {
      // 上流のステータスと body をそのまま透過する
      throw new HttpException(json ?? { code: "UPSTREAM_ERROR" }, res.status);
    }
    return json;
  }
}
