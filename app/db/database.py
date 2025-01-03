from motor.motor_asyncio import AsyncIOMotorClient
from pymongo.errors import ConnectionFailure

import os
from pymongo.errors import PyMongoError


async def start_database():
    """
    Initializes the MongoDB database connection.
    """
    try:
        USER = os.getenv("MONGODB_USER")
        PASSWORD = os.getenv("MONGODB_PASSWORD")
        CLUSTER = os.getenv("MONGODB_CLUSTER")
        COLLECTION = os.getenv("MONGODB_COLLECTION")

        if not all([USER, PASSWORD, CLUSTER, COLLECTION]):
            raise EnvironmentError(
                "One or more MongoDB environment variables are missing."
            )

        DB_CONNECTION_URL = (
            f"mongodb+srv://{USER}:{PASSWORD}@{CLUSTER}.yy6y8we.mongodb.net/"
            f"{COLLECTION}?retryWrites=true&w=majority&appName=Cluster0"
        )

        client = AsyncIOMotorClient(DB_CONNECTION_URL)

        return client
    except ConnectionFailure as e:
        print(f"Failed to connect to MongoDB: {e}")
        raise
    except Exception as e:
        print(f"An error occurred while connecting to MongoDB: {e}")
        raise e


async def close_database(client: AsyncIOMotorClient):
    """
    Closes the MongoDB database connection.
    """
    try:
        client.close()
        print("Closed MongoDB connection")
    except PyMongoError as e:
        print(f"An error occurred while closing the MongoDB connection: {e}")
        raise
    except Exception as e:
        print(f"An error occurred while closing the MongoDB connection: {e}")
        raise e


async def initialize_indexes(db, collection, index):
    """
    Initialize required indexes for MongoDB collections.
    """
    collection_to_index = db[collection]
    await collection_to_index.create_index(index, unique=True, background=True)
    print("Indexes created")
