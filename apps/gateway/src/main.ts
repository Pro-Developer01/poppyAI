import 'dotenv/config';
import { NestFactory } from '@nestjs/core';
import { AppModule } from './app.module';
import * as fs from 'fs';
import * as path from 'path';

async function bootstrap() {
  // Ensure the upload directory exists
  const uploadDir = process.env.UPLOAD_DIR || '../../data/uploads';
  fs.mkdirSync(path.resolve(uploadDir), { recursive: true });

  const app = await NestFactory.create(AppModule);
  await app.listen(process.env.PORT ?? 3000);
}
bootstrap();
