import { NestFactory } from '@nestjs/core';
import { AppModule } from './app.module';
import * as cookieParser from 'cookie-parser';

async function bootstrap() {
  const app = await NestFactory.create(AppModule);

  const server = app.getHttpServer();
  const router = server._events.request;

  app.setGlobalPrefix('api');
  app.use(cookieParser());
  app.enableCors({
    origin: 'http://localhost:3000',
    credentials: true,
    exposedHeaders: 'set-cookie',
  });
  await app.listen(4200, () => console.log(`Server is running`));
}
bootstrap();
