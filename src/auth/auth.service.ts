import {
  BadRequestException,
  Injectable,
  UnauthorizedException,
} from '@nestjs/common';
import { PrismaService } from 'src/prisma.service';
import { JwtService } from '@nestjs/jwt';

import { UserService } from 'src/user/user.service';
import { verify } from 'argon2';
import { Response } from 'express';
import { Role } from '@prisma/client';
import { AuthDto } from './dto/auth.dto';

@Injectable()
export class AuthService {
  EXPIRE_DAY_REFRESH_TOKEN = 1;
  REFRESH_TOKEN_NAME = 'refreshToken';
  constructor(
    private prisma: PrismaService,
    private jwt: JwtService,
    private userService: UserService
  ) {}

  async login(dto: AuthDto) {
    const { password, ...user } = await this.validateUser(dto);
    const tokens = await this.issueTokens(user.id, user.role);

    return {
      user,
      ...tokens,
    };
  }
  async register(dto: AuthDto) {
    const oldUser = await this.userService.findByEmail(dto.email);
    if (oldUser) throw new BadRequestException('User already exists');
    const { password, ...user } = await this.userService.create(dto);

    const tokens = await this.issueTokens(user.id, user.role);

    // await this.emailService.sendWelcome(user.email);

    return {
      user,
      ...tokens,
    };
  }

  async getNewTokens(refreshToken: string) {
    const result = await this.jwt.verifyAsync(refreshToken);
    if (!result) throw new UnauthorizedException('Invalid refresh token');
    const { password, ...user } = await this.userService.findById(result.id);
    const tokens = await this.issueTokens(user.id, user.role);
    return {
      user,
      ...tokens,
    };
  }

  private async issueTokens(userId: number, role?: Role) {
    const data = { id: userId, role };

    const accessToken = this.jwt.sign(data, {
      expiresIn: '1h',
    });

    const refreshToken = this.jwt.sign(data, {
      expiresIn: '7d',
    });

    return { accessToken, refreshToken };
  }

  private async validateUser(dto: AuthDto) {
    const user = await this.userService.findByEmail(dto.email);
    if (!user) {
      throw new UnauthorizedException('Email or password is incorrect');
    }
    const isValid = await verify(user.password, dto.password);
    if (!isValid) {
      throw new UnauthorizedException('Email or password is incorrect');
    }
    return user;
  }
  addRefreshTokenToResponse(res: Response, refreshToken: string) {
    const expire = new Date();
    expire.setDate(expire.getDate() + this.EXPIRE_DAY_REFRESH_TOKEN);
    res.cookie(this.REFRESH_TOKEN_NAME, refreshToken, {
      httpOnly: true,
      expires: expire,
      secure: true,
      //lax or none
      sameSite: 'none',
    });
  }
  removeRefreshTokenFromResponse(res: Response) {
    res.cookie(this.REFRESH_TOKEN_NAME, '', {
      httpOnly: true,
      domain: 'localhost',
      expires: new Date(0),
      //production
      secure: true,
      // lax if production
      sameSite: 'none',
    });
  }
}
