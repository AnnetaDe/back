import { applyDecorators, UseGuards } from '@nestjs/common';
import { Role } from '@prisma/client';
import { JwtAuthGuard } from '../guard/jwt.guard';
import { AdminAuthGuard } from '../guard/admin.guard';

export const Auth = (role: Role = Role.USER) => {
  if (role === Role.ADMIN) {
    return applyDecorators(UseGuards(JwtAuthGuard, AdminAuthGuard));
  }
  return applyDecorators(UseGuards(JwtAuthGuard));
};
