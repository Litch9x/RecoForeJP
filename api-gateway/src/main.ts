import { NestFactory } from "@nestjs/core";
import { Logger, ValidationPipe } from "@nestjs/common";
import { AppModule } from "./app.module";

async function bootstrap() {
  const app = await NestFactory.create(AppModule);
  // 全リクエストで DTO の class-validator を実行。未知フィールドは弾く。
  app.useGlobalPipes(
    new ValidationPipe({
      whitelist: true,
      forbidNonWhitelisted: true,
      transform: true,
    }),
  );
  const port = Number(process.env.PORT) || 3000;
  // 0.0.0.0 にバインドして Docker からも到達可能にする
  await app.listen(port, "0.0.0.0");
  Logger.log(`api-gateway listening on http://0.0.0.0:${port}`, "Bootstrap");
}
bootstrap();
