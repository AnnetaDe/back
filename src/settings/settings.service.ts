import { Injectable } from '@nestjs/common';
import { Settings } from '@prisma/client';

import { PrismaService } from 'src/prisma.service';

@Injectable()
export class SettingsService {
  constructor(private prisma: PrismaService) {}

  async getSettingByKey(key: string): Promise<Settings | null> {
    return this.prisma.settings.findUnique({
      where: { key },
    });
  }

  async setSetting(key: string, value: string): Promise<Settings> {
    return this.prisma.settings.upsert({
      where: { key },
      update: { value },
      create: { key, value },
    });
  }
}
