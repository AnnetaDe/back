import { Module } from '@nestjs/common';
import { AuthController } from './auth.controller';
import { AuthService } from './auth.service';
import { PrismaService } from 'src/prisma.service';
import { UserService } from 'src/user/user.service';

@Module({
  controllers: [AuthController],
  providers: [AuthService, PrismaService, UserService, JwtStrategy],
})
export class AuthModule {}
