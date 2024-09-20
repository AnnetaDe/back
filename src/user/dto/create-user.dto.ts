import { Role } from '@prisma/client';
import {
  IsEmail,
  MinLength,
  isEnum,
  IsOptional,
  IsString,
} from 'class-validator';

export class CreateUserDto {
  @IsEmail()
  email: string;

  @IsString()
  @IsOptional()
  name?: string;

  @IsString()
  @IsOptional()
  avatarUrl?: string;

  @IsString()
  @IsOptional()
  country?: string;

  @IsString()
  @MinLength(6)
  password: string;

  @IsOptional()
  role: Role;
}

export type UpdateUserDto = Partial<CreateUserDto>;
