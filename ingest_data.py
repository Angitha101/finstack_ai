import psycopg2
import pandas as pd
from dotenv import load_dotenv
import os
load_dotenv()
from config import config

CSV_FILE_PATH="/Users/angitha/Developer/finstack_ai/PNL Data(in).csv"


try:
    conn=psycopg2.connect(
        host=config.DB_HOST,
        port=config.DB_PORT, 
        dbname=config.DB_NAME, 
        user=config.DB_USER, 
        password=config.DB_PASSWORD
    )
    conn.autocommit=True,
    print("connected to database")
except Exception as e:
    print (f"Error connecting to database: {e}")
    exit()



def load_csv_to_df(path):
    try:
        df=pd.read_csv(path)
        print("CSV loaded successfully")
        return df
    except Exception as e:
        print(f"Error reading csv: {e}")
        exit()


def create_table_if_not_exists(conn, table_name):
    create_table_query = f"""
    CREATE TABLE IF NOT EXISTS {table_name} (
        pnl_type VARCHAR,
        category VARCHAR,
        realm_id INT,
        date DATE,
        account VARCHAR,
        account_type VARCHAR,
        account_sub_type VARCHAR,
        business_unit VARCHAR,
        class VARCHAR,
        customer VARCHAR,
        vendor VARCHAR,
        expense NUMERIC,
        revenue NUMERIC,
        net_revenue NUMERIC
    );
    """
    try:
        with conn.cursor() as cursor:
            cursor.execute(create_table_query)
            print(f"Table '{table_name}' is ready.")
    except Exception as e:
        print(f"Error creating table: {e}")
        exit()


def insert_data_postgres(conn, df, table_name):
    try:
        with conn.cursor() as cursor:
            for _, row in df.iterrows():
                cursor.execute(
                    f"""
                    INSERT INTO {table_name} (
                        pnl_type, category, realm_id, date, account, account_type, 
                        account_sub_type, business_unit, class, customer, vendor, 
                        expense, revenue, net_revenue
                    ) VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s)
                    """,
                    (
                        row['PNL Type'], row['Category'], row['realm_id'], row['Date'], row['Account'], 
                        row['Account Type'], row['Account Sub Type'], row['Business Unit'], 
                        row['Class'], row['Customer'], row['Vendor'], row['Expense'], 
                        row['Revenue'], row['Net Revenue']
                    )
                )
            print("Data inserted successfully")
    except Exception as e:
        print(f"Error inserting data into PostgreSQL: {e}")
        conn.rollback()



def main():
    create_table_if_not_exists(conn, config.TABLE_NAME)
    df = load_csv_to_df(CSV_FILE_PATH)
    insert_data_postgres(conn, df, config.TABLE_NAME)
    conn.close()

if __name__ == "__main__":
    main()
