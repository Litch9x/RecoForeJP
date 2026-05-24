import { ExecutionContext, ForbiddenException } from "@nestjs/common";
import { Reflector } from "@nestjs/core";

import type { AuthUser, Role } from "./auth-user";
import { Roles } from "./roles.decorator";
import { RolesGuard } from "./roles.guard";

describe("RolesGuard", () => {
  let reflector: Reflector;
  let guard: RolesGuard;

  beforeEach(() => {
    reflector = new Reflector();
    guard = new RolesGuard(reflector);
  });

  function makeCtx(user: AuthUser | undefined, required?: Role[]): ExecutionContext {
    const ctx = {
      switchToHttp: () => ({ getRequest: () => ({ user }) }),
      getHandler: () => () => {},
      getClass: () => class {},
    } as unknown as ExecutionContext;
    jest
      .spyOn(reflector, "getAllAndOverride")
      .mockImplementation((decorator) => (decorator === Roles ? required : undefined));
    return ctx;
  }

  it("passes when no @Roles is declared", () => {
    const ctx = makeCtx({ userId: "u", email: "a@b.com", role: "USER" });
    expect(guard.canActivate(ctx)).toBe(true);
  });

  it("passes when user has the required role", () => {
    const ctx = makeCtx({ userId: "u", email: "a@b.com", role: "ADMIN" }, ["ADMIN"]);
    expect(guard.canActivate(ctx)).toBe(true);
  });

  it("rejects with 403 when user role mismatches", () => {
    const ctx = makeCtx({ userId: "u", email: "a@b.com", role: "USER" }, ["ADMIN"]);
    expect(() => guard.canActivate(ctx)).toThrow(ForbiddenException);
  });

  it("rejects with 403 when there is no authenticated user", () => {
    const ctx = makeCtx(undefined, ["ADMIN"]);
    expect(() => guard.canActivate(ctx)).toThrow(ForbiddenException);
  });

  it("passes when user has any of multiple required roles", () => {
    const ctx = makeCtx({ userId: "u", email: "a@b.com", role: "USER" }, [
      "USER",
      "ADMIN",
    ]);
    expect(guard.canActivate(ctx)).toBe(true);
  });
});
