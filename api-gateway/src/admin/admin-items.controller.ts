import {
  Body,
  Controller,
  Delete,
  Get,
  HttpCode,
  HttpStatus,
  Param,
  Post,
  Put,
  UseGuards,
} from "@nestjs/common";

import { JwtAuthGuard } from "../auth/jwt-auth.guard";
import { Roles } from "../auth/roles.decorator";
import { RolesGuard } from "../auth/roles.guard";
import { AdminItemsService } from "./admin-items.service";

/**
 * Admin 用アイテム CRUD。全エンドポイントが ADMIN ロールを要求。
 * 上流の item-service にプロキシし、作成/更新後に ai-service で埋め込みを再生成する。
 */
@Controller("admin/items")
@UseGuards(JwtAuthGuard, RolesGuard)
@Roles(["ADMIN"])
export class AdminItemsController {
  constructor(private readonly service: AdminItemsService) {}

  @Get()
  list(): Promise<unknown> {
    return this.service.list();
  }

  @Get(":id")
  get(@Param("id") id: string): Promise<unknown> {
    return this.service.get(id);
  }

  @Post()
  @HttpCode(HttpStatus.CREATED)
  create(@Body() body: Record<string, unknown>): Promise<unknown> {
    return this.service.create(body);
  }

  @Put(":id")
  update(
    @Param("id") id: string,
    @Body() body: Record<string, unknown>,
  ): Promise<unknown> {
    return this.service.update(id, body);
  }

  @Delete(":id")
  @HttpCode(HttpStatus.NO_CONTENT)
  delete(@Param("id") id: string): Promise<void> {
    return this.service.delete(id);
  }
}
