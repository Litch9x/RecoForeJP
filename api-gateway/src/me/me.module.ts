import { Module } from "@nestjs/common";
import { AuthModule } from "../auth/auth.module";
import { JwtAuthGuard } from "../auth/jwt-auth.guard";
import { MeController } from "./me.controller";
import { MeService } from "./me.service";

/**
 * AuthModule から JwtModule を再エクスポートしているので、{@link JwtAuthGuard} が
 * JwtService を解決できる。
 */
@Module({
  imports: [AuthModule],
  controllers: [MeController],
  providers: [MeService, JwtAuthGuard],
})
export class MeModule {}
