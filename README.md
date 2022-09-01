
# skyhouse-backend-python

## Running (docker)
- Install Docker: `curl -sSL https://get.docker.com/ | sh`
- Install Docker Compose: `curl -L "https://github.com/docker/compose/releases/download/1.17.1/docker-compose-$(uname -s)-$(uname -m)" -o /usr/local/bin/docker-compose && chmod +x /usr/local/bin/docker-compose`
- Edit `.mongo_credentials.env` to the following format:
```env
MONGODB_INITDB_ROOT_USERNAME=admin
MONGODB_INITDB_ROOT_PASSWORD=<admin_password>
MONGODB_INITDB_DATABASE=skyhouse
MONGO_USERNAME=skyhouse
MONGO_PASSWORD=<database_password>

```
- Copy `config_template.json` to `config.json` and edit all appropriate fields.
- Ensure that mongodb and redis configurations will work with docker:
```json
{
    "mongodb_connection_string": "mongodb://skyhouse:<database_password>@%2Fetc%2Fsock%2Fmongodb-27017.sock",
    "mongodb_database_name": "skyhouse",
    "mongodb_user_collection_name": "users",
    "redis_options": {
        "unix_socket_path": "/etc/sock/redis.sock"
    },
}
```
- Start all services: `docker-compose up -d`
## Info
- The API runs on port 8000, and all endpoints are prefixed with `/api`.
