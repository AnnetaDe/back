import { Module } from '@nestjs/common';
import { AppController } from './app.controller';
import { AppService } from './app.service';
import { UserModule } from './user/user.module';
import { StatisticsModule } from './statistics/statistics.module';
import { MailModule } from './mail/mail.module';

@Module({
  imports: [UserModule, StatisticsModule, MailModule],
  controllers: [AppController],
  providers: [AppService],
})
export class AppModule {}
