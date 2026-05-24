import {
  InternalServerErrorException,
  UnauthorizedException,
} from "@nestjs/common";
import { ConfigService } from "@nestjs/config";
import { JwtService } from "@nestjs/jwt";
import { AuthService } from "./auth.service";

describe("AuthService", () => {
  let service: AuthService;
  let jwt: { signAsync: jest.Mock };
  let config: { get: jest.Mock };
  let fetchSpy: jest.SpyInstance;

  beforeEach(() => {
    jwt = { signAsync: jest.fn().mockResolvedValue("signed.jwt.token") };
    config = {
      get: jest.fn((key: string) => {
        if (key === "USER_SERVICE_URL") return "http://user-service:8081";
        if (key === "JWT_EXPIRES_IN_SECONDS") return "3600";
        return undefined;
      }),
    };
    service = new AuthService(
      jwt as unknown as JwtService,
      config as unknown as ConfigService,
    );
    fetchSpy = jest.spyOn(global, "fetch");
  });

  afterEach(() => {
    fetchSpy.mockRestore();
  });

  function mockFetchOk(body: unknown, status = 200) {
    fetchSpy.mockResolvedValue({
      ok: status >= 200 && status < 300,
      status,
      json: async () => body,
    } as unknown as Response);
  }

  it("returns signed JWT on successful verification", async () => {
    mockFetchOk({ userId: "u-123", email: "a@example.com" });

    const res = await service.login("a@example.com", "password123");

    expect(fetchSpy).toHaveBeenCalledWith(
      "http://user-service:8081/internal/auth/verify",
      expect.objectContaining({
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({ email: "a@example.com", password: "password123" }),
      }),
    );
    expect(jwt.signAsync).toHaveBeenCalledWith(
      { email: "a@example.com" },
      { subject: "u-123", expiresIn: 3600 },
    );
    expect(res).toEqual({
      accessToken: "signed.jwt.token",
      tokenType: "Bearer",
      expiresIn: 3600,
      userId: "u-123",
      email: "a@example.com",
    });
  });

  it("maps 401 from user-service to UnauthorizedException", async () => {
    mockFetchOk({ code: "INVALID_CREDENTIALS" }, 401);

    await expect(service.login("a@example.com", "wrong")).rejects.toBeInstanceOf(
      UnauthorizedException,
    );
    expect(jwt.signAsync).not.toHaveBeenCalled();
  });

  it("throws InternalServerErrorException when fetch rejects", async () => {
    fetchSpy.mockRejectedValue(new Error("ECONNREFUSED"));

    await expect(
      service.login("a@example.com", "password123"),
    ).rejects.toBeInstanceOf(InternalServerErrorException);
  });

  it("throws InternalServerErrorException on non-401 non-ok response", async () => {
    mockFetchOk({ error: "boom" }, 500);

    await expect(
      service.login("a@example.com", "password123"),
    ).rejects.toBeInstanceOf(InternalServerErrorException);
  });

  it("falls back to default user-service URL when env unset", async () => {
    config.get = jest.fn(() => undefined);
    mockFetchOk({ userId: "u-1", email: "a@example.com" });

    await service.login("a@example.com", "password123");

    expect(fetchSpy).toHaveBeenCalledWith(
      "http://localhost:8081/internal/auth/verify",
      expect.any(Object),
    );
  });
});
