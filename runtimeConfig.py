from flask import Flask
import redis as _redis

# Configuration

# MongoDB connection URI.
# From: configReader.py
mongodb_connection_string: str = None

# Redis connection host and port
# From: configReader.py
redis_options = {
    "host": "localhost",
    "port": 6347
}

redis:  _redis.Redis = None
pubsub: _redis.client.PubSub = None # noqa

# Cogs to load on startup.
# From: configReader.py
initial_cogs: list[str] = None

# Flask app.
# From: app.py
app: Flask = None

# All loaded cogs, in format {"path": cog}.
# From: app.py
loaded_cogs: dict = None
