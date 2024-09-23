import { Module } from '@nestjs/common';
import { UserModule } from './user/user.module';
import { StatisticsModule } from './statistics/statistics.module';
import { MailModule } from './mail/mail.module';
import { ConfigModule } from '@nestjs/config';
import { AuthModule } from './auth/auth.module';
import { SettingsModule } from './settings/settings.module';
import { MediaModule } from './media/media.module';

@Module({
  imports: [
    ConfigModule.forRoot(),
    AuthModule,
    UserModule,
    MediaModule,
    MailModule,
    SettingsModule,
    StatisticsModule,
  ],
})
export class AppModule {}
