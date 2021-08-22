from flask import Flask
import redis as _redis
from pymongo import MongoClient

# Configuration

# MongoDB connection URI.
# From: configReader.py
mongodb_connection_string: str = ""
mongodb_database_name: str = ""
mongodb_user_collection_name: str = ""

mongodb_client: MongoClient = None
mongodb_database = None
mongodb_user_collection = None

# Redis connection host and port
# From: configReader.py
redis_options = {
    "host": "localhost",
    "port": 6347
}

redis: _redis.Redis = None
pubsub: _redis.client.PubSub = None  # noqa

# Cogs to load on startup.
# From: configReader.py
initial_cogs: list[str] = None

# Flask app.
# From: app.py
app: Flask = None

# All loaded cogs, in format {"path": cog}.
# From: app.py
loaded_cogs: dict = None

# Discord config values
# From configReader.py
discord_oauth: dict = None
discord_guild_id: int = None
webhooks: dict = None

# Allowed domains for cors-protected endpoints
# From configReader.py
cors_host: str = "*"
