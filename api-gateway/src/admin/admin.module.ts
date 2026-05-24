import { Module } from "@nestjs/common";

import { AuthModule } from "../auth/auth.module";
import { JwtAuthGuard } from "../auth/jwt-auth.guard";
import { RolesGuard } from "../auth/roles.guard";
import { AdminItemsController } from "./admin-items.controller";
import { AdminItemsService } from "./admin-items.service";
import { AdminController } from "./admin.controller";

@Module({
  imports: [AuthModule],
  controllers: [AdminController, AdminItemsController],
  providers: [AdminItemsService, JwtAuthGuard, RolesGuard],
})
export class AdminModule {}
