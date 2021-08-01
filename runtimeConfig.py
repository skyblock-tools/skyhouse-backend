from flask import Flask


# Configuration

# MongoDB connection URI.
# From: configReader.py
mongodb_connection_string: str = None

# Redis connection host and port
# From: configReader.py
redis_host: str = "localhost"
redis_port: int = 6379

# Cogs to load on startup.
# From: configReader.py
initial_cogs: list[str] = None

# Flask app.
# From: app.py
app: Flask = None

# All loaded cogs, in format {"path": cog}.
# From: app.py
loaded_cogs: dict = None
