import { hash } from 'argon2';
import { PrismaClient } from '@prisma/client';
import { faker } from '@faker-js/faker';
import 'dotenv/config';

const prisma = new PrismaClient();
const countries = [
  'Afghanistan',
  'Albania',
  'Algeria',
  'Andorra',
  'Angola',
  'Antigua and Barbuda',
  'Argentina',
  'Armenia',
  'Australia',
  'Austria',
  'Azerbaijan',
  'Bahamas',
  'Bahrain',
  'Bangladesh',
  'Barbados',
];

async function main() {
  const NUM_USERS = 131;

  for (let i = 0; i < NUM_USERS; i++) {
    const email = faker.internet.email();
    const name = faker.person.firstName();
    const avatarUrl = faker.image.avatar();
    // const password = await hash('123456');
    const country = faker.helpers.arrayElement(countries);
    const createdAt = faker.date.past({ years: 1 });
    const updatedAt = new Date(
      createdAt.getTime() +
        Math.random() * (new Date().getTime() - createdAt.getTime())
    );

    await prisma.user.create({
      data: {
        email,
        name,
        avatarUrl,

        country,
        createdAt,
        updatedAt,
      },
    });
  }
}

main()
  .catch(e => {
    throw e;
  })
  .finally(async () => {
    await prisma.$disconnect();
  });
