from faker import Faker

# from app.db.database import init_database

from app.db.database import start_database
from app.helpers.hashed import hash_password


def generate_users(num_entries=10):
    fake = Faker()
    fake_users = []
    for _ in range(num_entries):
        fake_users.append(
            {
                "_id": str(fake.uuid4()),
                "role": fake.random_element(elements=("student", "teacher")),
                "name": fake.name(),
                "email": fake.email(),
                "password": hash_password(fake.password()),
                "verified": fake.boolean(),
            }
        )
    return fake_users


def seed_users(num_users=10):
    base = start_database()
    users_collection = base["users"]
    fake_users = generate_users(num_users)
    result = users_collection.insert_many(fake_users)
    print(f"Inserted {len(result.inserted_ids)} users into the database.")


# seed_users(10)
