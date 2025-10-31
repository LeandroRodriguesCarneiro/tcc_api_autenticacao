import os
from dotenv import load_dotenv

load_dotenv()

class Settings():
    SECRET_KEY = os.getenv("SECRET_KEY")
    ALGORITHM = os.getenv("ALGORITHM")
    DB_USER = os.getenv("DB_USER")
    DB_PSW = os.getenv("DB_PSW")
    DB_HOST = os.getenv("DB_HOST")
    DB_PORT = os.getenv("DB_PORT")
    DB_DATABASE = os.getenv("DB_DATABASE")
    ACCESS_TOKEN_EXPIRE_MINUTES = 30 * 60
    ACCESS_TOKEN_EXPIRE_HOURS = 3 * 60 ** 2