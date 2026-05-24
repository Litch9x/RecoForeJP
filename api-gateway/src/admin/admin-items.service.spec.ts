import { HttpException, InternalServerErrorException } from "@nestjs/common";
import { ConfigService } from "@nestjs/config";

import { AdminItemsService } from "./admin-items.service";

describe("AdminItemsService", () => {
  let service: AdminItemsService;
  let config: { get: jest.Mock };
  let fetchSpy: jest.SpyInstance;

  beforeEach(() => {
    config = {
      get: jest.fn((key: string) => {
        if (key === "ITEM_SERVICE_URL") return "http://item-service:8082";
        if (key === "AI_SERVICE_URL") return "http://ai-service:8000";
        return undefined;
      }),
    };
    service = new AdminItemsService(config as unknown as ConfigService);
    fetchSpy = jest.spyOn(global, "fetch");
  });

  afterEach(() => {
    fetchSpy.mockRestore();
  });

  function mockFetch(status: number, body?: unknown) {
    fetchSpy.mockResolvedValueOnce({
      ok: status >= 200 && status < 300,
      status,
      text: async () => (body === undefined ? "" : JSON.stringify(body)),
    } as unknown as Response);
  }

  it("list forwards to item-service /items", async () => {
    mockFetch(200, [{ id: "a" }, { id: "b" }]);
    await service.list();
    expect(fetchSpy).toHaveBeenCalledWith(
      "http://item-service:8082/items",
      expect.objectContaining({ method: "GET" }),
    );
  });

  it("create forwards to item-service then calls ai-service embeddings", async () => {
    const created = {
      id: "10000000-0000-0000-0000-000000000099",
      title: "テストアイテム",
      description: "説明文",
      categoryNameJa: "求人",
      tags: ["it", "remote"],
      region: "東京都-港区",
    };
    mockFetch(201, created); // item-service POST /items
    mockFetch(200, { item_id: created.id, dimension: 384 }); // ai-service POST /embeddings/items/{id}

    const result = await service.create({ title: "テストアイテム" });

    expect(result).toEqual(created);
    expect(fetchSpy).toHaveBeenNthCalledWith(
      1,
      "http://item-service:8082/items",
      expect.objectContaining({ method: "POST" }),
    );
    expect(fetchSpy).toHaveBeenNthCalledWith(
      2,
      `http://ai-service:8000/embeddings/items/${created.id}`,
      expect.objectContaining({
        method: "POST",
        body: JSON.stringify({
          text:
            "テストアイテム / 説明文 / カテゴリ: 求人 / タグ: it, remote / 地域: 東京都-港区",
        }),
      }),
    );
  });

  it("update also triggers embedding regeneration", async () => {
    const updated = { id: "u-1", title: "更新済み" };
    mockFetch(200, updated);
    mockFetch(200, { dimension: 384 });

    await service.update("u-1", { title: "更新済み" });

    expect(fetchSpy).toHaveBeenNthCalledWith(
      1,
      "http://item-service:8082/items/u-1",
      expect.objectContaining({ method: "PUT" }),
    );
    expect(fetchSpy).toHaveBeenNthCalledWith(
      2,
      "http://ai-service:8000/embeddings/items/u-1",
      expect.any(Object),
    );
  });

  it("delete forwards to item-service and does NOT call ai-service", async () => {
    mockFetch(204, undefined);

    await service.delete("d-1");

    expect(fetchSpy).toHaveBeenCalledTimes(1);
    expect(fetchSpy).toHaveBeenCalledWith(
      "http://item-service:8082/items/d-1",
      expect.objectContaining({ method: "DELETE" }),
    );
  });

  it("propagates upstream 400 from item-service", async () => {
    mockFetch(400, { code: "VALIDATION_ERROR" });

    await expect(service.create({ title: "" })).rejects.toMatchObject({ status: 400 });
    await expect(service.create({ title: "" })).rejects.toBeInstanceOf(HttpException);
  });

  it("propagates upstream 404 from item-service", async () => {
    mockFetch(404, { code: "ITEM_NOT_FOUND" });
    await expect(service.get("missing")).rejects.toMatchObject({ status: 404 });
  });

  it("returns InternalServerError when item-service unreachable", async () => {
    fetchSpy.mockRejectedValueOnce(new Error("ECONNREFUSED"));

    await expect(service.list()).rejects.toBeInstanceOf(InternalServerErrorException);
  });

  it("swallows embedding failure but still returns item (item save succeeded)", async () => {
    const created = { id: "i-1", title: "t" };
    mockFetch(201, created);
    mockFetch(500, { error: "model load failed" });

    // 例外を投げない（アイテム保存は成功しているので）
    const result = await service.create({ title: "t" });
    expect(result).toEqual(created);
  });
});
