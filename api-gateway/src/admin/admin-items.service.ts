import {
  HttpException,
  Injectable,
  InternalServerErrorException,
  Logger,
} from "@nestjs/common";
import { ConfigService } from "@nestjs/config";

type Body = Record<string, unknown>;

interface ItemSummary {
  id: string;
  title?: string;
  description?: string;
  categoryNameJa?: string;
  categorySlug?: string;
  region?: string;
  tags?: string[];
}

/**
 * Admin がアイテムを CRUD するための薄いプロキシ。
 *
 * 設計:
 *  - 上流（item-service）の status と body をそのまま透過
 *  - 作成 / 更新成功時、ai-service の埋め込みを **同期的に**再生成（失敗してもアイテムは保存済みなので
 *    warn ログを出して 200 を返す。Admin は seed_embeddings.py で再実行可能）
 *  - 削除時は ai.item_embeddings の掃除はしない（孤立 embedding は検索結果に出ないので無害。
 *    ai-service の DELETE /embeddings/items/{id} 追加は follow-up）
 */
@Injectable()
export class AdminItemsService {
  private readonly logger = new Logger(AdminItemsService.name);

  constructor(private readonly config: ConfigService) {}

  private itemSvcUrl(): string {
    return this.config.get<string>("ITEM_SERVICE_URL") ?? "http://localhost:8082";
  }

  private aiSvcUrl(): string {
    return this.config.get<string>("AI_SERVICE_URL") ?? "http://localhost:8000";
  }

  async list(): Promise<unknown> {
    return this.proxyItem("GET", "/items");
  }

  async get(id: string): Promise<unknown> {
    return this.proxyItem("GET", `/items/${id}`);
  }

  async create(body: Body): Promise<unknown> {
    const item = (await this.proxyItem("POST", "/items", body)) as ItemSummary;
    await this.regenerateEmbedding(item);
    return item;
  }

  async update(id: string, body: Body): Promise<unknown> {
    const item = (await this.proxyItem("PUT", `/items/${id}`, body)) as ItemSummary;
    await this.regenerateEmbedding(item);
    return item;
  }

  async delete(id: string): Promise<void> {
    await this.proxyItem("DELETE", `/items/${id}`);
  }

  // ---------------------------------------------------------------------

  private async proxyItem(
    method: "GET" | "POST" | "PUT" | "DELETE",
    path: string,
    body?: Body,
  ): Promise<unknown> {
    const url = `${this.itemSvcUrl()}${path}`;
    let res: Response;
    try {
      res = await fetch(url, {
        method,
        headers: body ? { "Content-Type": "application/json" } : undefined,
        body: body ? JSON.stringify(body) : undefined,
      });
    } catch (e) {
      this.logger.error(`item-service unreachable: ${method} ${url}`, e as Error);
      throw new InternalServerErrorException("item-service unreachable");
    }
    const text = await res.text();
    const json: unknown = text ? JSON.parse(text) : undefined;
    if (!res.ok) {
      // 上流のステータスと body をそのまま透過
      throw new HttpException(json ?? { code: "UPSTREAM_ERROR" }, res.status);
    }
    return json;
  }

  /**
   * scripts/seed_embeddings.py と同じテキスト構築ロジックを TS で再実装。
   * 検索性能を seed と一致させるため、変更時は両方を合わせる。
   */
  private buildEmbeddingText(item: ItemSummary): string {
    const parts: string[] = [];
    if (item.title) parts.push(item.title);
    if (item.description) parts.push(item.description);
    const cat = item.categoryNameJa ?? item.categorySlug;
    if (cat) parts.push(`カテゴリ: ${cat}`);
    if (item.tags && item.tags.length > 0) {
      parts.push(`タグ: ${item.tags.join(", ")}`);
    }
    if (item.region) parts.push(`地域: ${item.region}`);
    return parts.join(" / ");
  }

  private async regenerateEmbedding(item: ItemSummary): Promise<void> {
    if (!item?.id) {
      this.logger.warn("regenerateEmbedding: item.id 欠落、スキップ");
      return;
    }
    const text = this.buildEmbeddingText(item);
    const url = `${this.aiSvcUrl()}/embeddings/items/${item.id}`;
    try {
      const res = await fetch(url, {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({ text }),
      });
      if (!res.ok) {
        // アイテム保存自体は成功しているので、failure を吸って warn だけ残す。
        // Admin は seed_embeddings.py を再実行すれば追いつける。
        this.logger.warn(
          `Embedding regenerate failed (item=${item.id}, status=${res.status}). アイテムは保存済み。`,
        );
      }
    } catch (e) {
      this.logger.warn(
        `Embedding regenerate threw (item=${item.id}): ${(e as Error).message}. アイテムは保存済み。`,
      );
    }
  }
}
