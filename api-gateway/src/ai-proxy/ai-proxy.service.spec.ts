import { HttpException, InternalServerErrorException } from "@nestjs/common";
import { ConfigService } from "@nestjs/config";

import { AiProxyService } from "./ai-proxy.service";

describe("AiProxyService", () => {
  let service: AiProxyService;
  let config: { get: jest.Mock };
  let fetchSpy: jest.SpyInstance;

  beforeEach(() => {
    config = {
      get: jest.fn((k: string) =>
        k === "AI_SERVICE_URL" ? "http://ai-service:8000" : undefined,
      ),
    };
    service = new AiProxyService(config as unknown as ConfigService);
    fetchSpy = jest.spyOn(global, "fetch");
  });

  afterEach(() => {
    fetchSpy.mockRestore();
  });

  function mockFetch(status: number, body: unknown) {
    fetchSpy.mockResolvedValueOnce({
      ok: status >= 200 && status < 300,
      status,
      text: async () => JSON.stringify(body),
    } as unknown as Response);
  }

  it("searchItems forwards body to ai-service /search/items", async () => {
    mockFetch(200, { query: "x", results: [] });
    await service.searchItems({ query: "x", limit: 5 });
    expect(fetchSpy).toHaveBeenCalledWith(
      "http://ai-service:8000/search/items",
      expect.objectContaining({
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({ query: "x", limit: 5 }),
      }),
    );
  });

  it("recommendHybrid forwards to ai-service /recommend/hybrid", async () => {
    mockFetch(200, { items: [] });
    await service.recommendHybrid({ user: { id: "u1" }, query: "q" });
    expect(fetchSpy).toHaveBeenLastCalledWith(
      "http://ai-service:8000/recommend/hybrid",
      expect.objectContaining({ method: "POST" }),
    );
  });

  it("falls back to default URL when env unset", async () => {
    config.get = jest.fn(() => undefined);
    mockFetch(200, {});
    await service.searchItems({ query: "x" });
    expect(fetchSpy).toHaveBeenCalledWith(
      "http://localhost:8000/search/items",
      expect.any(Object),
    );
  });

  it("propagates upstream 422 (FastAPI validation) as HttpException", async () => {
    mockFetch(422, { detail: [{ msg: "value error" }] });
    await expect(service.searchItems({})).rejects.toMatchObject({ status: 422 });
    await expect(service.searchItems({})).rejects.toBeInstanceOf(HttpException);
  });

  it("propagates upstream 500 as HttpException", async () => {
    mockFetch(500, { error: "model load failed" });
    await expect(service.recommendHybrid({})).rejects.toMatchObject({ status: 500 });
  });

  it("returns 500 InternalServerError when ai-service unreachable", async () => {
    fetchSpy.mockRejectedValueOnce(new Error("ECONNREFUSED"));
    await expect(service.searchItems({})).rejects.toBeInstanceOf(
      InternalServerErrorException,
    );
  });
});
