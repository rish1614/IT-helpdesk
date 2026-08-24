import os
from dotenv import load_dotenv

load_dotenv()


class Config:
    SECRET_KEY = os.getenv("SECRET_KEY", "dev-secret-key")
    MONGO_URI = os.getenv("MONGO_URI", "mongodb://localhost:27017/")
    DB_NAME = os.getenv("DB_NAME", "it_helpdesk")
    TICKETS_COLLECTION = os.getenv("TICKETS_COLLECTION", "tickets")
    DEBUG = os.getenv("FLASK_DEBUG", "false").lower() == "true"
    USE_IN_MEMORY_DB = os.getenv("USE_IN_MEMORY_DB", "false").lower() == "true"
