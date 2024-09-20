import {
  Body,
  Controller,
  Delete,
  Get,
  Param,
  Post,
  Put,
  Query,
} from '@nestjs/common';
import { UserService } from './user.service';
import { Auth } from 'src/auth/decorators/auth.decorator';
import { PaginationArgsWithSearchTerm } from 'src/base/pagination.args';
import { CreateUserDto, UpdateUserDto } from './dto/create-user.dto';

@Controller('users')
export class UserController {
  constructor(private readonly userService: UserService) {}

  @Auth('ADMIN')
  @Get()
  async getList(@Query() params: PaginationArgsWithSearchTerm) {
    return this.userService.findAll(params);
  }
  @Auth('ADMIN')
  @Get(':id')
  async getById(@Param('id') id: string) {
    return await this.userService.findById(+id);
  }

  @Auth('ADMIN')
  @Post()
  async createUser(@Body() createUserDto: CreateUserDto) {
    return await this.userService.create(createUserDto);
  }

  @Auth('ADMIN')
  @Put(':id')
  async updateUser(
    @Param('id') id: string,
    @Body() updateUserDto: UpdateUserDto
  ) {
    return await this.userService.update(+id, updateUserDto);
  }

  @Auth('ADMIN')
  @Delete(':id')
  async deleteUser(@Param('id') id: string) {
    return await this.userService.delete(id);
  }
}
