
import re
from dateutil import parser

class TimePeriodExtractor:
    @staticmethod
    def extract_time_periods(question):
        year_pattern = r'\b(20\d{2})\b'
        month_year_pattern = r'\b(Jan(?:uary)?|Feb(?:ruary)?|Mar(?:ch)?|Apr(?:il)?|May|Jun(?:e)?|Jul(?:y)?|Aug(?:ust)?|Sep(?:tember)?|Oct(?:ober)?|Nov(?:ember)?|Dec(?:ember)?)\s+(\d{4})\b'
        quarter_pattern = r'\b(Q[1-4])\s+(\d{4})\b'

        time_periods = []

        years = re.findall(year_pattern, question)
        for year in years:
            time_periods.append({'type': 'year', 'value': int(year)})

        month_years = re.findall(month_year_pattern, question, re.IGNORECASE)
        for month, year in month_years:
            date = parser.parse(f"{month} {year}")
            time_periods.append({'type': 'month', 'value': date})

        quarters = re.findall(quarter_pattern, question)
        for quarter, year in quarters:
            quarter_num = int(quarter[1])
            time_periods.append({'type': 'quarter', 'year': int(year), 'quarter': quarter_num})

        return time_periods

    @staticmethod
    def construct_date_filter(time_periods):
        date_filter = []
        for period in time_periods:
            if period['type'] == 'year':
                date_filter.append(f"EXTRACT(YEAR FROM date) = {period['value']}")
            elif period['type'] == 'month':
                date_filter.append(f"EXTRACT(MONTH FROM date) = {period['value'].month} AND EXTRACT(YEAR FROM date) = {period['value'].year}")
            elif period['type'] == 'quarter':
                start_month = (period['quarter'] - 1) * 3 + 1
                end_month = start_month + 2
                date_filter.append(f"(EXTRACT(MONTH FROM date) BETWEEN {start_month} AND {end_month} AND EXTRACT(YEAR FROM date) = {period['year']})")

        return " AND ".join(date_filter) if date_filter else ""
    


time_period_extractor=TimePeriodExtractor()