import {
  BadRequestException,
  Injectable,
  UnauthorizedException,
} from '@nestjs/common';
import { PrismaService } from 'src/prisma.service';
import { JwtService } from '@nestjs/jwt';
import { AuthDto } from './dto/auth.dto';
import { UserService } from 'src/user/user.service';
import { verify } from 'argon2';
import { Response } from 'express';
import { Role } from '@prisma/client';

@Injectable()
export class AuthService {
  EXPIRE_DAY_REFRESH_TOKEN = 13;
  REFRESH_TOKEN_NAME = 'refreshToken';
  constructor(
    private prisma: PrismaService,
    private jwt: JwtService,
    private userService: UserService
  ) {}

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

  async getNewTokens(refreshToken: string) {
    const result = await this.jwt.verifyAsync(refreshToken);
    if (!result) throw new UnauthorizedException('Invalid refresh token');
    const { password, ...user } = await this.userService.findById(result.id);
    const tokens = await this.generateToken(user.id, user.role);
    return {
      user,
      ...tokens,
    };
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

  private async generateToken(userId: number, role?: Role) {
    const payload = { sub: userId, role };

    const accessToken = this.jwt.sign(payload, { expiresIn: '1d' });
    const refreshToken = this.jwt.sign(payload, {
      expiresIn: `${this.EXPIRE_DAY_REFRESH_TOKEN}d`,
    });
    return { accessToken, refreshToken };
  }
  async login(dto: AuthDto) {
    const { password, ...user } = await this.validateUser(dto);
    const tokens = await this.generateToken(user.id, user.role);

    return {
      user,
      ...tokens,
    };
  }

  async register(dto: AuthDto) {
    const oldUser = await this.userService.findByEmail(dto.email);
    if (oldUser) throw new BadRequestException('User already exists');
    const { password, ...user } = await this.userService.create(dto);

    const tokens = await this.generateToken(user.id, user.role);

    // await this.emailService.sendWelcome(user.email);

    return {
      user,
      ...tokens,
    };
  }
}
