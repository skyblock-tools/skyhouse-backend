db.getSiblingDB("skyhouse");

db.createUser({
    user: _getEnv("MONGO_USERNAME"),
    pwd: _getEnv("MONGO_PASSWORD"),
    roles: [
        {role: "readWrite", db: "skyhouse",},
        {role: "dbAdmin", db: "skyhouse",},
    ],
});
db.createCollection("users");
