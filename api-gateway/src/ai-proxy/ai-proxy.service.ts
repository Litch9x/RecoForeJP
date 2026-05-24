import {
  HttpException,
  Injectable,
  InternalServerErrorException,
  Logger,
} from "@nestjs/common";
import { ConfigService } from "@nestjs/config";

/**
 * ai-service への薄いプロキシ（認証不要・公開エンドポイント）。
 *
 * 設計意図:
 *  - フロントは ai-service の URL を一切知らなくてよい（gateway URL だけ知っていればよい）
 *  - 全トラフィックが gateway を通ることで、将来 rate-limit / ログ / メトリクスの
 *    挿入箇所が一箇所に集まる
 *  - 上流の status と body をそのまま透過させ、エラー解釈は ai-service の真実を尊重
 */
@Injectable()
export class AiProxyService {
  private readonly logger = new Logger(AiProxyService.name);

  constructor(private readonly config: ConfigService) {}

  private aiSvcUrl(): string {
    return this.config.get<string>("AI_SERVICE_URL") ?? "http://localhost:8000";
  }

  searchItems(body: unknown): Promise<unknown> {
    return this.proxy("POST", "/search/items", body);
  }

  recommendHybrid(body: unknown): Promise<unknown> {
    return this.proxy("POST", "/recommend/hybrid", body);
  }

  private async proxy(
    method: "POST",
    path: string,
    body: unknown,
  ): Promise<unknown> {
    const url = `${this.aiSvcUrl()}${path}`;
    let res: Response;
    try {
      res = await fetch(url, {
        method,
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify(body),
      });
    } catch (e) {
      this.logger.error(`ai-service unreachable: ${method} ${url}`, e as Error);
      throw new InternalServerErrorException("ai-service unreachable");
    }
    const text = await res.text();
    const json: unknown = text ? JSON.parse(text) : undefined;
    if (!res.ok) {
      throw new HttpException(json ?? { code: "UPSTREAM_ERROR" }, res.status);
    }
    return json;
  }
}
