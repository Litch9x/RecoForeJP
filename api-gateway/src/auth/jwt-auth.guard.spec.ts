import { ExecutionContext, UnauthorizedException } from "@nestjs/common";
import { JwtService } from "@nestjs/jwt";
import { AuthUser } from "./auth-user";
import { JwtAuthGuard } from "./jwt-auth.guard";

describe("JwtAuthGuard", () => {
  let jwt: { verifyAsync: jest.Mock };
  let guard: JwtAuthGuard;

  beforeEach(() => {
    jwt = { verifyAsync: jest.fn() };
    guard = new JwtAuthGuard(jwt as unknown as JwtService);
  });

  function ctxWithHeader(authorization?: string): {
    ctx: ExecutionContext;
    req: { headers: Record<string, string | undefined>; user?: AuthUser };
  } {
    const req = { headers: { authorization } as Record<string, string | undefined> };
    const ctx = {
      switchToHttp: () => ({ getRequest: () => req }),
    } as unknown as ExecutionContext;
    return { ctx, req };
  }

  it("attaches user when token is valid", async () => {
    jwt.verifyAsync.mockResolvedValue({ sub: "u-1", email: "a@example.com" });
    const { ctx, req } = ctxWithHeader("Bearer good.token");

    await expect(guard.canActivate(ctx)).resolves.toBe(true);
    expect(req.user).toEqual({ userId: "u-1", email: "a@example.com" });
  });

  it("rejects when Authorization header missing", async () => {
    const { ctx } = ctxWithHeader(undefined);
    await expect(guard.canActivate(ctx)).rejects.toBeInstanceOf(UnauthorizedException);
  });

  it("rejects when scheme is not Bearer", async () => {
    const { ctx } = ctxWithHeader("Basic abc");
    await expect(guard.canActivate(ctx)).rejects.toBeInstanceOf(UnauthorizedException);
  });

  it("rejects when token is empty", async () => {
    const { ctx } = ctxWithHeader("Bearer ");
    await expect(guard.canActivate(ctx)).rejects.toBeInstanceOf(UnauthorizedException);
  });

  it("rejects when signature verification throws", async () => {
    jwt.verifyAsync.mockRejectedValue(new Error("invalid signature"));
    const { ctx } = ctxWithHeader("Bearer bad.token");
    await expect(guard.canActivate(ctx)).rejects.toBeInstanceOf(UnauthorizedException);
  });

  it("rejects when payload missing sub", async () => {
    jwt.verifyAsync.mockResolvedValue({ email: "a@example.com" });
    const { ctx } = ctxWithHeader("Bearer ok.token");
    await expect(guard.canActivate(ctx)).rejects.toBeInstanceOf(UnauthorizedException);
  });
});
