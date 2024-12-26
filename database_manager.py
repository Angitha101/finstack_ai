from config import config
from sqlalchemy import create_engine, text
from datetime import datetime
from dateutil.relativedelta import relativedelta
from sql_connection import client


class DatabaseManager:
    def __init__(self, client):
        self.client = client
        self.table_name = config.TABLE_NAME

    def get_available_months(self):
        query = f"""
        SELECT DISTINCT 
        TO_CHAR(date, 'YYYY-MM') AS month
        FROM {self.table_name}
        ORDER BY month DESC
        """

        with self.client.connect() as connection:
            result = connection.execute(text(query))
            return [row[0] for row in result]

    def get_valid_time_range(self, available_months):
        if not available_months:
            return None, None
        available_months_dt = [datetime.strptime(month, '%Y-%m') for month in available_months]
        latest_month = max(available_months_dt)
        earliest_month = min(available_months_dt)
        valid_start = (earliest_month - relativedelta(months=2)).replace(day=1)


database_manager=DatabaseManager(client=client)