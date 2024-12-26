import os
from langchain.agents.agent_toolkits import SQLDatabaseToolkit
from langchain.agents import create_sql_agent
from langchain.chains import LLMChain
from langchain.prompts import PromptTemplate
from langchain.sql_database import SQLDatabase
from sqlalchemy import create_engine, text
from langchain_openai import ChatOpenAI
from time_period_extract import time_period_extractor
from config import config
from database_manager import database_manager
from sql_connection import client
from filter_constructor import filer_constructor
print(f" openai api {config.OPENAI_API_KEY}")

class FinancialDataAgent:
    def __init__(self, db_manager):
        self.llm = ChatOpenAI(
            model="gpt-4",
            temperature=0,
            max_tokens=None,
            timeout=None,
            max_retries=2,
            api_key=config.OPENAI_API_KEY
        )
        self.db_manager = db_manager
        self.toolkit = SQLDatabaseToolkit(db=SQLDatabase(db_manager.client), llm=self.llm)
        self.agent_executor = create_sql_agent(
            llm=self.llm,
            toolkit=self.toolkit,
            verbose=True
        )

    def find_matching_values(self, question):
        prompt = PromptTemplate(
            input_variables=["question"],
            template="""You are a financial data analyst. Based on the question, identify relevant 
            column names and their values from the dataset for filtering. The dataset includes the columns: 
            PNL Type, Category, realm_id, Account, Account Type, Account Sub Type, Business Unit, 
            Class, Customer, Vendor, Expense, Revenue, Net Revenue.

            Respond in this structured format:
            - PNL Type: [values]
            - Category: [values]
            - realm_id: [values]
            - Account: [values]
            - Account Type: [values]
            - Account Sub Type: [values]
            - Business Unit: [values]
            - Class: [values]
            - Customer: [values]
            - Vendor: [values]

            Question: {question}
            """
        )

        chain = LLMChain(llm=self.llm, prompt=prompt)
        extracted_terms = chain.run(question=question)
        relevant_terms = {
            'PNL Type': set(),
            'Category': set(),
            'realm_id': set(),
            'Account': set(),
            'Account Type': set(),
            'Account Sub Type': set(),
            'Business Unit': set(),
            'Class': set(),
            'Customer': set(),
            'Vendor': set()
        }

        for line in extracted_terms.split("\n"):
            line = line.strip()
            for key in relevant_terms.keys():
                if line.startswith(f"{key}:"):
                    values = line.replace(f"{key}:", "").strip()
                    relevant_terms[key].update(value.strip() for value in values.split(",") if value.strip())

        return relevant_terms

    def ask_question(self, question):
        time_periods = time_period_extractor.extract_time_periods(question)
        date_filter = time_period_extractor.construct_date_filter(time_periods)
        matches = self.find_matching_values(question)
        filter_clause = filer_constructor.construct_filter_clause(matches)

        if date_filter:
            filter_clause = f"{filter_clause} AND {date_filter}" if filter_clause else date_filter

        instruction = f"""You are a knowledgeable finance data analyst working for Rittman Analytics.
        Use the `{config.TABLE_NAME}` table to answer this question.
        Use the following SQL filter clause in your query: {filter_clause}, if the value is not null.
        Question: {question}
        """

        return self.agent_executor.run(instruction)





if __name__ == "__main__":
    OPENAI_API_KEY = config.OPENAI_API_KEY
    # db_manager = database_manager(client=db_client)
    agent = FinancialDataAgent(database_manager)

    available_months = database_manager.get_available_months()
    valid_time_range = database_manager.get_valid_time_range(available_months)

    print("Hi! Ask me a question about our company's profit and loss data")
    while True:
        question = input("\nYour question (or type 'QUIT' to exit): ")
        if question.lower() == 'quit':
            break

        final_answer = agent.ask_question(question)
        print(f"\nFinal Answer: {final_answer}\n")