from pymongo import MongoClient
import runtimeConfig


def setup():
    runtimeConfig.mongodb_client = MongoClient(runtimeConfig.mongodb_connection_string)
    runtimeConfig.mongodb_database = runtimeConfig.mongodb_client[runtimeConfig.mongodb_database_name]
    runtimeConfig.mongodb_user_collection = runtimeConfig.mongodb_database[runtimeConfig.mongodb_user_collection_name]