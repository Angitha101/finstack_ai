import os
from dotenv import load_dotenv
load_dotenv()

class Config:
    OPENAI_API_KEY=os.getenv("OPENAI_API_KEY")
    TABLE_NAME = os.getenv("TABLE_NAME")
    DB_HOST = os.getenv("DB_HOST")
    DB_PORT = os.getenv("DB_PORT")
    DB_NAME = os.getenv("DB_NAME")
    DB_USER = os.getenv("DB_USER")
    DB_PASSWORD = os.getenv("DB_PASSWORD")

config =Config()