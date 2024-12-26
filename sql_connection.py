from sqlalchemy import create_engine, text
import os
from dotenv import load_dotenv
load_dotenv()

DB_HOST = os.getenv("DB_HOST")
DB_PORT = os.getenv("DB_PORT")
DB_NAME = os.getenv("DB_NAME")
DB_USER = os.getenv("DB_USER")
DB_PASSWORD = os.getenv("DB_PASSWORD")
TABLE_NAME="finstack_pnl"


sqlalchemy_url=f'postgresql://{DB_USER}:{DB_PASSWORD}@{DB_HOST}:{DB_PORT}/{DB_NAME}'
client=create_engine(sqlalchemy_url)

# Connect to the database and perform operations
with client.connect() as connection:
    result = connection.execute(text(f"SELECT * FROM {TABLE_NAME}"))
    # for row in result:
    #     print(row)
    # Print column names
    column_names = result.keys()
    print("Column names:", column_names)