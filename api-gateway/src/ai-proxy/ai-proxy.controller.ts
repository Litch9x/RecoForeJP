import { Body, Controller, Post } from "@nestjs/common";

import { AiProxyService } from "./ai-proxy.service";

/**
 * 公開 (認証不要) で ai-service へプロキシするエンドポイント。
 * URL パスは ai-service と同じに保ち、フロントが直接叩いていた頃と
 * 同じ shape のリクエスト・レスポンスにする。
 */
@Controller()
export class AiProxyController {
  constructor(private readonly service: AiProxyService) {}

  @Post("search/items")
  searchItems(@Body() body: Record<string, unknown>): Promise<unknown> {
    return this.service.searchItems(body);
  }

  @Post("recommend/hybrid")
  recommendHybrid(@Body() body: Record<string, unknown>): Promise<unknown> {
    return this.service.recommendHybrid(body);
  }
}
