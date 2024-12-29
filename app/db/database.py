from pymongo import MongoClient
import logging
import os
from pymongo.errors import PyMongoError


def start_database():
    """
    Initializes the MongoDB database connection.
    """
    try:
        # Fetch environment variables
        USER = os.getenv("MONGODB_USER")
        PASSWORD = os.getenv("MONGODB_PASSWORD")
        CLUSTER = os.getenv("MONGODB_CLUSTER")
        COLLECTION = os.getenv("MONGODB_COLLECTION")

        # Validate environment variables
        if not all([USER, PASSWORD, CLUSTER, COLLECTION]):
            raise EnvironmentError(
                "One or more MongoDB environment variables are missing."
            )

        # Build the connection URL
        DB_CONNECTION_URL = (
            f"mongodb+srv://{USER}:{PASSWORD}@{CLUSTER}.yy6y8we.mongodb.net/"
            f"{COLLECTION}?retryWrites=true&w=majority&appName=Cluster0"
        )

        # Initialize MongoDB client
        client = MongoClient(DB_CONNECTION_URL)

        # Verify the connection
        client.admin.command("ping")
        logging.info("MongoDB connected successfully!")

        # Return the database instance
        return client["studapp"]

    except PyMongoError as e:
        logging.error(f"MongoDB connection error: {e}")
        raise
    except Exception as e:
        logging.error(f"Unexpected error: {e}")
        raise
