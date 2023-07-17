import os
from dotenv import load_dotenv

if not os.path.exists('.env'):
    raise Exception("No .env file found. Please create .env file. (README.md)")

load_dotenv('.env')

DB_HOST = os.getenv("DB_HOST"),
DB_NAME = os.getenv("DB_NAME"),
DB_USER = os.getenv("DB_USER"),
DB_PASSWORD = os.getenv("DB_PASSWORD")
