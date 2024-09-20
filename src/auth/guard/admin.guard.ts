import {
  CanActivate,
  ExecutionContext,
  ForbiddenException,
} from '@nestjs/common';
import { Reflector } from '@nestjs/core';
import { User, Role } from '@prisma/client';
import { Request } from 'express';

export class AdminAuthGuard implements CanActivate {
  constructor(private reflector: Reflector) {}
  canActivate(context: ExecutionContext): boolean {
    const request = context.switchToHttp().getRequest<Request>();
    const user = request.user as User;
    if (user.role !== Role.ADMIN) {
      throw new ForbiddenException(
        'You are not authorized to access this resource'
      );
    }
    return true;
  }
}
