import { Injectable } from '@nestjs/common';
import { PrismaService } from 'src/prisma.service';
import { UpdateUserDto, CreateUserDto } from './dto/create-user.dto';
import { hash } from 'argon2';
import { PaginationArgsWithSearchTerm } from 'src/base/pagination.args';
import { UserResponse } from './user.response';
import { Prisma } from '@prisma/client';
import { morePages } from 'src/base/more-pages';

@Injectable()
export class UserService {
  constructor(private prisma: PrismaService) {}

  async findById(id: number) {
    const user = await this.prisma.user.findUnique({
      where: { id },
    });
    if (!user) {
      throw new Error('User not found');
    }
    return user;
  }

  async findByEmail(email: string) {
    const user = await this.prisma.user.findUnique({
      where: { email },
    });
    if (!user) {
      throw new Error('User not found by email');
    }
    return user;
  }

  async create({ password, ...dto }: CreateUserDto) {
    const user = {
      ...dto,
      password: await hash(password),
    };
    return this.prisma.user.create({
      data: user,
    });
  }
  async update(id: number, { password, ...data }: UpdateUserDto) {
    await this.findById(id);

    const hashedPassword = password
      ? {
          password: await hash(password),
        }
      : {};

    return this.prisma.user.update({
      where: {
        id,
      },
      data: {
        ...data,
        ...hashedPassword,
      },
    });
  }

  async delete(id: string) {
    await this.findById(+id);

    return this.prisma.user.delete({
      where: {
        id: +id,
      },
    });
  }

  async findAll(args?: PaginationArgsWithSearchTerm): Promise<UserResponse> {
    const searchTermQuery = args?.searchTerm
      ? this.getSearchTermFilter(args?.searchTerm)
      : {};

    const users = await this.prisma.user.findMany({
      skip: +args?.skip,
      take: +args?.take,
      where: searchTermQuery,
    });

    const totalCount = await this.prisma.user.count({
      where: searchTermQuery,
    });

    const isHasMore = morePages(totalCount, +args?.skip, +args.take);

    return { items: users, isHasMore };
  }

  private getSearchTermFilter(searchTerm: string): Prisma.UserWhereInput {
    return {
      OR: [
        {
          email: {
            contains: searchTerm,
            mode: 'insensitive',
          },
        },
        {
          name: {
            contains: searchTerm,
            mode: 'insensitive',
          },
        },
        {
          country: {
            contains: searchTerm,
            mode: 'insensitive',
          },
        },
      ],
    };
  }
}
