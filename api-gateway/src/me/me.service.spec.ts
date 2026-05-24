import { HttpException, InternalServerErrorException } from "@nestjs/common";
import { ConfigService } from "@nestjs/config";
import { MeService } from "./me.service";

describe("MeService", () => {
  let service: MeService;
  let config: { get: jest.Mock };
  let fetchSpy: jest.SpyInstance;

  beforeEach(() => {
    config = {
      get: jest.fn((key: string) =>
        key === "USER_SERVICE_URL" ? "http://user-service:8081" : undefined,
      ),
    };
    service = new MeService(config as unknown as ConfigService);
    fetchSpy = jest.spyOn(global, "fetch");
  });

  afterEach(() => {
    fetchSpy.mockRestore();
  });

  function mockFetch(status: number, body: unknown) {
    fetchSpy.mockResolvedValue({
      ok: status >= 200 && status < 300,
      status,
      text: async () => (body === undefined ? "" : JSON.stringify(body)),
    } as unknown as Response);
  }

  it("getProfile forwards to user-service and returns body", async () => {
    mockFetch(200, { jlpt: "N3", region: "Tokyo" });

    const res = await service.getProfile("u-1");

    expect(fetchSpy).toHaveBeenCalledWith(
      "http://user-service:8081/users/u-1/profile",
      expect.objectContaining({ method: "GET" }),
    );
    expect(res).toEqual({ jlpt: "N3", region: "Tokyo" });
  });

  it("putProfile sends JSON body with Content-Type", async () => {
    mockFetch(200, { jlpt: "N2" });

    await service.putProfile("u-1", { jlpt: "N2" });

    expect(fetchSpy).toHaveBeenCalledWith(
      "http://user-service:8081/users/u-1/profile",
      expect.objectContaining({
        method: "PUT",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({ jlpt: "N2" }),
      }),
    );
  });

  it("propagates upstream 404 as HttpException", async () => {
    mockFetch(404, { code: "USER_NOT_FOUND", message: "no user" });

    await expect(service.getProfile("missing")).rejects.toMatchObject({
      status: 404,
    });
    await expect(service.getProfile("missing")).rejects.toBeInstanceOf(HttpException);
  });

  it("propagates upstream 400 validation body", async () => {
    mockFetch(400, { code: "VALIDATION_ERROR", details: ["jlpt: must be N1..N5"] });

    await expect(service.putProfile("u-1", { jlpt: "ZZ" })).rejects.toMatchObject({
      status: 400,
    });
  });

  it("maps fetch reject to 500", async () => {
    fetchSpy.mockRejectedValue(new Error("ECONNREFUSED"));

    await expect(service.getProfile("u-1")).rejects.toBeInstanceOf(
      InternalServerErrorException,
    );
  });

  it("preferences endpoints hit /users/{id}/preferences", async () => {
    mockFetch(200, { preferredLanguage: "ja" });

    await service.getPreferences("u-1");
    expect(fetchSpy).toHaveBeenLastCalledWith(
      "http://user-service:8081/users/u-1/preferences",
      expect.objectContaining({ method: "GET" }),
    );

    await service.putPreferences("u-1", { preferredLanguage: "en" });
    expect(fetchSpy).toHaveBeenLastCalledWith(
      "http://user-service:8081/users/u-1/preferences",
      expect.objectContaining({ method: "PUT" }),
    );
  });
});
