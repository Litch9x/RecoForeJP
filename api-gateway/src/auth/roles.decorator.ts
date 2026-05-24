import { Reflector } from "@nestjs/core";
import { Role } from "./auth-user";

/**
 * ハンドラ / コントローラに必要な権限ロールを宣言する。
 *
 * @example
 *   ＠UseGuards(JwtAuthGuard, RolesGuard)
 *   ＠Roles("ADMIN")
 *   ＠Post()
 *   createItem(...) { ... }
 */
export const Roles = Reflector.createDecorator<Role[]>();
